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
import socket
import sqlite3
import subprocess
import sys



MAX_DELIVERY_BYTES = 25 * 1024 * 1024
MAX_MANIFEST_BYTES = 256 * 1024
MAX_DELIVERY_FILES = 100


DEPENDENCY_BOUNDS = {
    "fastapi": ((0, 110, 0), (1, 0, 0)),
    "starlette": ((1, 3, 1), (2, 0, 0)),
    "uvicorn": ((0, 27, 0), (1, 0, 0)),
}


def _version_in_supported_range(
    version: str,
    bounds: tuple[tuple[int, int, int], tuple[int, int, int]],
) -> bool:
    """Check a stable version against both bounds without a non-stdlib dependency."""
    matched = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(.*)", version)
    if matched is None:
        return False
    actual = tuple(int(matched.group(index)) for index in (1, 2, 3))
    minimum, maximum = bounds
    if actual < minimum or actual >= maximum:
        return False
    suffix = matched.group(4)
    # Only a numeric post-release of a supported stable version is accepted.
    return not suffix or re.fullmatch(r"\.post\d+", suffix, flags=re.IGNORECASE) is not None


def _manifest_pairs(pairs: list[tuple[str, object]]) -> dict:
    """Refuse repeated keys in an extracted customer's JSON manifest."""
    unique = {}
    for name, value in pairs:
        if name in unique:
            raise ValueError("Duplicate delivery manifest JSON key")
        unique[name] = value
    return unique


def _reject_manifest_constant(value: str):
    raise ValueError("Non-finite delivery manifest JSON value")


def _manifest_depth_exceeds(doc, limit: int = 64) -> bool:
    pending = [(doc, 0)]
    while pending:
        value, depth = pending.pop()
        if isinstance(value, dict):
            if depth >= limit:
                return True
            pending.extend((child, depth + 1) for child in value.values())
        elif isinstance(value, list):
            if depth >= limit:
                return True
            pending.extend((child, depth + 1) for child in value)
    return False


def _safe_member(name: str) -> bool:
    """Standalone counterpart to the exporter Windows ZIP path policy."""
    if not isinstance(name, str):
        return False
    parts = name.split("/")
    reserved = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} | {
        f"COM{i}" for i in range(1, 10)
    } | {f"LPT{i}" for i in range(1, 10)} | {
        f"{prefix}{digit}" for prefix in ("COM", "LPT") for digit in ("¹", "²", "³")
    }
    return bool(
        name and len(name) <= 260 and not name.startswith("/")
        and "\\" not in name and ":" not in name
        and not any(ch in '<>"|?*' or ord(ch) < 32 for ch in name)
        and all(
            part not in ("", ".", "..") and not part.startswith(".")
            and not part.endswith((" ", "."))
            and part.split(".", 1)[0].upper() not in reserved
            and part != "__pycache__"
            for part in parts
        )
    )

