"""SITECRAFT AX P85 independent 3-site×2-viewport×3-step exact-source QA.

All sites and approval digests are synthetic; no production authorization.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from rea.sitecraft_p85 import (
    MODE, SCHEMA, WebsiteReviewError, VIEWPORTS, STEPS,
    build_three, inspect_three, read_p85_scope,
)

ROOT = Path(__file__).resolve().parents[1]
FABLE = ROOT / ".vendor" / "fable" / "engines" / "fable51"
ASTRA = ROOT / ".vendor" / "astra" / "engines" / "astra_p4"
XSS = "<img src=x onerror=alert(1)>"
CSV = (
    'id,title,category,note\n'
    'A001,커피,음료,"<img src=x onerror=alert(1)>"\n'
    'A002,차,음료,synthetic tea\n'
    'A003,연필,문구,synthetic pencil\n'
)
JS = """
const rows=[
 {id:'A001',title:'커피',category:'음료'},
 {id:'A002',title:'차',category:'음료'},
 {id:'A003',title:'연필',category:'문구'}
];
function rerender(){
 const q=document.querySelector('#search').value;
 const category=document.querySelector('#category').value;
 const matching=rows.filter(x=>(!q||x.title.includes(q)) &&
                                   (!category||x.category===category));
 document.querySelector('#count').textContent=matching.length+'건';
}
document.querySelector('#search').addEventListener('input',rerender);
document.querySelector('#category').addEventListener('change',rerender);
document.querySelector('#first-detail').addEventListener('click',()=>{
 document.querySelector('#detail').textContent='커피';
});
rerender();
"""
SITES = (
    ("search", "catalog", "<header><nav>상품 카탈로그</nav><h1>상품 관리</h1></header>"),
    ("filter", "inventory", "<main><h1>재고 관리자</h1><aside>상품 분류</aside></main>"),
    ("detail", "directory", "<main><article><h1>업무 목록</h1></article></main>"),
)


def webpage(name, header, extra=""):
    return (
        '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>synthetic ' + name + '</title>'
        '<style>body{margin:0;padding:16px;font-family:Arial,sans-serif}'
        'main{width:100%;max-width:840px;margin:auto}'
        'input,select{max-width:100%;box-sizing:border-box}</style></head><body>'
        + header +
        '<section><label>검색<input id="search" type="search"></label>'
        '<label>분류<select id="category"><option value="">전체</option>'
        '<option value="음료">음료</option><option value="문구">문구</option></select></label>'
        '<div id="count"></div><button id="first-detail" type="button">상세</button>'
        '<div id="detail"></div><table><tr><td>LOCAL_SYNTHETIC_CONTENT_NOT_FOR_COPY</td>'
        '</tr></table></section>'
        '<script>' + JS + extra + '</script></body></html>'
    )


def write_scope(scope, data):
    scope.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def packet(tmp_path):
    csv = tmp_path / "owner.csv"
    csv.write_text(CSV, encoding="utf-8")
    sites = []
    for case, name, header in SITES:
        fixture = tmp_path / (name + ".html")
        fixture.write_text(webpage(name, header), encoding="utf-8")
        sites.append({
            "case": case,
            "reference_html": fixture.name,
            "reference_sha256": hashlib.sha256(fixture.read_bytes()).hexdigest(),
            "approved_review_digest": "",
        })
    scope = tmp_path / "scope.json"
    data = {
        "schema": SCHEMA, "product": "SITECRAFT AX", "mode": MODE,
        "sites": sites, "owner_csv": "owner.csv",
        "owner_sha256": hashlib.sha256(csv.read_bytes()).hexdigest(),
        "mapping": {"id": "id", "title": "title", "category": "category"},
        "permission": "YES_OWNER_AUTHORIZED_LOCAL_FIXTURE",
        "approval": "APPROVE_SYNTHETIC_ONLY",
        "external_network_allowed": False,
        "commercial_release_allowed": False,
    }
    write_scope(scope, data)
    return scope, data, csv


def approved_packet(packet):
    scope, contract, csv = packet
    inspected = inspect_three(scope, astra_root=ASTRA)
    assert inspected["gate"] == "P85_SYNTHETIC_INSPECTION_ONLY"
    assert inspected["commercial_release"] == "HOLD"
    assert set(inspected["sites"]) == {"search", "filter", "detail"}
    for entry in contract["sites"]:
        receipt = inspected["sites"][entry["case"]]
        assert receipt["status"] == "REVIEW_REQUIRED"
        assert receipt["desktop_mobile_evidence_count"] == 8
        assert receipt["observed_claims"] == 6
        assert receipt["steps_per_viewport"] == 3
        entry["approved_review_digest"] = receipt["review_digest"]
    write_scope(scope, contract)
    return scope, contract, csv


def test_p85_contract_three_explicit_cases_local_only(packet):
    scope, original, _ = packet
    contract, owner, parsed = read_p85_scope(scope, require_approval=False)
    assert contract == original
    assert owner.name == "owner.csv"
    assert len(parsed) == 3
    assert {site["case"] for site, _ in parsed} == set(STEPS)
    assert len(VIEWPORTS) == 2


@pytest.mark.parametrize("field,value", [
    ("schema", "sitecraft.p70.synthetic.v1"),
    ("product", "OTHER"),
    ("mode", "three_synthetic_local_browser_cases"),
    ("permission", "NO_PERMISSION"),
    ("approval", "APPROVE_REAL_CUSTOMER"),
    ("external_network_allowed", True),
    ("commercial_release_allowed", True),
    ("owner_csv", "../owner.csv"),
    ("owner_csv", "https://example.com/private.csv"),
    ("owner_sha256", "0" * 64),
    ("mapping", {"id": "title", "title": "title", "category": "category"}),
    ("sites", []),
])
def test_untrusted_contract_rejected_without_publication(packet, tmp_path, field, value):
    scope, data, _ = packet
    data[field] = value
    write_scope(scope, data)
    target = tmp_path / "blocked"
    with pytest.raises((WebsiteReviewError, OSError)):
        build_three(scope, target, fable_root=FABLE, astra_root=ASTRA)
    assert not target.exists()


@pytest.mark.parametrize("bad", [
    "<iframe src='local'></iframe>",
    "fetch('https://example.invalid/forbidden')",
    "<object data='unsafe'></object>",
])
def test_hostile_synthetic_html_refused_before_browser(packet, tmp_path, bad):
    scope, data, _ = packet
    path = tmp_path / data["sites"][0]["reference_html"]
    path.write_text(webpage("catalog", SITES[0][2], extra=bad), encoding="utf-8")
    data["sites"][0]["reference_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    write_scope(scope, data)
    with pytest.raises(WebsiteReviewError, match="external URL|third-party"):
        inspect_three(scope, astra_root=ASTRA)


def test_reference_changed_hash_fails_before_capture(packet, tmp_path):
    scope, data, _ = packet
    (tmp_path / data["sites"][1]["reference_html"]).write_text(
        "<html>changed</html>", encoding="utf-8")
    with pytest.raises(WebsiteReviewError, match="SHA"):
        inspect_three(scope, astra_root=ASTRA)
    assert not (tmp_path / "blocked").exists()


def test_duplicate_case_and_unknown_field_refused(packet):
    scope, data, _ = packet
    data["sites"][1]["case"] = "search"
    write_scope(scope, data)
    with pytest.raises(WebsiteReviewError, match="distinct"):
        read_p85_scope(scope, require_approval=False)
    data["sites"][1]["case"] = "filter"
    data["rogue_key"] = True
    write_scope(scope, data)
    with pytest.raises(WebsiteReviewError, match="keys"):
        read_p85_scope(scope, require_approval=False)


def test_missing_p85_digest_never_publishes(packet, tmp_path):
    scope, _, _ = packet
    with pytest.raises(WebsiteReviewError, match="digest"):
        build_three(scope, tmp_path / "blocked", fable_root=FABLE, astra_root=ASTRA)
    assert not (tmp_path / "blocked").exists()


def test_preserve_existing_output(packet, tmp_path):
    scope, data, _ = packet
    for site in data["sites"]:
        site["approved_review_digest"] = "a" * 64
    write_scope(scope, data)
    target = tmp_path / "existing"
    target.mkdir()
    (target / "owner.txt").write_text("KEEP", encoding="utf-8")
    with pytest.raises(FileExistsError, match="already exists"):
        build_three(scope, target, fable_root=FABLE, astra_root=ASTRA)
    assert (target / "owner.txt").read_text(encoding="utf-8") == "KEEP"


def test_stale_digest_refuses_even_with_correct_html_sha(packet, tmp_path):
    scope, data, _ = approved_packet(packet)
    data["sites"][0]["approved_review_digest"] = "0" * 64
    write_scope(scope, data)
    with pytest.raises(WebsiteReviewError, match="changed or forged"):
        build_three(scope, tmp_path / "not_published",
                    fable_root=FABLE, astra_root=ASTRA)
    assert not (tmp_path / "not_published").exists()


def test_all_or_nothing_on_second_site_failure(packet, tmp_path, monkeypatch):
    scope, _, _ = approved_packet(packet)
    calls = []
    def injected_fail(html, owner, out, **kwargs):
        calls.append(out.name)
        if len(calls) == 2:
            raise WebsiteReviewError("Synthetic injected failure on site two")
        out.mkdir()
        (out / "review").mkdir()
        sample_diff = {"verdict": "VISUAL_DIFFERENCE_REQUIRES_HUMAN_REVIEW",
                       "mean_absolute_rgb_difference": 0.25}
        visual = {vp: {"functional_states": "MATCHED_SYNTHETIC_3_STEP_SEQUENCE",
                       "screenshots": [sample_diff] * 4} for vp in VIEWPORTS}
        (out / "review/p85_evidence_and_visual_diff.json").write_text(
            json.dumps({"review_digest": kwargs["approved_review_digest"],
                        "astra_spec_draft": {"implementation_ready": False},
                        "astra_observation_bundle": {"observations": [{}] * 6},
                        "source_visual_difference": visual}),
            encoding="utf-8")
        return {"status": "P85_SYNTHETIC_REVIEW_HOLD",
                "browser_sequences": 2, "steps_per_sequence": 3,
                "functional_parity": "PASS_SYNTHETIC",
                "visual_parity": "UNVERIFIED_DIFFERENCE_REPORTED",
                "commercial_release": "HOLD", "rows": 3}
    monkeypatch.setattr("rea.sitecraft_p85.build_p85", injected_fail)
    with pytest.raises(WebsiteReviewError, match="site two"):
        build_three(scope, tmp_path / "not_published",
                    fable_root=FABLE, astra_root=ASTRA)
    assert calls == ["search", "filter"]
    assert not (tmp_path / "not_published").exists()


def test_three_sites_real_responsive_chromium_astra_rgb_pro_and_xss(packet, tmp_path):
    scope, data, csv = approved_packet(packet)
    originals = {s["case"]: (tmp_path / s["reference_html"]).read_bytes()
                 for s in data["sites"]}
    original_csv = csv.read_bytes()
    target = tmp_path / "new_sitecraft_p85_bundle"
    result = build_three(scope, target, fable_root=FABLE, astra_root=ASTRA)
    assert result["gate"] == "P85_SYNTHETIC_RESPONSIVE_REVIEW_HOLD"
    assert result["observed_browser_actions"] == 18
    assert result["visual_acceptance"] == "HUMAN_REVIEW_REQUIRED"
    assert result["commercial_release"] == "HOLD"
    report = json.loads((target / "sitecraft_p85_report.json").read_text(encoding="utf-8"))
    assert report["total_observed_actions"] == 18
    assert report["total_png_evidence"] == 48
    assert report["total_rgb_difference_reports"] == 24
    assert report["source_assets_reused"] is False
    assert report["customer_identity_verified"] is False
    assert report["real_external_website"] is False
    assert report["commercial_release"] == "HOLD"
    for case in ("search", "filter", "detail"):
        app = target / case
        assert app.is_dir()
        site_report = report["sites"][case]
        assert site_report["observed_steps"] == 6
        assert site_report["rgb_diff_reports"] == 8
        evidence = json.loads((app / "review/p85_evidence_and_visual_diff.json").read_text(encoding="utf-8"))
        assert evidence["human_review"].startswith("PENDING")
        assert evidence["site_approval"] is False
        assert evidence["astra_spec_draft"]["implementation_ready"] is False
        assert len(evidence["astra_observation_bundle"]["observations"]) == 6
        assert len(evidence["astra_observation_bundle"]["evidence"]) == 8
        assert evidence["review_digest"] == site_report["review_digest"]
        for viewport in VIEWPORTS:
            visual = evidence["source_visual_difference"][viewport]
            assert visual["functional_states"] == "MATCHED_SYNTHETIC_3_STEP_SEQUENCE"
            assert visual["responsive_overflow"] is False
            for i, diff in enumerate(visual["screenshots"]):
                assert diff["verdict"] == "VISUAL_DIFFERENCE_REQUIRES_HUMAN_REVIEW"
                assert 0 <= diff["mean_absolute_rgb_difference"] <= 1
                assert (app / f"review/p85_{viewport}_{i}.png").read_bytes().startswith(b"\x89PNG")
                assert (app / f"review/p85_generated_{viewport}_{i}.png").read_bytes().startswith(b"\x89PNG")
        manifest = json.loads((app / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["website_p85"]["commercial_release"] == "HOLD"
        assert manifest["website_p85"]["visual_parity"] == "UNVERIFIED_DIFFERENCE_REPORTED"
        assert not (app / "catalog.html").exists()
        assert b"LOCAL_SYNTHETIC_CONTENT_NOT_FOR_COPY" not in b"".join(
            p.read_bytes() for p in app.rglob("*") if p.is_file()
        )
        # The independently built static client must never inject customer
        # fields as HTML. The input contains a synthetic XSS payload.
        browser_js = (app / "static/app.js").read_text(encoding="utf-8")
        assert "node.textContent = String(value)" in browser_js
        assert "innerHTML" not in browser_js
        static_html = (app / "static/index.html").read_text(encoding="utf-8")
        assert XSS not in static_html
        spec = importlib.util.spec_from_file_location("sitecraft_p85_" + case, app / "app.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with TestClient(module.app) as client:
            assert client.get("/health").status_code == 200
            row = client.get("/api/items/A001")
            assert row.status_code == 200
            assert row.json()["attributes"]["note"] == XSS
            assert client.get("/review/p85_evidence_and_visual_diff.json").status_code == 404
    assert csv.read_bytes() == original_csv
    assert all((tmp_path / s["reference_html"]).read_bytes() == originals[s["case"]]
               for s in data["sites"])
    assert not (target / "owner.csv").exists()
