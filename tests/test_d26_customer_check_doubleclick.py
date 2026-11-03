"""D26: generated customer Windows checker double-click is readable, CI --check is noninteractive."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

from rea.delivery import CHECK_LAUNCH, create_delivery

ROOT = Path(__file__).resolve().parents[1]


def unpack(tmp_path: Path) -> Path:
    archive = tmp_path / "synthetic.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", archive)
    extracted = tmp_path / "synthetic & safe folder with spaces"
    extracted.mkdir()
    with zipfile.ZipFile(archive) as z:
        z.extractall(extracted)
    return extracted


def test_packaged_check_has_exact_crlf_and_no_network_or_app_start(tmp_path):
    root = unpack(tmp_path)
    launcher = (root / "check_windows.cmd").read_bytes()
    assert launcher == CHECK_LAUNCH.encode("ascii")
    assert launcher.endswith(b"\r\n")
    assert b'python "%~dp0self_check.py"' in launcher
    assert b'if /I "%~1"=="--check" goto check' in launcher
    assert b'if "%~1"=="" (' in launcher
    assert b"  pause\r\n" in launcher
    assert b"exit /b %_rea_check_code%" in launcher
    assert b"INVALID_ARGUMENT" in launcher
    for text in [b"pip install", b"winget", b"powershell", b"curl ",
                 b"http://", b"https://", b"uvicorn", b"launch_windows.cmd",
                 b"%REA_WEB_PORT%", b"start ", b"setx ", b"reg add"]:
        assert text not in launcher.lower()
    assert "double-click check_windows.cmd" in (root / "README_WINDOWS.md").read_text()
    assert "check_windows.cmd --check" in (root / "README_WINDOWS.md").read_text()


def test_python_selfcheck_still_read_only_and_not_commercial(tmp_path):
    root = unpack(tmp_path)
    process = subprocess.run(
        [sys.executable, str(root / "self_check.py"), "--root", str(root)],
        cwd=root, capture_output=True, text=True, check=False, timeout=30,
    )
    assert process.returncode == 0, process.stderr
    report = json.loads(process.stdout)
    assert report["status"] == "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE"
    assert report["runtime_hosting"] == "NOT_STARTED"
    assert report["overall_commercial_clearance"] == "NOT_GRANTED"


if os.name == "nt":
    def native_cmd(root, *args, stdin=None, env=None):
        cmd = os.environ["COMSPEC"]
        script = root / "check_windows.cmd"
        tail = "".join(" " + subprocess.list2cmdline([arg]) for arg in args)
        run = f'"{cmd}" /d /s /c ""{script}"{tail}"'
        return subprocess.run(
            run, executable=cmd, cwd=root, env=env,
            input=stdin, capture_output=True, text=True,
            errors="replace", timeout=40, check=False,
        )

    def test_native_no_pause_with_check_argument(tmp_path):
        root = unpack(tmp_path)
        proc = native_cmd(root, "--check")
        assert proc.returncode == 0, (proc.stdout, proc.stderr)
        assert "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE" in proc.stdout
        assert "Press any key" not in proc.stdout
        assert "NOT_GRANTED" in proc.stdout

    def test_native_doubleclick_pause_readable_with_stdin(tmp_path):
        root = unpack(tmp_path)
        proc = native_cmd(root, stdin="\n")
        assert proc.returncode == 0, (proc.stdout, proc.stderr)
        assert "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE" in proc.stdout
        assert "NOT human or commercial acceptance" in proc.stdout
        assert "Press any key" in proc.stdout

    def test_native_bad_args_refused_without_launch(tmp_path):
        root = unpack(tmp_path)
        for args in [("--unexpected",), ("--check", "unexpected")]:
            proc = native_cmd(root, *args)
            assert proc.returncode == 2, (proc.stdout, proc.stderr)
            assert "INVALID_ARGUMENT" in proc.stdout
            assert "PASS_LOCAL_PREREQUISITES" not in proc.stdout
            assert "Press any key" not in proc.stdout

    def test_native_tampered_app_exit_code_passed_and_pause_on_doubleclick(tmp_path):
        root = unpack(tmp_path)
        (root / "app" / "static" / "app.js").write_bytes(b"UNAPPROVED MODIFICATION")
        automated = native_cmd(root, "--check")
        human = native_cmd(root, stdin="\n")
        for proc in (automated, human):
            assert proc.returncode == 2, (proc.stdout, proc.stderr)
            assert "FAIL_LOCAL_PREREQUISITES" in proc.stdout
            assert "LOCAL_PREREQUISITES_NOT_VERIFIED" in proc.stdout
        assert "Press any key" not in automated.stdout
        assert "Press any key" in human.stdout
