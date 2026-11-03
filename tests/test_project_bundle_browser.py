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
                # Real Chromium CSP enforcement against the ZIP-served document:
                # DevTools evaluation initiates the probes, but browser policy
                # must reject injected scripts and cross-origin network traffic.
                escaped_routes = []

                def record_external_route(route):
                    escaped_routes.append(route.request.url)
                    route.abort()

                page.route('https://rea-csp-blocked.invalid/**', record_external_route)
                page.evaluate("""() => {
                    window.__reaCspViolations = [];
                    document.addEventListener('securitypolicyviolation', event => {
                        window.__reaCspViolations.push({
                            directive: event.effectiveDirective,
                            blocked: event.blockedURI
                        });
                    });
                    const inline = document.createElement('script');
                    inline.textContent = 'window.__reaCspInlineExecuted = true';
                    document.head.appendChild(inline);
                    const external = document.createElement('script');
                    external.src = 'https://rea-csp-blocked.invalid/blocked.js';
                    document.head.appendChild(external);
                }""")
                page.evaluate("""async () => {
                    try {
                        await fetch('https://rea-csp-blocked.invalid/api/exfil');
                    } catch (error) {
                        window.__reaCspFetchRejected = true;
                    }
                }""")
                page.wait_for_function('window.__reaCspViolations.length >= 3', timeout=5000)
                violations = page.evaluate('window.__reaCspViolations')
                assert any(v['directive'] == 'script-src-elem' and
                           v['blocked'] == 'inline' for v in violations), violations
                assert any(v['directive'] == 'script-src-elem' and
                           v['blocked'].endswith('/blocked.js') for v in violations), violations
                assert any(v['directive'] == 'connect-src' and
                           v['blocked'].endswith('/api/exfil') for v in violations), violations
                assert page.evaluate('window.__reaCspInlineExecuted') is None
                assert page.evaluate('window.__reaCspFetchRejected') is True
                # Playwright's request event can record a CSP-blocked ATTEMPT.
                # A route callback indicates an actual outgoing network attempt.
                assert not escaped_routes, escaped_routes
                assert not errors, errors
            finally:
                browser.close()
    finally:
        child.terminate()
        try:
            child.communicate(timeout=8)
        except subprocess.TimeoutExpired:
            child.kill()
            child.communicate(timeout=8)
