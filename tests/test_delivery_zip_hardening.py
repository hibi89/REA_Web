"""Windows ZIP path / symlink hardening of the delivery verifier."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import stat
import sys
import zipfile

import pytest

from rea.delivery import DeliveryError, _member_paths_conflict, _members, _safe, verify_delivery
from rea.customer_self_check import _safe_member, inspect


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
    "app/question?.csv", "app/star*.txt", "app/control\x01name",
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


@pytest.mark.parametrize("name", [
    "app/<bad>.txt", "app/questions?.txt", "app/CONIN$",
    "app/NUL.log", "app/trailing.", "app/control\\x01name",
    "app/valid\\bad", "app/sub/../escape", "app/pipe|name",
])
def test_extracted_preflight_matches_exporter_path_policy(name):
    assert not _safe(name)
    assert not _safe_member(name)


@pytest.mark.parametrize("name", [
    "app/static/index.html", "app/catalog.csv", "README_WINDOWS.md",
])
def test_extracted_preflight_allows_exporter_normal_names(name):
    assert _safe(name)
    assert _safe_member(name)


@pytest.mark.skipif(sys.platform == "win32", reason="Windows itself cannot create case-clashing files")
def test_exporter_refuses_case_colliding_files_before_zip_publish(tmp_path):
    project = tmp_path / "app"
    project.mkdir()
    (project / "Items.csv").write_text("synthetic", encoding="utf-8")
    (project / "items.CSV").write_text("synthetic", encoding="utf-8")
    with pytest.raises(DeliveryError, match="collision"):
        _members(project)


@pytest.mark.parametrize("payload", ["[]", "null", '"string"', "123"])
def test_nonobject_manifest_is_bounded_failure(tmp_path, payload):
    archive = tmp_path / "malformed_manifest.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("delivery_manifest.json", payload)
    with pytest.raises(DeliveryError, match="Invalid manifest object"):
        verify_delivery(archive)


@pytest.mark.parametrize("payload", ["[]", "null", '"string"', "123"])
def test_customer_preflight_handles_nonobject_manifest_without_traceback(tmp_path, payload):
    (tmp_path / "delivery_manifest.json").write_text(payload, encoding="utf-8")
    report = inspect(tmp_path)
    assert report["integrity"] == "NOT_VERIFIED"
    assert report["status"] == "FAIL_LOCAL_PREREQUISITES"
    assert any("ValueError" in issue for issue in report["issues"])


@pytest.mark.parametrize("device", [
    "COM¹", "COM²", "COM³", "LPT¹", "LPT²", "LPT³",
])
def test_windows_superscript_device_names_are_rejected(tmp_path, device):
    """Windows recognizes Latin-1 superscript digits as COM/LPT device digits."""
    for name in (f"app/{device}", f"app/{device.lower()}.txt"):
        assert not _safe(name)
        assert not _safe_member(name)
    archive = tmp_path / "superscript_device.zip"
    _archive(archive, f"app/{device}.txt", link=False)
    with pytest.raises(DeliveryError, match="Unsafe"):
        verify_delivery(archive)


@pytest.mark.parametrize("names", [
    ["app/Foo", "app/foo/child.txt"],
    ["app/data", "app/data/items.csv"],
    ["app/a/B", "app/A/b/c.txt"],
])
def test_reject_parent_file_conflict_in_zip(tmp_path, names):
    payload = b"synthetic file-directory conflict"
    path = tmp_path / "conflicting_paths.zip"
    rows = [{"path": n, "bytes": len(payload),
             "sha256": hashlib.sha256(payload).hexdigest()} for n in names]
    with zipfile.ZipFile(path, "w") as zf:
        for name in names:
            zf.writestr(name, payload)
        zf.writestr("delivery_manifest.json", json.dumps({
            "schema_version": "rea.delivery.v0.1", "files": rows,
        }))
    assert _member_paths_conflict(names)
    with pytest.raises(DeliveryError, match="Unsafe"):
        verify_delivery(path)


def test_valid_nested_package_paths_remain_accepted():
    assert not _member_paths_conflict([
        "app/data.sqlite", "app/static/index.html",
        "app/static/app.js", "README_WINDOWS.md",
    ])


@pytest.mark.skipif(sys.platform == "win32", reason="Windows filesystem prohibits the fixture")
def test_exporter_refuses_case_insensitive_parent_file_conflict(tmp_path):
    project = tmp_path / "app"
    project.mkdir()
    (project / "Foo").write_bytes(b"synthetic parent")
    (project / "foo").mkdir()
    (project / "foo" / "child.txt").write_bytes(b"synthetic child")
    with pytest.raises(DeliveryError, match="collision"):
        _members(project)
