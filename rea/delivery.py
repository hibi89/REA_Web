"""Deterministic local delivery ZIP for an offline generated REA app.

Packages generated app and launch instructions. Never includes Fable original
capture or upstream vendor engine. This is not a commercial release gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

from rea.orchestrator import build
from rea.safe_publish import publish_archive

SCHEMA = "rea.delivery.v0.1"
FIXED_DATE = (2026, 1, 1, 0, 0, 0)
MAX_ARCHIVE_BYTES = 25 * 1024 * 1024
LAUNCH = "\r\n".join([
    "@echo off",
    "setlocal EnableExtensions DisableDelayedExpansion",
    "rem Fixed local Python launcher. Never expand a user-controlled port in CMD.",
    'python "%~dp0self_check.py" --launch',
    "exit /b %errorlevel%",
    "",
])
CHECK_LAUNCH = "\r\n".join([
    "@echo off",
    "setlocal",
    'python "%~dp0self_check.py"',
    "exit /b %errorlevel%",
    "",
])
WINDOWS_README = """# REA_Web D10 synthetic local delivery (NOT commercially approved)

This package contains generated local readonly FastAPI + SQLite source and a
synthetic dataset. It is not a standalone exe and never includes Python itself.
Python 3.11+ and Python packages are required. No admin required for the check.

1. Extract the entire ZIP to a NEW EMPTY folder on a writable local disk.
   The checker rejects ANY extra/unlisted files and directories, including
   hidden or executable additions, inside the extracted delivery. Do not run
   unfamiliar files. Re-extract the trusted ZIP into another clean folder if
   this check fails. The app launcher prevents local Python bytecode cache
   creation so later prerequisite checks remain repeatable.
2. In Windows File Explorer double-click check_windows.cmd (or from CMD run it).
   If it reports missing FastAPI/Uvicorn, open CMD in this folder and choose
   whether to run: python -m pip install --user -r app\\requirements.txt
   Package installation might need Internet; only the running app is local.
3. Run check_windows.cmd again; PASS checks files, SQLite and environment only.
4. Run launch_windows.cmd and visit http://127.0.0.1:8000/
   It verifies the local delivery files and prerequisites BEFORE starting
   the server. Python invokes Uvicorn with a fixed loopback host and a
   validated numeric port; the CMD file never expands REA_WEB_PORT.
5. Ctrl+C stops server. If port 8000 is taken, in Command Prompt type:
   set REA_WEB_PORT=8765
   launch_windows.cmd
   Open http://127.0.0.1:8765/
   Allowed port values are ASCII digits 1..65535 without leading zeros.
   Invalid/unsafe text stops before launching Python web server and
   does NOT run it as an OS shell command.

If 'python' is not recognized, install official Python 3.11+ for your user,
enable PATH, reopen CMD and repeat. Never run as administrator just for REA.
No files are uploaded by the self-check. Do not run from the Internet.
The app only binds 127.0.0.1 by default; never expose it with --host 0.0.0.0.

Supported generator types: one CSV or flat JSON with required fields;
owner-guided one-file field approval; strictly owner-confirmed same-schema
two-input ROW APPEND only (not SQL joins or cross-table relational mapping).
These modes generate the source before ZIP delivery. They are not a GUI.

No automatic backup, user login, payment, browser cloning, hosting, migration
or real-time data synchronization. app/data.sqlite contains input rows and may
contain sensitive information. Never share real customer ZIPs publicly.
The SHA256 check is not a digital signature or rights check. Source rights,
third-party licensing, security, privacy and clean Windows human acceptance
have NOT been cleared. Contact product owner for support and permissions.
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
    members["check_windows.cmd"] = CHECK_LAUNCH.encode("ascii")
    members["self_check.py"] = (Path(__file__).resolve().parent / "customer_self_check.py").read_bytes()
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
                    astra_root: Path | None = None,
                    approved_mapping: dict[str, str] | None = None,
                    expected_source_sha256: str | None = None) -> dict:
    csv_file, output_zip = Path(csv_file), Path(output_zip).absolute()
    if output_zip.exists() or output_zip.is_symlink():
        raise FileExistsError("Output archive already exists: " + str(output_zip))
    if output_zip.suffix.lower() != ".zip":
        raise DeliveryError("Output must end with .zip")
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".rea-export-", dir=output_zip.parent) as temp:
        work = Path(temp)
        project = work / "app"
        build(csv_file, project, name, fable_result=fable_result, astra_root=astra_root,
              approved_mapping=approved_mapping,
              expected_source_sha256=expected_source_sha256)
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
        publish_archive(stage, output_zip)
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
