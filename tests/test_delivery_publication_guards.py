"""Synthetic customer delivery regression: bounded inspection and atomic publication.

Never uses genuine customer data or creates commercial signoff.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3

import pytest

import rea.delivery as delivery
from rea.customer_self_check import (
    MAX_DELIVERY_BYTES, MAX_DELIVERY_FILES, MAX_MANIFEST_BYTES,
    _member_sha256_bounded, inspect,
)
from rea.mvp import DataError, source_sha256


def source_csv(tmp_path):
    path = tmp_path / "sample.csv"
    path.write_text("id,title,category\nA,Sample,Food\n", encoding="utf-8")
    return path


def synthetic_extracted_kit(tmp_path):
    root = tmp_path / "extracted"
    data = {
        "app/app.py": b"# synthetic app",
        "app/requirements.txt": b"fastapi>=0.110,<1\n",
        "app/manifest.json": b"{}",
        "app/static/index.html": b"<html></html>",
        "app/static/app.js": b"/* synthetic */",
        "app/static/style.css": b"/* synthetic */",
        "launch_windows.cmd": b"@echo off\r\n",
        "check_windows.cmd": b"@echo off\r\n",
        "self_check.py": b"# fixture",
        "README_WINDOWS.md": b"# fixture",
        "ACCEPTANCE_CHECKLIST.md": b"# fixture",
    }
    for name, value in data.items():
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(value)
    with sqlite3.connect(root / "app/data.sqlite") as connection:
        connection.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, title TEXT)")
        connection.execute("INSERT INTO items (title) VALUES ('synthetic')")
    data["app/data.sqlite"] = (root / "app/data.sqlite").read_bytes()
    rows = [
        {"path": name, "bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()}
        for name, value in data.items()
    ]
    manifest = {"schema_version": "rea.delivery.v0.1", "files": rows}
    (root / "delivery_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return root, manifest


def test_genuine_synthetic_extract_passes_sha_and_readonly_sqlite(tmp_path):
    root, _ = synthetic_extracted_kit(tmp_path)
    result = inspect(root)
    assert result["integrity"] == "MATCHED_DELIVERY_MANIFEST_SHA256"
    assert result["database"] == "READONLY_OPEN_SUCCESS"
    assert result["row_count_only"] == 1


def test_extract_hash_does_not_use_unbounded_read_bytes(tmp_path, monkeypatch):
    root, _ = synthetic_extracted_kit(tmp_path)
    original = Path.read_bytes

    def no_read_bytes(path):
        if path.parent == root / "app" or root in path.parents:
            raise AssertionError("Unbounded extracted file read")
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", no_read_bytes)
    result = inspect(root)
    assert result["integrity"] == "MATCHED_DELIVERY_MANIFEST_SHA256"


def test_oversized_extracted_manifest_rejected_before_read(tmp_path, monkeypatch):
    root, _ = synthetic_extracted_kit(tmp_path)
    manifest = root / "delivery_manifest.json"
    with manifest.open("ab") as handle:
        handle.seek(MAX_MANIFEST_BYTES)
        handle.write(b"x")
    assert inspect(root)["integrity"] == "NOT_VERIFIED"


@pytest.mark.parametrize("replacement", [
    lambda doc: doc.update(files=[{}] * (MAX_DELIVERY_FILES + 1)),
    lambda doc: doc["files"][0].update(bytes=MAX_DELIVERY_BYTES + 1),
    lambda doc: doc["files"][0].update(bytes=True),
    lambda doc: doc["files"][0].update(bytes=-1),
    lambda doc: doc["files"][0].update(sha256="bad-hash"),
    lambda doc: [item.update(bytes=MAX_DELIVERY_BYTES) for item in doc["files"]],
])
def test_manifest_limits_fail_closed(tmp_path, replacement):
    root, manifest = synthetic_extracted_kit(tmp_path)
    replacement(manifest)
    (root / "delivery_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    result = inspect(root)
    assert result["integrity"] == "NOT_VERIFIED"
    assert result["status"] == "FAIL_LOCAL_PREREQUISITES"


def test_extracted_file_size_change_during_stream_rejected(tmp_path, monkeypatch):
    root, _ = synthetic_extracted_kit(tmp_path)
    sample = root / "app/app.py"
    with pytest.raises(ValueError, match="changed size"):
        _member_sha256_bounded(sample, 1)


def test_zip_publication_refuses_mid_build_owner_change(tmp_path, monkeypatch):
    original_build = delivery.build
    original = source_csv(tmp_path)
    output = tmp_path / "must_not_publish.zip"

    def build_then_mutate(source, project, *args, **kwargs):
        result = original_build(source, project, *args, **kwargs)
        original.write_text("id,title,category\nB,Changed,Food\n", encoding="utf-8")
        return result

    monkeypatch.setattr(delivery, "build", build_then_mutate)
    with pytest.raises(DataError, match="changed before ZIP publication"):
        delivery.create_delivery(original, output)
    assert not output.exists()


def test_stale_owner_approval_rejected_before_zip_build(tmp_path, monkeypatch):
    source = source_csv(tmp_path)
    sha = source_sha256(source)
    source.write_text("id,title,category\nB,Changed,Food\n", encoding="utf-8")
    target = tmp_path / "new-parent" / "unapproved.zip"

    def should_not_build(*args, **kwargs):
        raise AssertionError("Stale approved source reached build")

    monkeypatch.setattr(delivery, "build", should_not_build)
    with pytest.raises(DataError, match="changed since approved preview"):
        delivery.create_delivery(source, target, expected_source_sha256=sha)
    assert not target.exists()
    assert not target.parent.exists()


def test_existing_archive_not_replaced_when_source_is_valid(tmp_path):
    source = source_csv(tmp_path)
    target = tmp_path / "existing.zip"
    target.write_bytes(b"owner-private-original")
    with pytest.raises(FileExistsError):
        delivery.create_delivery(source, target)
    assert target.read_bytes() == b"owner-private-original"


def test_semantic_audit_failure_keeps_zip_unpublished(tmp_path, monkeypatch):
    from rea import provenance

    source = source_csv(tmp_path)
    target = tmp_path / "blocked.zip"
    visited = []

    def reject_semantics(path):
        visited.append(path)
        raise provenance.AuditError("Synthetic semantic audit failure")

    monkeypatch.setattr(provenance, "inspect_delivery", reject_semantics)
    with pytest.raises(provenance.AuditError, match="semantic audit"):
        delivery.create_delivery(source, target)
    assert len(visited) == 1
    assert visited[0].is_file() is False  # Temporary staging removed on failure
    assert not target.exists()


def test_successful_delivery_passes_full_semantic_audit(tmp_path):
    from rea.provenance import inspect_delivery

    source = source_csv(tmp_path)
    target = tmp_path / "verified.zip"
    delivery.create_delivery(source, target)
    evidence = inspect_delivery(target)
    assert evidence["delivery_integrity"] == "VERIFIED_SHA256"
    assert evidence["overall_commercial_clearance"] == "NOT_GRANTED"


@pytest.mark.parametrize("payload", [
    b'{"schema_version":"rea.delivery.v0.1","files":[],"files":[]}',
    b'{"schema_version":"rea.delivery.v0.1","files":[],"extra":{"x":1,"x":2}}',
    b'{"schema_version":"rea.delivery.v0.1","files":[],"extra":NaN}',
    b'{"schema_version":"rea.delivery.v0.1","files":[],"extra":Infinity}',
])
def test_extracted_manifest_ambiguous_fields_are_rejected(tmp_path, payload):
    root, _ = synthetic_extracted_kit(tmp_path)
    (root / "delivery_manifest.json").write_bytes(payload)
    result = inspect(root)
    assert result["status"] == "FAIL_LOCAL_PREREQUISITES"
    assert result["integrity"] == "NOT_VERIFIED"
    assert any("ValueError" in issue for issue in result["issues"])


def test_extracted_manifest_1500_levels_rejected_bounded(tmp_path):
    root, _ = synthetic_extracted_kit(tmp_path)
    payload = (b'{"schema_version":"rea.delivery.v0.1","files":[],"extra":'
               + b"[" * 1500 + b"1" + b"]" * 1500 + b"}")
    (root / "delivery_manifest.json").write_bytes(payload)
    result = inspect(root)
    assert result["status"] == "FAIL_LOCAL_PREREQUISITES"
    assert result["integrity"] == "NOT_VERIFIED"
    assert any("ValueError" in issue or "RecursionError" in issue
               for issue in result["issues"])
