"""D15 REAL Tk two-input widget test, synthetic CSV+JSON only. No user data."""
from __future__ import annotations
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FIRST = ROOT / "samples/qa_guided.csv"
SECOND = ROOT / "samples/qa_pair_extra.json"
MAP = {"id": "sku", "title": "display_name", "category": "group_name"}


def execute(folder: Path, *, preserve_synthetic_zip: bool = False) -> dict:
    folder = Path(folder).absolute()
    if folder.exists() or folder.is_symlink():
        raise FileExistsError("Choose a NEW synthetic GUI report folder")
    import tkinter as tk
    from rea.creator_gui import build_window
    from rea.provenance import inspect_delivery
    before = (hashlib.sha256(FIRST.read_bytes()).hexdigest(),
              hashlib.sha256(SECOND.read_bytes()).hexdigest())
    with TemporaryDirectory(prefix="rea-d15-synthetic-") as scratch:
        archive = Path(scratch) / "approved_pair.zip"
        root = tk.Tk()
        root.geometry("900x850+20+20")
        try:
            single = build_window(root)
            root.update()
            single.pair_button.invoke()  # REAL Tk button opens real separate Toplevel
            root.update()
            assert len(single.pair_windows) == 1
            ui = single.pair_windows[0]
            assert ui.window.winfo_exists() == 1
            with ExitStack() as stack:
                source_dialog = stack.enter_context(
                    patch("tkinter.filedialog.askopenfilename",
                          side_effect=[str(FIRST), str(SECOND)]))
                save_dialog = stack.enter_context(
                    patch("tkinter.filedialog.asksaveasfilename",
                          return_value=str(archive)))
                errors = stack.enter_context(patch("tkinter.messagebox.showerror"))
                infos = stack.enter_context(patch("tkinter.messagebox.showinfo"))
                ui.source_buttons[0].invoke()
                ui.source_buttons[1].invoke()
                ui.choose_output()
                assert source_dialog.call_count == 2 and save_dialog.call_count == 1
                assert ui.source_vars[0].get() == str(FIRST)
                assert ui.source_vars[1].get() == str(SECOND)
                ui.inspect_button.invoke()
                root.update()
                assert ui.controller.inspected is not None
                assert "같은 스키마: YES" in ui.preview_label.cget("text")
                assert all(not v.get() for v in ui.mapped_vars.values())
                # Unapproved export must be denied by REAL GUI button.
                ui.export_button.invoke()
                assert errors.call_count == 1 and not archive.exists()

                for target, column in MAP.items():
                    combo = ui.combos[target]
                    choices = list(combo.cget("values"))
                    combo.current(choices.index(column))
                # Missing second file approval remains DENIED.
                ui.rights_checkboxes[0].invoke()
                ui.approval_entries[0].insert(0, "APPROVE")
                ui.append_entry.insert(0, "APPEND")
                ui.export_button.invoke()
                assert errors.call_count == 2 and not archive.exists()
                ui.rights_checkboxes[1].invoke()
                ui.approval_entries[1].insert(0, "APPROVE")
                root.update()
                assert all(v.get() for v in ui.rights_vars)
                assert [v.get() for v in ui.approval_vars] == ["APPROVE", "APPROVE"]
                assert ui.append_var.get() == "APPEND"
                assert {k: v.get() for k, v in ui.mapped_vars.items()} == MAP

                ui.export_button.invoke()
                root.update()
                assert infos.call_count == 1
                assert archive.is_file()
                audit = inspect_delivery(archive)
                assert audit["two_file_append_receipt_present"] is True
                assert audit["overall_commercial_clearance"] == "NOT_GRANTED"
                with zipfile.ZipFile(archive) as z:
                    proof = json.loads(z.read("app/append_report.json"))
                    manifest = json.loads(z.read("app/manifest.json"))
                    assert manifest["rows"] == 5
                    assert proof["mode"] == "SAME_SCHEMA_ROW_APPEND_NO_JOIN"
                    assert proof["combined_confirmation"] == "APPEND"
                    assert all(x["confirmed"] == "APPROVE" for x in proof["sources"])
                    assert "app/data.sqlite" in z.namelist()
                sha = hashlib.sha256(archive.read_bytes()).hexdigest()
                assert ui.controller.inspected is None
                assert not any(v.get() for v in ui.rights_vars)
                assert [v.get() for v in ui.approval_vars] == ["", ""]
                assert ui.append_var.get() == ""
                ui.export_button.invoke()  # cannot reuse prior permission
                assert errors.call_count == 3
                assert hashlib.sha256(archive.read_bytes()).hexdigest() == sha
                after = (hashlib.sha256(FIRST.read_bytes()).hexdigest(),
                         hashlib.sha256(SECOND.read_bytes()).hexdigest())
                assert before == after

                folder.mkdir(parents=True, exist_ok=False)
                if preserve_synthetic_zip:
                    # CI-only D18 handoff: never save a customer ZIP or overwrite.
                    with (folder / "synthetic_pair_d18.zip").open("xb") as target:
                        target.write(archive.read_bytes())
                ui.window.update()
                screen = {"status": "NOT_CAPTURED"}
                try:
                    from PIL import ImageGrab
                    x, y = ui.window.winfo_rootx(), ui.window.winfo_rooty()
                    w, h = ui.window.winfo_width(), ui.window.winfo_height()
                    p = folder / "two_file_tk_synthetic.png"
                    ImageGrab.grab(bbox=(x, y, x+w, y+h)).save(p)
                    screen = {"status":"CAPTURED", "file":p.name,
                              "sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
                except (ImportError, OSError, RuntimeError, ValueError) as exc:
                    screen = {"status":"NOT_CAPTURED", "reason":type(exc).__name__}
                result = {
                    "schema": "rea.d15.gui.synthetic.v1",
                    "status": "ACTUAL_TK_TWO_FILE_WIDGETS_PASS",
                    "source": "TWO_COMMITTED_NONCUSTOMER_FIXTURES",
                    "widget_actions": 12,
                    "distinct_approvals": "APPROVE_FIRST_APPROVE_SECOND_APPEND",
                    "both_origins_sha_unchanged": True,
                    "validated_zip_sha256": sha,
                    "cross_table_join": False,
                    "screenshot": screen,
                    "human_non_developer_acceptance": "NOT_RUN",
                    "commercial_clearance": "NOT_GRANTED",
                }
                (folder / "two_file_tk_acceptance.json").write_text(
                    json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)+"\n",
                    encoding="utf-8")
                return result
        finally:
            root.destroy()


def main(argv=None):
    import argparse
    p=argparse.ArgumentParser(description="real Tk two-file synthetic proof")
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--retain-synthetic-zip-for-d18", action="store_true",
                   help="CI-only synthetic fixture handoff, never customer ZIP")
    args=p.parse_args(argv)
    try:
        result=execute(args.out, preserve_synthetic_zip=args.retain_synthetic_zip_for_d18)
    except Exception as exc:
        print("D15_PAIR_TK_NOT_VERIFIED: "+type(exc).__name__,flush=True)
        return 2
    print(json.dumps({"status":result["status"],
                      "screenshot":result["screenshot"]["status"],
                      "human_acceptance":"NOT_RUN"}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
