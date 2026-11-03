"""Generate a runnable, first-party-only REA local app with a reviewed dashboard.

This is NOT a general customer backend ZIP installer/runner. The backend is
generated from REA's OWN checked-in read-only FastAPI template and a permitted
local CSV/flat JSON. No arbitrary ZIP member, Fable script, or external URL is
ever executed/fetched. Publication is atomic and refuses existing output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import zipfile

from rea.adapter.backend_zip import inspect_backend_zip, UnsafeBackendZip
from rea.adapter.backend_schema import inspect_backend_schema, UnsafeSchema
from rea.adapter.frontend_bridge import (
    BridgeError, _read_json, make_review, generate_frontend,
)
from rea.mvp import (
    DataError, TEMPLATES, generate as generate_catalog, source_sha256,
)
from rea.safe_publish import publish_directory

SCHEMA = "rea.firstparty_local_app.v0.1"

# Preflight and start ONLY the REA-owned local generated app.
# No pip install, no URL open, no hostname override, no public binding.
WINDOWS_CMD = "\r\n".join([
    "@echo off",
    "setlocal EnableExtensions DisableDelayedExpansion",
    "chcp 65001 >nul",
    'cd /d "%~dp0" || exit /b 2',
    'call python -c "import sys,fastapi,uvicorn;sys.exit(0 if sys.version_info[:2]>=(3,11) else 1)" >nul 2>nul',
    "if not errorlevel 1 goto use_python",
    'call py -3 -c "import sys,fastapi,uvicorn;sys.exit(0 if sys.version_info[:2]>=(3,11) else 1)" >nul 2>nul',
    "if not errorlevel 1 goto use_py",
    "echo [REA] Python 3.11+, FastAPI and Uvicorn required. See README.md. Nothing installed.",
    "exit /b 10",
    ":use_python",
    'if /I "%~1"=="--check" goto ok_check',
    'if not "%~1"=="" goto bad_arg',
    "echo [REA] Local only: http://127.0.0.1:8000/dashboard/",
    "call python -m uvicorn app:app --host 127.0.0.1 --port 8000",
    "exit /b %ERRORLEVEL%",
    ":use_py",
    'if /I "%~1"=="--check" goto ok_check',
    'if not "%~1"=="" goto bad_arg',
    "echo [REA] Local only: http://127.0.0.1:8000/dashboard/",
    "call py -3 -m uvicorn app:app --host 127.0.0.1 --port 8000",
    "exit /b %ERRORLEVEL%",
    ":ok_check",
    "echo [REA] Python, FastAPI, Uvicorn present. App/data integrity NOT checked.",
    "exit /b 0",
    ":bad_arg",
    "echo [REA] Usage: RUN_LOCAL_WINDOWS.cmd [--check]",
    "exit /b 2",
    "",
]).encode("utf-8")


# Added ONLY to a new generated copy; never modifies repo-owned template
# or imports/extracts/executes any customer-provided backend ZIP.
MOUNT = b'\n# REA-owned local dashboard, served on the same origin as the read-only API.\n' \
        b'app.mount("/dashboard", StaticFiles(directory=ROOT / "dashboard", html=True), name="rea-dashboard")\n'


def build(data: Path, fable: Path, bindings: Path, destination: Path, *,
          app_name: str = "REA local app", visual: Path | None = None,
          mapping: Path | None = None, owner_authorized_data: bool = False,
          owner_confirmed: bool = False, expected_source_sha256: str | None = None) -> dict:
    """Create a locally runnable first-party FastAPI/SQLite + frontend package.

    The signed-off mapping covers data semantics AND exact three GET bindings.
    The data source and Fable observation must already be lawfully obtained;
    two booleans indicate human confirmation, not proof of ownership.
    """
    if not owner_authorized_data or not owner_confirmed:
        raise BridgeError("owner-authorized-data and owner-confirmed required before reading owner data")
    target = Path(destination).absolute()
    if target.exists() or target.is_symlink():
        raise FileExistsError("output exists; choose a NEW local app directory")
    source = Path(data).absolute()
    baseline_sha = source_sha256(source)
    if expected_source_sha256 is not None and baseline_sha != expected_source_sha256:
        raise DataError("owner data changed since approved SHA")
    # Inputs are validated before any output publication. Fields are selected
    # by the owner; backend GET semantics remain tied to the first-party source.
    fable_data = _read_json(fable)
    binding_data = _read_json(bindings)
    visual_data = _read_json(visual) if visual is not None else None
    owner_mapping = _read_json(mapping) if mapping is not None else None
    original = (TEMPLATES / "app.py").read_bytes()
    original_sha = hashlib.sha256(original).hexdigest()

    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".rea-integrated-", dir=target.parent) as temp:
        scratch = Path(temp)
        # Construct and statically inspect only this checked-in REA template.
        # There is no arbitrary backend ZIP argument to this function.
        own_zip = scratch / "rea_firstparty_template.zip"
        with zipfile.ZipFile(own_zip, "w") as archive:
            info = zipfile.ZipInfo("app.py", date_time=(2026, 1, 1, 0, 0, 0))
            archive.writestr(info, original)
        declared = inspect_backend_zip(own_zip)
        typed = inspect_backend_schema(own_zip)
        review = make_review(fable_data, declared, binding_data,
                             visual=visual_data, schema=typed)

        folder = scratch / "local_app"
        manifest = generate_catalog(source, folder, app_name,
                                    approved_mapping=owner_mapping,
                                    expected_source_sha256=baseline_sha)
        output_app = folder / "app.py"
        if output_app.read_bytes() != original:
            raise BridgeError("generated first-party backend template mismatch")
        generated = generate_frontend(review, folder / "dashboard",
                                      owner_confirmed=True)
        # Do not replace/patch upstream or consume unknown backend ZIP code.
        # Add the single constant trusted mount to this newly generated copy.
        output_app.write_bytes(original + MOUNT)
        if source_sha256(source) != baseline_sha:
            raise DataError("owner data changed before integrated app publication")
        (folder / "README.md").write_text(
            (folder / "README.md").read_text(encoding="utf-8")
            + "\n## Integrated original REA dashboard\n\n"
            + "With Python 3.11+ and the declared requirements installed, "
              "run from this NEW folder:\n\n"
            + "    python -m uvicorn app:app --host 127.0.0.1 --port 8000\n\n"
            + "Open http://127.0.0.1:8000/dashboard/ for the reviewed dashboard; "
              "http://127.0.0.1:8000/ retains the previous app.\n"
            + "On Windows, RUN_LOCAL_WINDOWS.cmd --check validates installed Python/FastAPI/Uvicorn; "
              "double-click RUN_LOCAL_WINDOWS.cmd to launch localhost only. "
              "The check does not validate app data or replace live HTTP acceptance.\n"
            + "No internet exposure or customer authentication is provided. "
              "All CSV/JSON values are stored in local data.sqlite; "
              "keep this folder private. This package is NOT commercially approved.\n",
            encoding="utf-8",
        )
        receipt = {
            "schema_version": SCHEMA,
            "status": "LOCAL_APP_GENERATED_NOT_DEPLOYED",
            "owner_confirmed": True,
            "runtime_verified": False,
            "customer_auth_verified": False,
            "commercial_release_allowed": False,
            "backend_zip_executed": False,
            "external_network_performed": False,
            "source_sha256": baseline_sha,
            "template_sha256": original_sha,
            "static_backend_sha256": declared["input"]["sha256"],
            "frontend_manifest_sha256": hashlib.sha256(
                (folder / "dashboard" / "manifest.json").read_bytes()).hexdigest(),
            "row_count": manifest["rows"],
            "frontend_path": "/dashboard/",
            "backend_modified_in_repository": False,
            "run": "python -m uvicorn app:app --host 127.0.0.1 --port 8000",
        }
        (folder / "RUN_LOCAL_WINDOWS.cmd").write_bytes(WINDOWS_CMD)
        (folder / "REA_INTEGRATION_RECEIPT.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        publish_directory(folder, target)
    return receipt


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build runnable REA-owned local backend + reviewed dashboard")
    p.add_argument("--data", type=Path, required=True, help="local owner CSV/flat JSON")
    p.add_argument("--fable", type=Path, required=True, help="previously saved, authorized Fable JSON")
    p.add_argument("--bindings", type=Path, required=True, help="owner-approved first-party API mapping JSON")
    p.add_argument("--visual", type=Path, help="optional authorized saved visual hints")
    p.add_argument("--mapping", type=Path, help="optional explicit id/title/category source mapping")
    p.add_argument("--out", type=Path, required=True, help="NEW standalone local app folder")
    p.add_argument("--name", default="REA local app", help="bounded app title")
    p.add_argument("--expected-source-sha256", help="optional exact approved owner input digest")
    p.add_argument("--owner-authorized-data", action="store_true")
    p.add_argument("--owner-confirmed", action="store_true")
    args = p.parse_args(argv)
    try:
        receipt = build(args.data,args.fable,args.bindings,args.out,
                        app_name=args.name, visual=args.visual, mapping=args.mapping,
                        owner_authorized_data=args.owner_authorized_data,
                        owner_confirmed=args.owner_confirmed,
                        expected_source_sha256=args.expected_source_sha256)
        print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (BridgeError, DataError, UnsafeBackendZip, UnsafeSchema,
            OSError, ValueError, TypeError) as exc:
        print("REA integrated local app refused: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
