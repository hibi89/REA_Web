"""D21 synthetic-only Windows CMD wrapper: source and native cmd.exe tests."""
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

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "d21_check_pilot_windows.cmd"
EXPECTED = {
    "success": "OFFLINE_KIT_INTEGRITY_PASS",
    "failed": "KIT_NOT_VERIFIED",
    "python": "MISSING_PYTHON",
    "checker": "MISSING_CHECKER",
    "arg": "INVALID_ARGUMENT",
}


def _extract(tmp_path: Path) -> Path:
    archive = tmp_path / "one-owner.zip"
    builder.build_kit(archive)
    extracted = tmp_path / "folder with spaces & chars"
    extracted.mkdir()
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(extracted)
    return extracted


def test_wrapper_is_ninth_sha_pinned_member(tmp_path):
    root = _extract(tmp_path)
    actual = (root / "CHECK_PILOT_WINDOWS.cmd").read_bytes()
    expected = SOURCE.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    assert actual == expected and actual.endswith(b"\r\n")
    assert set(builder.MEMBER_NAMES) == checker.EXPECTED
    assert len(builder.MEMBER_NAMES) == 9
    assert builder.verify_kit(tmp_path / "one-owner.zip")["verified_members"] == 9
    assert checker.verify(root)["verified_files"] == 9
    assert "CHECK_PILOT_WINDOWS.cmd" in builder.GUIDE


def test_wrapper_only_dispatches_local_stdlib_checker():
    data = SOURCE.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    assert data.startswith("@echo off\nsetlocal ")
    assert '"%~dp0CHECK_PILOT_OFFLINE.py"' in data
    assert "py -3.11" in data
    assert "python -c" in data
    assert "goto python_fallback" in data
    assert "exit /b %_rea_result%" in data
    assert "MISSING_PYTHON" in data
    assert "MISSING_CHECKER" in data
    assert "INVALID_ARGUMENT" in data
    assert "pause" in data
    for forbidden in ["pip install", "winget", "powershell", "curl", "http://",
                      "https://", "start ", "launch_windows.cmd", "uvicorn",
                      "setx ", "reg add", "runas", "shutdown", "del /", "copy /"]:
        assert forbidden not in data.lower()
    assert "NOT human" in data or "NOT human" in data.lower() or "NOT human" in data.upper()


def test_wrapper_tamper_refused_by_extracted_kit_and_build_verifier(tmp_path):
    root = _extract(tmp_path)
    path = root / "CHECK_PILOT_WINDOWS.cmd"
    path.write_bytes(path.read_bytes() + b"rem faked outcome\r\n")
    with pytest.raises(ValueError, match="integrity mismatch"):
        checker.verify(root)


def test_wrapper_packaging_reproducible_and_no_overwrite(tmp_path):
    a, b = tmp_path / "one.zip", tmp_path / "two.zip"
    builder.build_kit(a)
    builder.build_kit(b)
    assert hashlib.sha256(a.read_bytes()).digest() == hashlib.sha256(b.read_bytes()).digest()
    with pytest.raises(FileExistsError):
        builder.build_kit(a)


if os.name == "nt":
    def _cmd(root: Path, *args: str, env=None, stdin=None):
        return subprocess.run(
            [os.environ["COMSPEC"], "/d", "/c",
             str(root / "CHECK_PILOT_WINDOWS.cmd"), *args],
            cwd=root, env=env, input=stdin,
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=45, check=False,
        )

    def test_native_cmd_check_no_pause_and_no_mutation(tmp_path):
        root = _extract(tmp_path)
        before = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                  for name in builder.MEMBER_NAMES}
        p = _cmd(root, "--check")
        assert p.returncode == 0, (p.stdout, p.stderr)
        assert EXPECTED["success"] in p.stdout
        assert "NOT_GRANTED" in p.stdout and "NOT_RUN" in p.stdout
        assert "Press any key" not in p.stdout
        after = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                 for name in builder.MEMBER_NAMES}
        assert before == after

    def test_native_cmd_rejects_tampered_checker_and_forwards_2(tmp_path):
        root = _extract(tmp_path)
        with (root / "CHECK_PILOT_OFFLINE.py").open("ab") as f:
            f.write(b"\n#not trusted\n")
        p = _cmd(root, "--check")
        assert p.returncode == 2, (p.stdout, p.stderr)
        assert EXPECTED["failed"] in p.stdout and "OFFLINE_KIT_INTEGRITY_PASS" not in p.stdout

    def test_native_cmd_missing_checker_11(tmp_path):
        root = _extract(tmp_path)
        (root / "CHECK_PILOT_OFFLINE.py").unlink()
        p = _cmd(root, "--check")
        assert p.returncode == 11, (p.stdout, p.stderr)
        assert EXPECTED["checker"] in p.stdout
        assert EXPECTED["success"] not in p.stdout

    def test_native_cmd_rejects_all_unapproved_args(tmp_path):
        root = _extract(tmp_path)
        for args in [("--bad",), ("--check", "garbage"), ("path/to/secret",)]:
            p = _cmd(root, *args)
            assert p.returncode == 2, (args, p.stdout, p.stderr)
            assert EXPECTED["arg"] in p.stdout
            assert EXPECTED["success"] not in p.stdout

    def test_native_cmd_absent_python_10_without_install(tmp_path):
        root = _extract(tmp_path)
        empty_bin = tmp_path / "bin-no-python"
        empty_bin.mkdir()
        env = os.environ.copy()
        env["PATH"] = str(empty_bin)
        p = _cmd(root, "--check", env=env)
        assert p.returncode == 10, (p.stdout, p.stderr)
        assert EXPECTED["python"] in p.stdout
        assert EXPECTED["success"] not in p.stdout

    def test_native_cmd_doubleclick_pause_can_finish(tmp_path):
        root = _extract(tmp_path)
        # Double click has no args; send Enter to the bounded CMD pause.
        p = _cmd(root, stdin="\n")
        assert p.returncode == 0, (p.stdout, p.stderr)
        assert EXPECTED["success"] in p.stdout
        assert "NOT human" in p.stdout
