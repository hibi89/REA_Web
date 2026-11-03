"""Real Windows cmd.exe acceptance: success, invalid argument, no-Python refusal.

This tests the creator launcher only. It never generates customer data,
installs a package, changes PATH globally or launches a persistent GUI.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CMD = ROOT / "START_REA_CREATOR.cmd"


def native_run(script: Path, argument: str, *, env=None, cwd=None):
    return subprocess.run(["cmd.exe", "/d", "/c", str(script), argument],
                          cwd=cwd or ROOT, env=env, capture_output=True,
                          text=True, errors="replace", timeout=40)


def main():
    if os.name != "nt":
        raise SystemExit("NOT_RUN: Windows cmd.exe required")
    assert CMD.is_file()
    # Check-only uses the real interpreter, real Tk display and installed modules.
    success = native_run(CMD, "--check", cwd=ROOT.parent)
    if success.returncode:
        raise RuntimeError("Real CMD --check failed: " + success.stdout[-1200:]
                           + success.stderr[-600:])
    assert "[REA] READY:" in success.stdout, success.stdout
    invalid = native_run(CMD, "--unrecognized", cwd=ROOT.parent)
    assert invalid.returncode == 2 and "INVALID_ARGUMENT" in invalid.stdout

    # A standalone CMD copy with no python on PATH cannot start, even if the
    # current CI host normally has Python. No real system-wide PATH is altered.
    with tempfile.TemporaryDirectory(prefix="rea-d16-cmd-negative-") as temp:
        isolated = Path(temp) / CMD.name
        shutil.copyfile(CMD, isolated)
        isolated_env = dict(os.environ)
        isolated_env["PATH"] = ""
        denied = native_run(isolated, "--check", env=isolated_env, cwd=temp)
        assert denied.returncode == 10, (denied.returncode, denied.stdout,
                                          denied.stderr)
        assert "NO_PYTHON" in denied.stdout

    print("PASS D16 native cmd.exe: READY --check + INVALID_ARGUMENT "
          "+ NO_PYTHON refusal; no GUI launched or packages installed")


if __name__ == "__main__":
    main()
