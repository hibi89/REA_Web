"""Unpack deterministic trusted SYNTHETIC bundle and run its REAL local FastAPI/Chromium."""
from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import urlopen
import zipfile

from playwright.sync_api import expect, sync_playwright
from test_project_bundle import package


def test_bundle_clean_extraction_real_http_and_browser(tmp_path):
    zipped, _ = package(tmp_path)
    clean = tmp_path / 'CLEAN_FRESH'
    clean.mkdir()
    with zipfile.ZipFile(zipped) as archive:
        archive.extractall(clean)
    check = subprocess.run([sys.executable, 'runtime_entry.py', '--check'], cwd=clean,
                           capture_output=True, text=True, timeout=15)
    assert check.returncode == 0, check.stderr
    with socket.socket() as port_sock:
        port_sock.bind(('127.0.0.1', 0))
        port = port_sock.getsockname()[1]
    child = subprocess.Popen([sys.executable, 'runtime_entry.py', '--run-trusted-synthetic', '--port', str(port)],
                             cwd=clean, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        base = f'http://127.0.0.1:{port}'
        for _ in range(80):
            assert child.poll() is None, 'trusted fixture stopped before startup'
            try:
                with urlopen(base + '/api/jobs', timeout=0.7) as result:
                    assert result.status == 200
                    assert len(json.load(result)['items']) == 2
                break
            except OSError:
                time.sleep(.15)
        else:
            raise AssertionError('trusted fixture server HTTP readiness failed')
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                page = browser.new_page(viewport={'width': 1280, 'height': 850})
                errors, failures, requests = [], [], []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.on('requestfailed', lambda r: failures.append(r.url))
                page.on('request', lambda r: requests.append(r.url))
                response = page.goto(base + '/dashboard/', wait_until='networkidle')
                assert response.status == 200
                expect(page.locator('#connection-text')).to_have_text('CONNECTED')
                expect(page.locator('#kpi-total')).to_have_text('2')
                expect(page.locator('#kpi-completed')).to_have_text('1')
                expect(page.locator('#kpi-pending')).to_have_text('1')
                expect(page.locator('#jobs tr')).to_have_count(2)
                page.locator('#search').fill('Pending')
                expect(page.locator('#jobs tr')).to_have_count(1)
                page.get_by_role('button', name='상세').click()
                expect(page.locator('#detail')).to_contain_text('X2')
                assert not errors, errors
                assert not failures, failures
                assert all(u.startswith(base + '/') for u in requests), requests
            finally:
                browser.close()
    finally:
        child.terminate()
        try:
            child.communicate(timeout=8)
        except subprocess.TimeoutExpired:
            child.kill()
            child.communicate(timeout=8)
