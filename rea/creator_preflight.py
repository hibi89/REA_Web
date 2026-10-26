"""Local Windows creator diagnostics; no package installation or network calls.

Return codes: 0 READY; 2 invalid CLI; 10 unsupported Python; 11 missing
installed Python packages; 12 Tk/display unavailable; 13 GUI launch failure.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys

RUNTIME = ("fastapi", "uvicorn", "pydantic")


def real_tk_probe() -> bool:
    """Open and immediately close a hidden root: import alone is not a GUI test."""
    try:
        import tkinter as tk
        root = tk.Tk()
        try:
            root.withdraw()
            root.update_idletasks()
        finally:
            root.destroy()
        return True
    except Exception:
        return False


def diagnose(*, version=None, module_exists=None, tk_probe=None) -> dict:
    """Bounded offline, read-only checks with injectable synthetic negative cases."""
    chosen = tuple(sys.version_info[:2] if version is None else version)
    if len(chosen) != 2 or not all(type(i) is int for i in chosen):
        raise ValueError("Expected Python version pair")
    if chosen < (3, 11):
        return {
            "status": "UNSUPPORTED_PYTHON", "exit_code": 10,
            "python_version": f"{chosen[0]}.{chosen[1]}",
            "guidance": "Python 3.11+ 필요. 기존 로컬 Python 환경을 확인하세요.",
        }
    exists = module_exists or (lambda name: importlib.util.find_spec(name) is not None)
    missing = [name for name in RUNTIME if not exists(name)]
    if missing:
        return {
            "status": "MISSING_MODULES", "exit_code": 11,
            "missing": missing,
            "guidance": "패키지 미설치. 자동 설치하지 않습니다. 승인된 로컬 환경에서 "
                        "fastapi, uvicorn, pydantic 설치 상태를 확인하세요.",
        }
    probe = real_tk_probe if tk_probe is None else tk_probe
    if not probe():
        return {
            "status": "TK_UNAVAILABLE", "exit_code": 12,
            "guidance": "Tkinter GUI 또는 Windows 화면 세션을 사용할 수 없습니다. "
                        "Python Tk 설치를 확인하거나 기존 rea.guided CLI를 사용하세요.",
        }
    return {
        "status": "READY", "exit_code": 0,
        "python_version": f"{chosen[0]}.{chosen[1]}",
        "guidance": "GUI 시작 조건 통과. 설치/사용자 인수 검수나 상용 승인 의미 아님.",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="REA creator offline prerequisites")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Check only; never launch")
    mode.add_argument("--launch", action="store_true", help="Check then start local Tk")
    args = p.parse_args(argv)
    try:
        result = diagnose()
    except Exception as exc:
        result = {"status": "LOCAL_DIAGNOSTIC_ERROR", "exit_code": 13,
                  "guidance": "진단 중 오류 발생: " + type(exc).__name__}
    print("[REA] " + result["status"] + ": " + result["guidance"], flush=True)
    if "missing" in result:
        print("[REA] missing: " + ", ".join(result["missing"]), flush=True)
    if result["exit_code"] != 0:
        return result["exit_code"]
    if args.check:
        return 0
    try:
        from rea.creator_gui import launch
        return int(launch())
    except Exception as exc:
        print("[REA] GUI_LAUNCH_FAILED: " + type(exc).__name__, file=sys.stderr)
        return 13


if __name__ == "__main__":
    raise SystemExit(main())