def _member_sha256_bounded(path: Path, expected_size: int) -> str:
    """Hash a bounded extracted member without loading customer rows into RAM."""
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(64 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > expected_size or total > MAX_DELIVERY_BYTES:
                raise ValueError("Extracted member changed size during hashing")
            digest.update(chunk)
    if total != expected_size:
        raise ValueError("Extracted member size changed")
    return digest.hexdigest()


def verify_exact_delivery_tree(root: Path, members: set[str]) -> None:
    """Refuse extra files, folders or symlinks inside an extracted delivery.

    This is an extracted-folder safety check, NOT publisher authentication.
    The manifest itself still needs a trustworthy origin. No network or writes.
    """
    expected_files = members | {"delivery_manifest.json"}
    expected_dirs = set()
    for name in expected_files:
        pieces = name.split("/")
        for end in range(1, len(pieces)):
            expected_dirs.add("/".join(pieces[:end]))
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Unsafe extracted delivery root")
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("Symlink in extracted delivery")
        name = path.relative_to(root).as_posix()
        if name in expected_files:
            if not path.is_file():
                raise ValueError("Expected extracted file is not a file")
        elif name in expected_dirs:
            if not path.is_dir():
                raise ValueError("Expected extracted directory is not a directory")
        else:
            raise ValueError("Unexpected file or directory in extracted delivery")




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
        if manifest_path.stat().st_size > MAX_MANIFEST_BYTES:
            raise ValueError("Delivery manifest exceeds 256 KiB")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"),
                              object_pairs_hook=_manifest_pairs,
                              parse_constant=_reject_manifest_constant)
        if not isinstance(manifest, dict):
            raise ValueError("Invalid delivery_manifest.json")
        if _manifest_depth_exceeds(manifest):
            raise ValueError("Delivery manifest nesting exceeds 64 levels")
        records = manifest.get("files")
        if (manifest.get("schema_version") != "rea.delivery.v0.1"
                or not isinstance(records, list) or len(records) > MAX_DELIVERY_FILES):
            raise ValueError("Invalid or oversized delivery manifest inventory")
        total_bytes = 0
        seen = set()
        seen_folded = set()
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("Invalid manifest record")
            rel = record.get("path")
            length = record.get("bytes")
            checksum = record.get("sha256")
            if (type(length) is not int or length < 0 or length > MAX_DELIVERY_BYTES
                    or not isinstance(checksum, str)
                    or re.fullmatch(r"[0-9a-f]{64}", checksum) is None):
                raise ValueError("Invalid or oversized delivery member metadata")
            total_bytes += length
            if total_bytes > MAX_DELIVERY_BYTES:
                raise ValueError("Extracted delivery exceeds 25 MiB")
            if not _safe_member(rel):
                raise ValueError("Unsafe package path")
            if rel in seen or rel.casefold() in seen_folded:
                raise ValueError("Duplicate/invalid member path")
            pieces = rel.split("/")
            seen.add(rel)
            seen_folded.add(rel.casefold())
            path = root.joinpath(*pieces)
            if any(item.is_symlink() for item in [path, *path.parents] if item != root.parent):
                raise ValueError("Symlink in extracted delivery")
            if not path.is_file() or path.stat().st_size != length:
                raise ValueError("Missing or wrong-size delivery file")
            if _member_sha256_bounded(path, length) != checksum:
                raise ValueError("Customer delivery hash mismatch")
        # On Windows, a manifest file cannot also act as a parent directory.
        for name in seen_folded:
            segments = name.split("/")
            if any("/".join(segments[:index]) in seen_folded
                   for index in range(1, len(segments))):
                raise ValueError("Conflicting file and directory paths in manifest")
        required = {
            "app/app.py", "app/data.sqlite", "app/manifest.json",
            "app/requirements.txt", "app/static/index.html", "app/static/app.js",
            "app/static/style.css", "launch_windows.cmd", "check_windows.cmd",
            "self_check.py", "README_WINDOWS.md", "ACCEPTANCE_CHECKLIST.md",
        }
        if not required.issubset(seen):
            raise ValueError("Missing essential app/launcher/diagnostic member")
        # SHA-only verification of listed paths is insufficient: unknown
        # executable or hidden entries beside them must also fail closed.
        verify_exact_delivery_tree(root, seen)
        result["integrity"] = "MATCHED_DELIVERY_MANIFEST_SHA256"
        db_file = (root / "app/data.sqlite").as_uri()
        with sqlite3.connect(db_file + "?mode=ro", uri=True) as db:
            db.execute("PRAGMA query_only=ON")
            count = db.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        result["database"] = "READONLY_OPEN_SUCCESS"
        result["row_count_only"] = count
    except (OSError, ValueError, KeyError, sqlite3.Error, json.JSONDecodeError, RecursionError) as exc:
        result["issues"].append("Archive/extraction/SQLite validation failed: " + type(exc).__name__)
    for name, bounds in DEPENDENCY_BOUNDS.items():
        minimum, maximum = bounds
        minimum_text = ".".join(map(str, minimum))
        maximum_text = ".".join(map(str, maximum))
        try:
            version = metadata.version(name)
            if _version_in_supported_range(version, bounds):
                state = "INSTALLED_UNVERIFIED_LICENSE"
            else:
                state = "VERSION_OUT_OF_RANGE"
                result["issues"].append(
                    f"Python dependency outside supported range: {name} {version}; "
                    f"required >= {minimum_text}, < {maximum_text}"
                )
        except metadata.PackageNotFoundError:
            version, state = None, "MISSING_INSTALL_REQUIRED"
            result["issues"].append("Missing Python dependency: " + name)
        result["dependencies"].append({
            "name": name, "version": version, "minimum_version": minimum_text,
            "maximum_exclusive": maximum_text, "status": state,
        })
    result["status"] = "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE" if (
        result["python_311_or_later"] and result["integrity"] == "MATCHED_DELIVERY_MANIFEST_SHA256"
        and result["database"] == "READONLY_OPEN_SUCCESS"
        and all(item["version"] and item["status"] == "INSTALLED_UNVERIFIED_LICENSE"
                for item in result["dependencies"])
    ) else "FAIL_LOCAL_PREREQUISITES"
    return result


