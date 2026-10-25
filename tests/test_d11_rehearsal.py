"""D11: three independent synthetic quote-to-delivery receipts, never real clients."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

from rea.provenance import inspect_delivery
from scripts import d11_rehearsal

ROOT = Path(__file__).resolve().parents[1]


def test_three_independent_real_zip_trials_and_gap_matrix(tmp_path):
    report = d11_rehearsal.make(tmp_path / "trial")
    assert report["three_case_count"] == 3
    assert report["classification"] == "SYNTHETIC_THREE_CASE_REHEARSAL_ONLY"
    assert report["overall_g0_g6_release"] == "BLOCKED"
    assert report["measured_manual_hours"] is None
    assert report["human_log_required"] is True
    assert report["real_windows_non_developer"] == "NOT_RUN"
    assert report["reference_site_authorization"] == "NOT_RUN"
    assert [case["case_id"] for case in report["three_cases"]] == ["cafe", "inventory", "trends"]
    for entry in report["three_cases"]:
        assert entry["quote_is_binding"] is False
        assert entry["price_krw_hypothesis"] == 300000
        assert entry["data_ownership"] == "TEST_FIXTURE_ONLY"
        assert entry["input_file_count"] <= 2
        assert 1 <= entry["screen_count"] <= 2
        assert len(entry["selected_features"]) == 3
        assert len(set(entry["selected_features"])) == 3
        assert entry["manual_labor_minutes"] is None
        assert entry["customer_acceptance"] == "NOT_RUN"
        assert entry["manual_correction_round"] == "NOT_RUN"
        assert entry["browser_acceptance"] == "NOT_RUN_IN_PACKAGING_PHASE"
        assert entry["gates"]["G0"]["status"] == "PARTIAL"
        assert entry["gates"]["G3"]["status"] == "PASS_SYNTHETIC_SUBCHECK"
        assert entry["gates"]["G4"]["status"] == "PARTIAL_AWAITING_BROWSER"
        assert entry["gates"]["G5"]["status"] == "BLOCKED"
        assert entry["gates"]["G6"]["status"] == "BLOCKED"
        archive = tmp_path / "trial" / entry["output_zip"]
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == entry["output_zip_sha256"]
        assert inspect_delivery(archive)["overall_commercial_clearance"] == "NOT_GRANTED"
        with zipfile.ZipFile(archive) as zf:
            paths = set(zf.namelist())
            assert "self_check.py" in paths and "check_windows.cmd" in paths
            assert not any(p.startswith("app/engines/") for p in paths)
            assert "app/data.sqlite" in paths
            assert entry["fixture_name"] not in paths


def test_rehearsal_repeatable_without_customer_data(tmp_path):
    a, b = tmp_path / "run1", tmp_path / "run2"
    first, second = d11_rehearsal.make(a), d11_rehearsal.make(b)
    assert first == second
    assert (a / "acceptance_scorecard.json").read_bytes() == (b / "acceptance_scorecard.json").read_bytes()
    for case in first["three_cases"]:
        assert (a / case["output_zip"]).read_bytes() == (b / case["output_zip"]).read_bytes()
    text = (a / "acceptance_scorecard.json").read_text(encoding="utf-8")
    assert "블렌드 커피" not in text
    assert "카페라떼" not in text
    assert "NAS HDD" not in text
    assert "JP 실버" not in text
    assert "NOT_GRANTED" in text


def test_manual_time_log_header_only_never_invent_hours(tmp_path):
    d11_rehearsal.make(tmp_path / "trial")
    log = tmp_path / "trial/MANUAL_TIME_LOG_BLANK.csv"
    with log.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        assert next(reader) == list(d11_rehearsal.LABOR_FIELDS)
        assert list(reader) == []
    guide = (tmp_path / "trial/README_KO.md").read_text(encoding="utf-8")
    assert "6~8시간" in guide and "판매 금지" in guide


@pytest.mark.parametrize("mutate", [
    lambda c: {**c, "selected_features": ("list", "search", "detail", "simple_summary")},
    lambda c: {**c, "selected_features": ("list", "list", "detail")},
    lambda c: {**c, "selected_features": ("list", "payment")},
    lambda c: {**c, "screen_count": 3},
    lambda c: {**c, "screen_count": True},
    lambda c: {**c, "source": "real_customer.csv"},
])
def test_draft_quote_rejects_unsupported_or_unowned_scope(mutate):
    with pytest.raises(ValueError):
        d11_rehearsal.validate_case(mutate(d11_rehearsal.CASES[0]))


def test_fail_closed_wrong_expected_row_count_does_not_publish(tmp_path, monkeypatch):
    cases = list(d11_rehearsal.CASES)
    cases[1] = {**cases[1], "expected_rows": 999}
    monkeypatch.setattr(d11_rehearsal, "CASES", tuple(cases))
    out = tmp_path / "trial"
    with pytest.raises(ValueError, match="row integrity"):
        d11_rehearsal.make(out)
    assert not out.exists()
    assert not list(tmp_path.glob(".rea-d11-*"))


def test_owner_existing_output_never_overwritten(tmp_path):
    out = tmp_path / "already"
    out.mkdir()
    (out / "owner.txt").write_text("KEEP")
    with pytest.raises(FileExistsError):
        d11_rehearsal.make(out)
    assert (out / "owner.txt").read_text() == "KEEP"


def test_cli_synthetic_rehearsal_writes_safe_status(tmp_path):
    out = tmp_path / "new_case_trial"
    command = [sys.executable, "-m", "scripts.d11_rehearsal", "--out", str(out)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=100)
    assert result.returncode == 0, result.stderr
    printed = json.loads(result.stdout)
    assert printed["three_case_count"] == 3
    assert printed["overall_g0_g6_release"] == "BLOCKED"
    assert printed["cases"] == ["cafe", "inventory", "trends"]
    assert (out / "acceptance_scorecard.json").is_file()
    repeat = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=100)
    assert repeat.returncode != 0
    assert (out / "acceptance_scorecard.json").is_file()


def test_browser_rehearsal_source_preserves_blocked_gates():
    import ast
    # Windows regression never needs the Linux-only Playwright browser binary.
    # Actual Chromium execution is independently required in the Linux CI job.
    path = ROOT / "scripts/d11_browser_rehearsal.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    functions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    assert {"run_case", "main", "free_port"} <= functions
    for case in d11_rehearsal.CASES:
        assert set(case["selected_features"]) <= d11_rehearsal.ALLOWED_FEATURES
