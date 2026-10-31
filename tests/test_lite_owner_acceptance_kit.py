"""Synthetic offline owner acceptance kit: immutable package, no false human PASS."""
from __future__ import annotations

import json
import zipfile

import pytest

from scripts.rea_lite_owner_acceptance_kit import build_kit, archive_kit, verify_kit


def test_kit_three_themes_and_all_owner_fixtures(tmp_path):
    destination = tmp_path / "fresh-owner-kit"
    report = build_kit(destination)
    assert report == {
        "status": "SYNTHETIC_OWNER_KIT_VERIFIED",
        "files": 10, "html_themes": 3,
        "human_windows_acceptance": "NOT_RUN",
        "commercial_release": "NOT_APPROVED",
    }
    assert verify_kit(destination) == report
    assert "NEW_CHECK_ITEM" in (destination / "valid_update.csv").read_text(encoding="utf-8")
    assert "D01" in (destination / "duplicate_id.csv").read_text(encoding="utf-8")
    checklist = (destination / "CHECKLIST_KO.txt").read_text(encoding="utf-8")
    assert "오프라인 HTML 열기: PASS / FAIL / BLOCKED / NOT_RUN" in checklist
    assert "실제 사용자 소요시간(분): ________ 또는 NOT_MEASURED" in checklist
    assert (destination / "CHECKLIST_KO.txt").read_bytes().startswith(b"\xef\xbb\xbf")
    assert (destination / "README_FIRST.txt").read_bytes().startswith(b"\xef\xbb\xbf")
    assert "검수 절차" in (destination / "CHECKLIST_KO.txt").read_text(encoding="utf-8-sig")
    manifest = json.loads((destination / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["human_windows_acceptance"] == "NOT_RUN"
    assert manifest["commercial_release"] == "NOT_APPROVED"


def test_kit_never_overwrites_existing_directory(tmp_path):
    destination = tmp_path / "owned"
    destination.mkdir()
    sentinel = destination / "do_not_touch.txt"
    sentinel.write_text("original", encoding="utf-8")
    with pytest.raises(FileExistsError):
        build_kit(destination)
    assert sentinel.read_text(encoding="utf-8") == "original"


def test_kit_tamper_detected_and_invalid_files_refused(tmp_path):
    destination = tmp_path / "accepted"
    build_kit(destination)
    file = destination / "cafe.html"
    file.write_bytes(file.read_bytes() + b"\nchanged")
    with pytest.raises(ValueError, match="Integrity mismatch"):
        verify_kit(destination)
    file.write_bytes(file.read_bytes().replace(b"\nchanged", b""))
    (destination / "extra.txt").write_text("unexpected", encoding="utf-8")
    with pytest.raises(ValueError, match="Unexpected or missing"):
        verify_kit(destination)


def test_zip_exact_inventory_no_overwrite(tmp_path):
    destination = tmp_path / "kit"
    build_kit(destination)
    archive = tmp_path / "package.zip"
    archive_kit(destination, archive)
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist()) == 10
        assert z.testzip() is None
        assert b"NOT_RUN" in z.read("MANIFEST.json")
        assert b"NEW_CHECK_ITEM" in z.read("valid_update.csv")
    original = archive.read_bytes()
    with pytest.raises(FileExistsError):
        archive_kit(destination, archive)
    assert archive.read_bytes() == original
