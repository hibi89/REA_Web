"""Deterministic, no-execution project archive for a manually trusted synthetic FastAPI fixture.

This first packaging unit is NOT an arbitrary customer ZIP runner. Source archive
and generated frontend are only read. A synthetic owner confirmation, source
SHA, reviewed route contract and manually supplied OpenAPI reconciliation are
required. Packaging never imports or launches backend code. The extracted demo
has a separate explicit local-run guard and no auto-install/deployment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import zipfile

from rea.adapter.backend_zip import _zip_members, inspect_backend_zip
from rea.adapter.frontend_bridge import (HTML as GENERATED_HTML, JS as GENERATED_JS,
                                         CSS as GENERATED_CSS, BridgeError,
                                         _valid_bindings, _js_config)
from rea.safe_publish import publish_archive

SCHEMA = "rea.project_bundle.v0.1"
FRONTEND_SCHEMA = "rea.frontend_bridge.v0.1"
RECONCILIATION_SCHEMA = "rea.runtime_reconciliation.v0.1"
REQUIRED_FRONTEND = ("index.html", "app.js", "style.css", "manifest.json", "README_KO.md")
OPTIONAL_BACKEND = ("requirements.txt", "README_KO.md")
MAX_FRONTEND_FILE = 1024 * 1024
SHA = re.compile(r"^[a-f0-9]{64}$")
FIXED_DATE = (2026, 1, 1, 0, 0, 0)


class UnsafeProjectBundle(ValueError):
    """Unsupported fixture or missing, unapproved, unverified assembly inputs."""


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(data: object) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _check_frontend(folder: Path, backend_sha: str) -> tuple[dict[str, bytes], dict]:
    if folder.is_symlink() or not folder.is_dir():
        raise UnsafeProjectBundle("frontend must be a real directory")
    actual = {x.name for x in folder.iterdir()}
    if actual != set(REQUIRED_FRONTEND):
        raise UnsafeProjectBundle("frontend file inventory mismatch")
    contents: dict[str, bytes] = {}
    for name in REQUIRED_FRONTEND:
        f = folder / name
        if f.is_symlink() or not f.is_file() or not stat.S_ISREG(f.stat().st_mode):
            raise UnsafeProjectBundle("frontend contains nonregular file")
        if f.stat().st_size > MAX_FRONTEND_FILE:
            raise UnsafeProjectBundle("oversized frontend file")
        contents[f"dashboard/{name}"] = f.read_bytes()
    try:
        data = json.loads(contents["dashboard/manifest.json"].decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise UnsafeProjectBundle("invalid frontend manifest") from exc
    if (not isinstance(data, dict) or data.get("schema_version") != FRONTEND_SCHEMA
            or data.get("status") != "FRONTEND_SOURCE_GENERATED_NOT_RUNTIME_VERIFIED"
            or data.get("owner_bindings_confirmed") is not True
            or data.get("backend_modified") is not False
            or data.get("frontend_path") != "/dashboard/"):
        raise UnsafeProjectBundle("unapproved frontend manifest")
    backend = data.get("backend")
    if not isinstance(backend, dict) or backend.get("sha256") != backend_sha:
        raise UnsafeProjectBundle("frontend/backend SHA mismatch")
    bindings = data.get("bindings")
    if not isinstance(bindings, dict) or not all(
        isinstance(bindings.get(k), dict) and isinstance(bindings[k].get("path"), str)
        for k in ("list", "metrics", "detail")
    ):
        raise UnsafeProjectBundle("frontend bindings unavailable")
    # A manifest can be rewritten alongside a modified app.js. The packaging
    # boundary must independently verify the published frontend sources, not
    # merely the names, SHA of the backend, or owner confirmation metadata.
    try:
        reviewed = _valid_bindings(bindings)
    except BridgeError as exc:
        raise UnsafeProjectBundle("invalid frontend mapping") from exc
    if reviewed != bindings:
        raise UnsafeProjectBundle("frontend mapping not canonical")
    expected_js = (GENERATED_JS.replace("__API_JSON__", _js_config(reviewed)) + "\n").encode("utf-8")
    if contents["dashboard/app.js"] != expected_js:
        raise UnsafeProjectBundle("frontend JavaScript differs from approved generator")
    if contents["dashboard/index.html"] != (GENERATED_HTML + "\n").encode("utf-8"):
        raise UnsafeProjectBundle("frontend HTML differs from approved generator")
    # For neutral dashboards, the stylesheet is also deterministic. A visually
    # observed palette/layout has legitimate additional CSS; it is not treated
    # as signed proof and requires a separate visual evidence review.
    reference = data.get("reference")
    if not isinstance(reference, dict):
        raise UnsafeProjectBundle("frontend reference metadata absent")
    if reference.get("visual_sha256") is None:
        if contents["dashboard/style.css"] != (GENERATED_CSS + "\n").encode("utf-8"):
            raise UnsafeProjectBundle("neutral frontend CSS differs from approved generator")
    return contents, data


def _backend_contents(source: Path) -> tuple[dict[str, bytes], str]:
    """This fixture-only packaging profile permits exactly app.py and two docs.

    Reject every unexpected member, including dotfiles/secrets, rather than
    silently copying all of an arbitrary ZIP into a runnable output.
    """
    static = inspect_backend_zip(source)  # Uses existing archive limits and member defenses.
    digest = static["input"]["sha256"]
    with zipfile.ZipFile(source) as archive:
        infos = _zip_members(archive)
        allowed = {"app.py", *OPTIONAL_BACKEND}
        observed = {item.filename for item in infos}
        if "app.py" not in observed or not observed.issubset(allowed):
            raise UnsafeProjectBundle("fixture profile only permits app.py and documentation")
        contents = {f"backend/{i.filename}": archive.read(i) for i in infos}
    if _hash(source.read_bytes()) != digest:
        raise UnsafeProjectBundle("source changed during packaging")
    if len(contents["backend/app.py"]) > MAX_FRONTEND_FILE:
        raise UnsafeProjectBundle("backend app.py exceeds fixture profile limit")
    return contents, digest


RUNNER = '''"""Only run the self-authored, owner-confirmed synthetic test fixture."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True  # Keep a clean extracted artifact for integrity checks.

