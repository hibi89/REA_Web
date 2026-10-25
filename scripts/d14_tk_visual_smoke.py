"""D14 real Tk widget smoke on isolated synthetic local display only.

Run under xvfb-run in Linux CI or a permitted interactive Windows desktop.
Uses tkinter widgets/button.invoke, dialog stubs for fixture-only local paths,
and optional Pillow screenshot. NOT human usability or commercial acceptance.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC = ROOT / "samples" / "qa_guided.csv"
FIELDS = {"id": "sku", "title": "display_name", "category": "group_name"}


def execute(folder: Path) -> dict:
    folder = Path(folder).absolute()
    if folder.exists() or folder.is_symlink():
        raise FileExistsError("D14 synthetic report destination must be NEW")
    if SYNTHETIC.name != "qa_guided.csv":
        raise RuntimeError("Only committed synthetic fixture is allowed")
    import tkinter as tk
    from rea.creator_gui import build_window
    from rea.provenance import inspect_delivery
    # Private transient output; must never reference any external owner data.
    from tempfile import TemporaryDirectory
    with TemporaryDirectory(prefix="rea-d14-local-") as temp:
        out = Path(temp) / "synthetic.zip"
        source_before = hashlib.sha256(SYNTHETIC.read_bytes()).hexdigest()
        root = tk.Tk()
        root.geometry("900x700+40+40")
        try:
            ui = build_window(root)
            root.update_idletasks()
            root.update()
            with ExitStack() as stack:
                ask_source = stack.enter_context(patch(
                    "tkinter.filedialog.askopenfilename", return_value=str(SYNTHETIC)))
                ask_zip = stack.enter_context(patch(
                    "tkinter.filedialog.asksaveasfilename", return_value=str(out)))
                report_error = stack.enter_context(patch("tkinter.messagebox.showerror"))
                report_success = stack.enter_context(patch("tkinter.messagebox.showinfo"))

                # Real widget/event bindings. Dialogs only supply permitted fixture paths.
                ui.choose_source()
                ui.choose_output()
                assert ask_source.call_count == 1 and ask_zip.call_count == 1
                assert ui.source_var.get() == str(SYNTHETIC)
                assert ui.output_var.get() == str(out)
                assert ui.controller.inspected is None

                ui.inspect_button.invoke()
                root.update()
                assert ui.controller.inspected is not None
                assert ui.controller.inspected.rows == 3
                assert "미승인 컬럼 힌트" in ui.preview_label.cget("text")
                assert all(not ui.fields[key].get() for key in FIELDS)
                assert not ui.rights_var.get()
                assert not ui.approval_var.get()

                # Attempt export without approval through actual Tk button -> denied.
                ui.export_button.invoke()
                root.update()
                assert report_error.call_count == 1
                assert not out.exists()

                # Real dropdown selection by index, checkbox click, entry typing.
                for target, source_column in FIELDS.items():
                    combo = ui.combos[target]
                    fields = list(combo.cget("values"))
                    combo.current(fields.index(source_column))
                ui.rights_checkbox.invoke()
                ui.approval_entry.insert(0, "APPROVE")
                root.update()
                assert ui.rights_var.get() is True
                assert ui.approval_var.get() == "APPROVE"
                assert {k: v.get() for k, v in ui.fields.items()} == FIELDS

                ui.export_button.invoke()
                root.update()
                assert report_success.call_count == 1
                assert out.is_file() and out.stat().st_size > 0
                assert ui.rights_var.get() is False
                assert ui.approval_var.get() == ""
                audit = inspect_delivery(out)
                assert audit["owner_mapping_receipt_present"] is True
                assert audit["overall_commercial_clearance"] == "NOT_GRANTED"
                with zipfile.ZipFile(out) as zf:
                    receipt = json.loads(zf.read("app/mapping_report.json"))
                    assert receipt["source_fields"] == FIELDS
                    assert "app/data.sqlite" in zf.namelist()
                    assert "qa_guided.csv" not in zf.namelist()
                out_digest = hashlib.sha256(out.read_bytes()).hexdigest()
                assert source_before == hashlib.sha256(SYNTHETIC.read_bytes()).hexdigest()

                # Second click cannot reuse consent or overwrite existing archive.
                ui.export_button.invoke()
                assert report_error.call_count == 2
                assert hashlib.sha256(out.read_bytes()).hexdigest() == out_digest

                screen = {"status": "NOT_CAPTURED"}
                folder.mkdir(parents=True, exist_ok=False)
                try:
                    from PIL import ImageGrab
                    x, y = root.winfo_rootx(), root.winfo_rooty()
                    width, height = root.winfo_width(), root.winfo_height()
                    shot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
                    screenshot = folder / "tk_creator_synthetic.png"
                    shot.save(screenshot)
                    screen = {"status": "CAPTURED", "image": screenshot.name,
                              "sha256": hashlib.sha256(screenshot.read_bytes()).hexdigest(),
                              "width": width, "height": height}
                except (ImportError, OSError, RuntimeError, ValueError) as exc:
                    screen = {"status": "NOT_CAPTURED",
                              "reason": type(exc).__name__}
                result = {
                    "schema_version": "rea.synthetic_tk_ui.v0.1",
                    "source": "COMMITTED_SYNTHETIC_FIXTURE_ONLY",
                    "actual_tk_window_opened": True,
                    "actual_tk_widget_actions": [
                        "SOURCE_FILE_CHOOSER_RETURNED_SYNTHETIC",
                        "OUTPUT_FILE_CHOOSER_RETURNED_NEW_TEMP_ZIP",
                        "INSPECT_BUTTON_INVOKED",
                        "UNAPPROVED_EXPORT_BUTTON_DENIED",
                        "THREE_REAL_COMBOBOX_SELECTIONS",
                        "RIGHTS_CHECKBOX_INVOKED",
                        "APPROVE_ENTRY_TYPED",
                        "APPROVED_EXPORT_BUTTON_INVOKED",
                        "SECOND_EXPORT_DENIED",
                    ],
                    "synthetic_source_sha256_before_and_after_match": True,
                    "generated_zip_sha256_validated": out_digest,
                    "delivery_legal_clearance": "NOT_GRANTED",
                    "screenshot": screen,
                    "human_non_developer_acceptance": "NOT_RUN",
                    "clean_consumer_windows_acceptance": "NOT_RUN",
                    "actual_customer_authorization": "NOT_RUN",
                    "commercial_release": "BLOCKED",
                }
                (folder / "synthetic_tk_ui_acceptance.json").write_text(
                    json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                    encoding="utf-8",
                )
                return result
        finally:
            root.destroy()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Real Tk widgets, synthetic display only")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = execute(args.out)
    except Exception as exc:
        print("D14_TK_UI_NOT_VERIFIED: " + type(exc).__name__, file=sys.stderr)
        return 2
    print(json.dumps({"actual_tk_window_opened": report["actual_tk_window_opened"],
                      "actions": len(report["actual_tk_widget_actions"]),
                      "screenshot": report["screenshot"]["status"],
                      "human_non_developer_acceptance": "NOT_RUN"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
