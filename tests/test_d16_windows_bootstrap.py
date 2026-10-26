"""D16 no-install creator bootstrap regression with mockable offline checks."""
from __future__ import annotations
from pathlib import Path
import subprocess
import sys

import pytest

from rea import creator_preflight as pre

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "START_REA_CREATOR.cmd"


@pytest.mark.parametrize("version", [(3, 8), (3, 9), (3, 10)])
def test_old_python_fail_before_import_or_tk(version):
    consulted = []
    def forbidden(name):
        consulted.append(name)
        raise AssertionError("modules should not be checked")
    d = pre.diagnose(version=version, module_exists=forbidden, tk_probe=lambda: True)
    assert d["status"] == "UNSUPPORTED_PYTHON" and d["exit_code"] == 10
    assert consulted == []


def test_missing_dependency_specific_no_display_probe():
    looked = []
    def available(module):
        looked.append(module)
        return module != "uvicorn"
    d = pre.diagnose(version=(3, 11), module_exists=available,
                     tk_probe=lambda: (_ for _ in ()).throw(
                         AssertionError("Tk not needed after missing dependency")))
    assert d["status"] == "MISSING_MODULES"
    assert d["missing"] == ["uvicorn"]
    assert d["exit_code"] == 11
    assert set(looked) == set(pre.RUNTIME)


@pytest.mark.parametrize("module", pre.RUNTIME)
def test_each_runtime_module_missing_is_fail_closed(module):
    d = pre.diagnose(version=(3, 12),
                     module_exists=lambda item: item != module,
                     tk_probe=lambda: True)
    assert d["missing"] == [module]
    assert d["exit_code"] == 11


def test_tk_import_or_display_fails_closed():
    d = pre.diagnose(version=(3, 11), module_exists=lambda _: True,
                     tk_probe=lambda: False)
    assert d["status"] == "TK_UNAVAILABLE" and d["exit_code"] == 12


@pytest.mark.parametrize("version", [(3, 11), (3, 12), (3, 13)])
def test_valid_installed_desktop_is_ready_without_network(version):
    d = pre.diagnose(version=version, module_exists=lambda _: True,
                     tk_probe=lambda: True)
    assert d["status"] == "READY" and d["exit_code"] == 0
    assert d["python_version"] == ".".join(map(str, version))


def test_empty_or_invalid_version_does_not_silently_pass():
    with pytest.raises(ValueError):
        pre.diagnose(version=(3, ), module_exists=lambda _: True,
                     tk_probe=lambda: True)
    with pytest.raises(ValueError):
        pre.diagnose(version=("3", 11), module_exists=lambda _: True,
                     tk_probe=lambda: True)


def test_cli_help_and_invalid_args_without_display():
    help_result = subprocess.run([sys.executable, "-m", "rea.creator_preflight",
                                  "--help"], cwd=ROOT, capture_output=True, text=True)
    assert help_result.returncode == 0
    assert "--check" in help_result.stdout and "--launch" in help_result.stdout
    invalid = subprocess.run([sys.executable, "-m", "rea.creator_preflight",
                              "--unknown"], cwd=ROOT, capture_output=True, text=True)
    assert invalid.returncode == 2


def test_check_mode_never_launches_gui(monkeypatch, capsys):
    monkeypatch.setattr(pre, "diagnose",
                        lambda: {"status":"READY", "exit_code":0,
                                 "guidance":"synthetic check"})
    import rea.creator_gui as gui
    monkeypatch.setattr(gui, "launch", lambda: (_ for _ in ()).throw(
        AssertionError("CHECK must not launch Tk GUI")))
    assert pre.main(["--check"]) == 0
    assert "READY" in capsys.readouterr().out


def test_launch_propagates_gui_exit_code(monkeypatch):
    monkeypatch.setattr(pre, "diagnose",
                        lambda: {"status":"READY", "exit_code":0,
                                 "guidance":"synthetic"})
    import rea.creator_gui as gui
    monkeypatch.setattr(gui, "launch", lambda: 12)
    assert pre.main(["--launch"]) == 12


def test_missing_dependency_cli_does_not_launch(monkeypatch):
    monkeypatch.setattr(pre, "diagnose",
                        lambda: {"status":"MISSING_MODULES", "exit_code":11,
                                 "missing":["fastapi"],"guidance":"missing"})
    assert pre.main(["--launch"]) == 11


def test_cmd_scope_no_install_download_or_elevation():
    data = LAUNCHER.read_text(encoding="utf-8").lower()
    assert "cd /d" in data and "%~dp0" in data
    assert ":check" in data and ":launch" in data
    assert "-m rea.creator_preflight --check" in data
    assert "-m rea.creator_preflight --launch" in data
    for forbidden in ("-m pip install", "curl.exe", "bitsadmin", "setx ",
                      "reg add", "winget install", "start-process",
                      "invoke-webrequest", "msiexec", "net user"):
        assert forbidden not in data
    assert not (ROOT / "rea" / "creator_gui.py").read_text(
        encoding="utf-8").startswith("import tkinter")
