"""REA original product: three synthetic local sites -> real Chromium/Astra -> Pro E2E.

Only loopback fixtures are used. The explicit approval token below is a
synthetic test stand-in; it is NOT a real customer/licensing approval.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from rea.website_p70 import (
    APPROVAL_TOKEN, PERMISSION_TOKEN, build_reviewed, inspect_local,
    WebsiteReviewError,
)

ROOT = Path(__file__).resolve().parents[1]
FABLE = ROOT / ".vendor" / "fable" / "engines" / "fable51"
ASTRA = ROOT / ".vendor" / "astra" / "engines" / "astra_p4"
CSV = "id,title,category,price\nA001,커피,음료,3000\nA002,차,음료,2000\nA003,연필,문구,500\n"

# The page's DOM and script are independently authored synthetic reference
# behavior; the REA generated application uses its existing own app.js.
JS = """
const items = [
  {id:'A001',title:'커피',category:'음료'},
  {id:'A002',title:'차',category:'음료'},
  {id:'A003',title:'연필',category:'문구'}
];
function redraw(){
 const q=document.querySelector('#search').value;
 const cat=document.querySelector('#category').value;
 const visible=items.filter(x=>(!q || x.title.includes(q)) && (!cat||x.category===cat));
 document.querySelector('#count').textContent=visible.length+'건';
}
document.querySelector('#search').addEventListener('input',redraw);
document.querySelector('#category').addEventListener('change',redraw);
document.querySelector('#first-detail').addEventListener('click',()=>{
 document.querySelector('#detail').textContent='커피';
});
redraw();
"""
LAYOUTS = [
    ("search", "catalog", "<nav><a href='#main'>메뉴</a></nav><h1>카탈로그</h1>"),
    ("filter", "inventory", "<header><nav>재고 검색</nav></header><h1>재고</h1>"),
    ("detail", "directory", "<main><article>상세 디렉터리</article></main>"),
]


def fixture_page(layout: str, header: str) -> str:
    return """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<title>synthetic """ + layout + """</title>
