"""P85: 3 actual local synthetic site DOMs, desktop/mobile 3-step workflows.

Reference scripts/layout are independently authored; generated Pro code is not
copied from the fixture. Approval tokens are synthetic TEST ONLY.
"""
from __future__ import annotations

import hashlib
import json

import pytest

from rea.website_p85 import (inspect_p85, build_p85, WebsiteReviewError,
                             VIEWPORTS, STEPS)
from rea.website_p70 import APPROVAL_TOKEN, PERMISSION_TOKEN

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
FABLE = ROOT / ".vendor" / "fable" / "engines" / "fable51"
ASTRA = ROOT / ".vendor" / "astra" / "engines" / "astra_p4"
CSV = "id,title,category,price\nA001,커피,음료,3000\nA002,차,음료,2000\nA003,연필,문구,500\n"
SITES = [
    ("catalog", "<header><nav>상품 카탈로그</nav><h1>상품 관리</h1></header>"),
    ("inventory", "<main><h1>재고 관리자</h1><aside>상품 분류</aside></main>"),
    ("directory", "<main><article><h1>업무 목록</h1></article></main>"),
]
REFERENCE_JS = """
const rows=[
{id:'A001',title:'커피',category:'음료'},
{id:'A002',title:'차',category:'음료'},
{id:'A003',title:'연필',category:'문구'}
];
function rerender() {
  const search=document.querySelector('#search').value;
  const category=document.querySelector('#category').value;
  const count=rows.filter(x=>(!search||x.title.includes(search)) &&
                             (!category||x.category===category)).length;
  document.querySelector('#count').textContent=count+'건';
}
document.querySelector('#search').addEventListener('input',rerender);
document.querySelector('#category').addEventListener('change',rerender);
document.querySelector('#first-detail').addEventListener('click',()=>{
  document.querySelector('#detail').textContent='커피';
});
rerender();
"""


def webpage(kind, heading, *, hostile=False):
    js = REFERENCE_JS
    if hostile:
        js += "\nfetch('https://example.invalid/forbidden');"
    return (
        '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Synthetic ' + kind + '</title>'
        '<style>body{margin:0;padding:16px;font-family:Arial,sans-serif}'
        'main{width:100%;max-width:840px;margin:auto} '
        'input,select{max-width:100%;box-sizing:border-box}</style></head><body>'
        + heading +
        '<section><label>검색<input id="search" type="search"></label>'
        '<label>분류<select id="category"><option value="">전체</option>'
        '<option value="음료">음료</option><option value="문구">문구</option></select></label>'
        '<div id="count"></div><button id="first-detail">상세 보기</button>'
        '<div id="detail"></div><table><tr><td>LOCAL_SYNTHETIC_CONTENT_NOT_FOR_COPY</td></tr></table>'
        '</section><script>' + js + '</script></body></html>'
    )


def make_inputs(tmp_path, kind="catalog", heading=None, *, hostile=False):
    if heading is None:
        heading = SITES[0][1]
    html = tmp_path / (kind + ".html")
    data = tmp_path / "customer.csv"
    html.write_text(webpage(kind, heading, hostile=hostile), encoding="utf-8")
    data.write_text(CSV, encoding="utf-8")
    args = {
        "fixture_sha256": hashlib.sha256(html.read_bytes()).hexdigest(),
        "owner_sha256": hashlib.sha256(data.read_bytes()).hexdigest(),
        "fixture_permission": PERMISSION_TOKEN, "owner_approval": APPROVAL_TOKEN,
        "fable_root": FABLE, "astra_root": ASTRA,
    }
    return html, data, args


