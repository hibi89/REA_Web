"""D13 optional offline creator — pure controller and display-unavailable regression."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

from rea.creator_gui import CreatorController, CLI_FALLBACK, OWNER_NOTICE
from rea.mvp import DataError
from rea.provenance import inspect_delivery

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "samples/qa_guided.csv"
JSON = ROOT / "samples/qa_guided.json"
CSV_MAP = {"id": "sku", "title": "display_name", "category": "group_name"}
JSON_MAP = {"id": "item_code", "title": "label", "category": "region"}


@pytest.mark.parametrize("source,mapping", [(CSV, CSV_MAP), (JSON, JSON_MAP)])
def test_gui_controller_inspects_and_exports_real_approved_zip(tmp_path, source, mapping):
    original = source.read_bytes()
    model = CreatorController()
    report = model.inspect(source)
    assert report.rows == 3
    assert report.fields == tuple(mapping.values()) + (
        ("price",) if source.suffix == ".csv" else ("engagement",))
    assert len(report.sha256) == 64
    assert all("name" in item and "inferred_type" in item for item in report.field_details)
    archive = tmp_path / "locally-reviewed.zip"
    model.export(source, archive, "Local approved fixture", mapping, True, "APPROVE")
    assert archive.is_file()
    assert model.inspected is None
    assert source.read_bytes() == original
    audit = inspect_delivery(archive)
    assert audit["overall_commercial_clearance"] == "NOT_GRANTED"
    assert audit["owner_mapping_receipt_present"] is True
    with zipfile.ZipFile(archive) as zipped:
        assert "app/data.sqlite" in zipped.namelist()
        assert "app/mapping_report.json" in zipped.namelist()
        receipt = json.loads(zipped.read("app/mapping_report.json"))
        assert receipt["source_fields"] == mapping
        assert source.name not in zipped.namelist()


@pytest.mark.parametrize("confirmation,rights", [
    ("", False), ("APPROVE", False), ("approve", True),
    ("NO", True), ("APPROVE ", True),
])
def test_gui_cannot_generate_without_explicit_owner_approval(tmp_path, confirmation, rights):
    model = CreatorController()
    model.inspect(CSV)
    target = tmp_path / "never.zip"
    with pytest.raises(DataError):
        model.export(CSV, target, "Test", CSV_MAP, rights, confirmation)
    assert model.inspected is not None
    assert not target.exists()


def test_uninspected_file_is_never_approved(tmp_path):
    model = CreatorController()
    with pytest.raises(DataError, match="Inspect"):
        model.export(CSV, tmp_path / "no.zip", "Test", CSV_MAP, True, "APPROVE")


def test_input_change_during_selection_clears_inspected_state(tmp_path):
    model = CreatorController()
    model.inspect(CSV)
    with pytest.raises(DataError, match="Input changed"):
        model.export(JSON, tmp_path / "no.zip", "Test", CSV_MAP, True, "APPROVE")
    assert model.inspected is None


def test_file_sha_change_since_preview_refuses_export(tmp_path):
    owned = tmp_path / "private.csv"
    owned.write_bytes(CSV.read_bytes())
    model = CreatorController()
    model.inspect(owned)
    owned.write_bytes(owned.read_bytes().replace(b"S01", b"X01"))
    with pytest.raises(DataError, match="SHA changed"):
        model.export(owned, tmp_path / "no.zip", "Test", CSV_MAP, True, "APPROVE")
    assert not (tmp_path / "no.zip").exists()


@pytest.mark.parametrize("mapping", [
    {"id": "sku", "title": "display_name", "category": "sku"},
    {"id": "sku", "title": "display_name", "category": "unseen"},
    {"id": "sku", "title": "display_name"},
    {"id": "sku", "title": "display_name", "category": "group_name", "other": "price"},
])
def test_guessed_invalid_ambiguous_field_mapping_is_rejected(tmp_path, mapping):
    model = CreatorController()
    model.inspect(CSV)
    with pytest.raises(DataError):
        model.export(CSV, tmp_path / "no.zip", "Test", mapping, True, "APPROVE")
    assert not (tmp_path / "no.zip").exists()


@pytest.mark.parametrize("name", ["", " ", "x" * 101])
def test_blank_or_oversize_app_name_not_exported(tmp_path, name):
    model = CreatorController()
    model.inspect(CSV)
    with pytest.raises(DataError, match="App name"):
        model.export(CSV, tmp_path / "no.zip", name, CSV_MAP, True, "APPROVE")


def test_existing_zip_never_replaced_and_bytes_preserved(tmp_path):
    existing = tmp_path / "original.zip"
    existing.write_bytes(b"original owner content")
    model = CreatorController()
    model.inspect(CSV)
    with pytest.raises(FileExistsError):
        model.export(CSV, existing, "Test", CSV_MAP, True, "APPROVE")
    assert existing.read_bytes() == b"original owner content"


def test_symlink_input_never_accepted(tmp_path):
    link = tmp_path / "linked.csv"
    try:
        link.symlink_to(CSV)
    except (NotImplementedError, OSError):
        pytest.skip("Symlinks are not available to this Windows test runner")
    model = CreatorController()
    with pytest.raises(DataError):
        model.inspect(link)
    assert model.inspected is None


def test_invalid_source_inspection_clears_prior_preview(tmp_path):
    model = CreatorController()
    model.inspect(CSV)
    fake = tmp_path / "unsafe.txt"
    fake.write_text("secret", encoding="utf-8")
    with pytest.raises(DataError):
        model.inspect(fake)
    assert model.inspected is None


def test_cancelled_and_unexpected_extensions_never_export(tmp_path):
    model = CreatorController()
    model.inspect(CSV)
    with pytest.raises(DataError, match="ZIP"):
        model.export(CSV, tmp_path / "data.json", "Test", CSV_MAP, True, "APPROVE")
    assert not (tmp_path / "data.json").exists()


def test_success_does_not_reuse_consent_for_second_zip(tmp_path):
    model = CreatorController()
    model.inspect(CSV)
    model.export(CSV, tmp_path / "first.zip", "Test", CSV_MAP, True, "APPROVE")
    with pytest.raises(DataError, match="Inspect"):
        model.export(CSV, tmp_path / "second.zip", "Test", CSV_MAP, True, "APPROVE")
    assert not (tmp_path / "second.zip").exists()


def test_import_has_no_tkinter_side_effect_and_cli_fallback_documented():
    assert "Tkinter" in CLI_FALLBACK
    assert "data.sqlite" in OWNER_NOTICE
    # Source smoke: GUI must not be imported by existing ZIP/CLI generator.
    source = (ROOT / "rea" / "creator_gui.py").read_text(encoding="utf-8")
    assert "import tkinter as tk" in source
    assert source.index("def launch(") < source.index("import tkinter as tk")
    assert "requests" not in source
    assert "urllib.request" not in source


def test_headless_gui_fails_with_actionable_cli_command(tmp_path):
    script = (
        "from rea.creator_gui import launch\n"
        "import sys, types\n"
        "m=types.ModuleType('tkinter')\n"
        "def fail(): raise RuntimeError('no display')\n"
        "m.Tk=fail\n"
        "sys.modules['tkinter']=m\n"
        "sys.exit(launch())\n"
    )
    proc = subprocess.run([sys.executable, "-c", script],
                          cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == 2
    assert "python -m rea.guided" in proc.stderr
    assert "RuntimeError" in proc.stderr
    assert "no display" not in proc.stderr


def test_controller_does_not_include_customer_cells_in_printable_preview():
    inspected = CreatorController().inspect(CSV)
    preview = repr(inspected)
    assert "아메리카노" not in preview and "카페라떼" not in preview
    assert "S01" not in preview
    assert hashlib.sha256(CSV.read_bytes()).hexdigest() == inspected.sha256
