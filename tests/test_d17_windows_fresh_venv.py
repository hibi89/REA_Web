"""D17 synthetic fresh-Windows-venv safety regressions."""
from pathlib import Path
from subprocess import CompletedProcess
import os
import pytest
from scripts import d17_windows_fresh_venv as fresh

ROOT = Path(__file__).resolve().parents[1]


def test_explicit_fixture_and_installed_dependency_allowlist():
    assert fresh.FIXTURES == ("qa_guided.csv", "qa_pair_extra.json")
    assert fresh.RUNTIME_REQUIREMENTS == (
        "fastapi>=0.110,<1", "uvicorn>=0.27,<1", "pydantic>=2.6,<3")


def test_stage_contains_synthetic_only_and_no_vendor_data(tmp_path):
    project = tmp_path / "new-project"
    fresh.stage_project(project)
    assert (project / "START_REA_CREATOR.cmd").is_file()
    assert (project / "rea" / "creator_preflight.py").is_file()
    for name in fresh.FIXTURES:
        assert (project / "samples" / name).read_bytes() == (
            ROOT / "samples" / name).read_bytes()
    assert (project / "scripts" / "d15_pair_tk_smoke.py").is_file()
    for excluded in (".venv", ".git", ".env", ".vendor"):
        assert not (project / excluded).exists()


def test_existing_folder_kept_unchanged(tmp_path):
    folder = tmp_path / "kept"
    folder.mkdir()
    marker = folder / "owned.txt"
    marker.write_text("KEEP", encoding="utf-8")
    with pytest.raises(FileExistsError):
        fresh.stage_project(folder)
    assert marker.read_text(encoding="utf-8") == "KEEP"


def test_cmd_requires_correct_status_and_exact_exit_code():
    good = CompletedProcess(["cmd"], 11, stdout="[REA] MISSING_MODULES:")
    fresh.assert_native(good, code=11, marker="MISSING_MODULES:")
    with pytest.raises(RuntimeError):
        fresh.assert_native(good, code=0, marker="READY:")
    with pytest.raises(RuntimeError):
        fresh.assert_native(good, code=11, marker="READY:")


def test_ci_only_pip_never_part_of_shipped_windows_launcher():
    launcher = (ROOT / "START_REA_CREATOR.cmd").read_text(encoding="utf-8").lower()
    diag = (ROOT / "rea" / "creator_preflight.py").read_text(
        encoding="utf-8").lower()
    assert "pip install" not in launcher
    assert "subprocess" not in diag
    assert "--check" in launcher and "goto launch" in launcher


def test_platform_specific_rehearsal_refusal_without_mutation(tmp_path):
    report = tmp_path / "owner-report.json"
    if os.name == "nt":
        # Native Windows still must never overwrite an owner's existing output.
        report.write_text("KEEP", encoding="utf-8")
        with pytest.raises(FileExistsError):
            fresh.execute(report)
        assert report.read_text(encoding="utf-8") == "KEEP"
    else:
        with pytest.raises(RuntimeError, match="Windows"):
            fresh.execute(report)
        assert not report.exists()


def test_human_and_commercial_gates_not_cleared():
    code = (ROOT / "scripts" / "d17_windows_fresh_venv.py").read_text(
        encoding="utf-8")
    assert '"human_non_developer_acceptance": "NOT_RUN"' in code
    assert '"commercial_clearance": "NOT_GRANTED"' in code
    assert '"customer_data": "NOT_USED"' in code
