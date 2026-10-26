"""D15 Windows GUI desktop probe: true PASS or explicit NOT_RUN evidence."""
import argparse
import json
from pathlib import Path

from scripts.d15_pair_tk_smoke import execute


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args(argv)
    folder=args.out.absolute()
    if folder.exists() or folder.is_symlink():
        raise FileExistsError("D15 Windows report location must be new")
    folder.mkdir(parents=True,exist_ok=False)
    try:
        import tkinter as tk
        trial=tk.Tk()
        trial.withdraw()
        trial.destroy()
    except Exception as exc:
        report={"status":"GUI_NOT_AVAILABLE_NOT_RUN",
                "reason":type(exc).__name__,
                "human_acceptance":"NOT_RUN",
                "commercial_clearance":"NOT_GRANTED"}
        code=0
    else:
        try:
            proof=execute(folder/"actual_widgets")
            report={"status":proof["status"],
                    "screenshot":proof["screenshot"]["status"],
                    "human_acceptance":"NOT_RUN",
                    "commercial_clearance":"NOT_GRANTED"}
            code=0
        except Exception as exc:
            report={"status":"ACTUAL_TK_TWO_FILE_WIDGETS_FAILED",
                    "reason":type(exc).__name__,
                    "human_acceptance":"NOT_RUN"}
            code=2
    (folder/"windows_pair_gui_status.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report))
    return code


if __name__=="__main__":
    raise SystemExit(main())
