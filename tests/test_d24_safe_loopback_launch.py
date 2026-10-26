"""D24: generated Windows launcher cannot interpolate an env port as CMD code."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import types
import zipfile

import pytest

from rea import customer_self_check as check
from rea.delivery import LAUNCH, create_delivery

ROOT = Path(__file__).resolve().parents[1]


def _unpacked(tmp_path):
    archive = tmp_path / "synthetic.zip"
    create_delivery(ROOT / "samples" / "qa_cafe.csv", archive)
    unpacked = tmp_path / "extracted"
    unpacked.mkdir()
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(unpacked)
    return unpacked


@pytest.mark.parametrize("literal,expected", [
    ("1", 1), ("80", 80), ("8000", 8000),
    ("8765", 8765), ("65535", 65535),
])
def test_port_ascii_decimal_bounds(monkeypatch, literal, expected):
    monkeypatch.setenv("REA_WEB_PORT", literal)
    assert check.port_from_environment() == expected


@pytest.mark.parametrize("malicious", [
    "0", "-1", "+80", "65536", "999999", "",
    "08000", " 8000", "8000 ", "12.3", "１２", "٣١٤",
    "8000&echo INJECTED", "8080|echo INJECTED",
    "8080>outside.txt", "8000&&whoami",
    "8000^&echo", "127.0.0.1:8000",
])
def test_port_refuses_non_decimal_or_cmd_metacharacters(monkeypatch, malicious):
    monkeypatch.setenv("REA_WEB_PORT", malicious)
    with pytest.raises(ValueError, match="Unsafe REA_WEB_PORT"):
        check.port_from_environment()


def test_default_port_and_shipped_cmd_never_expand_env(monkeypatch, tmp_path):
    monkeypatch.delenv("REA_WEB_PORT", raising=False)
    assert check.port_from_environment() == 8000
    extracted = _unpacked(tmp_path)
    batch_bytes = (extracted / "launch_windows.cmd").read_bytes()
    assert batch_bytes == LAUNCH.encode("ascii")
    batch = batch_bytes.decode("ascii")
    assert 'python "%~dp0self_check.py" --launch' in batch
    assert "%REA_WEB_PORT%" not in batch
    assert "set REA_WEB_PORT=" not in batch
    assert "--host 0.0.0.0" not in batch
    assert "pip " not in batch.lower() and "curl " not in batch.lower()


def test_verified_app_spawns_fixed_host_and_arg_vector_without_shell(monkeypatch, tmp_path):
    extracted = _unpacked(tmp_path)
    monkeypatch.setenv("REA_WEB_PORT", "8765")
    calls = []

    def fake_run(argv, **kwargs):
        calls.append((argv, kwargs))
        return types.SimpleNamespace(returncode=0)

    monkeypatch.setattr(check.subprocess, "run", fake_run)
    assert check.launch_local(extracted) == 0
    assert len(calls) == 1
    argv, kw = calls[0]
    assert argv == [
        sys.executable, "-m", "uvicorn", "app:app",
        "--host", "127.0.0.1", "--port", "8765",
    ]
    assert kw.get("cwd") == extracted / "app"
    assert kw.get("shell") is not True
    assert kw.get("check") is False


def test_tampered_delivery_cannot_start_runtime(monkeypatch, tmp_path, capsys):
    extracted = _unpacked(tmp_path)
    with (extracted / "app/static/app.js").open("ab") as out:
        out.write(b"\nmodified-not-approved")
    def should_not_run(*args, **kwargs):
        raise AssertionError("untrusted app executed")
    monkeypatch.setattr(check.subprocess, "run", should_not_run)
    assert check.launch_local(extracted) == 2
    assert "REA_LOCAL_LAUNCH_BLOCKED" in capsys.readouterr().err


def test_bad_port_cannot_start_runtime_even_when_zip_is_valid(monkeypatch, tmp_path, capsys):
    extracted = _unpacked(tmp_path)
    monkeypatch.setenv("REA_WEB_PORT", "8000&whoami")
    def should_not_run(*args, **kwargs):
        raise AssertionError("untrusted port became execution")
    monkeypatch.setattr(check.subprocess, "run", should_not_run)
    assert check.launch_local(extracted) == 2
    assert "unsafe REA_WEB_PORT" in capsys.readouterr().err


def test_shipped_selfcheck_has_launch_mode_and_never_checks_out_commmercial(tmp_path):
    extracted = _unpacked(tmp_path)
    selfcheck = (extracted / "self_check.py").read_text(encoding="utf-8")
    assert "port_from_environment" in selfcheck
    assert "subprocess.run(" in selfcheck
    assert 'command, cwd=root / "app", check=False, env=environment' in selfcheck
    assert 'environment["PYTHONDONTWRITEBYTECODE"] = "1"' in selfcheck
    assert '127.0.0.1' in selfcheck
    assert "shell=True" not in selfcheck
    proc = subprocess.run([sys.executable, str(extracted / "self_check.py"),
                           "--root", str(extracted)],
                          capture_output=True, text=True, timeout=30, check=False)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    assert result["overall_commercial_clearance"] == "NOT_GRANTED"
    assert result["runtime_hosting"] == "NOT_STARTED"


@pytest.mark.skipif(os.name != "nt", reason="Native Windows cmd.exe required")
def test_native_windows_cmd_refuses_unsafe_port_without_running_anything(tmp_path):
    extracted = _unpacked(tmp_path)
    script = extracted / "launch_windows.cmd"
    marker = tmp_path / "should-never-be-created.txt"
    env = os.environ.copy()
    env["REA_WEB_PORT"] = f"8000&echo INJECTED>{marker}"
    # Real cmd.exe using documented /s /c quoting for absolute script paths.
    cmd = os.environ["COMSPEC"]
    command = f'"{cmd}" /d /s /c ""{script}""'
    result = subprocess.run(command, executable=cmd,
                            env=env, cwd=extracted, capture_output=True,
                            text=True, errors="replace", timeout=35, check=False)
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert not marker.exists()
    assert "REA_LOCAL_LAUNCH_BLOCKED" in result.stderr
