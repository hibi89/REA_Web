"""Fail-closed seller release-gate evidence checker for REA_Web.

Evidence metadata is provided by humans. This tool never validates a legal
license, customer consent, or Windows usability; it only detects missing or
malformed sign-off records. It never loads customer data or starts a server.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys

SCHEMA = "rea.sale_gate.v1"
GATES = {
    "independent_windows_operator": "Independent nondeveloper Windows acceptance on synthetic data",
    "source_redistribution_rights": "Seller ownership/permission for shipped REA source",
    "dependency_license_notices": "Actual shipped dependencies and notices reviewed",
    "privacy_data_operations": "Authorized intake, privacy, retention and secure handoff reviewed",
    "seller_scope_terms": "Price, support, correction, cancellation and refund terms approved",
    "measured_delivery_rehearsal": "Human-timed quote-to-ZIP delivery rehearsal recorded",
}
MAX_BYTES = 64 * 1024


def template(source_commit: str) -> dict:
    if not re.fullmatch(r"[0-9a-fA-F]{40}", source_commit):
        raise ValueError("source_commit must be a full 40-hex commit SHA")
    return {
        "schema_version": SCHEMA,
        "source_commit": source_commit.lower(),
        "checks": {
            name: {"status": "NOT_RUN", "reviewer": "", "verified_on": "", "evidence_refs": []}
            for name in GATES
        },
    }


def _no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def load_record(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Evidence must be a regular JSON file <=64 KiB")
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_keys)
    if not isinstance(data, dict):
        raise ValueError("Evidence root must be an object")
    return data


def assess(record: dict, expected_sha: str) -> dict:
    if not re.fullmatch(r"[0-9a-fA-F]{40}", expected_sha):
        raise ValueError("expected SHA must be 40 hex characters")
    problems = []
    if set(record) != {"schema_version", "source_commit", "checks"}:
        problems.append("Root fields mismatch")
    if record.get("schema_version") != SCHEMA:
        problems.append("Schema mismatch")
    if record.get("source_commit") != expected_sha.lower():
        problems.append("Source SHA mismatch: evidence is not for the requested release")
    checks = record.get("checks")
    if not isinstance(checks, dict) or set(checks) != set(GATES):
        problems.append("Required gate inventory mismatch")
        checks = checks if isinstance(checks, dict) else {}
    gate_results = {}
    for name, label in GATES.items():
        item = checks.get(name)
        issue = None
        if not isinstance(item, dict) or set(item) != {"status", "reviewer", "verified_on", "evidence_refs"}:
            issue = "Missing or invalid evidence fields"
        elif item["status"] != "VERIFIED":
            issue = "Gate not independently verified"
        elif not isinstance(item["reviewer"], str) or not item["reviewer"].strip():
            issue = "Missing human reviewer"
        elif not isinstance(item["verified_on"], str):
            issue = "Missing review date"
        else:
            try:
                reviewed = date.fromisoformat(item["verified_on"])
                if reviewed > date.today():
                    issue = "Review date is in the future"
            except ValueError:
                issue = "Review date must be YYYY-MM-DD"
        if issue is None:
            refs = item["evidence_refs"]
            if not isinstance(refs, list) or not refs or any(
                not isinstance(r, str) or not r.strip() or len(r) > 512 for r in refs
            ):
                issue = "Missing bounded evidence reference"
        gate_results[name] = {"description": label, "result": "RECORDED" if issue is None else "BLOCKED"}
        if issue:
            problems.append(name + ": " + issue)
    return {
        "schema_version": SCHEMA,
        "source_commit": expected_sha.lower(),
        "decision": "READY_FOR_SELLER_FINAL_REVIEW" if not problems else "BLOCKED_NOT_APPROVED_FOR_SALE",
        "automated_legal_or_human_certification": False,
        "gates": gate_results,
        "issues": problems,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="REA_Web seller evidence ledger (not a legal clearance)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--init", type=Path, help="create an empty evidence ledger, never overwrite")
    group.add_argument("--check", type=Path, help="read and evaluate an existing evidence ledger")
    parser.add_argument("--source-sha", required=True, help="exact 40-character target Git commit")
    args = parser.parse_args(argv)
    try:
        if args.init is not None:
            doc = template(args.source_sha)
            with args.init.open("x", encoding="utf-8") as handle:
                json.dump(doc, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            print("CREATED_BLANK_LEDGER_NOT_APPROVED " + str(args.init))
            return 0
        report = assess(load_record(args.check), args.source_sha)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["decision"] == "READY_FOR_SELLER_FINAL_REVIEW" else 2
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("BLOCKED_NOT_APPROVED_FOR_SALE: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
