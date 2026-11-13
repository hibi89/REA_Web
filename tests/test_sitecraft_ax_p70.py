"""SITECRAFT AX P70 independent three-website synthetic browser and atomic QA.

All input sites, people, actions, and owner data are synthetic. No external site
access, customer account, or legal permission is implied by this test.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from rea.sitecraft_p70 import (
    SCHEMA, WebsiteReviewError, build_three, inspect_three, read_scope,
)

ROOT = Path(__file__).resolve().parents[1]
FABLE = ROOT / ".vendor" / "fable" / "engines" / "fable51"
ASTRA = ROOT / ".vendor" / "astra" / "engines" / "astra_p4"
DATA = "id,title,category,price\nA001,커피,음료,3000\nA002,차,음료,2000\nA003,연필,문구,500\n"
JS = """
const items = [
 {id:'A001',title:'커피',category:'음료'},
 {id:'A002',title:'차',category:'음료'},
 {id:'A003',title:'연필',category:'문구'}
];
function redraw(){
 const q=document.querySelector('#search').value;
 const cat=document.querySelector('#category').value;
 const filtered=items.filter(x=>(!q||x.title.includes(q))&&(!cat||x.category===cat));
 document.querySelector('#count').textContent=filtered.length+'건';
}
document.querySelector('#search').addEventListener('input',redraw);
document.querySelector('#category').addEventListener('change',redraw);
document.querySelector('#first-detail').addEventListener('click',()=>{
 document.querySelector('#detail').textContent='커피';
});
redraw();
"""
CASES = (
    ("search", "catalog", "<header><nav>카탈로그 메뉴</nav></header>"),
    ("filter", "inventory", "<header><nav>재고 검색</nav></header>"),
    ("detail", "directory", "<main><article>상세 디렉터리</article></main>"),
)


def reference_html(layout, header):
    return ("""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<title>synthetic """ + layout + """</title>
<style>body{font:17px sans-serif}main{max-width:900px}</style></head><body>"""
            + header + """
