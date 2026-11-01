"""Fail-closed, read-only behavior checks for REA's *trusted synthetic* bundle.

This is NOT a sandbox, and MUST NOT run arbitrary uploaded code. It checks a
separately trusted source ZIP package against an independently recorded ZIP
SHA256, then issues only bounded GETs to a local already-running test server.
On-disk identity does not establish the provenance of the listening process.
Raw response bodies, customer values and credentials are NEVER written out.
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import io
import json
import os
from pathlib import Path
import re
import stat
import sys
from urllib.parse import quote
import zipfile

SCHEMA = "rea.behavior_probe.v0.1"
BUNDLE_SCHEMA = "rea.project_bundle.v0.1"
FRONTEND_SCHEMA = "rea.frontend_bridge.v0.1"
SHA = re.compile(r"^[a-f0-9]{64}$")
NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")
PATH = re.compile(r"^/api(?:/[A-Za-z0-9_.{}-]+)+$")
SAFE_ID = re.compile(r"^[A-Za-z0-9_-][A-Za-z0-9_.-]{0,63}$")
MAX_ZIP = 25 * 1024 * 1024
MAX_RESPONSE = 256 * 1024
MAX_ITEMS = 200
MAX_PATH = 200
ALLOWED_FILES = {
    "backend/app.py", "backend/__init__.py", "backend/requirements.txt",
    "backend/README_KO.md", "dashboard/index.html", "dashboard/app.js",
    "dashboard/style.css", "dashboard/manifest.json", "dashboard/README_KO.md",
    "runtime_entry.py", "START_WINDOWS.cmd", "README_FIRST.md",
    "MANIFEST.json", "SHA256SUMS.json",
}


class UnsafeProbe(ValueError):
    """Provenance/input validation refusal; no HTTP requests performed."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_read(path: Path, limit: int) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise UnsafeProbe("expected regular input file")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        with os.fdopen(os.open(path, flags), "rb") as f:
            if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
                raise UnsafeProbe("input is not regular")
            data = f.read(limit + 1)
    except OSError as exc:
        raise UnsafeProbe("input cannot be safely read") from exc
    if len(data) > limit:
        raise UnsafeProbe("input exceeds size cap")
    return data


def _object(data: bytes, kind: str) -> dict:
    try:
        value = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise UnsafeProbe(f"invalid {kind} JSON") from exc
    if not isinstance(value, dict):
        raise UnsafeProbe(f"{kind} must be JSON object")
    return value


