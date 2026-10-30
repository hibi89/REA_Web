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