<section><label>검색<input id="search" type="search"></label>
<label>분류<select id="category"><option value="">전체</option>
<option value="음료">음료</option><option value="문구">문구</option></select></label>
<div id="count"></div><button type="button" id="first-detail">상세 보기</button>
<div id="detail"></div><table><tr><td>synthetic</td></tr></table></section>
<script>""" + JS + """</script></body></html>""")


def put_scope(scope, contract):
    scope.write_text(json.dumps(contract, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def packet(tmp_path):
    csv = tmp_path / "owner.csv"
    csv.write_text(DATA, encoding="utf-8")
    sites = []
    for case, layout, header in CASES:
        name = layout + ".html"
        html = tmp_path / name
        html.write_text(reference_html(layout, header), encoding="utf-8")
        sites.append({
            "case": case, "reference_html": name,
            "reference_sha256": hashlib.sha256(html.read_bytes()).hexdigest(),
            "approved_review_digest": "",
        })
    contract = {
        "schema": SCHEMA, "product": "SITECRAFT AX",
        "mode": "three_synthetic_local_browser_cases",
        "sites": sites, "owner_csv": "owner.csv",
        "owner_sha256": hashlib.sha256(csv.read_bytes()).hexdigest(),
        "mapping": {"id": "id", "title": "title", "category": "category"},
        "permission": "YES_OWNER_AUTHORIZED_LOCAL_FIXTURE",
        "approval": "APPROVE_SYNTHETIC_ONLY",
        "external_network_allowed": False,
        "commercial_release_allowed": False,
    }
    scope = tmp_path / "sitecraft_scope.json"
    put_scope(scope, contract)
    return scope, contract, csv


def approved_packet(packet):
    scope, contract, csv = packet
    observed = inspect_three(scope, astra_root=ASTRA)
    assert set(observed["cases"]) == {"search", "filter", "detail"}
    for site in contract["sites"]:
        result = observed["cases"][site["case"]]
        assert result["status"] == "REVIEW_REQUIRED"
        assert result["feature"] == site["case"]
        assert result["reference_sha256"] == site["reference_sha256"]
        site["approved_review_digest"] = result["review_digest"]
    put_scope(scope, contract)
    return scope, contract, csv


def test_three_case_contract_is_local_and_distinct(packet):
    scope, contract, _ = packet
    data, owner, sites = read_scope(scope, require_approval=False)
    assert data == contract and owner.name == "owner.csv"
    assert len({p.name for _, p in sites}) == 3
    assert {site["case"] for site, _ in sites} == {"search", "filter", "detail"}


@pytest.mark.parametrize("field,value", [
    ("schema", "legacy"),
    ("product", "other"),
    ("mode", "arbitrary_live_site"),
    ("permission", "PUBLIC_SITE"),
    ("approval", "APPROVE_CUSTOMER_PRODUCTION"),
    ("external_network_allowed", True),
    ("commercial_release_allowed", True),
    ("owner_csv", "../owner.csv"),
    ("owner_csv", "https://example.com/owner.csv"),
    ("owner_sha256", "0" * 64),
    ("mapping", {"id": "title", "title": "title", "category": "category"}),
    ("sites", []),
])
def test_invalid_scope_refuses_without_publishing(packet, tmp_path, field, value):
    scope, data, _ = packet
    data[field] = value
    put_scope(scope, data)
    with pytest.raises(WebsiteReviewError):
        build_three(scope, tmp_path / "blocked", fable_root=FABLE, astra_root=ASTRA)
    assert not (tmp_path / "blocked").exists()


def test_rejects_duplicated_case_and_reference_file(packet):
    scope, data, _ = packet
    data["sites"][1]["case"] = "search"
    put_scope(scope, data)
    with pytest.raises(WebsiteReviewError, match="distinct"):
        read_scope(scope, require_approval=False)
    data["sites"][1]["case"] = "filter"
    data["sites"][1]["reference_html"] = data["sites"][0]["reference_html"]
    put_scope(scope, data)
    with pytest.raises(WebsiteReviewError, match="Distinct"):
        read_scope(scope, require_approval=False)


def test_rejects_unrecognized_or_duplicate_keys(packet):
    scope, data, _ = packet
    data["secret_cookie"] = "UNSAFE"
    put_scope(scope, data)
    with pytest.raises(WebsiteReviewError, match="keys"):
        read_scope(scope, require_approval=False)
    scope.write_text('{"schema":"one","schema":"two"}', encoding="utf-8")
    with pytest.raises(WebsiteReviewError, match="Duplicate"):
        read_scope(scope, require_approval=False)


def test_source_sha_mutation_blocks_before_output(packet, tmp_path):
    scope, data, _ = packet
    (tmp_path / "catalog.html").write_text("<html>changed</html>", encoding="utf-8")
    with pytest.raises(WebsiteReviewError, match="SHA mismatch"):
        build_three(scope, tmp_path / "blocked", fable_root=FABLE, astra_root=ASTRA)
    assert not (tmp_path / "blocked").exists()


def test_refuses_unsafe_symlink_scope(packet, tmp_path):
    scope, _, _ = packet
    link = tmp_path / "scope_symlink.json"
    try:
        link.symlink_to(scope)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")
    with pytest.raises(WebsiteReviewError, match="non-symlink"):
        read_scope(link, require_approval=False)


def test_no_approval_digest_no_build(packet, tmp_path):
    scope, _, _ = packet
    with pytest.raises(WebsiteReviewError, match="digest"):
        build_three(scope, tmp_path / "blocked", fable_root=FABLE, astra_root=ASTRA)
    assert not (tmp_path / "blocked").exists()


def test_bad_review_digest_refused_after_real_observation(packet, tmp_path):
    scope, contract, _ = approved_packet(packet)
    contract["sites"][2]["approved_review_digest"] = "0" * 64
    put_scope(scope, contract)
    with pytest.raises(WebsiteReviewError, match="Stale or forged"):
        build_three(scope, tmp_path / "blocked", fable_root=FABLE, astra_root=ASTRA)
    assert not (tmp_path / "blocked").exists()


def test_existing_owner_files_preserved(packet, tmp_path):
    scope, _, _ = packet
    out = tmp_path / "existing"
    out.mkdir()
    (out / "KEEP.txt").write_text("KEEP", encoding="utf-8")
    with pytest.raises(WebsiteReviewError, match="digest"):
        # Without approved digests gate fails before the destination path
        build_three(scope, out, fable_root=FABLE, astra_root=ASTRA)
    assert (out / "KEEP.txt").read_text("utf-8") == "KEEP"


def test_atomicity_if_second_case_fails(packet, tmp_path, monkeypatch):
    scope, _, _ = approved_packet(packet)
    calls = []
    def fail_second(html, csv, out, **options):
        calls.append(options["case"])
        if len(calls) == 2:
            raise WebsiteReviewError("Injected second-case failure")
        out.mkdir()
        return {"status": "P70_SYNTHETIC_BROWSER_HOLD",
                "browser_parity": "MATCHED_OBSERVED_SYNTHETIC_BEHAVIOR",
                "commercial_release": "HOLD", "owner_rows": 3}
    monkeypatch.setattr("rea.sitecraft_p70.build_reviewed", fail_second)
    out = tmp_path / "never_publish"
    with pytest.raises(WebsiteReviewError, match="Injected"):
        build_three(scope, out, fable_root=FABLE, astra_root=ASTRA)
    assert calls == ["search", "filter"]
    assert not out.exists()


def test_real_three_site_chromium_before_after_astra_and_pro_batch(packet, tmp_path):
    scope, contract, owner = approved_packet(packet)
    original_owner = owner.read_bytes()
    old_sites = {x["case"]: (tmp_path / x["reference_html"]).read_bytes()
                 for x in contract["sites"]}
    out = tmp_path / "sitecraft_new_apps"
    result = build_three(scope, out, fable_root=FABLE, astra_root=ASTRA)
    assert result["gate"] == "P70_SYNTHETIC_BROWSER_REVIEW_HOLD"
    assert result["verified_browser_cases"] == ["detail", "filter", "search"]
    assert result["commercial_release"] == "HOLD"
    report = json.loads((out / "sitecraft_p70_report.json").read_text(encoding="utf-8"))
    assert report["actual_browser_cases"] == 3
    assert report["external_site_scanned"] is False
    assert report["reference_site_assets_reused"] is False
    assert report["customer_identity_verified"] is False
    assert report["commercial_release"] == "HOLD"
    for case in ("search", "filter", "detail"):
        app = out / case
        assert app.is_dir()
        evidence = json.loads((app / "review/p70_browser_evidence.json").read_text("utf-8"))
        assert evidence["status"] == "REVIEW_REQUIRED"
        assert evidence["generated_app_browser"]["status"] == "MATCHED_OBSERVED_SYNTHETIC_BEHAVIOR"
        assert evidence["astra_observation_bundle"]["observations"][0]["certainty"] == "observed"
        assert evidence["astra_functional_spec"]["implementation_ready"] is False
        assert (app / "review/p70_before.png").read_bytes().startswith(b"\x89PNG")
        assert (app / "review/p70_after.png").read_bytes().startswith(b"\x89PNG")
        manifest = json.loads((app / "manifest.json").read_text("utf-8"))
        assert manifest["website_p70"]["reference_behavior_auto_approved"] is False
        assert manifest["website_p70"]["browser_check"] == "MATCHED_OBSERVED_SYNTHETIC_BEHAVIOR"
        spec = importlib.util.spec_from_file_location("sc_" + case, app / "app.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with TestClient(module.app) as client:
            assert client.get("/health").status_code == 200
            assert client.get("/api/items").json()["total"] == 3
            assert client.get("/review/p70_browser_evidence.json").status_code == 404
        assert b"synthetic detail" not in b"".join(
            p.read_bytes() for p in app.rglob("*") if p.is_file() and "review" not in p.parts
        )
    assert owner.read_bytes() == original_owner
    assert all((tmp_path / x["reference_html"]).read_bytes() == old_sites[x["case"]]
               for x in contract["sites"])
    assert not (out / "owner.csv").exists()
    assert not (out / "catalog.html").exists()