def _archive_and_tree(bundle_zip: Path, extracted: Path, expected_sha: str) -> tuple[dict, dict]:
    """Verify exact ZIP bytes plus EXACT clean extraction; deny injected files."""
    if not isinstance(expected_sha, str) or not SHA.fullmatch(expected_sha):
        raise UnsafeProbe("independent SHA256 required")
    zip_data = _safe_read(Path(bundle_zip), MAX_ZIP)
    if _sha(zip_data) != expected_sha:
        raise UnsafeProbe("bundle ZIP digest mismatch")
    folder = Path(extracted)
    if folder.is_symlink() or not folder.is_dir():
        raise UnsafeProbe("extracted directory must be real")
    try:
        with zipfile.ZipFile(io.BytesIO(zip_data)) as archive:
            members = archive.infolist()
            names = [m.filename for m in members]
            if (not 12 <= len(names) <= len(ALLOWED_FILES)
                    or len(names) != len(set(names))
                    or len(names) != len({n.casefold() for n in names})
                    or not set(names).issubset(ALLOWED_FILES)
                    or any(m.is_dir() or m.flag_bits & 1 for m in members)):
                raise UnsafeProbe("unrecognized ZIP member inventory")
            # Before CRC/decompression, reject oversized declared members.
            # testzip() inflates members and therefore must not precede
            # bounded-size inventory checks (ZIP bomb denial).
            for m in members:
                if m.orig_filename != m.filename or m.filename not in ALLOWED_FILES:
                    raise UnsafeProbe("unsafe original member name")
                mode = (m.external_attr >> 16) & 0xFFFF
                if stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                    raise UnsafeProbe("special ZIP member denied")
                if m.file_size > 2 * 1024 * 1024 or m.file_size < 0:
                    raise UnsafeProbe("oversized member")
            if archive.testzip() is not None:
                raise UnsafeProbe("ZIP CRC mismatch")
            zipped = {m.filename: archive.read(m) for m in members}
    except (zipfile.BadZipFile, zipfile.LargeZipFile, EOFError) as exc:
        raise UnsafeProbe("damaged ZIP") from exc
    contents: dict[str, bytes] = {}
    observed = set()
    for node in folder.rglob("*"):
        if node.is_symlink():
            raise UnsafeProbe("extracted symlink denied")
        if node.is_dir():
            continue
        if not node.is_file():
            raise UnsafeProbe("extracted special file denied")
        name = node.relative_to(folder).as_posix()
        if name not in zipped or name in observed:
            raise UnsafeProbe("unexpected extracted file")
        observed.add(name)
        contents[name] = _safe_read(node, len(zipped[name]))
        if contents[name] != zipped[name]:
            raise UnsafeProbe("extracted content mismatch")
    if observed != set(zipped):
        raise UnsafeProbe("incomplete extraction")
    manifest = _object(contents["MANIFEST.json"], "project manifest")
    checks = _object(contents["SHA256SUMS.json"], "hash listing")
    if (manifest.get("schema_version") != BUNDLE_SCHEMA
            or manifest.get("trusted_synthetic_only") is not True
            or manifest.get("runtime_origin_attested") is not False
            or manifest.get("behavior_verified_by_bundle_generator") is not False
            or type(manifest.get("file_count")) is not int
            or manifest["file_count"] != len(zipped)
            or not SHA.fullmatch(str(manifest.get("original_backend_zip_sha256", "")))):
        raise UnsafeProbe("untrusted bundle profile")
    if set(checks) != set(zipped) - {"MANIFEST.json", "SHA256SUMS.json"}:
        raise UnsafeProbe("incomplete or altered SHA256SUMS")
    if any(not isinstance(digest, str) or not SHA.fullmatch(digest)
           or _sha(contents[name]) != digest for name, digest in checks.items()):
        raise UnsafeProbe("source/asset digest mismatch")
    front = _object(contents["dashboard/manifest.json"], "frontend manifest")
    if (front.get("schema_version") != FRONTEND_SCHEMA
            or front.get("owner_bindings_confirmed") is not True
            or front.get("backend_modified") is not False
            or not isinstance(front.get("backend"), dict)
            or front["backend"].get("sha256") != manifest["original_backend_zip_sha256"]):
        raise UnsafeProbe("unapproved frontend/source linkage")
    bindings = front.get("bindings")
    if not isinstance(bindings, dict):
        raise UnsafeProbe("binding map missing")
    for role in ("list", "metrics", "detail"):
        item = bindings.get(role)
        if (not isinstance(item, dict) or not isinstance(item.get("path"), str)
                or len(item["path"]) > MAX_PATH or not PATH.fullmatch(item["path"])
                or ".." in item["path"] or not isinstance(item.get("field"), str)):
            raise UnsafeProbe("unsafe API binding")
        if item["field"] in ("__proto__", "constructor", "prototype") or (item["field"] != "__root__" and not NAME.fullmatch(item["field"])):
            raise UnsafeProbe("invalid JSON field mapping")
    if "{" in bindings["list"]["path"] or "{" in bindings["metrics"]["path"]:
        raise UnsafeProbe("unsafe list/metrics route")
    detail = bindings["detail"]
    path_param = detail.get("path_param", "job_id")
    if (not isinstance(path_param, str) or not NAME.fullmatch(path_param)
            or detail["path"].count("{" + path_param + "}") != 1
            or detail["path"].count("{") != 1):
        raise UnsafeProbe("unsupported detail path placeholder")
    presentation = bindings.get("presentation")
    default = {"item": {k:k for k in ("id","name","category","status")},
               "metrics": {k:k for k in ("total","completed","pending")}}
    if presentation is not None:
        if (not isinstance(presentation, dict)
                or not isinstance(presentation.get("item"), dict)
                or not isinstance(presentation.get("metrics"), dict)
                or set(presentation["item"]) != set(default["item"])
                or set(presentation["metrics"]) != set(default["metrics"])):
            raise UnsafeProbe("invalid presentation mapping")
        for fields in (presentation["item"], presentation["metrics"]):
            if any(not isinstance(v, str) or not NAME.fullmatch(v) or v in ("__proto__", "constructor", "prototype") for v in fields.values()):
                raise UnsafeProbe("invalid presentation field")
    else:
        presentation = default
    return manifest, {"bindings":bindings,"presentation":presentation}


