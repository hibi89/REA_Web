"""D14 Windows CI desktop availability probe, no human acceptance assertion.

Runs actual Tk synthetic widget smoke only if a Tk root can be opened.
Always writes status evidence to a NEW local report path. Missing GUI is NOT_RUN.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

from scripts.d14_tk_visual_smoke import execute


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Optional real-Tk synthetic Windows CI probe")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.out.absolute()
    if out.exists() or out.is_symlink():
        print("D14_WINDOWS_REFUSED_EXISTING_DESTINATION", file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=False)
    try:
        import tkinter as tk
        trial = tk.Tk()
        trial.withdraw()
        trial.destroy()
    except Exception as exc:
        status = {
            "platform_test": "WINDOWS_CI_GUI_DESKTOP",
            "status": "GUI_NOT_AVAILABLE_NOT_RUN",
            "reason_type": type(exc).__name__,
            "human_acceptance": "NOT_RUN",
            "commercial_release": "BLOCKED",
        }
        (out / "windows_gui_status.json").write_text(
            json.dumps(status, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(status))
        return 0

    try:
        record = execute(out / "visual")
        result = {
            "platform_test": "WINDOWS_CI_GUI_DESKTOP",
            "status": "ACTUAL_SYNTHETIC_TK_WIDGETS_PASS",
            "visual_report": "visual/synthetic_tk_ui_acceptance.json",
            "screenshot_status": record["screenshot"]["status"],
            "human_acceptance": "NOT_RUN",
            "commercial_release": "BLOCKED",
        }
    except Exception as exc:
        result = {
            "platform_test": "WINDOWS_CI_GUI_DESKTOP",
            "status": "ACTUAL_TK_WIDGETS_FAILED",
            "reason_type": type(exc).__name__,
            "human_acceptance": "NOT_RUN",
            "commercial_release": "BLOCKED",
        }
    (out / "windows_gui_status.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0 if result["status"] == "ACTUAL_SYNTHETIC_TK_WIDGETS_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
