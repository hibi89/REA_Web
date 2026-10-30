"""Windows ZIP path / symlink hardening of the delivery verifier."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import stat
import zipfile

import pytest

from rea.delivery import DeliveryError, _safe, verify_delivery


@pytest.mark.parametrize("bad", [
    "app/CON", "app/con.txt", "app/PRN.log", "app/AUX", "app/NUL.db",
    "app/COM1.csv", "app/lpt9.log", "app/a:alternate",
    "app/trailing.", "app/trailing ", "app//empty", "app/../escape",
])
def test_reject_windows_unsafe_members(bad):
    assert not _safe(bad)


@pytest.mark.parametrize("good", [
    "app/data.sqlite", "app/static/index.html", "README_WINDOWS.md",
    "app/console.txt", "app/CATALOG.csv",
])
def test_allow_normal_windows_files(good):
    assert _safe(good)


def _archive(path: Path, member: str, *, link: bool) -> None:
    contents = b"synthetic fixture only"
    record = {
        "schema_version": "rea.delivery.v0.1",
        "files": [{
            "path": member,
            "bytes": len(contents),
            "sha256": hashlib.sha256(contents).hexdigest(),
        }],
    }
    with zipfile.ZipFile(path, "w") as archive:
        info = zipfile.ZipInfo(member)
        info.create_system = 3
        info.external_attr = (
            (stat.S_IFLNK | 0o777) << 16 if link
            else (stat.S_IFREG | 0o644) << 16
        )
        archive.writestr(info, contents)
        archive.writestr("delivery_manifest.json", json.dumps(record))


def test_rehashed_symlink_zip_entry_still_rejected(tmp_path):
    archive = tmp_path / "symlink.zip"
    _archive(archive, "app/static/executable.txt", link=True)
    with pytest.raises(DeliveryError, match="symlink"):
        verify_delivery(archive)


def test_rehashed_windows_special_path_rejected(tmp_path):
    archive = tmp_path / "colon.zip"
    _archive(archive, "app/innocent:stream", link=False)
    with pytest.raises(DeliveryError, match="Unsafe"):
        verify_delivery(archive)


def test_normal_regular_entry_keeps_manifest_check(tmp_path):
    archive = tmp_path / "normal.zip"
    _archive(archive, "app/static/normal.txt", link=False)
    result = verify_delivery(archive)
    assert result["files"][0]["path"] == "app/static/normal.txt"


@pytest.mark.parametrize("bad", [
    "app/<invalid>.txt", 'app/"quoted".json', "app/pipe|name",
    "app/question?.csv", "app/star*.txt", "app/control\\x01name",
    "app/CONIN$", "app/conout$.txt",
])
def test_windows_forbidden_characters_and_additional_devices(bad):
    assert not _safe(bad)


def test_casefold_collision_is_rejected_even_when_hashes_match(tmp_path):
    archive = tmp_path / "case_collision.zip"
    names = ["app/data/Items.csv", "app/data/items.CSV"]
    payload = b"synthetic collision fixture"
    records = [
        {"path": name, "bytes": len(payload),
         "sha256": hashlib.sha256(payload).hexdigest()}
        for name in names
    ]
    with zipfile.ZipFile(archive, "w") as zf:
        for name in names:
            zf.writestr(name, payload)
        zf.writestr("delivery_manifest.json", json.dumps({
            "schema_version": "rea.delivery.v0.1", "files": records,
        }))
    with pytest.raises(DeliveryError, match="duplicate"):
        verify_delivery(archive)
