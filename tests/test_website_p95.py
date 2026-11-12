"""Original REA_Web P95: GUI review, real pinned Fable Record schema and safe delivery.

All inputs are synthetic local fixtures. These tests do not grant legal site
rights or claim to have performed a human-operated headed Fable Record.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import socket
from threading import Thread
import time
import zipfile

import pytest
from fastapi.testclient import TestClient

from rea.website_p95 import (
    create_review_app, create_delivery_zip, inspect_fable_record,
    make_packet, verify_delivery_zip, WebsiteReviewError, _hash,
)
from rea.website_p85 import build_p85, inspect_p85
from rea.website_p70 import APPROVAL_TOKEN, PERMISSION_TOKEN

ROOT = Path(__file__).resolve().parents[1]
FABLE = ROOT / ".vendor/fable/engines/fable51"
ASTRA = ROOT / ".vendor/astra/engines/astra_p4"
CSV = "id,title,category,price\nA001,커피,음료,3000\nA002,차,음료,2000\nA003,연필,문구,500\n"
JS = """
const rows=[{id:'A001',title:'커피',category:'음료'},
{id:'A002',title:'차',category:'음료'},{id:'A003',title:'연필',category:'문구'}];
function draw(){
 const q=document.querySelector('#search').value, cat=document.querySelector('#category').value;
 document.querySelector('#count').textContent=rows.filter(
  x=>(!q||x.title.includes(q)) && (!cat||x.category===cat)).length+'건';
}
document.querySelector('#search').addEventListener('input',draw);
document.querySelector('#category').addEventListener('change',draw);
document.querySelector('#first-detail').addEventListener('click',()=>{
 document.querySelector('#detail').textContent='커피'; });
