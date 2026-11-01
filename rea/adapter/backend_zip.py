"""Read-only static FastAPI declarations from an untrusted backend source ZIP.

No extraction, imports, eval, subprocess, network, or execution of ZIP contents.
Static declarations are not proof that an endpoint is mounted or callable.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile

SCHEMA = "rea.backend_contract.v0.1"
MAX_ARCHIVE_BYTES = 25 * 1024 * 1024
MAX_FILES = 1000
MAX_TOTAL_UNCOMPRESSED = 20 * 1024 * 1024
MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAX_RATIO = 150
MAX_ENDPOINTS = 500
MAX_ROUTE_LENGTH = 200
VERBS = frozenset({"get", "post", "put", "patch", "delete", "options", "head", "trace"})
_DRIVE = re.compile(r"^[A-Za-z]:")


class UnsafeBackendZip(ValueError):
    """Archive is unsupported, malformed, or crosses the source-only boundary."""


def _safe_name(name: str) -> str:
    if (not isinstance(name, str) or len(name) > 400 or not name
            or "\\" in name or "\x00" in name or name.startswith("/")
            or _DRIVE.match(name) or any(ord(ch) < 32 for ch in name)):
        raise UnsafeBackendZip("unsafe archive member path")
    parts = name.rstrip("/").split("/")
    if any(p in ("", ".", "..") for p in parts):
        raise UnsafeBackendZip("unsafe archive member path")
    return str(PurePosixPath(*parts))


def _zip_members(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    infos = archive.infolist()
    if not infos or len(infos) > MAX_FILES:
        raise UnsafeBackendZip("invalid archive member count")
    total = 0
    seen: set[str] = set()
    for item in infos:
        name = _safe_name(item.filename)
        if name.casefold() in seen:
            raise UnsafeBackendZip("duplicate archive member")
        seen.add(name.casefold())
        if item.flag_bits & 1:
            raise UnsafeBackendZip("encrypted archives unsupported")
        mode = (item.external_attr >> 16) & 0xFFFF
        kind = stat.S_IFMT(mode)
        if kind and kind not in (stat.S_IFDIR if item.is_dir() else stat.S_IFREG,):
            raise UnsafeBackendZip("links and special members unsupported")
        if item.file_size > MAX_SOURCE_BYTES and name.lower().endswith(".py"):
            raise UnsafeBackendZip("Python source member exceeds 2 MiB")
        total += item.file_size
        if total > MAX_TOTAL_UNCOMPRESSED:
            raise UnsafeBackendZip("uncompressed archive exceeds 20 MiB")
        if item.file_size and (not item.compress_size or item.file_size > MAX_RATIO * item.compress_size):
            raise UnsafeBackendZip("excessive archive compression ratio")
    return infos


def _literal_str(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _keyword(call: ast.Call, name: str) -> ast.AST | None:
    return next((x.value for x in call.keywords if x.arg == name), None)


def _valid_route(path: str | None) -> bool:
    return bool(path is not None and path.startswith("/") and len(path) <= MAX_ROUTE_LENGTH
                and not any(ord(ch) < 32 or ch in "?#\\" for ch in path))


def _api_methods(decorator: ast.Call, verb: str) -> list[str]:
    if verb != "api_route":
        return [verb.upper()]
    n = _keyword(decorator, "methods")
    if not isinstance(n, (ast.List, ast.Tuple)):
        return []
    vals = [_literal_str(x) for x in n.elts]
    return sorted(set(x.upper() for x in vals if x and x.lower() in VERBS)) if all(
        x is not None and x.lower() in VERBS for x in vals
    ) else []


def _analysis_python(source: bytes, filename: str) -> tuple[list[dict], int, bool]:
    try:
        tree = ast.parse(source.decode("utf-8-sig"), filename=filename)
    except (UnicodeError, SyntaxError, ValueError):
        return [], 1, False
    owners: dict[str, tuple[str, str | None]] = {}
    mounted: dict[str, list[str]] = {}
    has_fastapi = False
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and isinstance(node.value, ast.Call):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            fn = node.value.func
            ctor = fn.id if isinstance(fn, ast.Name) else fn.attr if isinstance(fn, ast.Attribute) else ""
            if ctor in ("FastAPI", "APIRouter"):
                has_fastapi = True
                prefix = "" if ctor == "FastAPI" else _literal_str(_keyword(node.value, "prefix"))
                if ctor == "APIRouter" and _keyword(node.value, "prefix") is None:
                    prefix = ""
                for target in targets:
                    if isinstance(target, ast.Name):
                        owners[target.id] = ("app" if ctor == "FastAPI" else "router", prefix)
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            fn = call.func
            if (isinstance(fn, ast.Attribute) and fn.attr == "include_router"
                    and isinstance(fn.value, ast.Name)
                    and owners.get(fn.value.id, (None,))[0] == "app"
                    and call.args and isinstance(call.args[0], ast.Name)):
                raw = _keyword(call, "prefix")
                prefix = "" if raw is None else _literal_str(raw)
                if prefix is not None:
                    mounted.setdefault(call.args[0].id, []).append(prefix)
    endpoints: list[dict] = []
    unresolved = 0
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Attribute):
                continue
            attr = dec.func.attr
            if attr not in VERBS and attr != "api_route":
                continue
            if not isinstance(dec.func.value, ast.Name):
                continue
            owner = dec.func.value.id
            if owner not in owners:
                continue
            kind, base = owners[owner]
            path = _literal_str(dec.args[0]) if dec.args else _literal_str(_keyword(dec, "path"))
            methods = _api_methods(dec, attr)
            if not _valid_route(path) or not methods or base is None:
                unresolved += 1
                continue
            mount_options = [""] if kind == "app" else mounted.get(owner, [])
            if not mount_options:
                # Unmounted router is a declaration, not a verified exposed API.
                mount_options = [""]
                mount_status = "router_mount_unverified"
            else:
                mount_status = "app_declaration" if kind == "app" else "local_router_mount_declaration"
            for mount in mount_options:
                full = mount + base + path
                if not _valid_route(full):
                    unresolved += 1
                    continue
                endpoints.append({
                    "path": full,
                    "methods": methods,
                    "source": filename,
                    "line": node.lineno,
                    "mount": mount_status,
                    "verification": "STATIC_DECLARATION_ONLY",
                })
    return endpoints, unresolved, has_fastapi


def inspect_backend_zip(source: Path) -> dict:
    """Inspect a regular local ZIP; never execute, extract, or mutate its contents."""
    source = Path(source)
    try:
        if source.is_symlink() or not source.is_file() or source.suffix.lower() != ".zip":
            raise UnsafeBackendZip("regular .zip file required (no symlinks)")
        st = source.stat()
        if not 0 < st.st_size <= MAX_ARCHIVE_BYTES:
            raise UnsafeBackendZip("archive must be 1..25 MiB")
        digest = hashlib.sha256()
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        with os.fdopen(os.open(source, flags), "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise UnsafeBackendZip("archive must be regular")
            with zipfile.ZipFile(stream) as archive:
                infos = _zip_members(archive)
                endpoints: list[dict] = []
                unreadable = 0
                unresolved = 0
                python_count = 0
                framework_seen = False
                for item in infos:
                    if item.is_dir() or not item.filename.lower().endswith(".py"):
                        continue
                    python_count += 1
                    # The archive has already passed size/ratio limits.
                    raw = archive.read(item)
                    found, skipped, fastapi = _analysis_python(raw, item.filename)
                    unreadable += int(skipped > 0 and not found and not fastapi)
                    unresolved += skipped
                    framework_seen |= fastapi
                    endpoints.extend(found)
                    if len(endpoints) > MAX_ENDPOINTS:
                        raise UnsafeBackendZip("too many endpoint declarations")
            stream.seek(0)
            for block in iter(lambda: stream.read(65536), b""):
                digest.update(block)
            if os.fstat(stream.fileno()).st_size != st.st_size:
                raise UnsafeBackendZip("archive changed during scan")
        if source.is_symlink() or source.stat().st_size != st.st_size:
            raise UnsafeBackendZip("archive changed during scan")
    except (zipfile.BadZipFile, zipfile.LargeZipFile, EOFError) as exc:
        raise UnsafeBackendZip("invalid ZIP structure or CRC") from exc
    except OSError as exc:
        raise UnsafeBackendZip("could not safely read archive") from exc
    endpoints.sort(key=lambda e: (e["path"], e["source"], e["line"], ",".join(e["methods"])))
    return {
        "schema_version": SCHEMA,
        "status": "REVIEW_REQUIRED",
        "generation_allowed": False,
        "execution_performed": False,
        "input": {"sha256": digest.hexdigest(), "members": len(infos), "python_files": python_count},
        "framework_hints": ["FastAPI"] if framework_seen else [],
        "api": {"endpoints": endpoints, "declared_endpoint_count": len(endpoints),
                "unresolved_declarations": unresolved, "unreadable_python_files": unreadable},
        "limitations": ["static_declarations_not_runtime_verified",
                        "mounted_routes_across_modules_not_resolved",
                        "api_auth_and_return_shapes_not_verified",
                        "frontend_generation_not_performed"],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="REA offline read-only FastAPI ZIP contract scan")
    p.add_argument("zip_file", type=Path, help="owner-authorized local backend source ZIP")
    p.add_argument("--out", type=Path, help="write JSON to a NEW path (never overwrite)")
    args = p.parse_args(argv)
    try:
        result = inspect_backend_zip(args.zip_file)
        payload = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.out is None:
            sys.stdout.write(payload)
        else:
            with args.out.open("x", encoding="utf-8") as output:
                output.write(payload)
            print(f"[REA] static backend contract written: {args.out}")
        return 0
    except (UnsafeBackendZip, OSError) as exc:
        print(f"[REA] REFUSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
