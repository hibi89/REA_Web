"""REA original website engine: observed DOM states -> approved component tree.

This is not CSV2WEB Lite: the original source HTML is observed in Chromium,
Astra P4 observed features + screenshot evidence control the *component
structure*, and the independent Pro app is rebuilt with its own code/data.
Only three locally owned synthetic site structures are in this gate.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from rea.website_component_builder import (
    build_evidence_ui, observed_contract, WebsiteReviewError,
)
from rea.website_p85 import inspect_p85, build_p85, _generated_capture
from rea.website_p95 import create_review_app, make_packet
from rea.website_site_layout import OWNER_LAYOUT_APPROVAL

ROOT = Path(__file__).resolve().parents[1]
FABLE = ROOT / ".vendor/fable/engines/fable51"
ASTRA = ROOT / ".vendor/astra/engines/astra_p4"
CSV = "id,title,category,price\nA001,커피,음료,3000\nA002,차,음료,2000\nA003,연필,문구,500\n"
SOURCE_SCRIPT = """const a=[{title:'커피',category:'음료'},{title:'차',category:'음료'},
{title:'연필',category:'문구'}];
function x(){const q=document.querySelector('#search').value;
const c=document.querySelector('#category').value;
document.querySelector('#count').textContent=a.filter(v=>
(!q||v.title.includes(q))&&(!c||v.category===c)).length+'건'}
document.querySelector('#search').addEventListener('input',x);
document.querySelector('#category').addEventListener('change',x);
document.querySelector('#first-detail').addEventListener('click',()=>document.querySelector('#detail').textContent='커피');
x();"""
MARKS = {
    "top_navigation": "<nav>REFERENCE_BRAND_NOT_TO_COPY</nav>",
    "side_inventory": "<aside>REFERENCE_BRAND_NOT_TO_COPY</aside>",
    "article_directory": "<article>REFERENCE_BRAND_NOT_TO_COPY</article>",
}
SITE_HTML = (
    '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1">'
    '<title>Original owner synthetic</title><style>body{margin:0;padding:16px}</style>'
    '</head><body><header>{marker}</header><main><h1>REFERENCE_BRAND_NOT_TO_COPY</h1>'
    '<label>search<input id="search" type="search"></label>'
    '<label>category<select id="category"><option value="">전체</option>'
    '<option value="음료">음료</option><option value="문구">문구</option></select></label>'
    '<div id="count"></div><button id="first-detail">상세</button>'
    '<div id="detail"></div><script>' + SOURCE_SCRIPT +
    '</script></main></body></html>'
)


def create_sources(tmp_path, preset):
    html = tmp_path / ("owner-" + preset + ".html")
    data = tmp_path / "customer_owned.csv"
    html.write_text(SITE_HTML.replace("{marker}", MARKS[preset]), encoding="utf-8")
    data.write_text(CSV, encoding="utf-8")
    return html, data, hashlib.sha256(html.read_bytes()).hexdigest(), hashlib.sha256(data.read_bytes()).hexdigest()


def owner_decision(tmp_path, p85, preset):
    directory = tmp_path / "owner-opinion"
    directory.mkdir()
    packet = make_packet(p85)
    with TestClient(create_review_app(packet, directory)) as client:
        token = client.get("/api/packet").json()["session_token"]
        message = {
            "schema_version": "rea.website.p95.review.v1",
            "packet_sha256": packet["packet_sha256"],
            "review_digest": packet["review_digest"],
            "reviewer_claimed_label": "Local Synthetic Owner",
            "decision": "approve_synthetic_proposal",
            "rationale": "Only the bounded independently authored app proposal is approved for testing.",
            "layout_preset": preset,
        }
        response = client.post("/api/decisions", json=message,
                               headers={"X-REA-Review-Token": token})
        assert response.status_code == 200, response.text
        return directory / (response.json()["record_id"] + ".json")


def real_pipeline(tmp_path, preset="top_navigation"):
    fixture, csv, fixture_sha, csv_sha = create_sources(tmp_path, preset)
    receipt, _ = inspect_p85(fixture, fixture_sha256=fixture_sha, astra_root=ASTRA)
    contract, layout = observed_contract(fixture, fixture_sha256=fixture_sha,
                                          p85_receipt=receipt)
    original = tmp_path / "original_app"
    built = build_p85(
        fixture, csv, original,
        fixture_sha256=fixture_sha, owner_sha256=csv_sha,
        fixture_permission="YES_LOCAL_FIXTURE",
        owner_approval="APPROVE_SYNTHETIC_ONLY",
        fable_root=FABLE, astra_root=ASTRA,
        approved_review_digest=receipt["review_digest"])
    assert built["status"] == "P85_SYNTHETIC_REVIEW_HOLD"
    review = owner_decision(tmp_path, receipt, preset)
    return fixture, csv, receipt, contract, original, review, fixture_sha


def fake_receipt(fixture_sha):
    """Synthetic negative fixture with the SAME P85 evidence shape."""
    import hashlib as crypto
    from rea.website_p95 import _hash
    subject = {"fixture_sha256": fixture_sha, "site_use": "synthetic_local_only",
               "viewports": {}}
    bundle = {"evidence": [], "observations": []}
    for view in ("desktop", "mobile"):
        steps = []
        shas = []
        for i in range(4):
            digest = crypto.sha256((view + str(i)).encode()).hexdigest()
            shas.append(digest)
            bundle["evidence"].append({
                "id": f"ev_{view}_{i}", "notes": "SHA256 " + digest,
                "source_ref": f"review/p85_{view}_{i}.png",
            })
        prior = {"count": "3건", "detail": "", "search_value": "", "category_value": ""}
        for i, (feature, new) in enumerate([
            ("search", {"count":"1건","detail":"","search_value":"커피","category_value":""}),
            ("filter", {"count":"1건","detail":"","search_value":"커피","category_value":"음료"}),
            ("detail", {"count":"1건","detail":"커피","search_value":"커피","category_value":"음료"})
        ]):
            steps.append({"feature": feature, "before": prior, "after": new})
            bundle["observations"].append({
                "id": f"ob_{view}_{i}", "certainty": "observed",
                "feature": feature, "before": prior, "after": new,
                "evidence_ids": [f"ev_{view}_{i}", f"ev_{view}_{i+1}"],
            })
            prior = new
        subject["viewports"][view] = {"steps": steps, "screenshots_sha256": shas}
    candidates = [{"feature": feature, "review_status": "requires_review",
                   "evidence": [{"id":"ev_desktop_0"}]}
                  for _view in ("desktop", "mobile")
                  for feature in ("search", "filter", "detail")]
    return {"schema_version": "rea.website.p85.v1",
            "subject": subject, "review_digest": _hash(subject),
            "production_release": "HOLD", "site_approval": False,
            "astra_spec_draft": {
                "implementation_ready": False, "candidate_features": candidates},
            "astra_observation_bundle": bundle}


@pytest.mark.parametrize("preset", ["top_navigation", "side_inventory", "article_directory"])
def test_three_independent_ui_component_contracts_are_derived_from_states_and_semantics(preset, tmp_path):
    fixture, _, sha, _ = create_sources(tmp_path, preset)
    contract, layout = observed_contract(fixture, fixture_sha256=sha,
                                         p85_receipt=fake_receipt(sha))
    assert contract["semantic_layout"] == preset
    assert contract["semantic_layout_sha256"] == layout["contract_sha256"]
    assert len(contract["traceability"]) == 6
    assert [x["feature"] for x in contract["traceability"][:3]] == [
        "search", "filter", "detail"]
    assert set(x["viewport"] for x in contract["traceability"]) == {
        "desktop", "mobile"}
    assert contract["original_assets_code_or_text_copied"] is False
    assert "REFERENCE_BRAND_NOT_TO_COPY" not in json.dumps(contract)
    assert contract["commercial_release"] == "HOLD"


def test_real_fable_astra_chromium_approval_to_new_independent_component_tree(tmp_path):
    fixture, csv, p85, contract, original, opinion, fixture_sha = real_pipeline(tmp_path)
    out = tmp_path / "new_reconstructed_ui"
    original_html = (original / "static/index.html").read_bytes()
    result = build_evidence_ui(
        original, out, reference_html=fixture, fixture_sha256=fixture_sha,
        p85_receipt=p85, decision_record=opinion,
        approved_ui_contract_sha256=contract["contract_sha256"],
        owner_approval=OWNER_LAYOUT_APPROVAL)
    assert result["status"] == "P95_OBSERVED_SYNTHETIC_COMPONENT_WORKFLOW_HOLD"
    assert result["observed_states"] == 6
    assert result["applied_layout"] == "top_navigation"
    assert result["reference_design_or_copyright_approved"] is False
    assert (original / "static/index.html").read_bytes() == original_html
    html = (out / "static/index.html").read_text(encoding="utf-8")
    assert 'class="rea-scope-links"' in html
    assert "id=\"rea-overview\"" in html and "id=\"rea-list\"" in html
    assert "REFERENCE_BRAND_NOT_TO_COPY" not in html
    assert "rea-preset-top_navigation" in html
    evidence = json.loads((out / "review/p95_evidence_ui_contract.json").read_text("utf-8"))
    assert evidence["contract_sha256"] == contract["contract_sha256"]
    assert len(evidence["traceability"]) == 6
    manifest = json.loads((out / "manifest.json").read_text("utf-8"))
    assert manifest["website_p95_component"]["commercial_release"] == "HOLD"
    assert manifest["website_p95_component"]["reference_design_parity_verified"] is False
    # Real generated Pro FastAPI+SQLite application in real Chromium at both sizes.
    browser_result = _generated_capture(out)
    assert len(browser_result) == 2
    for view in ("desktop", "mobile"):
        assert len(browser_result[view]["steps"]) == 3
        assert browser_result[view]["steps"][-1]["after"]["detail"] == "커피"
        assert browser_result[view]["metrics"]["document_width"] <= browser_result[view]["metrics"]["width"] + 1
    assert csv.read_bytes() == CSV.encode()


@pytest.mark.parametrize("tamper", [
    "wrong_source", "wrong_evidence", "wrong_transition",
    "missing_viewport", "approved_without_review", "missing_feature",
])
def test_observed_contract_fail_closed_if_evidence_is_stale(tamper, tmp_path):
    fixture, _, sha, _ = create_sources(tmp_path, "top_navigation")
    data = fake_receipt(sha)
    if tamper == "wrong_source":
        data["subject"]["fixture_sha256"] = "b"*64
    elif tamper == "wrong_evidence":
        data["astra_observation_bundle"]["evidence"][0]["notes"] = "SHA256 " + "a"*64
    elif tamper == "wrong_transition":
        data["astra_observation_bundle"]["observations"][0]["after"]["count"] = "4건"
    elif tamper == "missing_viewport":
        data["subject"]["viewports"].pop("mobile")
    elif tamper == "approved_without_review":
        data["astra_spec_draft"]["implementation_ready"] = True
    elif tamper == "missing_feature":
        data["astra_spec_draft"]["candidate_features"].pop()
    if tamper in {"wrong_source", "wrong_transition", "missing_viewport"}:
        from rea.website_p95 import _hash
        data["review_digest"] = _hash(data["subject"])
    with pytest.raises(WebsiteReviewError):
        observed_contract(fixture, fixture_sha256=sha, p85_receipt=data)


@pytest.mark.parametrize("bad", ["wrong_digest", "no_approval", "output_exists", "wrong_reviewer_preset"])
def test_generation_gates_preserve_original_and_never_publishes_on_bad_input(tmp_path, bad):
    # Fast negative test: errors are rejected ahead of source app mutation.
    fixture, _, sha, _ = create_sources(tmp_path, "top_navigation")
    p85 = fake_receipt(sha)
    contract, _ = observed_contract(fixture, fixture_sha256=sha,
                                     p85_receipt=p85)
    opinion = owner_decision(tmp_path, p85,
                             "article_directory" if bad == "wrong_reviewer_preset" else "top_navigation")
    original = tmp_path / "original"
    original.mkdir()
    (original / "KEEP.txt").write_text("ORIGINAL", encoding="utf-8")
    output = tmp_path / "new"
    if bad == "output_exists":
        output.mkdir()
        (output / "owner.txt").write_text("KEEP", encoding="utf-8")
    with pytest.raises((FileExistsError, WebsiteReviewError)):
        build_evidence_ui(
            original, output, reference_html=fixture, fixture_sha256=sha,
            p85_receipt=p85, decision_record=opinion,
            approved_ui_contract_sha256="f"*64 if bad=="wrong_digest" else contract["contract_sha256"],
            owner_approval="NO" if bad=="no_approval" else OWNER_LAYOUT_APPROVAL)
    assert (original / "KEEP.txt").read_text("utf-8") == "ORIGINAL"
    if bad == "output_exists":
        assert (output / "owner.txt").read_text("utf-8") == "KEEP"
    else:
        assert not output.exists()
