"""Synthetic-only end-to-end recovery: never overwrites local source or target."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

import pytest

from rea.delivery import create_delivery, DeliveryError, verify_delivery
from rea.recovery import MAX_ARCHIVE_ON_DISK, restore_delivery
import rea.recovery as recovery
from rea.safe_publish import publish_directory
from rea.two_source import preflight_pair, pack_pair

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("filename,rows", [
    ("qa_cafe.csv", 4),
    ("qa_products.json", 4),
])
def test_real_synthetic_delivery_can_be_restored(tmp_path, filename, rows):
    archive = tmp_path / "source.zip"
    create_delivery(ROOT / "samples" / filename, archive)
    before = hashlib.sha256(archive.read_bytes()).hexdigest()
    result = restore_delivery(archive, tmp_path / "recovered")
    assert result["status"] == "RESTORED_INTEGRITY_AND_READONLY_SQLITE_ONLY"
    assert result["sqlite_row_count"] == rows
    assert result["archive_sha256"] == before
    assert result["commercial_clearance"] == "NOT_GRANTED"
    assert result["native_windows_launch_accepted"] is False
    assert (tmp_path / "recovered" / "app" / "data.sqlite").is_file()
    assert archive.is_file() and hashlib.sha256(archive.read_bytes()).hexdigest() == before


def test_real_synthetic_pair_archive_can_be_restored(tmp_path):
    first, second = tmp_path / "one.csv", tmp_path / "two.csv"
    first.write_text("sku,label,group\nA,Alpha,Food\n", encoding="utf-8")
    second.write_text("sku,label,group\nB,Beta,Food\n", encoding="utf-8")
    info = preflight_pair(first, second)
    hashes = [item["sha256"] for item in info["sources"]]
    archive = tmp_path / "approved-pair.zip"
    pack_pair(first, second, archive, "Synthetic paired build",
              {"id": "sku", "title": "label", "category": "group"},
              *hashes, "APPROVE", "APPROVE", "APPEND")
    result = restore_delivery(archive, tmp_path / "pair-restored")
    assert result["sqlite_row_count"] == 2
    assert (tmp_path / "pair-restored" / "app" / "append_report.json").is_file()


def test_existing_destination_cannot_be_overwritten(tmp_path):
    archive = tmp_path / "original.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", archive)
    destination = tmp_path / "existing"
    destination.mkdir()
    sentinel = destination / "keep.txt"
    sentinel.write_bytes(b"private-original")
    with pytest.raises(FileExistsError, match="exists"):
        restore_delivery(archive, destination)
    assert sentinel.read_bytes() == b"private-original"


def test_bad_zip_is_never_published_or_overwrites_owner(tmp_path):
    archive = tmp_path / "invalid.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", archive)
    with zipfile.ZipFile(archive) as original:
        values = {n: original.read(n) for n in original.namelist()}
    values["app/app.py"] = b"# unexpected mutated code"
    corrupted = tmp_path / "corrupted.zip"
    with zipfile.ZipFile(corrupted, "x") as bad:
        for name, contents in values.items():
            bad.writestr(name, contents)
    result_path = tmp_path / "not-published"
    with pytest.raises(DeliveryError, match="Checksum"):
        restore_delivery(corrupted, result_path)
    assert not result_path.exists()
    assert archive.is_file() and corrupted.is_file()


def test_rehashed_manifest_row_count_cannot_mislead_recovery(tmp_path):
    original = tmp_path / "original.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", original)
    with zipfile.ZipFile(original) as src:
        files = {p: src.read(p) for p in src.namelist()
                 if p != "delivery_manifest.json"}
    manifest = json.loads(files["app/manifest.json"])
    assert manifest["rows"] == 4
    manifest["rows"] = 999
    files["app/manifest.json"] = json.dumps(manifest).encode()
    rows = [{"path": p, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
            for p, b in sorted(files.items())]
    files["delivery_manifest.json"] = json.dumps({
        "schema_version": "rea.delivery.v0.1", "files": rows,
    }).encode()
    manipulated = tmp_path / "wrong-count.zip"
    with zipfile.ZipFile(manipulated, "x") as dst:
        for name, contents in files.items():
            dst.writestr(name, contents)
    verify_delivery(manipulated)  # Integrity alone cannot prove row semantics.
    destination = tmp_path / "should-not-exist"
    with pytest.raises(DeliveryError, match="row count"):
        restore_delivery(manipulated, destination)
    assert not destination.exists()


def test_publish_collision_during_restore_preserves_owner_directory(tmp_path, monkeypatch):
    archive = tmp_path / "source.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", archive)
    destination = tmp_path / "race-target"

    def raced_publish(stage, target):
        target.mkdir()
        (target / "owner.txt").write_bytes(b"no-overwrite")
        publish_directory(stage, target)

    monkeypatch.setattr(recovery, "publish_directory", raced_publish)
    with pytest.raises(FileExistsError):
        restore_delivery(archive, destination)
    assert (destination / "owner.txt").read_bytes() == b"no-overwrite"


def test_oversized_archive_does_not_create_parent(tmp_path):
    archive = tmp_path / "oversized.zip"
    with archive.open("wb") as stream:
        stream.truncate(MAX_ARCHIVE_ON_DISK + 1)
    target = tmp_path / "no-parent" / "recovered"
    with pytest.raises(DeliveryError, match="staging limit"):
        restore_delivery(archive, target)
    assert not target.parent.exists()


def test_symlink_archive_is_refused(tmp_path):
    original = tmp_path / "source.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", original)
    alias = tmp_path / "linked.zip"
    try:
        alias.symlink_to(original)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks unavailable in this environment")
    with pytest.raises(DeliveryError, match="non-symlink"):
        restore_delivery(alias, tmp_path / "no-restore")
    assert not (tmp_path / "no-restore").exists()
