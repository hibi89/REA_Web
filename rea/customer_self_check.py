"""Standalone customer-side Windows/Linux offline prerequisite checker.

Copied as self_check.py in generated ZIP; stdlib only. Does not install
packages, launch a server, read row values or certify legal rights.
"""
from __future__ import annotations

import argparse
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys


def inspect(root: Path) -> dict:
    root = Path(root).absolute()
    result = {
        "schema_version": "rea.rc.selfcheck.v0.1",
        "overall_commercial_clearance": "NOT_GRANTED",
        "runtime_network_call": False,
        "runtime_hosting": "NOT_STARTED",
        "source_data_privacy": "NOT_CERTIFIED",
        "python": ".".join(map(str, sys.version_info[:3])),
        "python_311_or_later": sys.version_info >= (3, 11),
        "integrity": "NOT_VERIFIED",
        "database": "NOT_CHECKED",
        "dependencies": [],
        "issues": [],
    }
    if not result["python_311_or_later"]:
        result["issues"].append("Python 3.11 or later required")
    try:
        manifest_path = root / "delivery_manifest.json"
        if manifest_path.is_symlink() or not manifest_path.is_file():
            raise ValueError("Missing safe delivery_manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        records = manifest.get("files")
        if manifest.get("schema_version") != "rea.delivery.v0.1" or not isinstance(records, list):
            raise ValueError("Invalid delivery_manifest.json")
        seen = set()
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("Invalid manifest record")
            rel = record.get("path")
            if not isinstance(rel, str) or rel in seen or len(rel) > 260:
                raise ValueError("Duplicate/invalid member path")
            pieces = rel.split("/")
            if (not pieces or any(not p or p in (".", "..") or p.startswith(".") for p in pieces)
                    or "\\" in rel or ":" in rel):
                raise ValueError("Unsafe package path")
            seen.add(rel)
            path = root.joinpath(*pieces)
            if any(item.is_symlink() for item in [path, *path.parents] if item != root.parent):
                raise ValueError("Symlink in extracted delivery")
            if not path.is_file() or path.stat().st_size != record.get("bytes"):
                raise ValueError("Missing or wrong-size delivery file")
            if hashlib.sha256(path.read_bytes()).hexdigest() != record.get("sha256"):
                raise ValueError("Customer delivery hash mismatch")
        required = {
            "app/app.py", "app/data.sqlite", "app/manifest.json",
            "app/requirements.txt", "app/static/index.html", "app/static/app.js",
            "app/static/style.css", "launch_windows.cmd", "check_windows.cmd",
            "self_check.py", "README_WINDOWS.md",
        }
        if not required.issubset(seen):
            raise ValueError("Missing essential app/launcher/diagnostic member")
        result["integrity"] = "MATCHED_DELIVERY_MANIFEST_SHA256"
        db_file = (root / "app/data.sqlite").as_uri()
        with sqlite3.connect(db_file + "?mode=ro", uri=True) as db:
            db.execute("PRAGMA query_only=ON")
            count = db.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        result["database"] = "READONLY_OPEN_SUCCESS"
        result["row_count_only"] = count
    except (OSError, ValueError, KeyError, sqlite3.Error, json.JSONDecodeError) as exc:
        result["issues"].append("Archive/extraction/SQLite validation failed: " + type(exc).__name__)
    for name in ("fastapi", "uvicorn"):
        try:
            version = metadata.version(name)
            state = "INSTALLED_UNVERIFIED_LICENSE"
        except metadata.PackageNotFoundError:
            version, state = None, "MISSING_INSTALL_REQUIRED"
            result["issues"].append("Missing Python dependency: " + name)
        result["dependencies"].append({"name": name, "version": version, "status": state})
    result["status"] = "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE" if (
        result["python_311_or_later"] and result["integrity"] == "MATCHED_DELIVERY_MANIFEST_SHA256"
        and result["database"] == "READONLY_OPEN_SUCCESS"
        and all(item["version"] for item in result["dependencies"])
    ) else "FAIL_LOCAL_PREREQUISITES"
    return result


def port_from_environment() -> int:
    """Parse only a plain ASCII decimal port, never shell or CMD syntax."""
    literal = os.environ.get("REA_WEB_PORT", "8000")
    if (re.fullmatch(r"[1-9][0-9]{0,4}", literal, flags=re.ASCII) is None
            or int(literal) > 65535):
        raise ValueError("Unsafe REA_WEB_PORT: expected ASCII decimal 1..65535")
    return int(literal)


def launch_local(root: Path) -> int:
    """Only after read-only integrity/preflight, spawn Uvicorn without shell."""
    root = Path(root).absolute()
    check = inspect(root)
    if check["status"] != "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE":
        print("REA_LOCAL_LAUNCH_BLOCKED: prerequisites or delivery SHA invalid",
              file=sys.stderr)
        return 2
    try:
        port = port_from_environment()
    except ValueError:
        print("REA_LOCAL_LAUNCH_BLOCKED: unsafe REA_WEB_PORT", file=sys.stderr)
        return 2
    # Fixed host and shell=False: an environment variable can never become
    # an additional shell command, an option, or an externally bound address.
    command = [sys.executable, "-m", "uvicorn", "app:app",
               "--host", "127.0.0.1", "--port", str(port)]
    try:
        return subprocess.run(command, cwd=root / "app", check=False).returncode
    except (OSError, ValueError):
        print("REA_LOCAL_LAUNCH_BLOCKED: local runtime could not start",
              file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="REA local package offline prerequisites only")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--launch", action="store_true",
                        help="Start validated localhost app using argv, never a shell")
    args = parser.parse_args(argv)
    if args.launch:
        return launch_local(args.root)
    result = inspect(args.root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["status"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