def _get_json(port: int, path: str) -> tuple[int, object | None, str | None]:
    """No redirects/cookies/credentials; bounded GET only to literal IPv4 loopback."""
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3.0)
    try:
        conn.request("GET", path, headers={"Accept":"application/json", "Cache-Control":"no-store"})
        response = conn.getresponse()
        status = response.status
        if status in (301, 302, 303, 307, 308):
            return status, None, "REDIRECT_DENIED"
        size = response.getheader("Content-Length")
        if size is not None and (not size.isdigit() or int(size) > MAX_RESPONSE):
            return status, None, "RESPONSE_TOO_LARGE"
        data = response.read(MAX_RESPONSE + 1)
        if len(data) > MAX_RESPONSE:
            return status, None, "RESPONSE_TOO_LARGE"
        ctype = (response.getheader("Content-Type") or "").split(";", 1)[0].strip().lower()
        if ctype != "application/json" and not ctype.endswith("+json"):
            return status, None, "NON_JSON_RESPONSE"
        try:
            obj = json.loads(data.decode("utf-8"))
        except (UnicodeError, ValueError):
            return status, None, "INVALID_JSON"
        return status, obj, None
    except (OSError, TimeoutError, http.client.HTTPException):
        return 0, None, "LOCAL_HTTP_UNREACHABLE"
    finally:
        conn.close()


def _field(container: object, name: str) -> object:
    if name == "__root__":
        return container
    return container.get(name) if isinstance(container, dict) else None


def _check_item(value: object, fields: dict) -> tuple[bool,str]:
    if not isinstance(value, dict):
        return False,"ITEM_NOT_OBJECT"
    ident = _field(value, fields["id"])
    label = _field(value, fields["name"])
    if (type(ident) not in (int, str) or not SAFE_ID.fullmatch(str(ident))
            or not isinstance(label,str) or not label.strip() or len(label)>512):
        return False,"ITEM_ID_OR_NAME_MISSING"
    if any(not isinstance(_field(value, fields[k]), str) for k in ("category", "status")):
        return False,"ITEM_DISPLAY_FIELDS_MISSING"
    return True,""


