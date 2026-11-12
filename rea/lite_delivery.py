"""Offline unsigned REA Lite delivery archive, preserving source and customer privacy.

All HTML data is plaintext. SHA-256 detects changes, but does not certify
authorship, rights, approval, authenticity, or customer Windows acceptance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import stat
import zipfile
from pathlib import Path

CONTRACT = "REA_LITE_DELIVERY_V1"
HTML_LIMIT = 16 * 1024 * 1024
META_LIMIT = 64 * 1024
README_NAME = "README_KO.txt"
FILES = ("catalog.html", "manifest.json", README_NAME)
SHA = re.compile(r"[a-f0-9]{64}\Z")
DATA = re.compile(r'<script type="application/json" id="rea-dataset">(.*?)</script>', re.S)
README = ("REA Lite 독립 고객 파일 (오프라인)\n"
          "1. 이 ZIP은 검증 전 고객 납품·판매 승인 자료가 아닙니다.\n"
          "2. catalog.html은 원본 행 데이터가 평문으로 포함된 파일입니다.\n"
          "3. 개인정보/영업기밀이 없는 소유자 승인 데이터에서만 생성하세요.\n"
          "4. 브라우저에서 HTML 파일을 열고 검색/필터/상세/CSV 교체/새 HTML 저장을 확인하세요.\n"
          "5. manifest SHA-256은 변경 감지만 제공하며 전자서명·작성자 인증·사용권 증명이 아닙니다.\n"
          "6. 서버/계정/원격 동기화는 제공되지 않으며 고객 파일은 자동 업로드되지 않습니다.\n")


class DeliveryError(ValueError):
    """Fail closed without printing customer row contents."""


def _pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise DeliveryError("DUPLICATE_JSON_KEY")
        obj[key] = value
    return obj


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_regular(path: Path, limit: int) -> bytes:
    if not path.is_absolute() or path.is_symlink():
        raise DeliveryError("UNSAFE_INPUT_PATH")
    handle = None
    try:
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        handle = os.fdopen(os.open(path, flags), "rb")
        meta = os.fstat(handle.fileno())
        if not stat.S_ISREG(meta.st_mode) or not 0 < meta.st_size <= limit:
            raise DeliveryError("INPUT_SIZE_OR_TYPE")
        data = handle.read(limit + 1)
        if len(data) > limit or path.is_symlink():
            raise DeliveryError("INPUT_CHANGED_OR_LARGE")
        return data
    except OSError as exc:
        raise DeliveryError("INPUT_READ_BLOCKED") from exc
    finally:
        if handle:
            handle.close()


def _new_path(path: Path):
    if not path.is_absolute() or path.suffix.lower() != ".zip" or path.exists() or path.is_symlink():
        raise DeliveryError("OUTPUT_NOT_NEW")
    if not path.parent.is_dir():
        raise DeliveryError("OUTPUT_PARENT_MISSING")
    for part in (path.parent, *path.parent.parents):
        st = part.lstat()
        if part.is_symlink() or getattr(st, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
            raise DeliveryError("LINKED_OUTPUT_PARENT")


def _scope(document: bytes) -> tuple[int, int]:
    try:
        value = document.decode("utf-8", "strict")
    except UnicodeError as exc:
        raise DeliveryError("HTML_NOT_UTF8") from exc
    matches = DATA.findall(value)
    if len(matches) != 1 or "connect-src 'none'" not in value:
        raise DeliveryError("UNKNOWN_LITE_TEMPLATE")
    try:
        payload = json.loads(matches[0], object_pairs_hook=_pairs)
    except ValueError as exc:
        raise DeliveryError("INVALID_LITE_JSON") from exc
    if not isinstance(payload, dict) or payload.get("contract") != "REA_LITE_V1" or payload.get("source_approval") != "OWNER_APPROVED_LOCAL_BUILD_ONLY":
        raise DeliveryError("INVALID_LITE_CONTRACT")
    columns, records = payload.get("fields"), payload.get("rows")
    if not isinstance(columns, list) or not 3 <= len(columns) <= 20 or not isinstance(records, list) or not 1 <= len(records) <= 10000:
        raise DeliveryError("INVALID_LITE_DIMENSIONS")
    if any(type(c) is not str or not c or len(c) > 2000 or c in ("__proto__", "constructor", "prototype") for c in columns) or len(set(columns)) != len(columns) or not {"id", "title", "category"} <= set(columns):
        raise DeliveryError("INVALID_LITE_FIELDS")
    seen = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != set(columns) or any(type(v) is not str or len(v) > 2000 or "\0" in v for v in record.values()):
            raise DeliveryError("INVALID_LITE_ROW")
        if any(not record[k].strip() for k in ("id", "title", "category")) or record["id"] in seen:
            raise DeliveryError("INVALID_LITE_ID")
        seen.add(record["id"])
    return len(records), len(columns)


def verify_lite_zip(path: Path) -> dict:
    """Validate only three bounded members in memory, never extract ZIP."""
    path = Path(path)
    if not path.is_absolute() or path.is_symlink() or path.suffix.lower() != ".zip":
        raise DeliveryError("UNSAFE_ZIP_PATH")
    handle = None
    try:
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        handle = os.fdopen(os.open(path, flags), "rb")
        st = os.fstat(handle.fileno())
        if not stat.S_ISREG(st.st_mode) or not 0 < st.st_size <= HTML_LIMIT + 4 * META_LIMIT:
            raise DeliveryError("ZIP_SIZE_INVALID")
        with zipfile.ZipFile(handle, "r") as archive:
            info = archive.infolist()
            if len(info) != 3 or set(x.filename for x in info) != set(FILES) or len({x.filename for x in info}) != 3:
                raise DeliveryError("UNEXPECTED_ZIP_MEMBERS")
            files = {}
            for member in info:
                if member.is_dir() or member.flag_bits & 1 or (member.create_system == 3 and stat.S_IFMT(member.external_attr >> 16) == stat.S_IFLNK):
                    raise DeliveryError("UNSAFE_ZIP_ENTRY")
                bound = HTML_LIMIT if member.filename == "catalog.html" else META_LIMIT
                if not 0 < member.file_size <= bound or member.compress_size > bound:
                    raise DeliveryError("ZIP_ENTRY_BOUNDS")
                with archive.open(member) as reader:
                    content = reader.read(bound + 1)
                if len(content) != member.file_size:
                    raise DeliveryError("ZIP_ENTRY_TRUNCATED")
                files[member.filename] = content
        try:
            manifest = json.loads(files["manifest.json"].decode("utf-8"), object_pairs_hook=_pairs)
        except (ValueError, UnicodeError) as exc:
            raise DeliveryError("MANIFEST_INVALID") from exc
        keys = {"contract", "html_sha256", "html_bytes", "rows", "columns", "readme_sha256",
                "sale_approved", "customer_windows_verified", "authenticity"}
        if (not isinstance(manifest, dict) or set(manifest) != keys or manifest["contract"] != CONTRACT
                or manifest["sale_approved"] is not False or manifest["customer_windows_verified"] is not False
                or manifest["authenticity"] != "UNSIGNED_SHA256_CHANGE_DETECTION_ONLY"):
            raise DeliveryError("MANIFEST_CONTRACT_INVALID")
        if manifest["readme_sha256"] != _digest(files[README_NAME]) or files[README_NAME] != README.encode("utf-8"):
            raise DeliveryError("README_CHANGED")
        html = files["catalog.html"]
        if (not isinstance(manifest["html_sha256"], str) or manifest["html_sha256"] != _digest(html)
                or type(manifest["html_bytes"]) is not int or manifest["html_bytes"] != len(html)):
            raise DeliveryError("HTML_INTEGRITY_FAILED")
        rows, columns = _scope(html)
        if (type(manifest["rows"]) is not int or manifest["rows"] != rows
                or type(manifest["columns"]) is not int or manifest["columns"] != columns):
            raise DeliveryError("ROW_FIELD_COUNTS_CHANGED")
        return {"contract": CONTRACT, "status": "UNSIGNED_LOCAL_PACKAGE_VERIFIED_RELEASE_HOLD",
                "html_sha256": manifest["html_sha256"], "rows": rows, "columns": columns,
                "sale_approved": False, "buyer_acceptance_verified": False,
                "plaintext_data_embedded": True, "remote_transfer": False}
    except (OSError, zipfile.BadZipFile, EOFError, RuntimeError) as exc:
        raise DeliveryError("ZIP_READ_BLOCKED") from exc
    finally:
        if handle:
            handle.close()


def package_lite(html_path: Path, zip_path: Path, *, expected_html_sha256: str, acknowledge: str) -> dict:
    """Build deterministic new output only from owner-pinned generated Lite HTML."""
    html_path, zip_path = Path(html_path), Path(zip_path)
    if (acknowledge != "ACK_PLAINTEXT_LOCAL_DATA" or not isinstance(expected_html_sha256, str)
            or SHA.fullmatch(expected_html_sha256) is None):
        raise DeliveryError("EXPLICIT_REVIEW_AND_HASH_REQUIRED")
    _new_path(zip_path)
    source = _read_regular(html_path, HTML_LIMIT)
    if _digest(source) != expected_html_sha256:
        raise DeliveryError("HTML_SHA_CHANGED")
    rows, columns = _scope(source)
    manifest = {"contract": CONTRACT, "html_sha256": _digest(source), "html_bytes": len(source),
                "rows": rows, "columns": columns, "readme_sha256": _digest(README.encode("utf-8")),
                "sale_approved": False, "customer_windows_verified": False,
                "authenticity": "UNSIGNED_SHA256_CHANGE_DETECTION_ONLY"}
    meta = (json.dumps(manifest, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    created = False
    try:
        with zip_path.open("xb") as file:
            created = True
            with zipfile.ZipFile(file, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                for name, body in (("catalog.html", source), ("manifest.json", meta),
                                   (README_NAME, README.encode("utf-8"))):
                    info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, body, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        if _digest(_read_regular(html_path, HTML_LIMIT)) != expected_html_sha256:
            raise DeliveryError("HTML_CHANGED_DURING_PACKAGE")
        receipt = verify_lite_zip(zip_path)
        if receipt["html_sha256"] != expected_html_sha256:
            raise DeliveryError("ZIP_VERIFY_MISMATCH")
        return receipt
    except Exception:
        if created:
            zip_path.unlink(missing_ok=True)
        raise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="REA Lite: offline unsigned delivery package")
    cmd = parser.add_subparsers(dest="command", required=True)
    build = cmd.add_parser("package")
    build.add_argument("--html", type=Path, required=True)
    build.add_argument("--out", type=Path, required=True)
    build.add_argument("--html-sha256", required=True)
    build.add_argument("--acknowledge-plaintext", required=True)
    check = cmd.add_parser("verify")
    check.add_argument("--zip", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = (package_lite(args.html, args.out, expected_html_sha256=args.html_sha256,
                               acknowledge=args.acknowledge_plaintext) if args.command == "package"
                  else verify_lite_zip(args.zip))
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 0
    except (OSError, ValueError, zipfile.BadZipFile):
        print("REA_LITE_DELIVERY_BLOCKED")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
