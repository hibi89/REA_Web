"""Deterministic local ZIP for a verified REA-owned FastAPI/SQLite app only.

No arbitrary backend ZIP execution, URL requests, dependency install or deployment.
The ZIP includes the owner's actual local SQLite rows; treat as private.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3
import stat
import sys
import tempfile
import zipfile

from rea.adapter.local_product import MOUNT, SELF_CHECK
from rea.mvp import TEMPLATES
from rea.safe_publish import publish_archive

PREFIX = "REA_LOCAL_APP/"
DATE = (2026, 1, 1, 0, 0, 0)
MAX_BYTES = 64 * 1024 * 1024
MAX_FILE = 32 * 1024 * 1024
SHA = re.compile(r"^[a-f0-9]{64}$")
REQUIRED = frozenset("""
app.py data.sqlite requirements.txt schema_preview.json manifest.json README.md
REA_INTEGRATION_RECEIPT.json RUN_LOCAL_WINDOWS.cmd SELF_CHECK.py
static/app.js static/index.html static/style.css
dashboard/app.js dashboard/index.html dashboard/style.css
dashboard/manifest.json dashboard/README_KO.md
""".split())


class UnsafeLocalDelivery(ValueError):
    pass


def _json(data: bytes) -> dict:
    if len(data) > 128 * 1024:
        raise UnsafeLocalDelivery("oversized metadata")
    try:
        result = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise UnsafeLocalDelivery("unreadable metadata") from exc
    if not isinstance(result, dict):
        raise UnsafeLocalDelivery("invalid metadata object")
    return result


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _check(members: dict[str, bytes]) -> dict:
    contract = _json(members.get("REA_PACKAGE_FILES.json", b""))
    checksums = contract.get("files")
    if (contract.get("schema_version") != "rea.firstparty_package_files.v1"
            or not isinstance(checksums, dict)
            or set(checksums) not in (REQUIRED, REQUIRED | {"mapping_report.json"})
            or set(members) != set(checksums) | {"REA_PACKAGE_FILES.json"}):
        raise UnsafeLocalDelivery("unexpected REA package file inventory")
    total = 0
    for name, expected in checksums.items():
        path = PurePosixPath(name)
        if (path.is_absolute() or any(x in (".", "..", "") for x in path.parts)
                or "\\" in name or not isinstance(expected, str)
                or not SHA.fullmatch(expected)):
            raise UnsafeLocalDelivery("unsafe file name or checksum")
        payload = members[name]
        total += len(payload)
        if len(payload) > MAX_FILE or total > MAX_BYTES:
            raise UnsafeLocalDelivery("local package exceeds size guardrail")
        if _digest(payload) != expected:
            raise UnsafeLocalDelivery("file hash mismatch: " + name)
    original = (TEMPLATES / "app.py").read_bytes()
    if (members["app.py"] != original + MOUNT
            or members["SELF_CHECK.py"] != SELF_CHECK.encode("utf-8")):
        raise UnsafeLocalDelivery("not the exact first-party REA source/checker")
    receipt = _json(members["REA_INTEGRATION_RECEIPT.json"])
    frontend = _json(members["dashboard/manifest.json"])
    if (receipt.get("schema_version") != "rea.firstparty_local_app.v0.1"
            or receipt.get("status") != "LOCAL_APP_GENERATED_NOT_DEPLOYED"
            or receipt.get("template_sha256") != _digest(original)
            or receipt.get("frontend_manifest_sha256") != checksums["dashboard/manifest.json"]
            or receipt.get("owner_confirmed") is not True
            or receipt.get("backend_zip_executed") is not False
            or receipt.get("external_network_performed") is not False
            or receipt.get("commercial_release_allowed") is not False
            or type(receipt.get("row_count")) is not int
            or not 1 <= receipt["row_count"] <= 10000
            or frontend.get("schema_version") != "rea.frontend_bridge.v0.1"
            or frontend.get("owner_bindings_confirmed") is not True
            or frontend.get("status") != "FRONTEND_SOURCE_GENERATED_NOT_RUNTIME_VERIFIED"):
        raise UnsafeLocalDelivery("unapproved or inconsistent source provenance")
    return {"files": len(checksums), "rows": receipt["row_count"]}


def _folder(source: Path) -> dict[str, bytes]:
    source = Path(source).absolute()
    if source.is_symlink() or not source.is_dir():
        raise UnsafeLocalDelivery("regular first-party local app directory required")
    members = {}
    dirs = set()
    size = 0
    for entry in source.rglob("*"):
        if entry.is_symlink():
            raise UnsafeLocalDelivery("symlink refused")
        name = entry.relative_to(source).as_posix()
        if entry.is_dir():
            dirs.add(name)
            continue
        if not entry.is_file() or not stat.S_ISREG(entry.stat().st_mode):
            raise UnsafeLocalDelivery("non-regular file refused")
        length = entry.stat().st_size
        size += length
        if len(members) >= 21 or length > MAX_FILE or size > MAX_BYTES:
            raise UnsafeLocalDelivery("app file count/size exceeds guardrail")
        members[name] = entry.read_bytes()
    if dirs != {"static", "dashboard"}:
        raise UnsafeLocalDelivery("unexpected app subdirectories")
    _check(members)
    try:
        db_file = source / "data.sqlite"
        with sqlite3.connect(db_file.as_uri() + "?mode=ro", uri=True) as db:
            status = db.execute("PRAGMA quick_check(1)").fetchone()
            row_count = db.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        receipt = _json(members["REA_INTEGRATION_RECEIPT.json"])
        if status is None or status[0] != "ok" or row_count != receipt["row_count"]:
            raise UnsafeLocalDelivery("SQLite integrity or row count mismatch")
    except sqlite3.Error as exc:
        raise UnsafeLocalDelivery("SQLite read-only validation failed") from exc
    return members


def verify_archive(path: Path) -> dict:
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise UnsafeLocalDelivery("bounded regular ZIP required")
    members = {}
    total = 0
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if not len(REQUIRED) <= len(infos) <= 21:
                raise UnsafeLocalDelivery("invalid archive inventory size")
            for info in infos:
                name = info.filename
                mode = stat.S_IFMT((info.external_attr >> 16) & 0xFFFF)
                if (info.is_dir() or not name.startswith(PREFIX)
                        or "\\" in name or ":" in name
                        or any(x in (".", "..", "") for x in PurePosixPath(name).parts)
                        or mode not in (0, stat.S_IFREG)):
                    raise UnsafeLocalDelivery("unsafe archive member")
                relative = name[len(PREFIX):]
                if not relative or relative in members or info.file_size > MAX_FILE:
                    raise UnsafeLocalDelivery("duplicate or oversized archive member")
                total += info.file_size
                if total > MAX_BYTES:
                    raise UnsafeLocalDelivery("expanded archive exceeds guardrail")
                members[relative] = archive.read(info)
    except (zipfile.BadZipFile, OSError, RuntimeError, EOFError) as exc:
        raise UnsafeLocalDelivery("ZIP read or CRC failure") from exc
    summary = _check(members)
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return {**summary, "status": "ZIP_VERIFIED_NOT_COMMERCIAL",
            "zip_sha256": digest.hexdigest()}


def pack(app: Path, out: Path, *, owner_confirmed: bool = False) -> dict:
    if owner_confirmed is not True:
        raise UnsafeLocalDelivery("explicit owner-confirmed-packaging required")
    out = Path(out).absolute()
    if out.suffix.lower() != ".zip" or out.exists() or out.is_symlink():
        raise UnsafeLocalDelivery("choose a NEW .zip output")
    files = _folder(app)
    out.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".rea-delivery-", suffix=".zip.tmp",
                                    dir=out.parent)
    os.close(fd)
    stage = Path(tmp_name)
    try:
        with zipfile.ZipFile(stage, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6, allowZip64=False) as archive:
            for name in sorted(files):
                info = zipfile.ZipInfo(PREFIX + name, date_time=DATE)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o600) << 16
                archive.writestr(info, files[name], compress_type=zipfile.ZIP_DEFLATED,
                                 compresslevel=6)
        summary = verify_archive(stage)
        publish_archive(stage, out)
        return {**summary, "status": "ZIP_CREATED_NOT_COMMERCIAL", "output": str(out)}
    finally:
        if stage.exists():
            stage.unlink()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="REA checked first-party ZIP pack/verify")
    subs = parser.add_subparsers(dest="action", required=True)
    p = subs.add_parser("pack")
    p.add_argument("--app", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--owner-confirmed-packaging", action="store_true")
    v = subs.add_parser("verify")
    v.add_argument("--zip", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = (pack(args.app, args.out, owner_confirmed=args.owner_confirmed_packaging)
                  if args.action == "pack" else verify_archive(args.zip))
        print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    except (UnsafeLocalDelivery, ValueError, OSError) as exc:
        print("REA delivery refused: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
