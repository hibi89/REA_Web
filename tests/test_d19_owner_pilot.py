"""D19 offline synthetic Windows pilot kit safety and reproducibility."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

import pytest

from scripts import d19_owner_pilot as pilot

ROOT = Path(__file__).resolve().parents[1]


def _build(tmp_path, name="synthetic-pilot.zip"):
    path = tmp_path / name
    result = pilot.build_kit(path)
    assert result["human_acceptance"] == "NOT_RUN"
    return path


def _rewrite(archive, changed_member, payload):
    """Repack an existing test-only ZIP, avoiding duplicate ZIP entries."""
    altered = archive.parent / "changed.zip"
    with zipfile.ZipFile(archive) as old, zipfile.ZipFile(
            altered, "x", compression=zipfile.ZIP_DEFLATED) as new:
        for item in old.infolist():
            data = payload if item.filename == changed_member else old.read(item.filename)
            new.writestr(pilot._zipinfo(item.filename), data)
    return altered


def test_pinned_fixture_integrity_and_source_only_contract():
    a, b = pilot._sources()
    assert [a.name, b.name] == ["qa_guided.csv", "qa_pair_extra.json"]
    assert [pilot.sha(pilot.canonical_fixture_bytes(name, source))
            for name, source in zip(pilot.FIXTURES, (a, b))] == list(pilot.FIXTURES.values())
    assert set(pilot.MAPPING) == {"id", "title", "category"}
    assert set(pilot.MAPPING.values()) == {"sku", "display_name", "group_name"}


def test_git_checkout_crlf_canonicalized_without_modifying_fixture(tmp_path):
    source = tmp_path / "qa_guided.csv"
    canonical = pilot.canonical_fixture_bytes(
        "qa_guided.csv", ROOT / "samples" / "qa_guided.csv")
    source.write_bytes(canonical.replace(b"\n", b"\r\n"))
    untouched = source.read_bytes()
    assert pilot.canonical_fixture_bytes("qa_guided.csv", source) == canonical
    assert source.read_bytes() == untouched
    source.write_bytes(untouched.replace(b"S01", b"R01"))
    with pytest.raises(ValueError, match="SHA mismatch"):
        pilot.canonical_fixture_bytes("qa_guided.csv", source)


def test_kit_contains_only_safe_and_expected_files(tmp_path):
    path = _build(tmp_path)
    audit = pilot.verify_kit(path)
    assert audit["verified_members"] == 10 and audit["rows"] == 5
    assert audit["human_acceptance"] == "NOT_RUN"
    with zipfile.ZipFile(path) as zf:
        assert set(zf.namelist()) == pilot.MEMBER_NAMES
        doc = json.loads(zf.read("MANIFEST.json"))
        assert doc["commercial_clearance"] == "NOT_GRANTED"
        assert doc["real_human_acceptance"] == "NOT_RUN"
        assert doc["manual_labor_measurements"] == "BLANK_NOT_RUN"
        for name in pilot.FIXTURES:
            assert zf.read("sources/" + name) == pilot.canonical_fixture_bytes(
                name, ROOT / "samples" / name)


def test_both_human_logs_are_truly_blank_header_only(tmp_path):
    path = _build(tmp_path)
    with zipfile.ZipFile(path) as zf:
        for name in ("HUMAN_PILOT_BLANK.csv", "MANUAL_TIME_LOG_BLANK.csv"):
            text = zf.read(name).decode("utf-8")
            records = list(csv.reader(io.StringIO(text)))
            assert len(records) == 1 and len(records[0]) >= 7
            assert all(field for field in records[0])
            assert "PASS" not in text and "SUCCESS" not in text


def test_build_is_byte_deterministic_same_operating_system(tmp_path):
    first = _build(tmp_path, "first.zip")
    second = _build(tmp_path, "second.zip")
    assert first.read_bytes() == second.read_bytes()
    assert pilot.verify_kit(first)["kit_sha256"] == pilot.verify_kit(second)["kit_sha256"]


def test_existing_output_never_overwritten(tmp_path):
    original = tmp_path / "existing.zip"
    original.write_bytes(b"KEEP OWNER")
    with pytest.raises(FileExistsError):
        pilot.build_kit(original)
    assert original.read_bytes() == b"KEEP OWNER"


def test_reject_unsafe_output_type(tmp_path):
    with pytest.raises(ValueError, match=r"\.zip"):
        pilot.build_kit(tmp_path / "not-a-zip.txt")


def test_changed_or_noncommitted_fixture_rejected_before_output(monkeypatch, tmp_path):
    forged_root = tmp_path / "wrong"
    folder = forged_root / "samples"
    folder.mkdir(parents=True)
    (folder / "qa_guided.csv").write_text("id,title,category\nREAL,secret,x\n", encoding="utf-8")
    (folder / "qa_pair_extra.json").write_text("[]", encoding="utf-8")
    monkeypatch.setattr(pilot, "ROOT", forged_root)
    with pytest.raises(ValueError, match="Fixture SHA mismatch"):
        pilot.build_kit(tmp_path / "out.zip")
    assert not (tmp_path / "out.zip").exists()


def test_modified_pilot_readme_rejected_even_when_manifest_old(tmp_path):
    archive = _build(tmp_path)
    forged = _rewrite(archive, "README_WINDOWS.txt", b"FAKE")
    with pytest.raises(ValueError):
        pilot.verify_kit(forged)


def test_manual_human_success_inserted_is_not_accepted(tmp_path):
    archive = _build(tmp_path)
    changed = pilot.HUMAN_LOG.encode() + b"fake,user,pass\n"
    forged = _rewrite(archive, "HUMAN_PILOT_BLANK.csv", changed)
    with pytest.raises(ValueError):
        pilot.verify_kit(forged)


def test_forged_outer_manifest_commercial_status_refused(tmp_path):
    archive = _build(tmp_path)
    with zipfile.ZipFile(archive) as zf:
        manifest = json.loads(zf.read("MANIFEST.json"))
    manifest["commercial_clearance"] = "GRANTED"
    forged = _rewrite(archive, "MANIFEST.json", pilot._json(manifest))
    with pytest.raises(ValueError, match="invariant"):
        pilot.verify_kit(forged)


def test_demo_requires_real_approved_pair_receipt_not_single_csv(tmp_path):
    archive = _build(tmp_path)
    with zipfile.ZipFile(archive) as zf:
        original = zf.read("demo/approved_pair.zip")
    forged = _rewrite(archive, "demo/approved_pair.zip", original[:-20])
    with pytest.raises(ValueError):
        pilot.verify_kit(forged)


def test_operator_guide_is_manual_and_local_only():
    guide = pilot.GUIDE
    assert "http://127.0.0.1:8000/" in guide
    assert "launch_windows.cmd" in guide
    assert "check_windows.cmd" in guide
    assert "python CHECK_PILOT_OFFLINE.py" in guide
    assert "Double-click CHECK_PILOT_WINDOWS.cmd" in guide
    assert "S01" in guide and "S05" in guide
    assert "Ctrl+C" in guide
    assert "APPEND" in guide and "JOIN" in guide
    assert "NOT a COMMERCIAL RELEASE" in guide or "NOT A COMMERCIAL RELEASE" in guide
    assert "No automatic package installation" in guide
    assert "HUMAN_PILOT_BLANK.csv" in guide


def test_cli_refuses_existing_evidence_and_verifies_created_zip(tmp_path):
    target = tmp_path / "kit.zip"
    assert pilot.main(["build", "--out", str(target)]) == 0
    assert pilot.main(["verify", "--zip", str(target)]) == 0
    assert pilot.main(["build", "--out", str(target)]) == 2