def render_customer_report(result: dict) -> str:
    """Render the bounded self-check result as plain, actionable Korean text."""
    status = result.get("status", "FAIL_LOCAL_PREREQUISITES")
    lines = ["REA_Web 납품 앱 사전 검사", f"결과: {status}"]
    if status == "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE":
        lines.append("파일 무결성, SQLite 읽기 검사, Python 버전과 필수 패키지를 확인했습니다.")
        lines.append("이 결과는 사람의 고객 검수나 상용 권리 승인을 뜻하지 않습니다.")
        lines.append("human_acceptance=NOT_RUN; commercial_clearance=NOT_GRANTED")
    else:
        if not result.get("python_311_or_later", False):
            lines.append("조치: Python 3.11 이상을 설치한 뒤 CMD 창을 새로 열고 다시 검사하세요.")
        if result.get("integrity") != "MATCHED_DELIVERY_MANIFEST_SHA256":
            lines.append("조치: 원본 ZIP을 보존하고, 비어 있는 새 폴더에 다시 압축을 푸세요.")
            lines.append("압축 해제 폴더의 파일을 직접 편집하거나 추가하지 마세요.")
        if result.get("database") != "READONLY_OPEN_SUCCESS":
            lines.append("조치: 앱 데이터 파일을 편집하지 말고, 신뢰한 원본 ZIP에서 새로 압축을 푸세요.")
        missing = [item.get("name") for item in result.get("dependencies", [])
                   if item.get("status") == "MISSING_INSTALL_REQUIRED"]
        out_of_range = [item for item in result.get("dependencies", [])
                        if item.get("status") == "VERSION_OUT_OF_RANGE"]
        if missing:
            lines.append("MISSING_INSTALL_REQUIRED: 필수 Python 패키지가 없습니다: "
                         + ", ".join(missing) + ".")
            lines.append("README_WINDOWS.md의 선택적 설치 절차를 따라 같은 Python 환경에 설치하세요.")
        if out_of_range:
            lines.append("VERSION_OUT_OF_RANGE: 지원 범위를 벗어난 Python 패키지: "
                         + ", ".join(
                             f"{item['name']} {item['version']} "
                             f"(필요 >= {item['minimum_version']}, < {item['maximum_exclusive']})"
                             for item in out_of_range
                         ) + ".")
            lines.append("README_WINDOWS.md의 업그레이드 명령으로 같은 Python 환경의 패키지를 갱신한 뒤 다시 검사하세요.")
        if result.get("issues") and not (missing or result.get("integrity") != "MATCHED_DELIVERY_MANIFEST_SHA256"
                                          or result.get("database") != "READONLY_OPEN_SUCCESS"
                                          or not result.get("python_311_or_later", False)):
            lines.append("조치: 원본 ZIP과 앱 폴더를 보존하고, 오류 종류를 확인해 지원을 요청하세요.")
        lines.append("검사가 실패하면 launch_windows.cmd를 실행하지 마세요.")
    lines.append("검사는 로컬 읽기 전용이며 고객 파일을 업로드하거나 자동 수정하지 않습니다.")
    return "\n".join(lines)


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
        print(render_customer_report(check), file=sys.stderr)
        print("REA_LOCAL_LAUNCH_BLOCKED: local prerequisites were not verified",
              file=sys.stderr)
        return 2
    try:
        port = port_from_environment()
    except ValueError:
        print("REA_LOCAL_LAUNCH_BLOCKED: unsafe REA_WEB_PORT. 포트 번호는 1~65535 숫자만 사용할 수 있습니다.",
              file=sys.stderr)
        print("CMD에서 set REA_WEB_PORT=8765 입력 후 다시 실행할 수 있습니다.",
              file=sys.stderr)
        return 2
    # Detect the common occupied/reserved-port case before starting Uvicorn.
    # Bind only to loopback and close immediately; this is a friendly preflight,
    # not a reservation, so Uvicorn still owns the definitive bind.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", port))
    except OSError:
        print(f"REA_LOCAL_PORT_UNAVAILABLE: 로컬 포트 {port}를 사용할 수 없습니다.",
              file=sys.stderr)
        print("다른 앱을 종료하거나 CMD에서 set REA_WEB_PORT=8765 입력 후 다시 실행하세요.",
              file=sys.stderr)
        return 2
    # Fixed host and shell=False: an environment variable can never become
    # an additional shell command, an option, or an externally bound address.
    command = [sys.executable, "-m", "uvicorn", "app:app",
               "--host", "127.0.0.1", "--port", str(port)]
    try:
        environment = os.environ.copy()
        # Do not create unlisted __pycache__ after a successful launch.
        # A subsequent clean-room preflight must still accept the same kit.
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            command, cwd=root / "app", check=False, env=environment
        ).returncode
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
    parser.add_argument("--customer-check", action="store_true",
                        help="Print a short customer-readable prerequisite report")
    args = parser.parse_args(argv)
    if args.launch:
        return launch_local(args.root)
    result = inspect(args.root)
    if args.customer_check:
        print(render_customer_report(result))
        return 0 if result["status"].startswith("PASS_") else 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["status"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())

