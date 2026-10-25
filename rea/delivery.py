"""Deterministic local delivery ZIP for an offline generated REA app.

Packages generated app and launch instructions. Never includes Fable original
capture or upstream vendor engine. This is not a commercial release gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

from rea.orchestrator import build

SCHEMA = "rea.delivery.v0.1"
FIXED_DATE = (2026, 1, 1, 0, 0, 0)
MAX_ARCHIVE_BYTES = 25 * 1024 * 1024
LAUNCH = "\r\n".join([
    "@echo off",
    "setlocal",
    'cd /d "%~dp0app"',
    "if errorlevel 1 exit /b 1",
    "if not defined REA_WEB_PORT set REA_WEB_PORT=8000",
    'python -m uvicorn app:app --host 127.0.0.1 --port %REA_WEB_PORT%',
    "endlocal",
    "",
])
WINDOWS_README = """# REA_Web v0.9 local delivery: Windows guide

This ZIP contains a locally generated read-only FastAPI/SQLite app.
No live customer database, Fable scanner, external AI, payment or login.
Use only authorized and non-sensitive CSV/JSON sample data.

1. Install Python 3.11 or later with python.exe on PATH.
2. Extract the entire ZIP to a NEW local folder.
3. Open Command Prompt in the extracted folder.
4. Run: python -m pip install -r app\\requirements.txt
   Internet may be required for installing packages; runtime is local only.
5. Run: launch_windows.cmd
6. Open: http://127.0.0.1:8000/
7. Press Ctrl+C to stop. If 8000 is occupied:
   set REA_WEB_PORT=8765
   launch_windows.cmd
   Open http://127.0.0.1:8765/

SQLite is a snapshot, not live synchronization. The archive file list and
SHA256 hashes are in delivery_manifest.json. Optional review/fable_review.json
is NOT an approved owner mapping and is not accessible from the web app.
Never expose this server to the public Internet or load sensitive data.