ROOT = Path(__file__).resolve().parent
EXPECTED_APP_SHA = "__EXPECTED_APP_SHA__"


def check():
    source = ROOT / "backend" / "app.py"
    if source.is_symlink() or not source.is_file():
        raise RuntimeError("backend/app.py missing or symbolic link")
    if hashlib.sha256(source.read_bytes()).hexdigest() != EXPECTED_APP_SHA:
        raise RuntimeError("backend source has changed; execution refused")
    dashboard = ROOT / "dashboard"
    if not dashboard.is_dir() or not (dashboard / "index.html").is_file():
        raise RuntimeError("dashboard missing")
    checks = json.loads((ROOT / "SHA256SUMS.json").read_text(encoding="utf-8"))
    if not isinstance(checks, dict) or not 1 <= len(checks) <= 50:
        raise RuntimeError("invalid SHA256SUMS")
    for name, sha in checks.items():
        part = Path(name)
        if (not isinstance(name, str) or part.is_absolute()
                or any(c in (".", "..") for c in part.parts)
                or not isinstance(sha, str) or len(sha) != 64):
            raise RuntimeError("unsafe SHA256SUMS")
        member = ROOT / part
        if member.is_symlink() or not member.is_file():
            raise RuntimeError("missing or symbolic-link package member")
        if hashlib.sha256(member.read_bytes()).hexdigest() != sha:
            raise RuntimeError("package content changed; execution refused")
    return True


