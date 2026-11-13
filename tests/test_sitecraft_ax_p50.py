"""Isolated SITECRAFT AX P50 acceptance: real frozen engines and Pro output."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3

from fastapi.testclient import TestClient
import pytest

from rea.sitecraft_ax import SCHEMA, build_p50, read_contract, WebsiteReviewError

ROOT = Path(__file__).resolve().parents[1]
FABLE = ROOT / ".vendor" / "fable" / "engines" / "fable51"
ASTRA = ROOT / ".vendor" / "astra" / "engines" / "astra_p4"

HTML = """<!doctype html><html><body><nav><a href="/fake">Nav</a></nav>
<h1>REFERENCE_SECRET_NEVER_COPY</h1>
<form><input type="search"></form><table><tr><td>sample</td></tr></table>
<article>synthetic detail</article><script>NEVER_COPY_SCRIPT</script>
</body></html>"""
CSV = "sku,name,group,amount\nA1,커피,음료,3000\nA2,차,음료,2000\nA3,연필,문구,500\n"


@pytest.fixture
def packet(tmp_path):
    html = tmp_path / "reference.html"
    csv = tmp_path / "items.csv"
    html.write_text(HTML, encoding="utf-8")
    csv.write_text(CSV, encoding="utf-8")
    spec = {"schema": SCHEMA, "product": "SITECRAFT AX",
            "mode": "synthetic_local_static_only",
            "reference_html": "reference.html",
            "reference_sha256": hashlib.sha256(html.read_bytes()).hexdigest(),
            "owner_csv": "items.csv",
            "owner_sha256": hashlib.sha256(csv.read_bytes()).hexdigest(),
            "mapping": {"id": "sku", "title": "name", "category": "group"},
            "permission": "YES_OWNER_AUTHORIZED_LOCAL_FIXTURE",
            "approval": "APPROVE_SYNTHETIC_ONLY",
            "external_network_allowed": False,
            "commercial_release_allowed": False}
    contract = tmp_path / "contract.json"
    contract.write_text(json.dumps(spec), encoding="utf-8")
    return contract, spec, html, csv


def test_contract_is_explicit_and_source_pinned(packet):
    path, spec, html, csv = packet
    data, actual_html, actual_csv = read_contract(path)
    assert data == spec and actual_html == html and actual_csv == csv


@pytest.mark.parametrize("key,value", [
    ("schema", "bad"), ("mode", "public_live"),
    ("permission", "PUBLIC_URL"), ("approval", "APPROVE"),
    ("external_network_allowed", True), ("commercial_release_allowed", True),
    ("reference_html", "../reference.html"),
    ("reference_html", "https://example.com/reference.html"),
    ("reference_html", r"C:\reference.html"),
    ("reference_sha256", "0" * 64),
    ("owner_sha256", "0" * 64),
    ("mapping", {"id": "sku", "title": "sku", "category": "group"}),
])
def test_fail_closed_no_output(packet, tmp_path, key, value):
    path, spec, *_ = packet
    spec[key] = value
    path.write_text(json.dumps(spec), encoding="utf-8")
    with pytest.raises((WebsiteReviewError, OSError)):
        build_p50(path, tmp_path / "blocked", fable_root=FABLE, astra_root=ASTRA)
    assert not (tmp_path / "blocked").exists()


def test_unknown_field_rejected(packet):
    path, spec, *_ = packet
    spec["cookie"] = "cannot pass"
    path.write_text(json.dumps(spec), encoding="utf-8")
    with pytest.raises(WebsiteReviewError):
        read_contract(path)


def test_duplicate_key_rejected(packet):
    path, *_ = packet
    path.write_text('{"schema":"one","schema":"two"}', encoding="utf-8")
    with pytest.raises(WebsiteReviewError, match="Duplicate"):
        read_contract(path)


def test_changed_owner_data_rejected(packet, tmp_path):
    path, _, _, csv = packet
    csv.write_text(CSV + "A4,사탕,식품,100\n", encoding="utf-8")
    with pytest.raises(WebsiteReviewError, match="SHA"):
        build_p50(path, tmp_path / "blocked", fable_root=FABLE, astra_root=ASTRA)
    assert not (tmp_path / "blocked").exists()


def test_existing_customer_output_preserved(packet, tmp_path):
    path, *_ = packet
    out = tmp_path / "existing"
    out.mkdir()
    (out / "keep.txt").write_text("KEEP", encoding="utf-8")
    with pytest.raises(FileExistsError):
        build_p50(path, out, fable_root=FABLE, astra_root=ASTRA)
    assert (out / "keep.txt").read_text("utf-8") == "KEEP"


def test_symlink_contract_refused(packet, tmp_path):
    path, *_ = packet
    link = tmp_path / "linked.json"
    try:
        link.symlink_to(path)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks unavailable")
    with pytest.raises(WebsiteReviewError):
        read_contract(link)


def test_real_fable_astra_pro_and_http_sqlite_end_to_end(packet, tmp_path):
    path, _, html, csv = packet
    html_before, csv_before = html.read_bytes(), csv.read_bytes()
    out = tmp_path / "new_app"
    result = build_p50(path, out, fable_root=FABLE, astra_root=ASTRA)
    assert result["product"] == "SITECRAFT AX"
    assert result["gate"] == "P50_SYNTHETIC_ONLY"
    assert result["fable_local_get_count"] == 1
    assert result["approved_synthetic_rows"] == 3
    assert result["commercial_release"] == "HOLD"
    assert result["site_behavior_approved"] is False
    assert html.read_bytes() == html_before and csv.read_bytes() == csv_before
    review = json.loads((out / "review" / "website_p50_review.json").read_text("utf-8"))
    assert review["fable_actual_scanner"]
    assert review["fable_astra_validation"] == "NO_UI_OBSERVATIONS"
    assert review["reference_behavior_status"] == "REVIEW_REQUIRED"
    assert review["astra_site_spec"]["implementation_ready"] is False
    manifest = json.loads((out / "manifest.json").read_text("utf-8"))
    assert manifest["rows"] == 3
    assert manifest["reference_review"]["used_for_app_data"] is False
    with sqlite3.connect(out / "data.sqlite") as conn:
        assert conn.execute("select count(*) from items").fetchone()[0] == 3
    module_spec = importlib.util.spec_from_file_location("sitecraft_test_generated", out / "app.py")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    with TestClient(module.app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/api/items").json()["total"] == 3
        assert client.get("/api/items?category=음료").json()["total"] == 2
        assert client.get("/api/items/A1").json()["title"] == "커피"
        assert client.get("/review/website_p50_review.json").status_code == 404
    contents = b"".join(p.read_bytes() for p in out.rglob("*") if p.is_file())
    assert b"REFERENCE_SECRET_NEVER_COPY" not in contents
    assert b"NEVER_COPY_SCRIPT" not in contents
    assert not (out / "reference.html").exists()
