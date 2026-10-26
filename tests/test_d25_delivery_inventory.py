"""D25: SHA-checking expected delivery files must not approve unknown additions."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import types
import zipfile

import pytest

from rea import customer_self_check as checker
from rea.delivery import create_delivery

ROOT = Path(__file__).resolve().parents[1]


def extracted(tmp_path: Path) -> Path:
    archive = tmp_path / "only-public-synthetic.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", archive)
    directory = tmp_path / "fresh-extracted"
    directory.mkdir()
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(directory)
    return directory


def test_unmodified_delivery_and_repeat_preflight_pass(tmp_path):
    root = extracted(tmp_path)
    before = {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*") if p.is_file()
    }
    for _ in range(2):
        result = checker.inspect(root)
        assert result["status"] == "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE"
        assert result["integrity"] == "MATCHED_DELIVERY_MANIFEST_SHA256"
        assert result["overall_commercial_clearance"] == "NOT_GRANTED"
        assert result["runtime_hosting"] == "NOT_STARTED"
    assert {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()} == before


@pytest.mark.parametrize("name", [
    "extra.cmd",
    "start_other.bat",
    "unknown.exe",
    ".hidden",
    "desktop.ini",
    "NOTICE_FROM_SOMEONE_ELSE.txt",
    "app/extra.py",
    "app/.hidden.py",
    "app/unknown.exe",
    "app/static/extra.js",
    "app/static/.hidden",
])
def test_extra_file_rejects_false_sha_pass(tmp_path, name):
    root = extracted(tmp_path)
    (root / name).write_bytes(b"UNTRUSTED_NEEDED_NOBODY")
    report = checker.inspect(root)
    assert report["status"] == "FAIL_LOCAL_PREREQUISITES"
    assert report["integrity"] == "NOT_VERIFIED"
    assert report["database"] == "NOT_CHECKED"
    assert report["overall_commercial_clearance"] == "NOT_GRANTED"
    assert any("ValueError" in issue for issue in report["issues"])


@pytest.mark.parametrize("name", [
    "unknown-folder", "app/another-folder",
    "app/static/deep-folder", "app/__pycache__",
])
def test_additional_empty_directory_also_rejected(tmp_path, name):
    root = extracted(tmp_path)
    (root / name).mkdir()
    assert checker.inspect(root)["integrity"] == "NOT_VERIFIED"


def test_external_symlink_is_never_followed(tmp_path):
    root = extracted(tmp_path)
    external = tmp_path / "private.txt"
    external.write_text("PRIVATE NOT AN APP FILE", encoding="utf-8")
    try:
        (root / "app" / "unexpected.txt").symlink_to(external)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable in current runner")
    assert checker.inspect(root)["integrity"] == "NOT_VERIFIED"
    assert external.read_text(encoding="utf-8") == "PRIVATE NOT AN APP FILE"


def test_symlink_replacing_expected_directory_is_refused(tmp_path):
    root = extracted(tmp_path)
    other = tmp_path / "external-assets"
    other.mkdir()
    shutil.rmtree(root / "app" / "static")
    try:
        (root / "app" / "static").symlink_to(other, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable in current runner")
    assert checker.inspect(root)["integrity"] == "NOT_VERIFIED"


def test_unknown_file_prevents_actual_launch(monkeypatch, tmp_path, capsys):
    root = extracted(tmp_path)
    (root / "app" / "unlisted.exe").write_bytes(b"UNLISTED")
    monkeypatch.setattr(checker.subprocess, "run",
                        lambda *a, **kw: pytest.fail("Unsafe extracted app launched"))
    assert checker.launch_local(root) == 2
    assert "REA_LOCAL_LAUNCH_BLOCKED" in capsys.readouterr().err


def test_clean_launch_does_not_create_python_bytecode_caches(monkeypatch, tmp_path):
    root = extracted(tmp_path)
    recorded = []
    def fake_run(args, **kwargs):
        recorded.append((list(args), dict(kwargs)))
        return types.SimpleNamespace(returncode=0)
    monkeypatch.setattr(checker.subprocess, "run", fake_run)
    assert checker.launch_local(root) == 0
    assert len(recorded) == 1
    args, kw = recorded[0]
    assert args[0] == sys.executable
    assert args[args.index("--host") + 1] == "127.0.0.1"
    assert kw["env"]["PYTHONDONTWRITEBYTECODE"] == "1"
    assert kw["cwd"] == root / "app"
    assert kw.get("shell") is not True
    assert checker.inspect(root)["status"] == "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE"


def test_shipped_stdout_is_not_a_false_success_after_extra_file(tmp_path):
    root = extracted(tmp_path)
    (root / "app" / "extra_exec.py").write_text("raise RuntimeError('bad')")
    result = subprocess.run([
        sys.executable, str(root / "self_check.py"), "--root", str(root)
    ], capture_output=True, text=True, timeout=30, check=False)
    assert result.returncode == 2, result.stderr
    body = json.loads(result.stdout)
    assert body["status"] == "FAIL_LOCAL_PREREQUISITES"
    assert body["integrity"] == "NOT_VERIFIED"
    assert body["overall_commercial_clearance"] == "NOT_GRANTED"
    assert "PRIVATE" not in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="Real Windows cmd.exe needed")
def test_native_windows_cmd_will_not_launch_with_extra_file(tmp_path):
    root = extracted(tmp_path)
    (root / "evil_extra.cmd").write_bytes(b"@echo off\r\nexit /b 0\r\n")
    cmd = os.environ["COMSPEC"]
    launch = root / "launch_windows.cmd"
    proc = subprocess.run(f'"{cmd}" /d /s /c ""{launch}""',
                          executable=cmd, cwd=root, env=os.environ.copy(),
                          capture_output=True, text=True, errors="replace",
                          timeout=35, check=False)
    assert proc.returncode == 2, (proc.stdout, proc.stderr)
    assert "REA_LOCAL_LAUNCH_BLOCKED" in proc.stderr
