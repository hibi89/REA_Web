"""D22 prevents machine-verified demo evidence becoming a fake human claim."""
from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path
import shutil
import zipfile

import pytest

from scripts import d19_owner_pilot as builder
from scripts import d20_offline_kit_check as checker

ROOT = Path(__file__).resolve().parents[1]
ONE_PAGE = ROOT / "scripts" / "d22_operator_one_page.txt"
LOGS = ("HUMAN_PILOT_BLANK.csv", "MANUAL_TIME_LOG_BLANK.csv")


def _unpack(tmp_path):
    zipped = tmp_path / "demo-kit.zip"
    builder.build_kit(zipped)
    kit = tmp_path / "SEALED_DEMO"
    kit.mkdir()
    with zipfile.ZipFile(zipped) as zf:
        zf.extractall(kit)
    return kit


def test_ten_member_exact_synthetic_demo(tmp_path):
    kit = _unpack(tmp_path)
    assert len(builder.MEMBER_NAMES) == 10
    assert checker.verify(kit)["verified_files"] == 10
    assert (kit / "OPERATOR_ONE_PAGE_WINDOWS.txt").read_bytes() == ONE_PAGE.read_bytes()
    assert "OPERATOR_ONE_PAGE_WINDOWS.txt" in builder.MEMBER_NAMES


def test_operator_copy_outside_sealed_kit_remains_user_not_machine_data(tmp_path):
    kit = _unpack(tmp_path)
    hashes_before = {
        name: hashlib.sha256((kit / name).read_bytes()).hexdigest()
        for name in builder.MEMBER_NAMES
    }
    external = tmp_path / "PRIVATE_USER_TRIAL_UNSHARED"
    external.mkdir()
    for name in LOGS:
        source = kit / name
        dest = external / name
        shutil.copyfile(source, dest)
        rows = list(csv.reader(io.StringIO(dest.read_text(encoding="utf-8"))))
        assert len(rows) == 1 and len(rows[0]) > 7  # header, not a fake pass
        with dest.open("a", encoding="utf-8", newline="") as out:
            out.write("HUMAN_NOT_AUTOMATICALLY_VERIFIED\n")
    assert checker.verify(kit)["human_acceptance"] == "NOT_RUN"
    assert {
        name: hashlib.sha256((kit / name).read_bytes()).hexdigest()
        for name in builder.MEMBER_NAMES
    } == hashes_before


@pytest.mark.parametrize("name", LOGS)
def test_editing_sealed_kit_logs_is_detected_and_refused(tmp_path, name):
    kit = _unpack(tmp_path)
    with (kit / name).open("a", encoding="utf-8") as out:
        out.write("FAKE,HUMAN,PASS\n")
    with pytest.raises(ValueError, match="integrity mismatch"):
        checker.verify(kit)


def test_human_one_page_is_sha_pinned(tmp_path):
    kit = _unpack(tmp_path)
    p = kit / "OPERATOR_ONE_PAGE_WINDOWS.txt"
    with p.open("a", encoding="utf-8") as out:
        out.write("\nALTERED SOURCE\n")
    with pytest.raises(ValueError, match="integrity mismatch"):
        checker.verify(kit)


def test_guide_separates_real_human_trial_and_machine_pass():
    card = ONE_PAGE.read_text(encoding="utf-8")
    guide = builder.GUIDE
    assert "CHECK_PILOT_WINDOWS.cmd" in card
    assert "HUMAN_PILOT_BLANK.csv" in card
    assert "MANUAL_TIME_LOG_BLANK.csv" in card
    assert "DIFFERENT" in card
    assert "Do NOT edit the original blank files" in card
    assert "NOT an automated PASS" in card
    assert "OUTSIDE" in card or "different" in card
    assert "ONE_PAGE_WINDOWS" in guide
    assert "COPY BOTH HUMAN_PILOT_BLANK.csv" in guide
    assert "PRIVATE" in card or "personal working folder" in card
    assert "one-page" in guide
    assert "machine verification = human acceptance" in card


def test_no_customer_or_operator_results_packed(tmp_path):
    kit = _unpack(tmp_path)
    for name in LOGS:
        body = (kit / name).read_text(encoding="utf-8")
        assert len(body.splitlines()) == 1
        assert "PASS" not in body
    meta = (kit / "MANIFEST.json").read_text(encoding="utf-8")
    assert '"real_human_acceptance": "NOT_RUN"' in meta
    assert '"commercial_clearance": "NOT_GRANTED"' in meta


def test_d22_output_non_overwriting_and_reproducible(tmp_path):
    a, b = tmp_path / "one.zip", tmp_path / "two.zip"
    builder.build_kit(a)
    builder.build_kit(b)
    assert a.read_bytes() == b.read_bytes()
    with pytest.raises(FileExistsError):
        builder.build_kit(a)
