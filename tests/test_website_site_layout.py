"""Owner-selected REA_Web independent layout structure: no source code cloning.

One real Chromium/P85/Astra/Fable/Pro end-to-end synthetic demo and negative
fail-closed tests; three static structural layouts are separate test fixtures.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from rea.website_p95 import create_review_app, create_delivery_zip, verify_delivery_zip, make_packet, _hash
from rea.website_p85 import inspect_p85, build_p85, _generated_capture
from rea.website_site_layout import (observe_layout_contract, apply_owner_layout,
                                     OWNER_LAYOUT_APPROVAL, WebsiteReviewError)

ROOT = Path(__file__).resolve().parents[1]
FABLE = ROOT / ".vendor/fable/engines/fable51"
ASTRA = ROOT / ".vendor/astra/engines/astra_p4"
CSV = "id,title,category,price\nA001,커피,음료,3000\nA002,차,음료,2000\nA003,연필,문구,500\n"
JS = """
const rows=[{title:'커피',category:'음료'},{title:'차',category:'음료'},{title:'연필',category:'문구'}];
function draw() {const q=document.querySelector('#search').value;
const c=document.querySelector('#category').value;
document.querySelector('#count').textContent=rows.filter(x=>(!q||x.title.includes(q))&&(!c||x.category===c)).length+'건';}
document.querySelector('#search').addEventListener('input',draw);
document.querySelector('#category').addEventListener('change',draw);
document.querySelector('#first-detail').addEventListener('click',()=>
document.querySelector('#detail').textContent='커피');
draw();
"""
REFERENCE = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
             '<meta name="viewport" content="width=device-width,initial-scale=1"></head>'
             '<body>{heading}<main><label>검색<input id="search" type="search"></label>'
             '<label>분류<select id="category"><option value="">전체</option>'
             '<option value="음료">음료</option><option value="문구">문구</option></select></label>'
             '<div id="count"></div><button id="first-detail">상세</button>'
             '<div id="detail"></div><script>' + JS + '</script></main></body></html>')
STRUCTURES = [
    ("top_navigation", "<header><nav>LOCAL_REFERENCE_LABEL_DO_NOT_COPY</nav></header>"),
    ("side_inventory", "<header><aside>LOCAL_REFERENCE_LABEL_DO_NOT_COPY</aside></header>"),
    ("article_directory", "<header><article>LOCAL_REFERENCE_LABEL_DO_NOT_COPY</article></header>"),
]


def owner_fixture(tmp_path, heading):
    html = tmp_path / "reference.html"
    csv = tmp_path / "owner.csv"
    html.write_text(REFERENCE.format(heading=heading), encoding="utf-8")
    csv.write_text(CSV, encoding="utf-8")
    sha = hashlib.sha256(html.read_bytes()).hexdigest()
    data_sha = hashlib.sha256(csv.read_bytes()).hexdigest()
    return html, csv, sha, data_sha


def synthetic_receipt(sha):
    subject = {"fixture_sha256": sha, "viewports": {}, "site_use": "synthetic_local_only"}
    return {
        "schema_version": "rea.website.p85.v1",
        "production_release": "HOLD", "site_approval": False,
        "subject": subject, "review_digest": _hash(subject),
        "astra_spec_draft": {"implementation_ready": False, "candidate_features": [
            {"feature": "search", "review_status": "requires_review",
             "evidence": [{"id":"e1"}]}]},
    }


@pytest.mark.parametrize("layout,heading", STRUCTURES)
def test_three_reference_structures_propose_bounded_owned_layout_only(layout, heading, tmp_path):
    fixture, _, sha, _ = owner_fixture(tmp_path, heading)
    contract = observe_layout_contract(
        fixture, fixture_sha256=sha, p85_receipt=synthetic_receipt(sha))
    assert contract["proposed_preset"] == layout
    assert contract["source_html_css_js_copied"] is False
    assert contract["status"] == "REVIEW_REQUIRED"
    assert contract["commercial_release"] == "HOLD"
    assert "LOCAL_REFERENCE_LABEL_DO_NOT_COPY" not in json.dumps(contract)


def reviewer_record(tmp_path, packet, preset):
    directory = tmp_path / "owner_opinion"
    directory.mkdir(exist_ok=True)
    with TestClient(create_review_app(packet, directory)) as client:
        token = client.get("/api/packet").json()["session_token"]
        payload = {
            "schema_version": "rea.website.p95.review.v1",
            "packet_sha256": packet["packet_sha256"],
            "review_digest": packet["review_digest"],
            "reviewer_claimed_label": "Synthetic Layout Reviewer",
            "decision": "approve_synthetic_proposal",
            "rationale": "Only the synthetic independent layout preset is acceptable as a test.",
            "layout_preset": preset,
        }
        r = client.post("/api/decisions", json=payload,
                        headers={"X-REA-Review-Token":token})
        assert r.status_code == 200, r.text
        result = directory / (r.json()["record_id"] + ".json")
        data = json.loads(result.read_text("utf-8"))
        assert data["layout_preset"] == preset
        assert data["site_use_license_verified"] is False
        return result


def test_actual_semantic_reference_to_owner_selected_independent_pro_layout(tmp_path):
    fixture, csv, sha, data_sha = owner_fixture(tmp_path, STRUCTURES[0][1])
    review, _ = inspect_p85(fixture, fixture_sha256=sha, astra_root=ASTRA)
    original = tmp_path / "real_p85_app"
    result = build_p85(
        fixture, csv, original,
        fixture_sha256=sha, owner_sha256=data_sha,
        fixture_permission="YES_LOCAL_FIXTURE", owner_approval="APPROVE_SYNTHETIC_ONLY",
        fable_root=FABLE, astra_root=ASTRA,
        approved_review_digest=review["review_digest"])
    assert result["status"] == "P85_SYNTHETIC_REVIEW_HOLD"
    packet = make_packet(review)
    opinion = reviewer_record(tmp_path, packet, "top_navigation")
    contract = observe_layout_contract(fixture, fixture_sha256=sha, p85_receipt=review)
    derived = tmp_path / "site_guided_independent_app"
    applied = apply_owner_layout(original, derived, contract=contract,
                                 approved_contract_sha256=contract["contract_sha256"],
                                 decision_record=opinion,
                                 owner_layout_approval=OWNER_LAYOUT_APPROVAL)
    assert applied["status"] == "SYNTHETIC_LAYOUT_PRESET_REBUILT_WITH_REVIEW_HOLD"
    assert applied["original_site_design_reproduced"] is False
    assert (derived / "static/index.html").read_text("utf-8").count("rea-preset-top_navigation") == 1
    assert "rea-preset-top_navigation" not in (original / "static/index.html").read_text("utf-8")
    assert (derived / "review/p95_owner_site_layout_contract.json").is_file()
    output_html = (derived / "static/index.html").read_text("utf-8")
    assert "LOCAL_REFERENCE_LABEL_DO_NOT_COPY" not in output_html
    output = _generated_capture(derived)
    assert len(output) == 2
    assert all(len(x["steps"]) == 3 for x in output.values())
    assert all(x["steps"][-1]["after"]["detail"] == "커피" for x in output.values())
    manifest = json.loads((derived / "manifest.json").read_text("utf-8"))
    assert manifest["website_p95_layout"]["commercial_release"] == "HOLD"
    assert manifest["website_p95_layout"]["source_html_css_js_copied"] is False
    archive = tmp_path / "owned_site_app.zip"
    delivered = create_delivery_zip(derived, opinion, archive, quote_label="Synthetic test scope")
    assert delivered["status"] == "VERIFIED_SYNTHETIC_RELEASE_HOLD"
    assert verify_delivery_zip(archive) == delivered
    assert csv.read_text("utf-8") == CSV


@pytest.mark.parametrize("case", ["wrong_digest", "wrong_preset", "missing_permission", "existing_destination"])
def test_layout_requires_matching_owner_review_and_never_overwrites(tmp_path, case):
    heading = STRUCTURES[0][1]
    fixture, _, sha, _ = owner_fixture(tmp_path, heading)
    p85 = synthetic_receipt(sha)
    contract = observe_layout_contract(fixture, fixture_sha256=sha, p85_receipt=p85)
    packet = make_packet(p85)
    opinion = reviewer_record(tmp_path, packet, "article_directory" if case == "wrong_preset" else "top_navigation")
    input_app = tmp_path / "synthetic_app"
    input_app.mkdir()
    dest = tmp_path / "derived_app"
    if case == "existing_destination":
        dest.mkdir()
        (dest / "keep.txt").write_text("PRESERVE", encoding="utf-8")
    with pytest.raises((ValueError, FileExistsError)):
        apply_owner_layout(input_app, dest, contract=contract,
                           decision_record=opinion,
                           approved_contract_sha256="0"*64 if case=="wrong_digest" else contract["contract_sha256"],
                           owner_layout_approval="NO" if case=="missing_permission" else OWNER_LAYOUT_APPROVAL)
    if case == "existing_destination":
        assert (dest / "keep.txt").read_text("utf-8") == "PRESERVE"
    else:
        assert not dest.exists()


def test_structural_html_without_supported_semantic_landmark_is_hold(tmp_path):
    html, _, sha, _ = owner_fixture(tmp_path, "<div>NO_SEMANTIC_PATTERN</div>")
    with pytest.raises(WebsiteReviewError, match="supported semantic"):
        observe_layout_contract(html, fixture_sha256=sha, p85_receipt=synthetic_receipt(sha))


def test_stale_source_invalidates_layout_contract(tmp_path):
    fixture, _, sha, _ = owner_fixture(tmp_path, STRUCTURES[0][1])
    fixture.write_text("<html>changed</html>", encoding="utf-8")
    with pytest.raises(WebsiteReviewError, match="SHA mismatch"):
        observe_layout_contract(fixture, fixture_sha256=sha, p85_receipt=synthetic_receipt(sha))
