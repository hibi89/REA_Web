"""Real REA first-party generated FastAPI template with original read-only SQLite API.

Only the repository's own trusted code is launched after writing test-owned SQLite;
the inspected ZIP is never imported/extracted/executed by the adapter.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import time
from urllib.request import urlopen
import zipfile

from playwright.sync_api import expect, sync_playwright

from rea.adapter.backend_zip import inspect_backend_zip
from rea.adapter.backend_schema import inspect_backend_schema
from rea.adapter.frontend_bridge import make_review, generate_frontend, BridgeError
from tests_static_fixture import FABLE

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = REPO_ROOT / "rea" / "templates" / "app.py"

FIRSTPARTY_BINDINGS = {
    "list": {
        "path": "/api/items", "field": "items",
        "pagination": {
            "total_field": "total", "limit_param": "limit",
            "offset_param": "offset", "page_size": 100,
        },
    },
    "metrics": {"path": "/api/summary", "field": "__root__"},
    "detail": {"path": "/api/items/{item_id}", "field": "__root__",
               "path_param": "item_id"},
    "presentation": {
        "item": {"id": "id", "name": "title", "category": "category", "status": None},
        "metrics": {"total": "total_items", "completed": "total_categories",
                    "pending": None},
        "metric_labels": {"total": "전체 항목", "completed": "분류 수",
                          "pending": None},
        "detail_fields": ["id", "title", "category"],
    },
}


def test_firstparty_backend_paginated_browser_contract(tmp_path):
    original = TEMPLATE.read_bytes()
    source = tmp_path / "owned_firstparty.zip"
    with zipfile.ZipFile(source, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("app.py", original)
    backend = inspect_backend_zip(source)
    schema = inspect_backend_schema(source)
    review = make_review(FABLE, backend, FIRSTPARTY_BINDINGS, schema=schema)
    assert review["backend"]["runtime_verified"] is False
    assert review["bindings"]["list"]["pagination"]["page_size"] == 100
    dashboard = tmp_path / "dashboard"
    generate_frontend(review, dashboard, owner_confirmed=True)

    # Run the repo-owned template, not any submitted customer code or ZIP member.
    (tmp_path / "static").mkdir()
    trusted = original.decode("utf-8") + (
        "\nfrom fastapi.staticfiles import StaticFiles\n"
        'app.mount("/dashboard", StaticFiles(directory=ROOT / "dashboard", '
        'html=True), name="dashboard")\n'
    )
    (tmp_path / "app.py").write_text(trusted, encoding="utf-8")
    (tmp_path / "schema_preview.json").write_text(json.dumps({
        "review_status": "UNAPPROVED", "source_kind": "csv", "fields": [],
    }), encoding="utf-8")

    with sqlite3.connect(tmp_path / "data.sqlite") as db:
        db.execute("CREATE TABLE items (id TEXT PRIMARY KEY, title TEXT, "
                   "category TEXT, attributes_json TEXT)")
        db.executemany("INSERT INTO items VALUES (?,?,?,?)", [
            (f"item-{i:03d}", f"Item {i:03d}",
             "alpha" if i % 2 == 0 else "beta", "{}")
            for i in range(130)
        ])
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    origin = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1",
         "--port", str(port), "--log-level", "warning"],
        cwd=tmp_path, env={**os.environ, "PYTHONPATH": str(tmp_path)},
        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
    )
    try:
        for _ in range(80):
            if process.poll() is not None:
                raise AssertionError("first-party FastAPI failed to start")
            try:
                with urlopen(origin + "/health", timeout=0.7) as result:
                    if result.status == 200:
                        break
            except OSError:
                time.sleep(0.15)
        else:
            raise AssertionError("first-party FastAPI not ready")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page(viewport={"width": 1360, "height": 800})
                errors, requests = [], []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.on("request", lambda request: requests.append(request.url))
                result = page.goto(origin + "/dashboard/", wait_until="networkidle",
                                   timeout=30000)
                assert result is not None and result.status == 200
                expect(page.locator("#connection-text")).to_have_text("CONNECTED")
                expect(page.locator("#jobs tr")).to_have_count(130)
                expect(page.locator("#kpi-total")).to_have_text("130")
                expect(page.locator("#kpi-completed")).to_have_text("2")
                expect(page.locator("#kpi-label-completed")).to_have_text("분류 수")
                assert page.locator("#kpi-pending").locator("xpath=..").is_hidden()
                page.locator("#search").fill("Item 129")
                expect(page.locator("#jobs tr")).to_have_count(1)
                page.locator("#jobs button").click()
                expect(page.locator("#detail")).to_contain_text("item-129")
                expect(page.locator("#detail")).to_contain_text("Item 129")
                assert not errors, errors
                assert all(request.startswith(origin + "/") for request in requests)
                assert any("offset=100" in request for request in requests)
            finally:
                browser.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
