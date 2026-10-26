"""D3 three independent synthetic domains and reproducible delivery tests."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import zipfile

import pytest
from fastapi.testclient import TestClient

from rea.orchestrator import build
from rea.delivery import DeliveryError, create_delivery, verify_delivery

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("qa_cafe.csv", 4, "음료", 2, "카페라떼", "C02"),
    ("qa_inventory.csv", 5, "저장장치", 2, "NAS", "I02"),
    ("qa_trends.csv", 5, "JP", 2, "실버", "T03"),
]


def client(out: Path) -> TestClient:
    spec = importlib.util.spec_from_file_location("rea_d3_generated", out / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return TestClient(module.app)


@pytest.mark.parametrize("filename,total,category,count,query,expected_id", CASES)
def test_three_independent_data_domains(tmp_path, filename, total, category, count, query, expected_id):
    out = tmp_path / "generated"
    original = (ROOT / "samples" / filename).read_bytes()
    manifest = build(ROOT / "samples" / filename, out)
    assert manifest["rows"] == total
    assert manifest["fable_review"]["status"] == "NOT_REQUESTED"
    assert manifest["generation_input"] == "customer_supplied_csv_only"
    assert (ROOT / "samples" / filename).read_bytes() == original
    c = client(out)
    assert c.get("/health").json()["status"] == "ok"
    assert c.get("/api/items").json()["total"] == total
    assert c.get("/api/items", params={"category": category}).json()["total"] == count
    r = c.get("/api/items", params={"q": query}).json()
    assert r["total"] == 1 and r["items"][0]["id"] == expected_id
    assert c.get("/api/items/" + expected_id).status_code == 200
    assert c.get("/api/items/missing").status_code == 404
    with sqlite3.connect(out / "data.sqlite") as db:
        assert db.execute("SELECT count(*) FROM items").fetchone()[0] == total


def test_export_integrity_and_contents(tmp_path):
    path = tmp_path / "cafe.zip"
    manifest = create_delivery(ROOT / "samples/qa_cafe.csv", path, "Cafe demo")
    verified = verify_delivery(path)
    assert manifest == verified
    assert verified["runtime_binding"] == "127.0.0.1"
    assert not verified["vendor_engines_bundled"]
    assert not verified["raw_fable_capture_bundled"]
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        assert "launch_windows.cmd" in names and "README_WINDOWS.md" in names
        assert "app/data.sqlite" in names and "app/app.py" in names
        assert not any("fable_record_redacted" in n for n in names)
        assert b"127.0.0.1" in z.read("launch_windows.cmd")
        assert b"REA_WEB_PORT" in z.read("launch_windows.cmd")


def test_deterministic_archive_bytes(tmp_path):
    a, b = tmp_path / "a.zip", tmp_path / "b.zip"
    create_delivery(ROOT / "samples/qa_inventory.csv", a)
    create_delivery(ROOT / "samples/qa_inventory.csv", b)
    assert a.read_bytes() == b.read_bytes()


def test_export_existing_zip_preserved(tmp_path):
    out = tmp_path / "existing.zip"
    out.write_bytes(b"OWNER-DATA")
    with pytest.raises(FileExistsError):
        create_delivery(ROOT / "samples/qa_cafe.csv", out)
    assert out.read_bytes() == b"OWNER-DATA"


def test_bad_input_never_creates_delivery(tmp_path):
    source = tmp_path / "bad.csv"
    source.write_text("id,title,category\nX,one,a\nX,two,b\n", encoding="utf-8")
    out = tmp_path / "never.zip"
    with pytest.raises(ValueError):
        create_delivery(source, out)
    assert not out.exists()


def test_unsafe_output_extension_rejected(tmp_path):
    with pytest.raises(DeliveryError):
        create_delivery(ROOT / "samples/qa_cafe.csv", tmp_path / "app.exe")


def test_zip_manifest_checksum_tamper_detected(tmp_path):
    original = tmp_path / "original.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", original)
    corrupted = tmp_path / "corrupted.zip"
    with zipfile.ZipFile(original) as src, zipfile.ZipFile(corrupted, "x") as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "README_WINDOWS.md":
                data += b"\nMODIFIED"
            dst.writestr(item, data)
    with pytest.raises(DeliveryError, match="Checksum mismatch"):
        verify_delivery(corrupted)


def test_zip_traversal_rejected(tmp_path):
    original = tmp_path / "malicious.zip"
    with zipfile.ZipFile(original, "x") as z:
        z.writestr("../outside", b"unsafe")
        z.writestr("delivery_manifest.json", "{}")
    with pytest.raises(DeliveryError, match="Unsafe"):
        verify_delivery(original)


def test_optional_fable_export_review_unserved(tmp_path):
    pytest.importorskip("astra_contracts.observation")
    archive = tmp_path / "review.zip"
    original = (ROOT / "samples/fable_record_redacted.json").read_bytes()
    create_delivery(ROOT / "samples/qa_trends.csv", archive,
                    fable_result=ROOT / "samples/fable_record_redacted.json")
    verify_delivery(archive)
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        assert "app/review/fable_review.json" in names
        assert not any(n.endswith("fable_record_redacted.json") for n in names)
        review = json.loads(z.read("app/review/fable_review.json"))
        assert review["status"] == "REVIEW_REQUIRED"
        assert not review["generation_allowed"]
        assert review["astra_contract_validation"] == "VALIDATED"
    assert (ROOT / "samples/fable_record_redacted.json").read_bytes() == original


def test_cli_pack_verify(tmp_path):
    archive = tmp_path / "demo.zip"
    result = subprocess.run([
        sys.executable, "-m", "rea.delivery", "pack", "--csv",
        "samples/qa_cafe.csv", "--out", str(archive)],
        cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    result2 = subprocess.run([
        sys.executable, "-m", "rea.delivery", "verify", "--zip", str(archive)],
        cwd=ROOT, capture_output=True, text=True)
    assert result2.returncode == 0, result2.stderr
    assert json.loads(result.stdout) == json.loads(result2.stdout)


def test_xss_payload_is_data_not_markup(tmp_path):
    out = tmp_path / "site"
    build(ROOT / "samples/qa_inventory.csv", out)
    item = client(out).get("/api/items/I02").json()
    assert item["attributes"]["notes"] == "<script>alert(1)</script>"
    assert "textContent" in (out / "static/app.js").read_text(encoding="utf-8")