def main(argv=None):
    p = argparse.ArgumentParser(description="REA local synthetic backend + dashboard")
    p.add_argument("--check", action="store_true")
    p.add_argument("--run-trusted-synthetic", action="store_true")
    p.add_argument("--port", type=int, default=8766)
    args = p.parse_args(argv)
    if args.check == args.run_trusted_synthetic or not (1024 <= args.port <= 65535):
        p.error("choose --check OR --run-trusted-synthetic and a nonprivileged port")
    try:
        check()
    except Exception as exc:
        print("[REA] REFUSED:", str(exc), file=sys.stderr)
        return 2
    if args.check:
        print("[REA] SOURCE_HASH_AND_DASHBOARD_PRESENT (not runtime verification)")
        return 0
    # Explicit operator opt-in. Only use with a SELF-AUTHORED trusted fixture.
    from fastapi.staticfiles import StaticFiles
    import uvicorn
    from backend.app import app
    if not hasattr(app, "mount"):
        raise RuntimeError("trusted fixture has no FastAPI app")
    app.mount("/dashboard", StaticFiles(directory=str(ROOT / "dashboard"), html=True), name="rea-dashboard")
    # Synthetic managed process challenge: no endpoint in normal manual runs.
    # This is not a sandbox or defense against a hostile host with same-user access.
    import os
    import hmac
    token = os.environ.get("REA_TRUSTED_SYNTHETIC_ATTEST_TOKEN", "")
    if token and len(token) == 64 and all(c in "0123456789abcdef" for c in token):
        from fastapi import Request, HTTPException
        @app.get("/__rea/provenance", include_in_schema=False)
        def provenance(request: Request):
            supplied = request.headers.get("X-REA-Synthetic-Challenge", "")
            if not hmac.compare_digest(supplied, token):
                raise HTTPException(status_code=404, detail="Not found")
            return {"pid": os.getpid(), "source_sha256": EXPECTED_APP_SHA,
                    "synthetic_process_challenge_verified": True}
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

WINDOWS_CMD = ("@echo off\r\n"
               "setlocal EnableExtensions DisableDelayedExpansion\r\n"
               "cd /d \"%~dp0\"\r\n"
               "python runtime_entry.py --check\r\n"
               "if errorlevel 1 (echo [REA] Integrity check failed.& pause & exit /b 2)\r\n"
               "echo [REA] SELF-AUTHORED SYNTHETIC FIXTURE ONLY. No package installs.\r\n"
               "python runtime_entry.py --run-trusted-synthetic\r\n"
               "set \"REACODE=%ERRORLEVEL%\"\r\n"
               "if not \"%REACODE%\"==\"0\" pause\r\n"
               "exit /b %REACODE%\r\n").encode("ascii")

README = '''# REA_WEB — trusted synthetic API + frontend sample

This source bundle is generated from a SELF-AUTHORED SYNTHETIC FastAPI fixture.
It does not validate arbitrary customer source and is NOT a production release.

## Windows (Python 3.11+; preinstalled fastapi + uvicorn)
Double-click START_WINDOWS.cmd, or run:
`python runtime_entry.py --check`
`python runtime_entry.py --run-trusted-synthetic`
Open `http://127.0.0.1:8766/dashboard/`.
No dependencies are installed automatically. Ctrl+C stops the server.

## Important boundaries
- This bundle DOES NOT execute ZIP code when it is generated.
- Running the extracted backend imports Python code: **NEVER** use this demo
  runner with unreviewed or third-party code.
- HTTP binds ONLY to 127.0.0.1; no public hosting, authentication or payment.
- Original backend ZIP is not edited; generated frontend is independently authored.
- Verify SHA256SUMS.json and MANIFEST.json before distributing.
- Route and OpenAPI reviews do NOT prove customer business logic or authorization.
- Do not include real customer data, .env, tokens, passwords, or licensed assets.
'''.encode("utf-8")