def probe_trusted_bundle(bundle_zip: Path, extracted: Path, *,
                         expected_bundle_sha256: str, port: int,
                         developer_authorized_synthetic: bool = False) -> dict:
    """Check an already running trusted fixture; NEVER start backend Python.

    Source-on-disk is verified but listening process identity remains unknown.
    A PASS proves observed local responses and UI mapping only for these samples.
    """
    if developer_authorized_synthetic is not True:
        raise UnsafeProbe("explicit trusted synthetic authorization required")
    if type(port) is not int or not 1024 <= port <= 65535:
        raise UnsafeProbe("nonprivileged loopback port required")
    manifest, front = _archive_and_tree(Path(bundle_zip),Path(extracted),expected_bundle_sha256)
    b = front["bindings"]
    display = front["presentation"]
    statuses = {}
    issues = []

    def call(role: str, path: str) -> object | None:
        status, payload, reason = _get_json(port, path)
        statuses[role] = status
        if reason:
            issues.append(role.upper() + "_" + reason)
        elif status != (404 if role == "missing_detail" else 200):
            issues.append(role.upper() + "_UNEXPECTED_HTTP_STATUS")
        return payload if reason is None and status == 200 else None

    listing = call("list",b["list"]["path"])
    rows = _field(listing,b["list"]["field"])
    safe_first_id = None
    count = 0
    if listing is not None:
        if not isinstance(rows,list) or not 1 <= len(rows) <= MAX_ITEMS:
            issues.append("LIST_UNSUPPORTED_SHAPE_OR_SIZE")
        else:
            count = len(rows)
            for row in rows:
                ok, error = _check_item(row, display["item"])
                if not ok:
                    issues.append("LIST_" + error)
                    break
            if not any(issue.startswith("LIST_") for issue in issues):
                safe_first_id = str(_field(rows[0],display["item"]["id"]))
    metrics = call("metrics", b["metrics"]["path"])
    values = _field(metrics,b["metrics"]["field"])
    if metrics is not None:
        if not isinstance(values,dict):
            issues.append("METRICS_NOT_OBJECT")
        else:
            numbers = [_field(values,display["metrics"][k]) for k in ("total","completed","pending")]
            if any(type(n) is not int or n < 0 or n > 1000000 for n in numbers):
                issues.append("METRICS_INVALID_COUNTS")
            elif numbers[0] < count or numbers[0] < numbers[1] + numbers[2]:
                issues.append("METRICS_INCONSISTENT_TOTAL")
    if safe_first_id is not None:
        path = b["detail"]["path"].replace("{"+b["detail"].get("path_param", "job_id")+"}",quote(safe_first_id,safe=""))
        detail = call("detail",path)
        info = _field(detail,b["detail"]["field"])
        if detail is not None:
            ok, reason = _check_item(info, display["item"])
            if not ok:
                issues.append("DETAIL_"+reason)
            elif str(_field(info,display["item"]["id"])) != safe_first_id:
                issues.append("DETAIL_ID_MISMATCH")
        # 404 check uses an impossible synthetic ID, does not change backend.
        missing_id = "REA_MISSING_A3F90C"
        if safe_first_id != missing_id:
            invalid = b["detail"]["path"].replace("{"+b["detail"].get("path_param", "job_id")+"}",missing_id)
            call("missing_detail",invalid)
    else:
        issues.append("DETAIL_NOT_TESTED_LIST_INVALID")
    return {
        "schema_version": SCHEMA,
        "status": "PASS_REVIEW_REQUIRED" if not issues else "FAIL",
        "scope": "TRUSTED_SYNTHETIC_LOOPBACK_GET_ONLY",
        "backend_source_zip_sha256": manifest["original_backend_zip_sha256"],
        "bundle_sha256": expected_bundle_sha256,
        "bundle_and_extracted_bytes_match": True,
        "runtime_process_identity_attested": False,
        "business_logic_comprehensively_verified": False,
        "generation_allowed": False,
        "external_network_access_performed": False,
        "raw_response_data_retained": False,
        "observed_statuses": statuses,
        "list_count_observed": count,
        "issues": sorted(set(issues)),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="REA trusted synthetic local GET behavior review")
    parser.add_argument("--bundle-zip",type=Path,required=True)
    parser.add_argument("--extracted",type=Path,required=True)
    parser.add_argument("--expected-bundle-sha256",required=True)
    parser.add_argument("--port",type=int,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--developer-authorized-synthetic",action="store_true")
    args=parser.parse_args(argv)
    try:
        dest = args.out
        if dest.exists() or dest.is_symlink():
            raise UnsafeProbe("output already exists")
        review=probe_trusted_bundle(args.bundle_zip,args.extracted,
                                    expected_bundle_sha256=args.expected_bundle_sha256,
                                    port=args.port,
                                    developer_authorized_synthetic=args.developer_authorized_synthetic)
        with dest.open("x",encoding="utf-8") as f:
            json.dump(review,f,ensure_ascii=False,indent=2,sort_keys=True)
            f.write("\n")
    except (UnsafeProbe,OSError,zipfile.BadZipFile) as exc:
        parser.exit(2,"[REA] REFUSED: "+str(exc)+"\n")
    return 0 if review["status"]=="PASS_REVIEW_REQUIRED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