@pytest.mark.parametrize("kind,heading", SITES)
def test_three_domains_two_viewports_real_chromium_astra_and_pro(kind, heading, tmp_path):
    html, data, opts = make_inputs(tmp_path, kind, heading)
    original_html = html.read_bytes()
    original_csv = data.read_bytes()
    receipt, observed = inspect_p85(html, fixture_sha256=opts["fixture_sha256"], astra_root=ASTRA)
    assert receipt["schema_version"] == "rea.website.p85.v1"
    assert receipt["site_approval"] is False
    assert receipt["production_release"] == "HOLD"
    assert len(receipt["review_digest"]) == 64
    assert len(receipt["astra_observation_bundle"]["observations"]) == 6
    assert len(receipt["astra_observation_bundle"]["evidence"]) == 8
    spec = receipt["astra_spec_draft"]
    assert not spec["implementation_ready"]
    assert all(x["review_status"] == "requires_review" for x in spec["candidate_features"])
    assert all(x["status"] == "pending" for x in spec["approval_gates"])
    assert list(receipt["subject"]["viewports"]) == list(VIEWPORTS)
    for name in VIEWPORTS:
        assert [x["feature"] for x in observed[name]["steps"]] == list(STEPS)
        assert observed[name]["steps"][-1]["after"]["detail"] == "커피"
        assert len(observed[name]["snapshots"]) == 4
        assert observed[name]["metrics"]["document_width"] <= observed[name]["metrics"]["width"] + 1

    out = tmp_path / "independent_app"
    outcome = build_p85(html, data, out,
                        approved_review_digest=receipt["review_digest"], **opts)
    assert outcome["status"] == "P85_SYNTHETIC_REVIEW_HOLD"
    assert outcome["rows"] == 3
    assert outcome["browser_sequences"] == 2 and outcome["steps_per_sequence"] == 3
    assert outcome["functional_parity"] == "PASS_SYNTHETIC"
    assert outcome["visual_parity"] == "UNVERIFIED_DIFFERENCE_REPORTED"
    assert out.exists()
    assert html.read_bytes() == original_html
    assert data.read_bytes() == original_csv
    audit = json.loads((out / "review/p85_evidence_and_visual_diff.json").read_text("utf-8"))
    assert audit["review_digest"] == receipt["review_digest"]
    assert audit["human_review"].startswith("PENDING")
    assert len(audit["astra_spec_draft"]["candidate_features"]) == 6
    for name, report in audit["source_visual_difference"].items():
        assert name in VIEWPORTS
        assert report["functional_states"] == "MATCHED_SYNTHETIC_3_STEP_SEQUENCE"
        assert report["responsive_overflow"] is False
        assert len(report["screenshots"]) == 4
        for difference in report["screenshots"]:
            assert difference["verdict"] == "VISUAL_DIFFERENCE_REQUIRES_HUMAN_REVIEW"
            assert 0 <= difference["mean_absolute_rgb_difference"] <= 1
        for i in range(4):
            assert (out / f"review/p85_{name}_{i}.png").read_bytes().startswith(b"\x89PNG")
            assert (out / f"review/p85_generated_{name}_{i}.png").read_bytes().startswith(b"\x89PNG")
    manifest = json.loads((out / "manifest.json").read_text("utf-8"))
    assert manifest["website_p85"]["commercial_release"] == "HOLD"
    assert manifest["website_p85"]["visual_parity"] == "UNVERIFIED_DIFFERENCE_REPORTED"
    assert not (out / html.name).exists()
    assert b"LOCAL_SYNTHETIC_CONTENT_NOT_FOR_COPY" not in b"".join(
        file.read_bytes() for file in out.rglob("*") if file.is_file()
    )


@pytest.mark.parametrize("bad_field,bad_value", [
    ("fixture_permission", "NO"),
    ("owner_approval", "NO"),
    ("owner_sha256", "0" * 64),
])
def test_permission_or_customer_sha_fail_closed_before_publish(tmp_path, bad_field, bad_value):
    html, data, opts = make_inputs(tmp_path)
    opts[bad_field] = bad_value
    out = tmp_path / "independent_app"
    with pytest.raises((ValueError, OSError)):
        build_p85(html, data, out, approved_review_digest="0" * 64, **opts)
    assert not out.exists()


def test_reject_stale_approval_digest_without_delivery(tmp_path):
    html, data, opts = make_inputs(tmp_path)
    out = tmp_path / "independent_app"
    with pytest.raises(WebsiteReviewError, match="digest"):
        build_p85(html, data, out, approved_review_digest="0" * 64, **opts)
    assert not out.exists()


def test_existing_owner_output_must_not_be_modified(tmp_path):
    html, data, opts = make_inputs(tmp_path)
    out = tmp_path / "independent_app"
    out.mkdir()
    (out / "customer_document.txt").write_text("KEEP")
    with pytest.raises(FileExistsError):
        build_p85(html, data, out, approved_review_digest="0" * 64, **opts)
    assert (out / "customer_document.txt").read_text() == "KEEP"


def test_external_resource_marker_fails_before_browser(tmp_path):
    html, _, opts = make_inputs(tmp_path, hostile=True)
    with pytest.raises(WebsiteReviewError, match="external URL"):
        inspect_p85(html, fixture_sha256=opts["fixture_sha256"], astra_root=ASTRA)


def test_modified_reference_sha_not_scanned(tmp_path):
    html, _, opts = make_inputs(tmp_path)
    html.write_text("<html>CHANGED</html>", encoding="utf-8")
    with pytest.raises(WebsiteReviewError, match="SHA mismatch"):
        inspect_p85(html, fixture_sha256=opts["fixture_sha256"], astra_root=ASTRA)


def test_symlink_fixture_is_rejected(tmp_path):
    html, _, opts = make_inputs(tmp_path)
    link = tmp_path / "other.html"
    try:
        link.symlink_to(html)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks prohibited by platform")
    with pytest.raises(WebsiteReviewError, match="non-symlink"):
        inspect_p85(link, fixture_sha256=opts["fixture_sha256"], astra_root=ASTRA)
