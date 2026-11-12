"""Windows Chrome + Edge real owner review UI smoke on loopback.

Runs only on hosted Windows, not a user's physical Windows 10/11 PC. Uses
a synthetic unapproved packet and saves local opinion JSON only.
"""
from __future__ import annotations

import json
import socket
import sys
from pathlib import Path
from threading import Thread
import time

import pytest

from rea.website_p95 import create_review_app, make_packet, _hash


def synthetic_packet():
    subject = {"fixture_sha256": "f" * 64, "viewports": {"desktop": {}},
               "site_use": "synthetic_local_only"}
    p85 = {
        "schema_version": "rea.website.p85.v1",
        "subject": subject, "review_digest": _hash(subject),
        "production_release": "HOLD", "site_approval": False,
        "astra_spec_draft": {
            "implementation_ready": False,
            "candidate_features": [{
                "feature": "search", "review_status": "requires_review",
                "evidence": [{"id": "evidence_synthetic"}],
            }],
        },
    }
    return make_packet(p85)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows Chrome/Edge channel verification")
@pytest.mark.parametrize("channel", ["chrome", "msedge"])
def test_real_windows_browser_local_owner_review_app(channel, tmp_path):
    from playwright.sync_api import sync_playwright
    import uvicorn

    storage = tmp_path / ("opinions-" + channel)
    storage.mkdir()
    packet = synthetic_packet()
    app = create_review_app(packet, storage)
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(
        app, host="127.0.0.1", port=port, log_level="error",
        access_log=False))
    worker = Thread(target=server.run, daemon=True)
    worker.start()
    try:
        for _ in range(140):
            if server.started:
                break
            time.sleep(0.05)
        assert server.started
        with sync_playwright() as p:
            browser = p.chromium.launch(channel=channel, headless=True)
            try:
                context = browser.new_context(
                    service_workers="block",
                    accept_downloads=False)
                page = context.new_page()
                browser_errors = []
                page.on("pageerror", lambda err: browser_errors.append(str(err)))
                response = page.goto(f"http://127.0.0.1:{port}/",
                                     wait_until="domcontentloaded", timeout=12000)
                assert response.status == 200
                page.wait_for_function(
                    "document.getElementById('status').textContent.includes('근거 SHA:')",
                    timeout=10000)
                assert page.locator("#features li").count() == 1
                page.locator("#reviewer").fill("Windows Human Reviewer")
                page.locator("#decision").select_option("approve_synthetic_proposal")
                page.locator("#reason").fill(
                    "Synthetic local browser evidence is only a functional proposal.")
                page.locator("#save").click()
                page.wait_for_function(
                    "document.getElementById('out').textContent.includes('검토 기록 ID:')",
                    timeout=10000)
                assert "HOLD" in page.locator("#out").inner_text()
                assert not browser_errors
                saved = list(storage.glob("*.json"))
                assert len(saved) == 1
                record = json.loads(saved[0].read_text(encoding="utf-8"))
                assert record["decision"] == "approve_synthetic_proposal"
                assert record["site_use_license_verified"] is False
                assert record["commercial_release"] == "HOLD"
                assert record["reviewer_identity_verified"] is False
                context.close()
            finally:
                browser.close()
    finally:
        server.should_exit = True
        worker.join(timeout=8)