draw();
"""
HTML = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>synthetic owner test</title><style>'
        'body{padding:16px;margin:0;font-family:Arial}input,select{max-width:100%}'
        '</style></head><body><main><h1>합성 사이트 샘플</h1>'
        '<label>검색<input id="search" type="search"></label>'
        '<label>분류<select id="category"><option value="">전체</option>'
        '<option value="음료">음료</option><option value="문구">문구</option></select></label>'
        '<div id="count"></div><button id="first-detail">상세 보기</button>'
        '<div id="detail"></div><script>' + JS + '</script></main></body></html>')


def write_inputs(tmp_path):
    html, csv = tmp_path / "reference.html", tmp_path / "owner.csv"
    html.write_text(HTML, encoding="utf-8")
    csv.write_text(CSV, encoding="utf-8")
    kwargs = {
        "fixture_sha256": hashlib.sha256(html.read_bytes()).hexdigest(),
        "owner_sha256": hashlib.sha256(csv.read_bytes()).hexdigest(),
        "fixture_permission": PERMISSION_TOKEN,
        "owner_approval": APPROVAL_TOKEN,
        "fable_root": FABLE, "astra_root": ASTRA,
    }
    return html, csv, kwargs


def record_fixture(tmp_path):
    """Matches safe, explicit structural subset of frozen Fable 5.1 schema."""
    # Pin real package/source availability before checking the contract.
    assert (FABLE / "scanner/record_scan.py").is_file()
    record = {
        "schema_version": "1.0", "scan_mode": "record",
        "target": {"input_url": "http://127.0.0.1:19999"},
        "record": {
            "allowed_origins": ["http://127.0.0.1:19999"],
            "stop_reason": "enter", "scope": "allowed_origin_main_frames_only",
            "pages": [{"page_id": "page-001", "navigation_id": "nav-0001",
                       "frame_id": "page-001-main", "allowed": True,
                       "url": "http://127.0.0.1:19999/"}],
            "interactions": [
                {"type": "click", "at_ms": 12345, "tag": "button",
                 "selector": "html:nth-of-type(1) > body:nth-of-type(1) > button:nth-of-type(1)"},
                {"type": "change", "at_ms": 12346, "tag": "select",
                 "selector": "html:nth-of-type(1) > body:nth-of-type(1) > select:nth-of-type(1)"},
            ],
        },
    }
    path = tmp_path / "record.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def fake_receipt():
    subject = {"fixture_sha256": "a" * 64, "viewports": {"desktop": {}},
               "site_use": "synthetic_local_only"}
    return {
        "schema_version": "rea.website.p85.v1",
        "review_digest": _hash(subject), "subject": subject,
        "production_release": "HOLD", "site_approval": False,
        "astra_spec_draft": {
            "implementation_ready": False,
            "candidate_features": [
                {"feature": "search", "review_status": "requires_review",
                 "evidence": [{"id": "ev_1"}]},
                {"feature": "detail", "review_status": "requires_review",
                 "evidence": [{"id": "ev_2"}]},
            ],
        },
    }


def _approval_json(packet, decision="approve_synthetic_proposal", **extra):
    return {
        "schema_version": "rea.website.p95.review.v1",
        "packet_sha256": packet["packet_sha256"],
        "review_digest": packet["review_digest"],
        "reviewer_claimed_label": "Local Synthetic Reviewer",
        "decision": decision,
        "rationale": "Synthetic evidence only; not a website rights or license approval.",
    } | extra


def _approved_record(tmp_path, packet):
    dest = tmp_path / "opinions"
    dest.mkdir(exist_ok=True)
    app = create_review_app(packet, dest)
    with TestClient(app) as client:
        token = client.get("/api/packet").json()["session_token"]
        response = client.post("/api/decisions", json=_approval_json(packet),
                               headers={"X-REA-Review-Token": token})
        assert response.status_code == 200, response.text
        assert response.json()["authorization_verified"] is False
        record = dest / (response.json()["record_id"] + ".json")
    return record


def test_real_fable_record_schema_safe_intake(tmp_path):
    path, sha = record_fixture(tmp_path)
    result = inspect_fable_record(path, expected_sha256=sha)
    assert result["record_mode"] == "record"
    assert result["same_origin_pages"] == 1
    assert result["interaction_marker_count"] == 2
    assert result["evidence_grade"] == "MANUAL_MARKERS_ONLY_NOT_CAUSAL"
    assert result["recorded_ui_behavior_approved"] is False
    assert "127.0.0.1" not in json.dumps(result)


@pytest.mark.parametrize("mutate", [
    lambda d: d.update(scan_mode="static"),
    lambda d: d["record"].update(allowed_origins=["https://example.org"]),
    lambda d: d["record"].update(allowed_origins=["http://127.0.0.1:19999",
                                                  "http://127.0.0.1:18888"]),
    lambda d: d["record"].update(stop_reason="stdin_unavailable"),
    lambda d: d["record"]["pages"][0].update(allowed=False),
    lambda d: d["record"]["interactions"][0].update(type="password"),
    lambda d: d["record"].update(scope="all_domains"),
])
def test_fable_record_scope_fail_closed(tmp_path, mutate):
    path, _ = record_fixture(tmp_path)
    source = json.loads(path.read_text())
    mutate(source)
    path.write_text(json.dumps(source), encoding="utf-8")
    with pytest.raises(WebsiteReviewError):
        inspect_fable_record(path, expected_sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def test_fable_record_tamper_sha_and_symlink_rejected(tmp_path):
    path, sha = record_fixture(tmp_path)
    path.write_text(path.read_text() + " ", encoding="utf-8")
    with pytest.raises(WebsiteReviewError, match="SHA"):
        inspect_fable_record(path, expected_sha256=sha)
    link = tmp_path / "record-link.json"
    try:
        link.symlink_to(path)
    except OSError:
        pytest.skip("Symlink not available")
    with pytest.raises(WebsiteReviewError):
        inspect_fable_record(link, expected_sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def test_packet_binds_p85_fingerprint_and_record(tmp_path):
    file, sha = record_fixture(tmp_path)
    record = inspect_fable_record(file, expected_sha256=sha)
    packet = make_packet(fake_receipt(), record)
    assert packet["commercial_release"] == "HOLD"
    assert packet["code_generation_authorized"] is False
    assert packet["fable_record"]["record_mode"] == "record"
    assert len(packet["features"]) == 2
    assert len(packet["packet_sha256"]) == 64
    bad = fake_receipt()
    bad["subject"]["fixture_sha256"] = "b" * 64
    with pytest.raises(WebsiteReviewError, match="fingerprint"):
        make_packet(bad, record)


def test_local_review_workbench_security_and_no_external_authorization(tmp_path):
    packet = make_packet(fake_receipt())
    folder = tmp_path / "opinions"
    folder.mkdir()
    app = create_review_app(packet, folder)
    with TestClient(app) as client:
        front = client.get("/")
        assert front.status_code == 200
        assert "script-src 'self'" in front.headers["content-security-policy"]
        assert client.get("/review.js").status_code == 200
        info = client.get("/api/packet")
        assert info.status_code == 200
        token = info.json()["session_token"]
        assert info.json()["permission_to_reconstruct"] is False
        assert client.get("/api/packet", headers={"host":"evil.example"}).status_code == 403
        assert client.post("/api/decisions", json=_approval_json(packet)).status_code == 403
        assert client.post("/api/decisions", json=_approval_json(packet),
                           headers={"X-REA-Review-Token": "forged"}).status_code == 403
        assert client.post("/api/decisions", json=_approval_json(packet),
                           headers={"X-REA-Review-Token": token,
                                    "Origin":"https://evil.example"}).status_code == 403
        bad = _approval_json(packet, review_digest="0"*64)
        assert client.post("/api/decisions", json=bad,
                           headers={"X-REA-Review-Token":token}).status_code == 422
        approved = client.post("/api/decisions", json=_approval_json(packet),
                               headers={"X-REA-Review-Token":token})
        assert approved.status_code == 200
        assert approved.json()["commercial_release"] == "HOLD"
        record = folder / (approved.json()["record_id"] + ".json")
        saved = json.loads(record.read_text(encoding="utf-8"))
        assert saved["reviewer_identity_verified"] is False
        assert saved["site_use_license_verified"] is False
        assert saved["code_generation_authorized"] is False
        assert len(list(folder.iterdir())) == 1


def test_actual_chromium_owner_review_ui_saves_opinion(tmp_path):
    from playwright.sync_api import sync_playwright
    import uvicorn
    packet = make_packet(fake_receipt())
    folder = tmp_path / "opinions"
    folder.mkdir()
    app = create_review_app(packet, folder)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    runner = Thread(target=server.run, daemon=True)
    runner.start()
    try:
        for _ in range(100):
            if server.started:
                break
            time.sleep(.05)
        assert server.started
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(f"http://127.0.0.1:{port}/", timeout=10000)
                page.locator("#status").get_by_text("근거 SHA:", exact=False).count()
                page.locator("#reviewer").fill("Human Demo")
                page.locator("#reason").fill("User selected a synthetic feature contract only.")
                page.locator("#decision").select_option("approve_synthetic_proposal")
                page.locator("#save").click()
                page.wait_for_function("document.querySelector('#out').textContent.includes('검토 기록 ID:')")
                assert "HOLD" in page.locator("#out").inner_text()
                assert len(list(folder.glob("*.json"))) == 1
            finally:
                browser.close()
    finally:
        server.should_exit = True
        runner.join(timeout=8)


@pytest.mark.parametrize("decision", ["hold", "reject"])
def test_reviewer_hold_or_reject_cannot_deliver(tmp_path, decision):
    packet = make_packet(fake_receipt())
    folder = tmp_path / "opinions"
    folder.mkdir()
    with TestClient(create_review_app(packet, folder)) as client:
        token = client.get("/api/packet").json()["session_token"]
        result = client.post("/api/decisions", json=_approval_json(packet, decision),
                             headers={"X-REA-Review-Token":token})
        assert result.status_code == 200
        record = folder / (result.json()["record_id"] + ".json")
    app = tmp_path / "generated"
    app.mkdir()
    with pytest.raises(WebsiteReviewError):
        create_delivery_zip(app, record, tmp_path / "out.zip", quote_label="Synthetic Demo")


def test_p85_real_generated_app_into_p95_portable_zip_and_verifier(tmp_path):
    html, csv, opts = write_inputs(tmp_path)
    receipt, _ = inspect_p85(html, fixture_sha256=opts["fixture_sha256"], astra_root=ASTRA)
    built = tmp_path / "generated"
    result = build_p85(html, csv, built,
                       approved_review_digest=receipt["review_digest"], **opts)
    assert result["status"] == "P85_SYNTHETIC_REVIEW_HOLD"
    fable_file, sha = record_fixture(tmp_path)
    packet = make_packet(receipt, inspect_fable_record(fable_file, expected_sha256=sha))
    record = _approved_record(tmp_path, packet)
    dest = tmp_path / "customer_delivery.zip"
    response = create_delivery_zip(built, record, dest, quote_label="Synthetic offline demo")
    assert response["status"] == "VERIFIED_SYNTHETIC_RELEASE_HOLD"
    assert response["price"] == "PENDING_OWNER_APPROVAL"
    assert response["rights_verified"] is False
    assert verify_delivery_zip(dest) == response
    with zipfile.ZipFile(dest) as z:
        assert "p95/delivery_manifest.json" in z.namelist()
        assert "p95/reviewer_opinion.json" in z.namelist()
        assert "app.py" in z.namelist()
        assert "review/p85_evidence_and_visual_diff.json" in z.namelist()
        assert json.loads(z.read("p95/delivery_manifest.json"))["commercial_release"] == "HOLD"
    assert html.read_text(encoding="utf-8") == HTML
    assert csv.read_text(encoding="utf-8") == CSV
    with pytest.raises(WebsiteReviewError):
        create_delivery_zip(built, record, dest, quote_label="Second delivery")
    assert verify_delivery_zip(dest) == response


def test_verifier_detects_member_tamper_and_zip_slip(tmp_path):
    root = tmp_path / "app"
    root.mkdir()
    for name, value in {"app.py":b"print('safe')", "manifest.json":b"{}",
                        "data.sqlite":b"db", "README.md":b"synthetic",
                        "review/p85_evidence_and_visual_diff.json":b"{}"}.items():
        target = root / name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(value)
    path = tmp_path / "hostile.zip"
    with zipfile.ZipFile(path,"w", compression=zipfile.ZIP_STORED) as z:
        z.writestr("../outside", "escape")
        z.writestr("p95/delivery_manifest.json","{}")
        z.writestr("p95/reviewer_opinion.json","{}")
    with pytest.raises(WebsiteReviewError, match="Unsafe archive member"):
        verify_delivery_zip(path)
