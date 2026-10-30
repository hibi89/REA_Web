"""Strict synthetic ZIP-manifest parsing and file-metadata bounds."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

import pytest

from rea.delivery import DeliveryError, verify_delivery


def archive(tmp_path: Path, manifest: bytes, files: dict[str, bytes] | None = None) -> Path:
    target = tmp_path / "synthetic.zip"
    with zipfile.ZipFile(target, "x") as zf:
        for name, value in (files or {}).items():
            zf.writestr(name, value)
        zf.writestr("delivery_manifest.json", manifest)
    return target


def test_valid_minimal_manifest_still_accepted(tmp_path):
    doc = {"schema_version": "rea.delivery.v0.1", "files": []}
    assert verify_delivery(archive(tmp_path, json.dumps(doc).encode())) == doc


@pytest.mark.parametrize("payload,pattern", [
    (b'{"schema_version":"rea.delivery.v0.1","schema_version":"rea.delivery.v0.1","files":[]}', "Duplicate"),
    (b'{"schema_version":"rea.delivery.v0.1","files":[],"files":[]}', "Duplicate"),
    (b'{"schema_version":"rea.delivery.v0.1","files":[],"meta":{"x":1,"x":2}}', "Duplicate"),
    (b'{"schema_version":"rea.delivery.v0.1","files":[],"other":NaN}', "Non-finite"),
    (b'{"schema_version":"rea.delivery.v0.1","files":[],"other":Infinity}', "Non-finite"),
    (b'{"schema_version":"rea.delivery.v0.1","files":', "Malformed"),
    (b"\\xff", "Malformed"),
    (b'{"schema_version":"rea.delivery.v0.1","files":{}}', "count mismatch"),
])
def test_unsafe_or_ambiguous_manifest_fails_closed(tmp_path, payload, pattern):
    with pytest.raises(DeliveryError, match=pattern):
        verify_delivery(archive(tmp_path, payload))


@pytest.mark.parametrize("depth", [80, 1500])
def test_manifest_depth_is_bounded_to_error_not_crash(tmp_path, depth):
    payload = (b'{"schema_version":"rea.delivery.v0.1","files":[],"extra":'
               + b"[" * depth + b"1" + b"]" * depth + b"}")
    with pytest.raises(DeliveryError, match="nesting"):
        verify_delivery(archive(tmp_path, payload))


def test_manifest_over_256_kib_is_refused_before_json_parse(tmp_path):
    payload = b" " * (256 * 1024 + 1)
    with pytest.raises(DeliveryError, match="256 KiB"):
        verify_delivery(archive(tmp_path, payload))


@pytest.mark.parametrize("alteration", [
    {"bytes": True}, {"bytes": False}, {"bytes": -1},
    {"bytes": 25 * 1024 * 1024 + 1},
    {"sha256": 123}, {"sha256": "short"},
])
def test_invalid_member_metadata_rejected_even_if_zip_crc_valid(tmp_path, alteration):
    raw = b"x"
    row = {"path": "README_WINDOWS.md", "bytes": 1,
           "sha256": hashlib.sha256(raw).hexdigest()}
    row.update(alteration)
    doc = {"schema_version": "rea.delivery.v0.1", "files": [row]}
    target = archive(tmp_path, json.dumps(doc).encode(), {"README_WINDOWS.md": raw})
    with pytest.raises(DeliveryError, match="Invalid manifest entry"):
        verify_delivery(target)