Known exclusions: live URL capture, cloning, production DB, user accounts,
wizard, custom mapping approval, aggregates, CRUD, hosting, licensing clearance.
"""


class DeliveryError(ValueError):
    pass


def _zipinfo(name: str) -> zipfile.ZipInfo:
    item = zipfile.ZipInfo(name, FIXED_DATE)
    item.compress_type = zipfile.ZIP_DEFLATED
    item.external_attr = 0o100644 << 16
    item.create_system = 3
    return item


def _safe(name: str) -> bool:
    parts = name.split("/")
    return bool(name and len(name) <= 260 and not name.startswith("/")
                and "\\" not in name and all(p not in ("", ".", "..") for p in parts)
                and not any(p.startswith(".") or p == "__pycache__" for p in parts))


def _members(project: Path) -> dict[str, bytes]:
    members: dict[str, bytes] = {}
    for path in project.rglob("*"):
        if path.is_symlink():
            raise DeliveryError("Symlink in delivery output prohibited")
        if not path.is_file():
            continue
        rel = "app/" + path.relative_to(project).as_posix()
        if not _safe(rel):
            raise DeliveryError("Unsafe ZIP member")
        if path.stat().st_size > MAX_ARCHIVE_BYTES:
            raise DeliveryError("A generated file exceeds size limit")
        members[rel] = path.read_bytes()
    members["README_WINDOWS.md"] = WINDOWS_README.encode("utf-8")
    members["launch_windows.cmd"] = LAUNCH.encode("ascii")
    if sum(len(x) for x in members.values()) > MAX_ARCHIVE_BYTES:
        raise DeliveryError("Delivery exceeds 25 MiB")
    required = ("app/app.py", "app/data.sqlite", "app/requirements.txt",
                "app/manifest.json", "app/static/index.html",
                "app/static/app.js", "app/static/style.css")
    if any(x not in members for x in required):
        raise DeliveryError("Incomplete generated app")
    return members


def _manifest(members: dict[str, bytes]) -> dict:
    return {
        "schema_version": SCHEMA, "product": "REA_Web local synthetic MVP v0.9",
        "status": "REVIEW_ONLY_NOT_COMMERCIALLY_APPROVED",
        "runtime_binding": "127.0.0.1",
        "windows_native_validated_by_exporter": False,
        "raw_fable_capture_bundled": False,
        "vendor_engines_bundled": False,
        "files": [
            {"path": name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
            for name, data in sorted(members.items())
        ],
    }


def verify_delivery(archive: Path) -> dict:
    """Validate ZIP members and SHA256 (does not execute them)."""
    with zipfile.ZipFile(archive, "r") as zf:
        info = zf.infolist()
        names = [item.filename for item in info]
        if len(names) > 100 or len(names) != len(set(names)) or any(not _safe(n) for n in names):
            raise DeliveryError("Unsafe or duplicate ZIP member")
        if "delivery_manifest.json" not in names:
            raise DeliveryError("Missing manifest")
        if sum(item.file_size for item in info) > MAX_ARCHIVE_BYTES:
            raise DeliveryError("ZIP contents too large")
        doc = json.loads(zf.read("delivery_manifest.json").decode("utf-8"))
        if doc.get("schema_version") != SCHEMA:
            raise DeliveryError("Unsupported manifest")
        rows = doc.get("files")
        if not isinstance(rows, list) or len(rows) != len(names) - 1:
            raise DeliveryError("Manifest file count mismatch")
        expected = {}
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("path"), str) or row["path"] in expected:
                raise DeliveryError("Invalid manifest entry")
            expected[row["path"]] = row
        if set(expected) != set(names) - {"delivery_manifest.json"}:
            raise DeliveryError("Manifest member mismatch")
        for name, row in expected.items():
            data = zf.read(name)
            if len(data) != row.get("bytes") or hashlib.sha256(data).hexdigest() != row.get("sha256"):
                raise DeliveryError("Checksum mismatch: " + name)
        return doc


def create_delivery(csv_file: Path, output_zip: Path, name: str = "REA local app",
                    *, fable_result: Path | None = None,
                    astra_root: Path | None = None) -> dict:
    csv_file, output_zip = Path(csv_file), Path(output_zip).absolute()
    if output_zip.exists() or output_zip.is_symlink():
        raise FileExistsError("Output archive already exists: " + str(output_zip))
    if output_zip.suffix.lower() != ".zip":
        raise DeliveryError("Output must end with .zip")
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".rea-export-", dir=output_zip.parent) as temp:
        work = Path(temp)
        project = work / "app"
        build(csv_file, project, name, fable_result=fable_result, astra_root=astra_root)
        members = _members(project)
        manifest = _manifest(members)
        members["delivery_manifest.json"] = (
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        ).encode("utf-8")
        stage = work / "ready.zip"
        with zipfile.ZipFile(stage, "x", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9, allowZip64=False) as zf:
            for filename, data in sorted(members.items()):
                zf.writestr(_zipinfo(filename), data, compress_type=zipfile.ZIP_DEFLATED,
                            compresslevel=9)
        verify_delivery(stage)
        with output_zip.open("xb") as target:
            try:
                with stage.open("rb") as source:
                    shutil.copyfileobj(source, target)
            except Exception:
                target.close()
                output_zip.unlink(missing_ok=True)
                raise
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create/verify offline REA delivery ZIP")
    sub = parser.add_subparsers(dest="command", required=True)
    pack = sub.add_parser("pack")
    source = pack.add_mutually_exclusive_group(required=True)
    source.add_argument("--csv", type=Path)
    source.add_argument("--json", type=Path)
    pack.add_argument("--out", required=True, type=Path)
    pack.add_argument("--name", default="REA local app")
    pack.add_argument("--fable-result", type=Path)
    pack.add_argument("--astra-root", type=Path)
    check = sub.add_parser("verify")
    check.add_argument("--zip", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = (create_delivery(args.csv or args.json, args.out, args.name,
                    fable_result=args.fable_result, astra_root=args.astra_root)
                  if args.command == "pack" else verify_delivery(args.zip))
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
