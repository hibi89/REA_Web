"""One-command synthetic technical go/no-go: four generated ZIPs + real ASGI."""
from __future__ import annotations

import json
import os

import pytest

from scripts.rea_final_technical_smoke import main, run, SYNTHETIC_CASES


def test_four_real_generated_zip_restore_and_http_contracts(tmp_path):
    output = tmp_path / "actual-four-cases"
    report = run(out=output)
    assert report["status"] == "PASS_SYNTHETIC_TECHNICAL_ONLY"
    assert report["case_count"] == 4
    assert [item["case"] for item in report["cases"]] == list(SYNTHETIC_CASES)
    assert [item["rows"] for item in report["cases"]] == [4, 4, 3, 2]
    assert all(item["recovery_integrity"] == "PASS" and
               item["generated_inprocess_http"] == "PASS"
               for item in report["cases"])
    assert all(item["windows_cmd_prerequisites"] == "NOT_RUN"
               for item in report["cases"])
    assert report["commercial_clearance"] == "NOT_GRANTED"
    assert report["seller_final_approval"] == "NOT_APPROVED"
    assert report["native_windows_launcher"] == "NOT_RUN"
    assert report["human_windows_acceptance"] == "NOT_RUN"
    assert (output / "technical_smoke_report.json").is_file()
    assert json.loads((output / "technical_smoke_report.json").read_text(
        encoding="utf-8")) == report
    assert len(list((output / "packages").glob("*.zip"))) == 4
    assert len(list((output / "restored").iterdir())) == 4


def test_output_can_never_be_overwritten(tmp_path):
    target = tmp_path / "existing"
    target.mkdir()
    (target / "owner.txt").write_text("KEEP", encoding="utf-8")
    with pytest.raises(FileExistsError, match="NEW directory"):
        run(out=target)
    assert (target / "owner.txt").read_text(encoding="utf-8") == "KEEP"


@pytest.mark.skipif(os.name == "nt", reason="native command permitted only on Windows")
def test_native_mode_cannot_claim_windows_evidence_on_linux(tmp_path):
    with pytest.raises(ValueError, match="actual Windows"):
        run(out=tmp_path / "never", native=True)
    assert not (tmp_path / "never").exists()


def test_cli_fails_closed_on_existing_owner_output(tmp_path, capsys):
    target = tmp_path / "already"
    target.mkdir()
    assert main(["--out", str(target)]) == 2
    assert "FAIL_SYNTHETIC_TECHNICAL" in capsys.readouterr().err
    assert target.exists()
