"""D27: shipped Windows app uses existing python >=3.11, or Windows py -3 fallback."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

from rea.delivery import CHECK_LAUNCH, LAUNCH, create_delivery

ROOT = Path(__file__).resolve().parents[1]


def _unpacked(tmp_path):
    archive = tmp_path / "synthetic.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", archive)
    root = tmp_path / "fresh app folder & spaces"
    root.mkdir()
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(root)
    return root


def test_shipped_cmds_offer_python_and_py_fallback_without_install(tmp_path):
    root = _unpacked(tmp_path)
    checker = (root / "check_windows.cmd").read_bytes()
    launcher = (root / "launch_windows.cmd").read_bytes()
    assert checker == CHECK_LAUNCH.encode("ascii")
    assert launcher == LAUNCH.encode("ascii")
    assert b"\r\n" in checker and b"\r\n" in launcher
    # Both genuine .exe and optional .cmd wrappers must return to the owner
    # launcher to preserve its errorlevel and fallback control flow.
    assert b'call python -c "' in checker and b'call python -c "' in launcher
    assert b'call py -3 -c "' in checker and b'call py -3 -c "' in launcher
    assert b'call python "%~dp0self_check.py"' in checker
    assert b'call py -3 "%~dp0self_check.py"' in checker
    assert b'call python "%~dp0self_check.py" --launch' in launcher
    assert b'call py -3 "%~dp0self_check.py" --launch' in launcher
    assert b'python -c "import sys;sys.exit(0 if sys.version_info[:2]>=(3,11) else 1)" >nul 2>nul' in checker
    assert b'py -3 -c "import sys;sys.exit(0 if sys.version_info[:2]>=(3,11) else 1)" >nul 2>nul' in checker
    assert b'py -3 "%~dp0self_check.py"' in checker
    assert b'py -3 "%~dp0self_check.py" --launch' in launcher
    assert b'python "%~dp0self_check.py" --launch' in launcher
    assert b"MISSING_PYTHON" in checker and b"MISSING_PYTHON" in launcher
    assert b'set "_rea_check_code=10"' in checker
    assert b"exit /b %_rea_check_code%" in checker
    assert b"exit /b 10" in launcher
    assert b"%REA_WEB_PORT%" not in checker + launcher
    for cmd in (checker, launcher):
        low = cmd.lower()
        for forbidden in (b"pip install", b"winget", b"powershell",
                          b"curl ", b"http://", b"https://",
                          b"setx ", b"reg add", b"start "):
            assert forbidden not in low
    guide = (root / "README_WINDOWS.md").read_text(encoding="utf-8")
    assert 'Windows launcher "py -3"' in guide
    assert "same" in guide.lower()
    assert "NOT commercially approved" in guide


@pytest.mark.skipif(os.name != "nt", reason="Actual Windows cmd.exe required")
def test_native_python_launcher_only_fallback_and_error_codes(tmp_path):
    root = _unpacked(tmp_path)
    cmd_path = Path(os.environ["COMSPEC"])
    system_path = str(Path(os.environ["SystemRoot"]) / "System32")
    shim_dir = tmp_path / "shim bin"
    shim_dir.mkdir()
    shim = shim_dir / "py.cmd"
    # Deliberately do not add python.exe to PATH. Fake py.cmd emulates the
    # standardized Windows launcher "-3" switch using the known CI interpreter.
    shim.write_text(
        '@echo off\r\n'
        'if not "%~1"=="-3" exit /b 72\r\n'
        f'"{sys.executable}" %2 %3 %4\r\n',
        encoding="ascii", newline="",
    )
    environment = dict(os.environ)
    environment["PATH"] = str(shim_dir) + os.pathsep + system_path
    environment["PYTHONIOENCODING"] = "utf-8"

    def run(script, *args, stdin=None, env=None):
        target = root / script
        tail = "".join(" " + subprocess.list2cmdline([arg]) for arg in args)
        command = f'"{cmd_path}" /d /s /c ""{target}"{tail}"'
        return subprocess.run(command, executable=str(cmd_path),
                              cwd=root, env=environment if env is None else env,
                              input=stdin, capture_output=True,
                              text=True, errors="replace",
                              timeout=40, check=False)

    # No 'python' command; only 'py -3' is available via our controlled shim.
    checked = run("check_windows.cmd", "--check")
    assert checked.returncode == 0, (checked.stdout, checked.stderr)
    assert "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE" in checked.stdout
    assert "Press any key" not in checked.stdout

    manual = run("check_windows.cmd", stdin="\n")
    assert manual.returncode == 0, (manual.stdout, manual.stderr)
    assert "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE" in manual.stdout
    assert "Press any key" in manual.stdout

    # Same fallback for the app launcher: invalid port must refuse BEFORE
    # any server process, and CMD must not expand hostile port metacharacters.
    environment["REA_WEB_PORT"] = "8000&echo PWNED"
    blocked = run("launch_windows.cmd")
    assert blocked.returncode == 2, (blocked.stdout, blocked.stderr)
    assert "REA_LOCAL_LAUNCH_BLOCKED" in blocked.stderr
    assert "PWNED" not in blocked.stdout

    # Simulate an out-of-date python command. It must refuse during the
    # version probe and choose the working Windows py launcher instead.
    (shim_dir / "python.cmd").write_text("@echo off\r\nexit /b 7\r\n",
                                        encoding="ascii", newline="")
    fallback = run("check_windows.cmd", "--check")
    assert fallback.returncode == 0, (fallback.stdout, fallback.stderr)

    # Neither command usable: explicit code 10 with no install/network.
    shim.unlink()
    missing = run("check_windows.cmd", "--check")
    assert missing.returncode == 10, (missing.stdout, missing.stderr)
    assert "MISSING_PYTHON" in missing.stdout
    assert "LOCAL_PREREQUISITES_NOT_VERIFIED" in missing.stdout
    no_launch = run("launch_windows.cmd")
    assert no_launch.returncode == 10, (no_launch.stdout, no_launch.stderr)
    assert "MISSING_PYTHON" in no_launch.stdout
    no_pause = run("check_windows.cmd", stdin="\n")
    assert no_pause.returncode == 10, (no_pause.stdout, no_pause.stderr)
    assert "Press any key" in no_pause.stdout


@pytest.mark.skipif(os.name != "nt", reason="Actual Windows cmd.exe required")
def test_native_regular_python_remains_preferred(tmp_path):
    root = _unpacked(tmp_path)
    comspec = os.environ["COMSPEC"]
    script = root / "check_windows.cmd"
    command = f'"{comspec}" /d /s /c ""{script}" --check"'
    result = subprocess.run(command, executable=comspec, cwd=root,
                            capture_output=True, text=True, errors="replace",
                            timeout=40, check=False)
    assert result.returncode == 0, (result.stdout, result.stderr)
    assert "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE" in result.stdout