def build_synthetic_project(backend_zip: Path, frontend_dir: Path,
                            runtime_review: dict, destination: Path, *,
                            expected_backend_sha256: str,
                            developer_authorized_synthetic: bool = False) -> dict:
    """Package, without executing, only an explicitly authorized synthetic fixture.

    The runtime review is an independently supplied declaration comparison;
    a status match does NOT attest execution of this exact ZIP.
    """
    if developer_authorized_synthetic is not True:
        raise UnsafeProjectBundle("explicit synthetic fixture authorization required")
    if not isinstance(expected_backend_sha256, str) or not SHA.fullmatch(expected_backend_sha256):
        raise UnsafeProjectBundle("expected backend SHA256 required")
    if (not isinstance(runtime_review, dict)
            or runtime_review.get("schema_version") != RECONCILIATION_SCHEMA
            or runtime_review.get("status") != "DECLARATIONS_MATCH_REVIEW_REQUIRED"
            or runtime_review.get("generation_allowed") is not False
            or runtime_review.get("runtime_origin_attested") is not False
            or runtime_review.get("backend_sha256") != expected_backend_sha256
            or runtime_review.get("issues") != []):
        raise UnsafeProjectBundle("runtime declaration review mismatch or not review-gated")
    summary = runtime_review.get("summary")
    if not isinstance(summary, dict) or not (0 < summary.get("matched", 0) == summary.get("declared_operations")):
        raise UnsafeProjectBundle("not all static operations match supplied OpenAPI")
    source = Path(backend_zip)
    if source.is_symlink() or not source.is_file():
        raise UnsafeProjectBundle("backend ZIP must be a regular file")
    backend, actual_sha = _backend_contents(source)
    if actual_sha != expected_backend_sha256:
        raise UnsafeProjectBundle("backend ZIP SHA mismatch")
    frontend, front_manifest = _check_frontend(Path(frontend_dir), actual_sha)
    routes = {(x.get("path"), x.get("method")) for x in runtime_review.get("matched_declarations", [])
              if isinstance(x, dict)}
    for role in ("list", "metrics", "detail"):
        if (front_manifest["bindings"][role]["path"], "GET") not in routes:
            raise UnsafeProjectBundle("frontend binding not in reviewed GET routes")
    files = {**backend, **frontend}
    files["backend/__init__.py"] = b"# Trusted synthetic backend package.\n"
    files["runtime_entry.py"] = RUNNER.replace("__EXPECTED_APP_SHA__", _hash(backend["backend/app.py"])).encode("utf-8")
    files["START_WINDOWS.cmd"] = WINDOWS_CMD
    files["README_FIRST.md"] = README
    digest_table = {name: _hash(data) for name, data in sorted(files.items())}
    manifest = {
        "schema_version": SCHEMA,
        "status": "TRUSTED_SYNTHETIC_PROJECT_SOURCE_NOT_CUSTOMER_RELEASE",
        "trusted_synthetic_only": True,
        "original_backend_zip_sha256": actual_sha,
        "frontend_source_review": FRONTEND_SCHEMA,
        "runtime_declarations_review": RECONCILIATION_SCHEMA,
        "runtime_origin_attested": False,
        "behavior_verified_by_bundle_generator": False,
        "file_count": len(files) + 2,
        "limitations": ["requires_installed_fastapi_uvicorn", "no_customer_zip_auto_execution",
                        "no_production_deployment", "requires_clean_extract_and_manual_local_run"],
    }
    files["MANIFEST.json"] = _json(manifest)
    files["SHA256SUMS.json"] = _json(digest_table)
    output = Path(destination).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError("bundle output already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".rea-package-", dir=output.parent) as staging:
        temp = Path(staging) / "project.zip"
        with zipfile.ZipFile(temp, "w") as archive:
            for name, data in sorted(files.items()):
                info = zipfile.ZipInfo(name, FIXED_DATE)
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        with zipfile.ZipFile(temp) as audit:
            if audit.testzip() is not None or set(audit.namelist()) != set(files):
                raise UnsafeProjectBundle("generated ZIP integrity failed")
            for name, expected in digest_table.items():
                if _hash(audit.read(name)) != expected:
                    raise UnsafeProjectBundle("generated package SHA256 mismatch")
        publish_archive(temp, output)
    return {"schema_version": SCHEMA, "status": manifest["status"],
            "archive_sha256": _hash(output.read_bytes()), "source_sha256": actual_sha,
            "files": len(files), "output": str(output)}


def _read_json(path: Path) -> dict:
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2 * 1024 * 1024:
        raise UnsafeProjectBundle("local JSON must be regular and <=2 MiB")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise UnsafeProjectBundle("invalid JSON") from exc
    if not isinstance(value, dict):
        raise UnsafeProjectBundle("JSON must be object")
    return value


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="REA trusted SYNTHETIC project archive only")
    p.add_argument("--backend-zip", type=Path, required=True)
    p.add_argument("--frontend", type=Path, required=True)
    p.add_argument("--runtime-review", type=Path, required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--developer-authorized-synthetic", action="store_true")
    args = p.parse_args(argv)
    try:
        result = build_synthetic_project(args.backend_zip, args.frontend,
                _read_json(args.runtime_review), args.out,
                expected_backend_sha256=args.expected_sha256,
                developer_authorized_synthetic=args.developer_authorized_synthetic)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        p.exit(2, "[REA] REFUSED: " + str(exc) + "\n")
    print(_json({k:v for k,v in result.items() if k != 'output'}).decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
