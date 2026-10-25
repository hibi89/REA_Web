"""D10 test-only RC packages, offline self-check, observed metadata honesty."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import pytest

from rea.delivery import create_delivery
from rea.observed_deps import inventory
from rea.provenance import inspect_delivery
from scripts.d10_make_rc import REQUIRED_OPTIONS, make

ROOT = Path(__file__).resolve().parents[1]


def _unpack(archive: Path, out: Path):
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(out)


def _self_check(extracted: Path):
    check = subprocess.run(
        [sys.executable, str(extracted / "self_check.py"), "--root", str(extracted)],
        capture_output=True, text=True,
    )
    return check, json.loads(check.stdout)


def test_all_three_rc_modes_and_reproducible_archive_digests(tmp_path):
    first, second = tmp_path / "rc1", tmp_path / "rc2"
    report1, report2 = make(first), make(second)
    assert report1 == report2
    assert report1["classification"] == "SYNTHETIC_LOCAL_TEST_ONLY_NOT_FOR_SALE"
    assert report1["compliance"] == "NOT_CLEARED"
    assert [p["filename"] for p in report1["packages"]] == list(REQUIRED_OPTIONS)
    for entry in report1["packages"]:
        a, b = first / entry["filename"], second / entry["filename"]
        assert a.read_bytes() == b.read_bytes()
        assert hashlib.sha256(a.read_bytes()).hexdigest() == entry["sha256"]
        checked = inspect_delivery(a)
        assert checked["delivery_integrity"] == "VERIFIED_SHA256"
        assert checked["overall_commercial_clearance"] == "NOT_GRANTED"
        unpack = tmp_path / entry["filename"].replace(".zip", "")
        _unpack(a, unpack)
        assert (unpack / "check_windows.cmd").is_file()
        assert (unpack / "self_check.py").is_file()
        assert "127.0.0.1" in (unpack / "launch_windows.cmd").read_text()
        assert "NOT commercially approved" in (unpack / "README_WINDOWS.md").read_text(encoding="utf-8")
        check, payload = _self_check(unpack)
        assert check.returncode == 0, check.stderr
        assert payload["status"] == "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE"
        assert payload["database"] == "READONLY_OPEN_SUCCESS"
        assert payload["integrity"] == "MATCHED_DELIVERY_MANIFEST_SHA256"
        assert payload["row_count_only"] in (3, 4, 5)
        assert payload["overall_commercial_clearance"] == "NOT_GRANTED"
        assert payload["runtime_network_call"] is False
    assert inspect_delivery(first / REQUIRED_OPTIONS[1])["owner_mapping_receipt_present"]
    assert inspect_delivery(first / REQUIRED_OPTIONS[2])["two_file_append_receipt_present"]
    assert not inspect_delivery(first / REQUIRED_OPTIONS[0])["two_file_append_receipt_present"]


def test_rc_never_overwrites_existing_destination(tmp_path):
    dest = tmp_path / "existing"
    dest.mkdir()
    (dest / "owner.txt").write_text("DO NOT TOUCH")
    with pytest.raises(FileExistsError):
        make(dest)
    assert (dest / "owner.txt").read_text() == "DO NOT TOUCH"


def test_customer_selfcheck_detects_sha_tampering(tmp_path):
    archive = tmp_path / "customer.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", archive)
    extracted = tmp_path / "extracted"
    _unpack(archive, extracted)
    target = extracted / "app/static/app.js"
    target.write_bytes(target.read_bytes() + b"\nunauthorized_content")
    process, payload = _self_check(extracted)
    assert process.returncode == 2
    assert payload["status"] == "FAIL_LOCAL_PREREQUISITES"
    assert payload["integrity"] == "NOT_VERIFIED"
    assert payload["overall_commercial_clearance"] == "NOT_GRANTED"


def test_customer_selfcheck_detects_missing_sqlite(tmp_path):
    archive = tmp_path / "customer.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", archive)
    unpacked = tmp_path / "unpacked"
    _unpack(archive, unpacked)
    (unpacked / "app/data.sqlite").unlink()
    proc, payload = _self_check(unpacked)
    assert proc.returncode == 2
    assert payload["database"] == "NOT_CHECKED"


def test_self_check_missing_dependencies_fail_closed(monkeypatch, tmp_path):
    archive = tmp_path / "customer.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", archive)
    out = tmp_path / "extracted"
    _unpack(archive, out)
    spec = importlib.util.spec_from_file_location("customer_selfcheck_example", out / "self_check.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    original = mod.metadata.version
    def missing(name):
        if name == "uvicorn":
            raise mod.metadata.PackageNotFoundError(name)
        return original(name)
    monkeypatch.setattr(mod.metadata, "version", missing)
    report = mod.inspect(out)
    assert report["status"] == "FAIL_LOCAL_PREREQUISITES"
    assert "Missing Python dependency: uvicorn" in report["issues"]
    assert report["runtime_network_call"] is False


def test_customer_windows_cmd_uses_local_selfcheck_only(tmp_path):
    archive = tmp_path / "delivery.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", archive)
    out = tmp_path / "space containing folder"
    _unpack(archive, out)
    launch = (out / "check_windows.cmd").read_text(encoding="ascii")
    assert "self_check.py" in launch
    assert "pip install" not in launch
    assert "curl " not in launch
    assert "https://" not in launch
    if sys.platform == "win32":
        result = subprocess.run(["cmd", "/c", str(out / "check_windows.cmd")],
                                cwd=out, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert "PASS_LOCAL_PREREQUISITES" in result.stdout


def test_observed_dependency_inventory_is_not_license_approval():
    report = inventory()
    assert report["classification"] == "CI_ENVIRONMENT_ONLY"
    assert report["commercial_license_clearance"] == "NOT_GRANTED"
    assert report["wheels_bundled_in_delivery_zip"] is False
    assert report["transitive_licensing_and_vulnerabilities_reviewed"] is False
    observed = {x["name"]: x for x in report["distributions"]}
    assert observed["fastapi"]["version"]
    assert observed["uvicorn"]["version"]
    assert report["exact_installed_versions_are_observations_not_customer_lock"] is True
    assert all(not x.get("legal_contents_reviewed", False)
               for x in report["distributions"])
