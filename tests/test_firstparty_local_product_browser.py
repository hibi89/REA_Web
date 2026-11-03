"""Actual one-command first-party CSV→SQLite→reviewed dashboard→Chromium.

No customer ZIP, no external network, no changing original REA template.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright
import pytest

from rea.adapter.local_product import build, MOUNT
from rea.adapter.frontend_bridge import BridgeError
from rea.mvp import TEMPLATES
from tests_static_fixture import FABLE

ROOT = Path(__file__).resolve().parents[1]


def fixture(tmp_path):
    data = tmp_path / "owned_test.csv"
    with data.open("w", encoding="utf-8", newline="") as handle:
        writer=csv.writer(handle)
        writer.writerow(("id","title","category"))
        for index in range(130):
            writer.writerow((f"item-{index:03d}", f"Item {index:03d}",
                             "alpha" if index%2==0 else "beta"))
    fable = tmp_path / "fable.json"
    fable.write_text(json.dumps(FABLE), encoding="utf-8")
    bindings = ROOT / "samples" / "rea_firstparty_bindings.json"
    return data, fable, bindings


def test_all_guards_before_owner_read_or_publish(tmp_path):
    dest=tmp_path/"missing"
    with pytest.raises(BridgeError,match="owner-authorized"):
        build(tmp_path/"absent.csv",tmp_path/"none.json",tmp_path/"none.json",
              dest, owner_confirmed=True)
    assert not dest.exists()
    data,fable,bindings=fixture(tmp_path)
    with pytest.raises(BridgeError,match="owner-confirmed"):
        build(data,fable,bindings,dest,owner_authorized_data=True)
    assert not dest.exists()
    with pytest.raises(ValueError,match="changed since approved"):
        build(data,fable,bindings,dest,owner_confirmed=True,
              owner_authorized_data=True,expected_source_sha256="0"*64)
    assert not dest.exists()


def test_full_local_runnable_app_with_native_backend_and_real_chromium(tmp_path):
    data,fable,bindings=fixture(tmp_path)
    out=tmp_path/"REA_my_app"
    start_hash=hashlib.sha256((TEMPLATES/"app.py").read_bytes()).hexdigest()
    cp=subprocess.run(
        [sys.executable,"-m","rea.adapter.local_product",
         "--data",str(data),"--fable",str(fable),
         "--bindings",str(bindings),"--out",str(out),
         "--owner-authorized-data","--owner-confirmed"],
        cwd=ROOT,capture_output=True,text=True,timeout=30)
    assert cp.returncode==0,cp.stderr
    receipt=json.loads(cp.stdout)
    assert receipt["status"]=="LOCAL_APP_GENERATED_NOT_DEPLOYED"
    assert receipt["row_count"]==130
    assert receipt["runtime_verified"] is False
    assert receipt["commercial_release_allowed"] is False
    assert receipt["source_sha256"]==hashlib.sha256(data.read_bytes()).hexdigest()
    assert (TEMPLATES/"app.py").read_bytes() == (out/"app.py").read_bytes()[:-len(MOUNT)]
    assert hashlib.sha256((TEMPLATES/"app.py").read_bytes()).hexdigest()==start_hash
    assert set(x.name for x in (out/"dashboard").iterdir())=={
        "README_KO.md","manifest.json","index.html","style.css","app.js"}
    assert (out/"data.sqlite").is_file()
    assert (out/"README.md").is_file()
    assert (out/"RUN_LOCAL_WINDOWS.cmd").read_bytes().endswith(b"\r\n")
    if sys.platform=="win32":
        check = subprocess.run(["cmd", "/d", "/c", str(out/"RUN_LOCAL_WINDOWS.cmd"), "--check"],
                               cwd=out, capture_output=True,text=True,timeout=20)
        assert check.returncode==0,check.stderr
        assert "NOT checked" in check.stdout
    assert not (out/"owned_test.csv").exists()
    assert not (out/"fable.json").exists()

    repeat=subprocess.run(
        [sys.executable,"-m","rea.adapter.local_product",
         "--data",str(data),"--fable",str(fable),
         "--bindings",str(bindings),"--out",str(out),
         "--owner-authorized-data","--owner-confirmed"],
        cwd=ROOT,capture_output=True,text=True,timeout=30)
    assert repeat.returncode==2
    assert "output exists" in repeat.stderr

    with socket.socket() as sock:
        sock.bind(("127.0.0.1",0))
        port=sock.getsockname()[1]
    origin=f"http://127.0.0.1:{port}"
    process=subprocess.Popen(
        [sys.executable,"-m","uvicorn","app:app","--host","127.0.0.1",
         "--port",str(port),"--log-level","warning"],
        cwd=out,env={**os.environ,"PYTHONPATH":str(out)},
        stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)
    try:
        for _ in range(80):
            if process.poll() is not None:
                raise AssertionError("generated first-party server died")
            try:
                with urlopen(origin+"/health",timeout=0.7) as response:
                    if response.status==200:
                        break
            except OSError:
                time.sleep(0.15)
        else:
            raise AssertionError("generated backend not ready")
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True)
            try:
                page=browser.new_page(viewport={"width":1360,"height":800})
                errors,requests=[],[]
                page.on("pageerror",lambda error: errors.append(str(error)))
                page.on("request",lambda request: requests.append(request.url))
                assert page.goto(origin+"/",wait_until="domcontentloaded").status==200
                result=page.goto(origin+"/dashboard/",wait_until="networkidle",timeout=30000)
                assert result.status==200
                expect(page.locator("#connection-text")).to_have_text("CONNECTED")
                expect(page.locator("#jobs tr")).to_have_count(130)
                expect(page.locator("#kpi-total")).to_have_text("130")
                expect(page.locator("#kpi-completed")).to_have_text("2")
                assert page.locator("#kpi-pending").locator("xpath=..").is_hidden()
                page.locator("#search").fill("Item 129")
                expect(page.locator("#jobs tr")).to_have_count(1)
                page.locator("#jobs button").click()
                expect(page.locator("#detail")).to_contain_text("item-129")
                assert any("offset=100" in url for url in requests)
                assert all(url.startswith(origin+"/") for url in requests)
                assert not errors,errors
            finally:
                browser.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
