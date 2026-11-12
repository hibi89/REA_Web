"""P50: real pinned Fable static scan + actual Astra P4 + original REA Pro.

All inputs synthetic, loopback-only. No third-party website contacted.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3

from fastapi.testclient import TestClient
import pytest

from rea.website_rebuild import rebuild_local_fixture, WebsiteReviewError

ROOT = Path(__file__).resolve().parents[1]
FABLE = ROOT / ".vendor" / "fable" / "engines" / "fable51"
ASTRA = ROOT / ".vendor" / "astra" / "engines" / "astra_p4"
HTML = """<!doctype html><html lang="ko"><head><title>synthetic store</title></head>
<body><nav><a href="/fake">상품 메뉴</a></nav>
<h1>LOCAL_SAMPLE_DO_NOT_REUSE</h1>
<form><input type="search" aria-label="Search"></form>
<table><tr><th>상품</th></tr><tr><td>demo</td></tr></table>
<article><p>synthetic detail</p></article>
<script>window.FAKE_SECRET_DO_NOT_COPY='not-a-real-secret';</script>
</body></html>"""
CSV = "id,title,category,price\nA001,커피,음료,3000\nA002,차,음료,2000\nA003,연필,문구,500\n"


@pytest.fixture
def materials(tmp_path):
    html = tmp_path / "fixture.html"
    csv = tmp_path / "owner.csv"
    html.write_text(HTML, encoding="utf-8")
    csv.write_text(CSV, encoding="utf-8")
    return html, csv, {
        "fixture_sha256": hashlib.sha256(html.read_bytes()).hexdigest(),
        "owner_sha256": hashlib.sha256(csv.read_bytes()).hexdigest(),
        "id_field": "id", "title_field": "title", "category_field": "category",
        "fixture_permission": "YES_LOCAL_FIXTURE", "owner_approval": "APPROVE",
        "fable_root": FABLE, "astra_root": ASTRA,
    }


def invoke(materials, output, **override):
    html, csv, args = materials
    return rebuild_local_fixture(html, csv, output, **(args | override))


def test_real_fable_astra_to_independent_app(materials, tmp_path):
    html, csv, _ = materials
    html_before, csv_before = html.read_bytes(), csv.read_bytes()
    out = tmp_path / "generated"
    result = invoke(materials, out)
    assert result["status"] == "P50_SYNTHETIC_REVIEW_HOLD"
    assert result["fable_requests"] == 1
    assert result["fable_real_static_scan"] and result["rows"] == 3
    assert html.read_bytes() == html_before and csv.read_bytes() == csv_before
    record = json.loads((out / "review" / "website_p50_review.json").read_text("utf-8"))
    assert record["schema_version"] == "rea.website.p50.v1"
    assert record["fable_actual_scanner"]
    assert record["fable_scan_mode"] == "static"
    assert record["fable_http_requests"] == 1
    assert record["fable_astra_validation"] == "NO_UI_OBSERVATIONS"
    assert record["reference_behavior_status"] == "REVIEW_REQUIRED"
    assert record["site_inferred_behavior_approved"] is False
    spec = record["astra_site_spec"]
    assert spec["candidate_features"] == []
    assert sorted(x["feature"] for x in spec["unresolved"]) == [
        "detail", "list", "navigation", "search",
    ]
    assert not spec["implementation_ready"]
    assert spec["db_api_mapping_status"] == "not_started"
    assert all(x["status"] == "pending" for x in spec["approval_gates"])
    manifest = json.loads((out / "manifest.json").read_text("utf-8"))
    assert manifest["reference_review"]["used_for_app_data"] is False
    assert manifest["rows"] == 3
    assert not (out / "fixture.html").exists()
    assert not (out / "fable_result.json").exists()
    with sqlite3.connect(out / "data.sqlite") as db:
        assert db.execute("select count(*) from items").fetchone()[0] == 3
    spec = importlib.util.spec_from_file_location("generated_website_p50", out / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with TestClient(module.app) as client:
        assert client.get("/health").json()["mode"] == "local_readonly"
        assert client.get("/api/items").json()["total"] == 3
        assert client.get("/api/items?category=음료").json()["total"] == 2
        assert client.get("/api/items/A001").json()["title"] == "커피"
        assert client.get("/review/website_p50_review.json").status_code == 404
        assert client.get("/manifest.json").status_code == 404
    output_blobs = b"".join(x.read_bytes() for x in out.rglob("*") if x.is_file())
    assert b"FAKE_SECRET_DO_NOT_COPY" not in output_blobs
    assert b"LOCAL_SAMPLE_DO_NOT_REUSE" not in output_blobs


@pytest.mark.parametrize("field,value", [
    ("fixture_permission", "NO"),
    ("owner_approval", "NO"),
    ("fixture_sha256", "0" * 64),
    ("owner_sha256", "0" * 64),
    ("id_field", "title"),
    ("fable_root", Path("/nonexistent/fable")),
    ("astra_root", Path("/nonexistent/astra")),
])
def test_fail_closed_gates(materials, tmp_path, field, value):
    out = tmp_path / "output"
    with pytest.raises((ValueError, OSError)):
        invoke(materials, out, **{field: value})
    assert not out.exists()


def test_existing_owner_folder_preserved(materials, tmp_path):
    out = tmp_path / "output"
    out.mkdir()
    (out / "owner.txt").write_text("KEEP", "utf-8")
    with pytest.raises(FileExistsError):
        invoke(materials, out)
    assert (out / "owner.txt").read_text("utf-8") == "KEEP"


def test_fixture_hash_mismatch_no_publish(materials, tmp_path):
    html, _, _ = materials
    html.write_text("<html>changed</html>", encoding="utf-8")
    with pytest.raises(WebsiteReviewError, match="SHA mismatch"):
        invoke(materials, tmp_path / "output")
    assert not (tmp_path / "output").exists()


def test_owner_source_mismatch_no_publish(materials, tmp_path):
    _, csv, _ = materials
    csv.write_text(CSV + "A004,사탕,식품,100\n", encoding="utf-8")
    with pytest.raises(WebsiteReviewError, match="SHA mismatch"):
        invoke(materials, tmp_path / "output")
    assert not (tmp_path / "output").exists()


def test_symlink_fixture_rejected(materials, tmp_path):
    html, csv, options = materials
    link = tmp_path / "linked.html"
    try:
        link.symlink_to(html)
    except (OSError, NotImplementedError):
        pytest.skip("Platform forbids symlink creation")
    with pytest.raises(WebsiteReviewError, match="non-symlink"):
        rebuild_local_fixture(link, csv, tmp_path / "output", **options)
    assert not (tmp_path / "output").exists()


def test_output_parent_must_exist(materials, tmp_path):
    with pytest.raises(WebsiteReviewError, match="Parent output directory"):
        invoke(materials, tmp_path / "missing-parent" / "output")
    assert not (tmp_path / "missing-parent").exists()
