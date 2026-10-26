"""D23 strict extracted synthetic kit inventory: no extra executable/hidden entries."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

from scripts import d19_owner_pilot as builder
from scripts import d20_offline_kit_check as checker


def _kit(tmp_path: Path) -> Path:
    archive = tmp_path / "synthetic-only.zip"
    builder.build_kit(archive)
    root = tmp_path / "clean-extracted-folder"
    root.mkdir()
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(root)
    return root


def _hashes(root: Path) -> dict:
    return {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in builder.MEMBER_NAMES
    }


def test_valid_ten_member_kit_passes_and_does_not_mutate_source(tmp_path):
    root = _kit(tmp_path)
    before = _hashes(root)
    result = checker.verify(root)
    assert result["status"] == "OFFLINE_KIT_INTEGRITY_PASS"
    assert result["verified_files"] == 10
    assert result["human_acceptance"] == "NOT_RUN"
    assert result["commercial_clearance"] == "NOT_GRANTED"
    assert result["network_requests"] == "NONE"
    assert _hashes(root) == before


@pytest.mark.parametrize("name", [
    "UNTRUSTED.EXE",
    "RUN_UNTRUSTED.cmd",
    ".hidden",
    "desktop.ini",
    "sources/extra.csv",
    "sources/.hidden",
    "demo/another.zip",
    "demo/launch.cmd",
])
def test_unexpected_file_in_any_extracted_directory_is_refused(tmp_path, name):
    root = _kit(tmp_path)
    before = _hashes(root)
    dest = root / name
    dest.write_bytes(b"not from signed synthetic ZIP")
    with pytest.raises(ValueError, match="Unexpected or unsafe"):
        checker.verify(root)
    assert _hashes(root) == before


@pytest.mark.parametrize("relative", [
    "UNAPPROVED", "sources/unapproved-folder", "demo/additional-folder",
])
def test_unexpected_empty_directory_also_refused(tmp_path, relative):
    root = _kit(tmp_path)
    (root / relative).mkdir()
    with pytest.raises(ValueError, match="Unexpected or unsafe"):
        checker.verify(root)


def test_removed_expected_directory_refused_without_external_reads(tmp_path):
    root = _kit(tmp_path)
    (root / "sources" / "qa_guided.csv").unlink()
    with pytest.raises(ValueError):
        checker.verify(root)


def test_symlink_unknown_entry_is_never_followed(tmp_path):
    root = _kit(tmp_path)
    outside = tmp_path / "outside-file.txt"
    outside.write_text("private marker", encoding="utf-8")
    try:
        (root / "NEW_SOURCE").symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks restricted by test runner")
    with pytest.raises(ValueError, match="Symlinks"):
        checker.verify(root)
    assert outside.read_text(encoding="utf-8") == "private marker"


def test_symlink_expected_directory_rejected(tmp_path):
    root = _kit(tmp_path)
    import shutil
    shutil.rmtree(root / "sources")
    real_sources = tmp_path / "external-public-fixtures"
    real_sources.mkdir()
    try:
        (root / "sources").symlink_to(real_sources, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks restricted by test runner")
    with pytest.raises(ValueError, match="Symlinks"):
        checker.verify(root)


def test_shipped_checker_cli_refuses_extra_file_without_success_claim(tmp_path):
    root = _kit(tmp_path)
    (root / "UNEXPECTED.txt").write_text("unknown", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(root / "CHECK_PILOT_OFFLINE.py")],
        cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=30, check=False
    )
    assert proc.returncode == 2
    assert "OFFLINE_KIT_NOT_VERIFIED" in proc.stderr
    assert "OFFLINE_KIT_INTEGRITY_PASS" not in proc.stdout
    assert "human_acceptance" not in proc.stdout


def test_human_logs_remain_external_no_unexpected_files(tmp_path):
    root = _kit(tmp_path)
    external = tmp_path / "external-private-observations"
    external.mkdir()
    (external / "HUMAN_PILOT_BLANK.csv").write_bytes(
        (root / "HUMAN_PILOT_BLANK.csv").read_bytes())
    assert checker.verify(root)["human_acceptance"] == "NOT_RUN"
    assert "EXACT_TWO_PINNED_PUBLIC_SYNTHETIC_FIXTURES" in (
        root / "MANIFEST.json").read_text(encoding="utf-8")
