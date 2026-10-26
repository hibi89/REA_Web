"""D20 extracted synthetic Windows kit offline self-check regressions."""
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


def unpack(tmp_path):
    archive = tmp_path / "pilot.zip"
    builder.build_kit(archive)
    root = tmp_path / "unpacked"
    root.mkdir()
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(root)
    return root


def test_extracted_real_kit_self_check_stdio(tmp_path):
    root = unpack(tmp_path)
    code = root / "CHECK_PILOT_OFFLINE.py"
    assert code.read_bytes() == Path(checker.__file__).read_bytes()
    result = subprocess.run([sys.executable, str(code)], cwd=root,
                            text=True, capture_output=True, timeout=30, check=False)
    assert result.returncode == 0, result.stderr
    proof = json.loads(result.stdout.strip())
    assert proof["status"] == "OFFLINE_KIT_INTEGRITY_PASS"
    assert proof["verified_files"] == 10
    assert proof["rows"] == 5
    assert proof["human_acceptance"] == "NOT_RUN"
    assert proof["commercial_clearance"] == "NOT_GRANTED"
    assert proof["network_requests"] == "NONE"


def test_checker_is_read_only_and_does_not_change_kit_bytes(tmp_path):
    root = unpack(tmp_path)
    names = sorted(builder.MEMBER_NAMES)
    before = {p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in names}
    result = checker.verify(root)
    assert result["status"] == "OFFLINE_KIT_INTEGRITY_PASS"
    after = {p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in names}
    assert before == after


@pytest.mark.parametrize("name", [
    "README_WINDOWS.txt", "sources/qa_guided.csv",
    "sources/qa_pair_extra.json", "CHECK_PILOT_OFFLINE.py",
    "HUMAN_PILOT_BLANK.csv", "MANUAL_TIME_LOG_BLANK.csv",
    "demo/approved_pair.zip", "CHECK_PILOT_WINDOWS.cmd",
    "OPERATOR_ONE_PAGE_WINDOWS.txt",
])
def test_changed_extracted_member_refused(tmp_path, name):
    root = unpack(tmp_path)
    source = root / name
    with source.open("ab") as handle:
        handle.write(b"MALICIOUS")
    with pytest.raises(ValueError, match="mismatch"):
        checker.verify(root)


def test_forged_human_acceptance_refused(tmp_path):
    root = unpack(tmp_path)
    manifest = root / "MANIFEST.json"
    meta = json.loads(manifest.read_text(encoding="utf-8"))
    meta["real_human_acceptance"] = "PASS"
    manifest.write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(ValueError, match="contract"):
        checker.verify(root)


def test_missing_demo_app_refused(tmp_path):
    root = unpack(tmp_path)
    (root/"demo"/"approved_pair.zip").unlink()
    with pytest.raises(ValueError):
        checker.verify(root)


def test_invalid_root_cannot_claim_success(tmp_path):
    with pytest.raises(ValueError, match="root"):
        checker.verify(tmp_path/"does-not-exist")


def test_symlink_refused_with_no_follow(tmp_path):
    root = unpack(tmp_path)
    original = root / "sources" / "qa_guided.csv"
    substitute = tmp_path / "external.csv"
    substitute.write_bytes(original.read_bytes())
    original.unlink()
    try:
        original.symlink_to(substitute)
    except (OSError, NotImplementedError):
        pytest.skip("Runner disallows symlink without developer mode")
    with pytest.raises(ValueError, match="Symlink"):
        checker.verify(root)


def test_stdlib_only_and_no_dynamic_installs_or_network():
    text = Path(checker.__file__).read_text(encoding="utf-8")
    assert "pip install" not in text
    assert "subprocess" not in text
    assert "urllib" not in text
    assert "import requests" not in text
    assert "httpx" not in text
    assert "import socket" not in text
    assert "eval(" not in text
    assert "exec(" not in text
    assert "OFFLINE_KIT_INTEGRITY_PASS" in text
    assert "NOT_GRANTED" in text


def test_no_overwrite_and_reproducibility_across_two_builds(tmp_path):
    a = tmp_path / "A.zip"
    b = tmp_path / "B.zip"
    builder.build_kit(a)
    builder.build_kit(b)
    assert a.read_bytes() == b.read_bytes()
    with pytest.raises(FileExistsError):
        builder.build_kit(a)
    assert checker.EXPECTED == builder.MEMBER_NAMES


def test_human_blank_log_remains_blank_after_check(tmp_path):
    root = unpack(tmp_path)
    checker.verify(root)
    for name in ("HUMAN_PILOT_BLANK.csv", "MANUAL_TIME_LOG_BLANK.csv"):
        assert (root / name).read_text(encoding="utf-8").count("\n") == 1
