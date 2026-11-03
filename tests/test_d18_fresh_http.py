"""D18 tests: synthetic-only HTTP contract, archive provenance and fail-closed CI."""
from __future__ import annotations

import hashlib
import inspect
import json
import os
from pathlib import Path

import pytest

from rea.delivery import create_delivery
from rea.pair_creator import PairCreatorController
from scripts import d15_pair_tk_smoke as gui
from scripts import d18_http_probe as probe
from scripts import d18_windows_fresh_http as fresh

ROOT = Path(__file__).resolve().parents[1]
FIRST = ROOT / "samples" / "qa_guided.csv"
SECOND = ROOT / "samples" / "qa_pair_extra.json"
MAP = {"id": "sku", "title": "display_name", "category": "group_name"}


def synthetic_controller_zip(tmp_path):
    """Unit fixture, NOT actual Tk. Native D18 script separately runs real widgets."""
    archive = tmp_path / "fixture.zip"
    controller = PairCreatorController()
    controller.inspect(FIRST, SECOND)
    controller.export(FIRST, SECOND, archive, "D18 unit only", MAP,
                      True, True, "APPROVE", "APPROVE", "APPEND")
    ui = tmp_path / "test_only_mock_ui.json"
    ui.write_text(json.dumps({
        "status": "ACTUAL_TK_TWO_FILE_WIDGETS_PASS",
        "both_origins_sha_unchanged": True,
        "commercial_clearance": "NOT_GRANTED",
        "validated_zip_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }), encoding="utf-8")
    return archive, ui


def test_d15_normal_smoke_does_not_retain_zip():
    signature = inspect.signature(gui.execute)
    assert signature.parameters["preserve_synthetic_zip"].default is False
    assert gui.MAP == MAP


def test_d18_accepts_exact_fixture_hashes_and_receipts(tmp_path):
    archive, mocked_ui = synthetic_controller_zip(tmp_path)
    evidence = probe.check_synthetic_archive(archive, mocked_ui)
    assert evidence["sources"] == 2 and evidence["rows"] == 5
    assert evidence["zip_sha256"] == hashlib.sha256(archive.read_bytes()).hexdigest()


def test_d18_real_http_from_controller_only_not_ui(tmp_path):
    archive, mocked_ui = synthetic_controller_zip(tmp_path)
    result = probe.serve_archive(archive, mocked_ui)
    assert result["status"] == probe.STATUS
    assert result["rows"] == 5
    assert result["binding"] == "127.0.0.1"
    assert result["server_cleanup"] == "CONFIRMED"
    assert result["commercial_clearance"] == "NOT_GRANTED"


def test_d18_rejects_edited_zip_and_preserves_original(tmp_path):
    archive, mocked_ui = synthetic_controller_zip(tmp_path)
    original = archive.read_bytes()
    archive.write_bytes(original + b"modified")
    with pytest.raises(ValueError, match="mismatch"):
        probe.check_synthetic_archive(archive, mocked_ui)
    assert archive.read_bytes() == original + b"modified"


def test_d18_rejects_changed_owner_proof(tmp_path):
    archive, mocked_ui = synthetic_controller_zip(tmp_path)
    metadata = json.loads(mocked_ui.read_text(encoding="utf-8"))
    metadata["commercial_clearance"] = "GRANTED"
    mocked_ui.write_text(json.dumps(metadata), encoding="utf-8")
    with pytest.raises(ValueError, match="mismatch"):
        probe.check_synthetic_archive(archive, mocked_ui)


def test_d18_rejects_one_file_even_with_mocked_ui(tmp_path):
    archive = tmp_path / "one.zip"
    create_delivery(ROOT / "samples" / "qa_cafe.csv", archive)
    ui = tmp_path / "mock-ui.json"
    ui.write_text(json.dumps({
        "status": "ACTUAL_TK_TWO_FILE_WIDGETS_PASS",
        "both_origins_sha_unchanged": True,
        "commercial_clearance": "NOT_GRANTED",
        "validated_zip_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="receipt"):
        probe.check_synthetic_archive(archive, ui)


def test_d18_new_output_only_no_existing_report_change(tmp_path):
    archive, mocked_ui = synthetic_controller_zip(tmp_path)
    report = tmp_path / "existing.json"
    report.write_text("KEEP", encoding="utf-8")
    code = probe.main(["--archive", str(archive), "--ui-report", str(mocked_ui),
                       "--out", str(report)])
    assert code == 2
    assert report.read_text(encoding="utf-8") == "KEEP"


def test_windows_runner_existing_output_or_linux_refusal(tmp_path):
    existing = tmp_path / "dont-overwrite.json"
    existing.write_bytes(b"KEEP")
    if os.name == "nt":
        with pytest.raises(FileExistsError):
            fresh.execute(existing)
    else:
        with pytest.raises(RuntimeError, match="Windows"):
            fresh.execute(existing)
    assert existing.read_bytes() == b"KEEP"


def test_ephemeral_port_only_loopback_and_no_automatic_owner_install():
    assert 1 <= probe.loopback_port() <= 65535
    source = (ROOT / "scripts" / "d18_windows_fresh_http.py").read_text(encoding="utf-8")
    assert 'stage_project(project)' in source
    assert 'marker="[REA] MISSING_MODULES:"' in source
    assert '"APPROVE_APPROVE_APPEND"' in source
    assert '"NOT_RUN"' in source
    assert "0.0.0.0" not in (ROOT / "scripts" / "d18_http_probe.py").read_text(encoding="utf-8")
