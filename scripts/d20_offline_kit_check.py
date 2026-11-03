"""D20 standalone, read-only pilot kit integrity check (Python stdlib only).

This script is copied verbatim into an extracted SYNTHETIC kit. It neither
installs packages, starts a listener, contacts the Internet, nor declares
rights/human acceptance. SHA256 is an integrity check, NOT a signature.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import stat
import sys
import zipfile

EXPECTED = frozenset({
    "sources/qa_guided.csv", "sources/qa_pair_extra.json",
    "demo/approved_pair.zip", "README_WINDOWS.txt",
    "HUMAN_PILOT_BLANK.csv", "MANUAL_TIME_LOG_BLANK.csv",
    "CHECK_PILOT_OFFLINE.py", "CHECK_PILOT_WINDOWS.cmd", "MANIFEST.json",
})
FIXTURE_SHA = {
    "sources/qa_guided.csv": "86bee9d74d474baf502cffbfd3071568337812744d143f432dc04b79554025f2",
    "sources/qa_pair_extra.json": "e40182bafa08c90629908d6566433839e054fe37b6bc057ed175b870476d1a9d",
}
SCHEMA = "rea.d19.synthetic_owner_pilot.v1"
MAX_FILE = 25 * 1024 * 1024
MAX_TOTAL = 25 * 1024 * 1024


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def checked_bytes(root: Path, name: str) -> bytes:
    if name not in EXPECTED or name.startswith("/") or ".." in name.split("/"):
        raise ValueError("File is not in fixed synthetic kit allowlist")
    parts = name.split("/")
    path = root
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("Symlinks are not allowed in the pilot kit")
    if not path.is_file() or path.stat().st_size > MAX_FILE:
        raise ValueError("Required pilot kit file missing or oversized")
    content = path.read_bytes()
    if len(content) > MAX_FILE:
        raise ValueError("Pilot file exceeds size boundary")
    return content


def _inner_zip_checks(blob: bytes) -> None:
    import io
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        members = z.infolist()
        names = [m.filename for m in members]
        if (len(names) > 100 or len(names) != len(set(names))
                or sum(m.file_size for m in members) > MAX_TOTAL
                or any(m.filename.startswith("/") or "\\" in m.filename
                       or any(p in ("", ".", "..") or p.startswith(".")
                              for p in m.filename.split("/"))
                       or stat.S_ISLNK(m.external_attr >> 16) for m in members)):
            raise ValueError("Unsafe inner delivery ZIP")
        needed = {"app/append_report.json", "app/manifest.json",
                  "app/data.sqlite", "delivery_manifest.json"}
        if not needed.issubset(names):
            raise ValueError("Incomplete APPEND demo ZIP")
        signed_inventory = json.loads(z.read("delivery_manifest.json"))
        rows = signed_inventory.get("files")
        if (not isinstance(rows, list) or len(rows) != len(names) - 1
                or signed_inventory.get("runtime_binding") != "127.0.0.1"):
            raise ValueError("Inner ZIP hash manifest invalid")
        by_name = {}
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("path"), str):
                raise ValueError("Unexpected inner inventory")
            if row["path"] in by_name:
                raise ValueError("Duplicate inner inventory")
            by_name[row["path"]] = row
        if set(by_name) != set(names) - {"delivery_manifest.json"}:
            raise ValueError("Inner ZIP inventory mismatch")
        for name, row in by_name.items():
            data = z.read(name)
            if len(data) != row.get("bytes") or sha256(data) != row.get("sha256"):
                raise ValueError("Inner ZIP SHA mismatch")
        receipt = json.loads(z.read("app/append_report.json"))
        manifest = json.loads(z.read("app/manifest.json"))
        sources = receipt.get("sources")
        if (receipt.get("mode") != "SAME_SCHEMA_ROW_APPEND_NO_JOIN"
                or receipt.get("combined_confirmation") != "APPEND"
                or receipt.get("external_join_or_lookup_used") is not False
                or receipt.get("fable_inferred_mapping_used") is not False
                or receipt.get("rows") != 5 or manifest.get("rows") != 5
                or manifest.get("source_count") != 2
                or receipt != manifest.get("two_file_append")
                or not isinstance(sources, list) or len(sources) != 2
                or [x.get("row_count") for x in sources] != [3, 2]
                or [x.get("sha256") for x in sources] != list(FIXTURE_SHA.values())
                or [x.get("confirmed") for x in sources] != ["APPROVE", "APPROVE"]):
            raise ValueError("Inner ZIP APPEND/rights receipt mismatch")
        if not z.read("app/data.sqlite").startswith(b"SQLite format 3\x00"):
            raise ValueError("Expected read-only database snapshot missing")


def verify(root: Path) -> dict:
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Pilot root must be a real directory")
    meta = json.loads(checked_bytes(root, "MANIFEST.json").decode("utf-8"))
    if (meta.get("schema") != SCHEMA
            or meta.get("status") != "SYNTHETIC_ONLY_NOT_HUMAN_ACCEPTED"
            or meta.get("source_policy") != "EXACT_TWO_PINNED_PUBLIC_SYNTHETIC_FIXTURES"
            or meta.get("approval_tokens") != "SYNTHETIC_DEMO_ONLY_NOT_EXTERNAL_CONSENT"
            or meta.get("dataset_rows") != 5
            or meta.get("mode") != "SAME_SCHEMA_ROW_APPEND_NO_JOIN"
            or meta.get("real_human_acceptance") != "NOT_RUN"
            or meta.get("manual_labor_measurements") != "BLANK_NOT_RUN"
            or meta.get("commercial_clearance") != "NOT_GRANTED"
            or meta.get("network_runtime") != "MANUAL_LOCAL_127.0.0.1_ONLY"
            or meta.get("customer_data") != "NOT_USED"):
        raise ValueError("Pilot is not the unaccepted synthetic-only contract")
    inventory = meta.get("files")
    if not isinstance(inventory, list) or len(inventory) != len(EXPECTED) - 1:
        raise ValueError("Wrong inventory length")
    keyed = {}
    for entry in inventory:
        if (not isinstance(entry, dict) or entry.get("path") in keyed
                or entry.get("path") not in EXPECTED - {"MANIFEST.json"}):
            raise ValueError("Invalid inventory entry")
        keyed[entry["path"]] = entry
    if set(keyed) != EXPECTED - {"MANIFEST.json"}:
        raise ValueError("Missing inventory member")
    total = 0
    for name, item in keyed.items():
        data = checked_bytes(root, name)
        total += len(data)
        if len(data) != item.get("bytes") or sha256(data) != item.get("sha256"):
            raise ValueError("Extracted synthetic file integrity mismatch")
    if total > MAX_TOTAL:
        raise ValueError("Combined files exceed size limit")
    for name, digest in FIXTURE_SHA.items():
        if sha256(checked_bytes(root, name)) != digest:
            raise ValueError("Fixture no longer equals public pinned synthetic original")
    for name in ("HUMAN_PILOT_BLANK.csv", "MANUAL_TIME_LOG_BLANK.csv"):
        data = checked_bytes(root, name).decode("utf-8")
        if len(data.splitlines()) != 1 or not data.endswith("\n"):
            raise ValueError("Human logs must remain empty until a real human runs pilot")
    _inner_zip_checks(checked_bytes(root, "demo/approved_pair.zip"))
    return {
        "status": "OFFLINE_KIT_INTEGRITY_PASS",
        "verified_files": len(EXPECTED),
        "rows": 5,
        "human_acceptance": "NOT_RUN",
        "customer_data": "NOT_USED",
        "commercial_clearance": "NOT_GRANTED",
        "network_requests": "NONE",
    }


def main() -> int:
    try:
        result = verify(Path(__file__).resolve().parent)
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print("OFFLINE_KIT_NOT_VERIFIED: " + type(error).__name__, file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
