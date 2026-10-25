"""Offline supply-chain evidence for REA local deliveries and pinned source snapshots.

No registry/network access, commercial licence grants or scanning customer cell
contents. A PASS means only the explicit file/hash assertions passed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

from rea.delivery import DeliveryError, verify_delivery

BASE = Path(__file__).resolve().parents[1]
VENDORS = {
    "fable51": {
        "path": "engines/fable51",
        "upstream": "hibi89/fable5.1_web_catcher",
        "commit": "bbe72c0acd3a3e355062d6bd0d866af33e5274b0",
        "count": 88,
        "batches": 8,
    },
    "astra_p4": {
        "path": "engines/astra_p4",
        "upstream": "hibi89/astra_web_catcher",
        "commit": "b3166b67604381a9d2afd41667b65f9a9b103b37",
        "count": 103,
        "batches": 9,
        "subset": "PARTIAL",
    },
}
ALLOWED_DELIVERY = frozenset({
    "app/app.py", "app/data.sqlite", "app/manifest.json", "app/README.md",
    "app/schema_preview.json", "app/mapping_report.json", "app/append_report.json", "app/requirements.txt",
    "app/static/index.html", "app/static/app.js", "app/static/style.css",
    "app/review/fable_review.json", "app/review/README.md",
    "README_WINDOWS.md", "launch_windows.cmd", "check_windows.cmd",
    "self_check.py", "delivery_manifest.json",
})
REQUIRED_DELIVERY = frozenset({
    "app/app.py", "app/data.sqlite", "app/manifest.json",
    "app/requirements.txt", "app/static/index.html",
    "app/static/app.js", "app/static/style.css",
    "README_WINDOWS.md", "launch_windows.cmd", "check_windows.cmd",
    "self_check.py", "delivery_manifest.json",
})
# Source requirements are bounded ranges, NOT a locked/verified dependency set.
EXPECTED_DIRECT = {
    "fastapi": ">=0.110,<1",
    "uvicorn": ">=0.27,<1",
}
REQUIREMENT = re.compile(r"([a-z][a-z0-9_-]*)([<>=!0-9.,]+)\Z")


class AuditError(ValueError):
    pass


def _direct_deps(contents: str) -> list[dict]:
    result = {}
    for line in contents.splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        matched = REQUIREMENT.fullmatch(value)
        if matched is None:
            raise AuditError("Unsupported requirement syntax or URL")
        name, constraint = matched.groups()
        if name in result or name not in EXPECTED_DIRECT or constraint != EXPECTED_DIRECT[name]:
            raise AuditError("Unknown, duplicate or modified runtime requirement")
        result[name] = {
            "name": name, "constraint": constraint,
            "installed_version": None, "license_id": None,
            "license_verified": False,
            "classification": "DIRECT_RUNTIME_NOT_VERSION_LOCKED",
        }
    if set(result) != set(EXPECTED_DIRECT):
        raise AuditError("Missing runtime dependency")
    return [result[key] for key in sorted(result)]


def inspect_delivery(archive: Path) -> dict:
    """Verify every ZIP member and report only bounded, source-free metadata."""
    archive = Path(archive)
    verify_delivery(archive)  # SHA256 and traversal/duplicate/size bounds
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        missing = REQUIRED_DELIVERY - names
        forbidden = names - ALLOWED_DELIVERY
        if missing or forbidden:
            raise AuditError(
                f"Delivery allowlist mismatch: {len(missing)} required missing, "
                f"{len(forbidden)} unexpected paths")
        app_manifest = json.loads(zf.read("app/manifest.json"))
        kind = app_manifest.get("input_kind")
        if kind is None:  # Older D3 CSV snapshots before input_kind was explicit
            kind = "customer_supplied_csv"
        if kind not in {"customer_supplied_csv", "customer_supplied_json"}:
            raise AuditError("Unknown source kind in generated app")
        if app_manifest.get("scope") != "LOCAL_SYNTHETIC_OR_USER_SUPPLIED_DATA_ONLY":
            raise AuditError("Unexpected runtime scope")
        if app_manifest.get("run") != "python -m uvicorn app:app --host 127.0.0.1 --port 8000":
            raise AuditError("Non-loopback runtime command")
        schema = json.loads(zf.read("app/schema_preview.json"))
        if schema.get("review_status") != "UNAPPROVED" or schema.get("approved_semantic_bindings") != []:
            raise AuditError("Schema approval gate changed")
        if schema.get("source_kind") != kind:
            raise AuditError("Schema source kind does not match app")
        mapped = "app/mapping_report.json" in names
        if mapped:
            receipt = json.loads(zf.read("app/mapping_report.json"))
            mapped_in_manifest = app_manifest.get("owner_field_mapping")
            if (receipt != mapped_in_manifest
                    or receipt.get("status") != "OWNER_CONFIRMED_FOR_THIS_LOCAL_BUILD"
                    or receipt.get("confirmation_scope") != "ONE_LOCAL_GENERATION_ONLY"
                    or receipt.get("source_sha256") != app_manifest.get("sha256")
                    or receipt.get("fable_inferred_mapping_used") is not False
                    or set(receipt.get("source_fields", {})) != {"id", "title", "category"}
                    or len(set(receipt["source_fields"].values())) != 3):
                raise AuditError("Unapproved or inconsistent owner mapping report")
        elif "owner_field_mapping" in app_manifest:
            raise AuditError("Owner mapping report missing")
        appended = "app/append_report.json" in names
        if appended:
            receipt = json.loads(zf.read("app/append_report.json"))
            sources = receipt.get("sources")
            if (receipt != app_manifest.get("two_file_append")
                    or receipt.get("schema_version") != "rea.two_file_append.v0.1"
                    or receipt.get("status") != "OWNER_CONFIRMED_EXPLICIT_APPEND_ONLY"
                    or receipt.get("mode") != "SAME_SCHEMA_ROW_APPEND_NO_JOIN"
                    or receipt.get("combined_confirmation") != "APPEND"
                    or receipt.get("fable_inferred_mapping_used") is not False
                    or receipt.get("external_join_or_lookup_used") is not False
                    or app_manifest.get("source_count") != 2
                    or receipt.get("source_count") != 2
                    or app_manifest.get("source") != "TWO_OWNER_INPUTS_APPENDED"
                    or receipt.get("rows") != app_manifest.get("rows")
                    or receipt.get("fields") != app_manifest.get("fields")
                    or not isinstance(sources, list) or len(sources) != 2):
                raise AuditError("Two-source receipt does not match app manifest")
            count = 0
            for index, item in enumerate(sources, 1):
                if not isinstance(item, dict):
                    raise AuditError("Invalid source entry")
                digest, fields = item.get("sha256"), item.get("source_fields")
                if (item.get("position") != index or item.get("confirmed") != "APPROVE"
                        or item.get("input_kind") not in {"customer_supplied_csv", "customer_supplied_json"}
                        or type(item.get("row_count")) is not int or item["row_count"] < 1
                        or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
                        or not isinstance(fields, dict)
                        or set(fields) != {"id", "title", "category"}
                        or any(not isinstance(value, str) for value in fields.values())
                        or len(set(fields.values())) != 3):
                    raise AuditError("Invalid source confirmation in append receipt")
                count += item["row_count"]
            if count != receipt["rows"]:
                raise AuditError("Two-source row count mismatch")
        elif "two_file_append" in app_manifest:
            raise AuditError("Missing append receipt")
        review_present = "app/review/fable_review.json" in names
        if review_present:
            doc = json.loads(zf.read("app/review/fable_review.json"))
            if (doc.get("status") != "REVIEW_REQUIRED"
                    or doc.get("generation_allowed") is not False
                    or doc.get("approved_semantic_bindings") != []):
                raise AuditError("Fable review incorrectly marked approved")
        dependencies = _direct_deps(zf.read("app/requirements.txt").decode("utf-8"))
        files = verify_delivery(archive)["files"]
    return {
        "schema_version": "rea.provenance.v0.1",
        "evidence_scope": "SYNTHETIC_OFFLINE_ARCHIVE_FILE_AND_HASH_INVENTORY_ONLY",
        "overall_commercial_clearance": "NOT_GRANTED",
        "delivery_integrity": "VERIFIED_SHA256",
        "source_kind": kind,
        "archive_member_count": len(files) + 1,
        "archive_file_inventory": files,  # paths/sizes/checksums, NO app cell data
        "vendor_source_files_bundled": False,
        "vendor_upstream_licenses_cleared": False,
        "raw_fable_capture_bundled": False,
        "review_report_present": review_present,
        "owner_mapping_receipt_present": mapped,
        "two_file_append_receipt_present": appended,
        "dependencies": dependencies,
        "transitive_dependency_inventory": "NOT_ASSESSED",
        "customer_data_sensitivity": "NOT_ASSESSED",
        "license_and_attribution": "BLOCKED_PENDING_EVIDENCE",
        "unresolved": [
            "Runtime dependency exact versions not locked",
            "PyPI licence/NOTICE terms and transitive dependencies not independently verified",
            "Packaged data.sqlite can contain customer-supplied content; secrets/PII not certified absent",
            "Source rights, independent app source licence and third-party attribution require review",
            "Draft two-file intake commercial scope not implemented",
            "Clean end-user Windows and genuine customer acceptance not performed",
        ],
    }


def _git_blob_sha(contents: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(contents)).encode() + b"\0" + contents).hexdigest()


def verify_vendor_snapshot(vendor: str, checkout: Path) -> dict:
    """Check immutable source files from actual pinned checkout; not licence approval."""
    if vendor not in VENDORS:
        raise AuditError("Unknown vendor")
    details = VENDORS[vendor]
    root = Path(checkout)
    folder = root / details["path"]
    batches = sorted((folder / "provenance").glob("BATCH_*.json"))
    if len(batches) != details["batches"]:
        raise AuditError("Missing vendor provenance batch files")
    seen = set()
    for batch in batches:
        doc = json.loads(batch.read_text(encoding="utf-8"))
        if doc.get("source_commit") != details["commit"]:
            raise AuditError("Vendor upstream commit mismatch")
        rows = doc.get("upstream_github_git_blob_sha")
        if not isinstance(rows, dict):
            raise AuditError("Missing vendor Git blob digest map")
        for rel, expected in rows.items():
            path = Path(rel)
            if (path.is_absolute() or ".." in path.parts or "\\" in rel
                    or rel in seen or not re.fullmatch(r"[a-f0-9]{40}", expected)):
                raise AuditError("Unsafe or duplicated vendor manifest entry")
            seen.add(rel)
            source = folder / path
            if source.is_symlink() or not source.is_file():
                raise AuditError("Vendor source missing or symlinked")
            if _git_blob_sha(source.read_bytes()) != expected:
                raise AuditError("Vendor Git blob SHA mismatch")
    if len(seen) != details["count"]:
        raise AuditError("Unexpected pinned vendor source count")
    legal = []
    for target in (root, folder):
        for name in ("LICENSE", "LICENSE.md", "LICENSE.txt",
                     "LICENCE", "COPYING", "NOTICE", "NOTICE.txt"):
            path = target / name
            if path.is_file():
                legal.append(path.relative_to(root).as_posix())
    return {
        "vendor": vendor,
        "source": details["upstream"],
        "commit": details["commit"],
        "snapshot_kind": details.get("subset", "PINNED_SOURCE_SNAPSHOT"),
        "checked_source_count": len(seen),
        "checked_source_sha": "GIT_BLOB_MATCH",
        "license_or_notice_artifacts_in_snapshot": sorted(set(legal)),
        "license_grant_status": "NOT_ASSESSED" if legal else "NO_LICENSE_ARTIFACT_FOUND",
        "commercial_redistribution_cleared": False,
        "warning": "Pinned source/hash equality does not demonstrate ownership or rights to redistribute.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="REA offline supply chain evidence; NOT licence clearance")
    sub = parser.add_subparsers(dest="command", required=True)
    package = sub.add_parser("inspect-zip")
    package.add_argument("--zip", type=Path, required=True)
    package.add_argument("--out", type=Path)
    vendor = sub.add_parser("verify-vendor")
    vendor.add_argument("--vendor", choices=sorted(VENDORS), required=True)
    vendor.add_argument("--root", type=Path, required=True)
    vendor.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        result = (inspect_delivery(args.zip) if args.command == "inspect-zip"
                  else verify_vendor_snapshot(args.vendor, args.root))
        serialized = json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
        if args.out:
            with args.out.open("x", encoding="utf-8") as target:
                target.write(serialized)
        print(serialized)
        return 0
    except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        parser.exit(2, f"AUDIT_FAILED: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
