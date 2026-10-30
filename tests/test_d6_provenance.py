"""D6 offline shipment/vendor provenance tests. PASS is not license clearance."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest
from rea.delivery import create_delivery
from rea.provenance import (
    ALLOWED_DELIVERY, AuditError, _direct_deps, _git_blob_sha,
    inspect_delivery, verify_vendor_snapshot,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("name,kind", [
    ("qa_cafe.csv", "customer_supplied_csv"),
    ("qa_products.json", "customer_supplied_json"),
])
def test_csv_json_package_allowlist_and_bounded_sbom(tmp_path, name, kind):
    archive = tmp_path / "delivery.zip"
    create_delivery(ROOT / "samples" / name, archive)
    report = inspect_delivery(archive)
    assert report["delivery_integrity"] == "VERIFIED_SHA256"
    assert report["overall_commercial_clearance"] == "NOT_GRANTED"
    assert report["source_kind"] == kind
    assert report["vendor_source_files_bundled"] is False
    assert report["raw_fable_capture_bundled"] is False
    assert report["customer_data_sensitivity"] == "NOT_ASSESSED"
    assert report["transitive_dependency_inventory"] == "NOT_ASSESSED"
    assert {d["name"] for d in report["dependencies"]} == {"fastapi", "starlette", "uvicorn"}
    assert all(d["license_verified"] is False for d in report["dependencies"])
    assert all(d["installed_version"] is None for d in report["dependencies"])
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        assert names <= ALLOWED_DELIVERY
        assert not any("engines/" in x or "fable_record_redacted" in x for x in names)
    metadata = json.dumps(report, ensure_ascii=False)
    assert "블렌드 커피" not in metadata
    assert "아메리카노" not in metadata
    assert "J01" not in metadata
    assert name not in metadata
    assert "secrets/PII not certified absent" in metadata


def test_optional_fable_review_not_autoapproved(tmp_path):
    pytest.importorskip("astra_contracts.observation")
    archive = tmp_path / "reference.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", archive,
                    fable_result=ROOT / "samples/fable_record_redacted.json")
    report = inspect_delivery(archive)
    assert report["review_report_present"] is True
    assert report["vendor_source_files_bundled"] is False


def test_validly_rehashed_malicious_archive_is_still_rejected(tmp_path):
    ordinary = tmp_path / "normal.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", ordinary)
    evil = tmp_path / "malicious.zip"
    with zipfile.ZipFile(ordinary) as zf:
        files = {name: zf.read(name) for name in zf.namelist()
                 if name != "delivery_manifest.json"}
    files["app/engines/fable51/scan.py"] = b"not authorized vendor source"
    manifest = {
        "schema_version": "rea.delivery.v0.1",
        "files": [{"path": name, "sha256": hashlib.sha256(data).hexdigest(),
                   "bytes": len(data)} for name, data in sorted(files.items())],
    }
    files["delivery_manifest.json"] = json.dumps(manifest).encode()
    with zipfile.ZipFile(evil, "x") as zf:
        for name, contents in files.items():
            zf.writestr(name, contents)
    with pytest.raises(AuditError, match="allowlist"):
        inspect_delivery(evil)


def test_unauthorized_dotenv_rejected(tmp_path):
    ordinary = tmp_path / "normal.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", ordinary)
    evil = tmp_path / "secret.zip"
    with zipfile.ZipFile(ordinary) as source, zipfile.ZipFile(evil, "x") as target:
        for entry in source.infolist():
            target.writestr(entry, source.read(entry.filename))
        target.writestr("app/.env", b"SECRET=DO_NOT_SHIP")
    with pytest.raises((AuditError, ValueError)):
        inspect_delivery(evil)


@pytest.mark.parametrize("requirements", [
    "fastapi>=0.110,<1\nstarlette>=1.3.1,<2\nuvicorn>=0.27,<1\nrequests>=2,<3\n",
    "fastapi>=0.110,<1\nstarlette>=1.3.1,<2\nuvicorn @ https://example.com/pkg.whl\n",
    "fastapi>=0.110,<1\nstarlette>=1.3.1,<2\nfastapi>=0.110,<1\nuvicorn>=0.27,<1\n",
    "fastapi>=0.110,<1\nstarlette>=1.3.1,<2\n",
    "fastapi==0.115.2\nstarlette>=1.3.1,<2\nuvicorn>=0.27,<1\n",
    "fastapi>=0.110,<1\nstarlette>=0.46.0,<2\nuvicorn>=0.27,<1\n",
])
def test_unreviewed_runtime_dependency_changes_rejected(requirements):
    with pytest.raises(AuditError):
        _direct_deps(requirements)


def test_missing_vendor_checkout_fails_closed(tmp_path):
    with pytest.raises(AuditError, match="Missing vendor"):
        verify_vendor_snapshot("astra_p4", tmp_path)


def test_git_blob_hash_matches_git_object_formula():
    payload = b"hello\n"
    assert _git_blob_sha(payload) == hashlib.sha1(b"blob 6\0hello\n").hexdigest()


def test_synthetic_vendor_file_verified_but_licence_not_assumed(tmp_path, monkeypatch):
    from rea import provenance
    root = tmp_path / "vendor"
    folder = root / "engines" / "test_vendor"
    (folder / "provenance").mkdir(parents=True)
    (folder / "example.py").write_text("a=1\n", encoding="utf-8")
    blob = (folder / "example.py").read_bytes()
    manifest = {"source_commit": "f" * 40,
                "upstream_github_git_blob_sha": {"example.py": _git_blob_sha(blob)}}
    (folder / "provenance" / "BATCH_01.json").write_text(
        json.dumps(manifest), encoding="utf-8")
    monkeypatch.setitem(provenance.VENDORS, "test_vendor", {
        "path": "engines/test_vendor", "upstream": "synthetic/source",
        "commit": "f" * 40, "count": 1, "batches": 1,
    })
    evidence = verify_vendor_snapshot("test_vendor", root)
    assert evidence["checked_source_count"] == 1
    assert evidence["license_or_notice_artifacts_in_snapshot"] == []
    assert evidence["license_grant_status"] == "NO_LICENSE_ARTIFACT_FOUND"
    assert evidence["commercial_redistribution_cleared"] is False
    (folder / "example.py").write_text("a=2\n", encoding="utf-8")
    with pytest.raises(AuditError, match="SHA mismatch"):
        verify_vendor_snapshot("test_vendor", root)


def test_cli_writes_readonly_metadata_without_overwriting(tmp_path):
    archive, audit = tmp_path / "cafe.zip", tmp_path / "audit.json"
    create_delivery(ROOT / "samples/qa_cafe.csv", archive)
    argv = [sys.executable, "-m", "rea.provenance", "inspect-zip",
            "--zip", str(archive), "--out", str(audit)]
    check = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True)
    assert check.returncode == 0, check.stderr
    doc = json.loads(audit.read_text(encoding="utf-8"))
    assert doc["overall_commercial_clearance"] == "NOT_GRANTED"
    assert doc["delivery_integrity"] == "VERIFIED_SHA256"
    check2 = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True)
    assert check2.returncode != 0
    assert json.loads(audit.read_text(encoding="utf-8")) == doc
