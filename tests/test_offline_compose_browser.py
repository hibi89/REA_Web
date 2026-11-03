"""One-command ZIP+Fable+mapping -> generated UI -> actual localhost HTTP/Chromium.

The FastAPI backend is fully self-authored by this test. It is written from
the same source bytes placed in the demo ZIP; the CLI itself never runs ZIP
members, downloads external content, or claims customer authorization.
"""
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
from tests_static_fixture import FABLE, BINDINGS


TRUSTED_SOURCE = '''from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()
JOBS = [
    {"id":"A-1","name":"검사 결과","category":"quality","status":"done"},
    {"id":"B-2","name":"월간 보고서","category":"report","status":"pending"},
    {"id":"C-3","name":"정산 작업","category":"finance","status":"done"}
]

@app.get("/api/health")
def health(): return {"ok":True}

@app.get("/api/jobs")
def jobs(): return {"items":JOBS}

@app.get("/api/metrics")
def metrics(): return {"total":3,"completed":2,"pending":1}

@app.get("/api/jobs/{job_id}")
def detail(job_id:str):
    for item in JOBS:
        if item["id"] == job_id: return item
    raise HTTPException(status_code=404)

app.mount("/dashboard", StaticFiles(
    directory=str(Path(__file__).parent / "dashboard"), html=True), name="dashboard")
'''


def test_one_command_generated_frontend_serves_actual_localhost_api(tmp_path):
    source_zip = tmp_path / "self_authored_backend.zip"
    with zipfile.ZipFile(source_zip,"w",compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("trusted_backend.py", TRUSTED_SOURCE)
    fable = tmp_path / "fable.json"
    fable.write_text(json.dumps(FABLE),encoding="utf-8")
    bindings = tmp_path / "bindings.json"
    bindings.write_text(json.dumps(BINDINGS),encoding="utf-8")

    command = [sys.executable, "-m", "rea.adapter.offline_compose",
               "--backend-zip",str(source_zip),"--fable",str(fable),
               "--bindings",str(bindings),"--out",str(tmp_path/"dashboard"),
               "--owner-authorized-source","--owner-confirmed"]
    generated = subprocess.run(command, capture_output=True, text=True, timeout=25)
    assert generated.returncode == 0, generated.stderr
    report = json.loads(generated.stdout)
    assert report["frontend_source_generated"] is True
    assert report["backend_executed"] is False
    assert report["customer_runtime_verified"] is False
    assert report["release_allowed"] is False
    assert (tmp_path/"dashboard"/"app.js").is_file()

    # Trusted test code (not a ZIP import/extraction) is launched separately
    # to assess the actual generated frontend against real read-only HTTP.
    (tmp_path/"trusted_backend.py").write_bytes(TRUSTED_SOURCE.encode("utf-8"))
    with socket.socket() as sock:
        sock.bind(("127.0.0.1",0))
        port = sock.getsockname()[1]
    address = f"http://127.0.0.1:{port}"
    env = {**os.environ,"PYTHONPATH":str(tmp_path)}
    process = subprocess.Popen(
        [sys.executable,"-m","uvicorn","trusted_backend:app",
         "--host","127.0.0.1","--port",str(port),"--log-level","warning"],
        cwd=tmp_path, env=env, stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    try:
        for _ in range(75):
            if process.poll() is not None:
                raise AssertionError("trusted synthetic backend exited")
            try:
                with urlopen(address+"/api/health",timeout=0.6) as response:
                    if response.status==200: break
            except OSError:
                time.sleep(0.15)
        else:
            raise AssertionError("trusted synthetic localhost did not become ready")

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page(viewport={"width":1280,"height":800})
                errors, requests = [], []
                page.on("pageerror",lambda error:errors.append(str(error)))
                page.on("request",lambda request:requests.append(request.url))
                response=page.goto(address+"/dashboard/",
                                   wait_until="networkidle",timeout=30000)
                assert response is not None and response.status==200
                expect(page.locator("#connection-text")).to_have_text("CONNECTED")
                expect(page.locator("#kpi-total")).to_have_text("3")
                expect(page.locator("#kpi-completed")).to_have_text("2")
                expect(page.locator("#kpi-pending")).to_have_text("1")
                expect(page.locator("#jobs tr")).to_have_count(3)

                page.locator("#search").fill("보고서")
                expect(page.locator("#jobs tr")).to_have_count(1)
                page.locator("#jobs button").click()
                expect(page.locator("#detail")).to_contain_text("B-2")
                expect(page.locator("#detail")).to_contain_text("월간 보고서")

                # Test-only access denial: no stale private table/KPIs remain.
                page.route("**/api/metrics",lambda route:route.fulfill(
                    status=401,content_type="application/json",body="{}"))
                page.reload(wait_until="networkidle")
                expect(page.locator("#connection-text")).to_have_text("API ERROR")
                expect(page.locator("#jobs tr")).to_have_count(0)
                expect(page.locator("#kpi-total")).to_have_text("—")
                page.unroute("**/api/metrics")
                page.locator("#retry").click()
                expect(page.locator("#connection-text")).to_have_text("CONNECTED")
                expect(page.locator("#kpi-total")).to_have_text("3")
                # Reload preserved the page, including its active search query.
                expect(page.locator("#jobs tr")).to_have_count(3)
                assert not errors,errors
                assert requests and all(x.startswith(address+"/") for x in requests)
                assert any("/api/jobs" in x for x in requests)
            finally:
                browser.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