<style>body { font: 17px sans-serif; } main { max-width: 900px }</style>
</head><body>""" + header + """
<section id="main"><label>찾기<input id="search" type="search"></label>
<label>카테고리<select id="category"><option value="">전체</option>
<option value="음료">음료</option><option value="문구">문구</option></select></label>
<div id="count"></div><button id="first-detail" type="button">상세 보기</button>
<div id="detail"></div><table><tr><td>synthetic</td></tr></table></section>
<script>""" + JS + """</script></body></html>"""


def inputs(tmp_path, case, layout, header):
    html = tmp_path / (layout + ".html")
    csv = tmp_path / "owner.csv"
    html.write_text(fixture_page(layout, header), encoding="utf-8")
    csv.write_text(CSV, encoding="utf-8")
    args = {
        "fixture_sha256": hashlib.sha256(html.read_bytes()).hexdigest(),
        "owner_sha256": hashlib.sha256(csv.read_bytes()).hexdigest(),
        "case": case, "id_field": "id", "title_field": "title",
        "category_field": "category", "fixture_permission": PERMISSION_TOKEN,
        "owner_approval": APPROVAL_TOKEN, "fable_root": FABLE, "astra_root": ASTRA,
    }
    return html, csv, args


@pytest.mark.parametrize("case,layout,header", LAYOUTS)
def test_three_distinct_real_browser_site_flows(case, layout, header, tmp_path):
    html, csv, args = inputs(tmp_path, case, layout, header)
    before_html, before_csv = html.read_bytes(), csv.read_bytes()
    review, bpng, apng = inspect_local(
        html, fixture_sha256=args["fixture_sha256"],
        case=case, astra_root=ASTRA,
    )
    assert review["schema_version"] == "rea.website.p70.v1"
    assert review["status"] == "REVIEW_REQUIRED"
    assert not review["implementation_ready"]
    assert review["subject"]["case"] == case
    assert len(review["review_digest"]) == 64
    assert bpng.startswith(b"\x89PNG") and apng.startswith(b"\x89PNG")
    spec = review["astra_functional_spec"]
    assert not spec["implementation_ready"] and len(spec["candidate_features"]) == 1
    assert spec["candidate_features"][0]["feature"] == case
    assert spec["candidate_features"][0]["review_status"] == "requires_review"
    assert all(g["status"] == "pending" for g in spec["approval_gates"])
    assert len(review["astra_observation_bundle"]["evidence"]) == 2
    assert len(review["astra_observation_bundle"]["observations"]) == 1
    assert review["astra_observation_bundle"]["observations"][0]["certainty"] == "observed"
    out = tmp_path / "new_app"
    response = build_reviewed(
        html, csv, out, approved_review_digest=review["review_digest"], **args,
    )
    assert response["status"] == "P70_SYNTHETIC_BROWSER_HOLD"
    assert response["browser_parity"] == "MATCHED_OBSERVED_SYNTHETIC_BEHAVIOR"
    assert response["owner_rows"] == 3
    assert html.read_bytes() == before_html
    assert csv.read_bytes() == before_csv
    detail = json.loads((out / "review/p70_browser_evidence.json").read_text("utf-8"))
    assert detail["review_digest"] == review["review_digest"]
    assert detail["generated_app_browser"]["case"] == case
    assert detail["status"] == "REVIEW_REQUIRED"
    manifest = json.loads((out / "manifest.json").read_text("utf-8"))
    assert manifest["website_p70"]["reference_behavior_auto_approved"] is False
    assert manifest["website_p70"]["browser_check"] == "MATCHED_OBSERVED_SYNTHETIC_BEHAVIOR"
    assert (out / "review/p70_before.png").read_bytes().startswith(b"\x89PNG")
    assert (out / "review/p70_after.png").read_bytes().startswith(b"\x89PNG")
    assert not (out / html.name).exists()
    assert not (out / "fable_result.json").exists()
    assert response["commercial_release"] == "HOLD"


def test_rejects_forged_approval_digest_before_output(tmp_path):
    case, layout, header = LAYOUTS[0]
    html, csv, args = inputs(tmp_path, case, layout, header)
    out = tmp_path / "new_app"
    with pytest.raises(WebsiteReviewError, match="digest"):
        build_reviewed(html, csv, out, approved_review_digest="0" * 64, **args)
    assert not out.exists()


@pytest.mark.parametrize("key,value", [
    ("fixture_permission", "NO"),
    ("owner_approval", "NO"),
    ("owner_sha256", "0" * 64),
])
def test_missing_permission_or_stale_owner_prevents_output(tmp_path, key, value):
    case, layout, header = LAYOUTS[0]
    html, csv, args = inputs(tmp_path, case, layout, header)
    args[key] = value
    with pytest.raises((WebsiteReviewError, ValueError)):
        build_reviewed(html, csv, tmp_path / "new_app",
                       approved_review_digest="0" * 64, **args)
    assert not (tmp_path / "new_app").exists()


def test_preserves_existing_output_owner_files(tmp_path):
    case, layout, header = LAYOUTS[0]
    html, csv, args = inputs(tmp_path, case, layout, header)
    out = tmp_path / "new_app"
    out.mkdir()
    (out / "owner-keeps.txt").write_text("PRESERVE", encoding="utf-8")
    with pytest.raises(FileExistsError):
        build_reviewed(html, csv, out,
                       approved_review_digest="0" * 64, **args)
    assert (out / "owner-keeps.txt").read_text("utf-8") == "PRESERVE"


def test_stale_html_source_never_published(tmp_path):
    case, layout, header = LAYOUTS[0]
    html, csv, args = inputs(tmp_path, case, layout, header)
    html.write_text("<html><h1>edited</h1></html>", encoding="utf-8")
    with pytest.raises(WebsiteReviewError, match="SHA mismatch"):
        inspect_local(html, fixture_sha256=args["fixture_sha256"], case=case,
                      astra_root=ASTRA)
    assert not (tmp_path / "new_app").exists()


def test_wrong_case_not_accepted(tmp_path):
    case, layout, header = LAYOUTS[0]
    html, _, args = inputs(tmp_path, case, layout, header)
    with pytest.raises(WebsiteReviewError, match="Unknown interaction"):
        inspect_local(html, fixture_sha256=args["fixture_sha256"],
                      case="unsafe_script", astra_root=ASTRA)
