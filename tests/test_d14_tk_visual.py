"""D14 safety guarantees for the opt-in real-Tk synthetic visual runner."""
from __future__ import annotations

import ast
import inspect
from pathlib import Path
import pytest

from rea import creator_gui
from scripts import d14_tk_visual_smoke

ROOT = Path(__file__).resolve().parents[1]


def test_gui_build_window_is_optional_and_real_launch_uses_it():
    source = inspect.getsource(creator_gui.launch)
    assert "build_window(root)" in source
    assert "root.mainloop()" in source
    assert "import tkinter as tk" in source
    assert "root = tk.Tk()" in source
    # Tk is imported only inside the optional GUI, not normal customer CLI.
    assert "tkinter" not in (ROOT / "rea" / "__init__.py").read_text(encoding="utf-8")


def test_visual_script_is_strictly_synthetic_source():
    assert d14_tk_visual_smoke.SYNTHETIC.name == "qa_guided.csv"
    assert d14_tk_visual_smoke.SYNTHETIC.is_file()
    assert set(d14_tk_visual_smoke.FIELDS) == {"id", "title", "category"}
    assert set(d14_tk_visual_smoke.FIELDS.values()) == {
        "sku", "display_name", "group_name"}


def test_visual_runner_refuses_overwrite_without_opening_tk(tmp_path):
    out = tmp_path / "existing"
    out.mkdir()
    marker = out / "owner.txt"
    marker.write_text("keep", encoding="utf-8")
    with pytest.raises(FileExistsError):
        d14_tk_visual_smoke.execute(out)
    assert marker.read_text(encoding="utf-8") == "keep"


def test_gui_visual_smoke_uses_actual_widget_methods_not_just_controller():
    text = (ROOT / "scripts" / "d14_tk_visual_smoke.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    attributes = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert {"invoke", "current", "insert", "update", "destroy"} <= attributes
    assert "messagebox.showerror" in text
    assert "COMMITTED_SYNTHETIC_FIXTURE_ONLY" in text
    assert "NOT_RUN" in text
