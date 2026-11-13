"""SITECRAFT AX P70: three authorized synthetic browser flows, atomic delivery.

Build only after SHA-pinned local fixtures, separate owner CSV, and three
case-specific approval digests pass. The tokens are synthetic-test acknowledgments
and are NOT authenticated legal permission or customer acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

from rea.safe_publish import publish_directory
from rea.sitecraft_ax import _local_input, _unique_pairs, SHA, WebsiteReviewError
from rea.website_p70 import CASES, inspect_local, build_reviewed

SCHEMA = "sitecraft.p70.synthetic.v1"
MAX_SCOPE_BYTES = 16 * 1024
SCOPE_KEYS = frozenset({
    "schema", "product", "mode", "sites", "owner_csv", "owner_sha256",
    "mapping", "permission", "approval", "external_network_allowed",
    "commercial_release_allowed",
})
SITE_KEYS = frozenset({"case", "reference_html", "reference_sha256",
                       "approved_review_digest"})


def _read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise WebsiteReviewError("Scope must be a regular, non-symlink JSON file")
    if not 0 < path.stat().st_size <= MAX_SCOPE_BYTES:
        raise WebsiteReviewError("Scope exceeds safe size limit")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
    try:
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as handle:
            raw = handle.read(MAX_SCOPE_BYTES + 1)
    except OSError as exc:
        raise WebsiteReviewError("Cannot safely open scope") from exc
    if not raw or len(raw) > MAX_SCOPE_BYTES:
        raise WebsiteReviewError("Scope exceeds safe byte limit")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise WebsiteReviewError("Scope must contain valid UTF-8 JSON") from exc
    return data


def read_scope(scope_path: Path, *, require_approval: bool) -> tuple[dict, Path, list[tuple[dict, Path]]]:
    """Validate all three local sites and the owner data before any output."""
    path = Path(scope_path)
    data = _read_json(path)
    if not isinstance(data, dict) or set(data) != SCOPE_KEYS:
        raise WebsiteReviewError("Unsupported SITECRAFT scope keys")
    if (data["schema"] != SCHEMA or data["product"] != "SITECRAFT AX"
            or data["mode"] != "three_synthetic_local_browser_cases"
            or data["permission"] != "YES_OWNER_AUTHORIZED_LOCAL_FIXTURE"
            or data["approval"] != "APPROVE_SYNTHETIC_ONLY"
            or data["external_network_allowed"] is not False
            or data["commercial_release_allowed"] is not False):
        raise WebsiteReviewError("Local-only synthetic permission and HOLD required")
    mapping = data["mapping"]
    if (not isinstance(mapping, dict) or set(mapping) != {"id", "title", "category"}
            or any(not isinstance(v, str) or not v or len(v) > 80 for v in mapping.values())
            or len(set(mapping.values())) != 3):
        raise WebsiteReviewError("Three distinct explicit owner CSV fields required")
    if not isinstance(data["owner_sha256"], str) or not SHA.fullmatch(data["owner_sha256"]):
        raise WebsiteReviewError("Explicit owner CSV digest required")
    owner = _local_input(path.parent, data["owner_csv"], ".csv")
    if hashlib.sha256(owner.read_bytes()).hexdigest() != data["owner_sha256"]:
        raise WebsiteReviewError("Owner CSV SHA mismatch")
    sites = data["sites"]
    if not isinstance(sites, list) or len(sites) != 3:
        raise WebsiteReviewError("Exactly three local sites required")
    parsed = []
    seen_names, seen_cases = set(), set()
    for site in sites:
        if not isinstance(site, dict) or set(site) != SITE_KEYS:
            raise WebsiteReviewError("Invalid site contract")
        case = site["case"]
        if not isinstance(case, str) or case not in CASES or case in seen_cases:
            raise WebsiteReviewError("Require distinct search/filter/detail cases")
        seen_cases.add(case)
        name = site["reference_html"]
        if not isinstance(name, str) or name in seen_names:
            raise WebsiteReviewError("Distinct reference HTML files required")
        seen_names.add(name)
        html = _local_input(path.parent, name, ".html")
        digest = site["reference_sha256"]
        if not isinstance(digest, str) or not SHA.fullmatch(digest):
            raise WebsiteReviewError("Exact reference SHA256 digest required")
        if hashlib.sha256(html.read_bytes()).hexdigest() != digest:
            raise WebsiteReviewError("Reference HTML SHA mismatch")
        approved = site["approved_review_digest"]
        if not isinstance(approved, str) or (
            require_approval and not SHA.fullmatch(approved)
        ) or (not require_approval and approved != "" and not SHA.fullmatch(approved)):
            raise WebsiteReviewError("Approval digest missing or invalid")
        parsed.append((site, html))
    if seen_cases != set(CASES):
        raise WebsiteReviewError("Incomplete three-case scope")
    return data, owner, parsed


def inspect_three(scope_path: Path, *, astra_root: Path) -> dict:
    """Real Chromium observation; returns digests for explicit synthetic review."""
    data, _owner, sites = read_scope(scope_path, require_approval=False)
    results = {}
    for site, html in sites:
        receipt, before, after = inspect_local(
            html, fixture_sha256=site["reference_sha256"],
            case=site["case"], astra_root=astra_root,
        )
        if (receipt["status"] != "REVIEW_REQUIRED"
                or receipt["implementation_ready"] is not False
                or not before.startswith(b"\x89PNG")
                or not after.startswith(b"\x89PNG")):
            raise WebsiteReviewError("Astra/Chromium review gate changed")
        results[site["case"]] = {
            "reference_sha256": site["reference_sha256"],
            "review_digest": receipt["review_digest"],
            "status": receipt["status"],
            "feature": receipt["subject"]["feature"],
        }
    return {
        "product": data["product"],
        "gate": "P70_SYNTHETIC_INSPECTION_ONLY",
        "cases": results,
        "commercial_release": "HOLD",
        "customer_identity_verified": False,
    }


def build_three(scope_path: Path, out: Path, *, fable_root: Path,
                astra_root: Path) -> dict:
    """Atomically publish all three independently generated site E2Es or none."""
    data, owner, sites = read_scope(scope_path, require_approval=True)
    out = Path(out).absolute()
    if out.exists() or out.is_symlink():
        raise FileExistsError("SITECRAFT destination already exists")
    if not out.parent.is_dir() or out.parent.is_symlink():
        raise WebsiteReviewError("Destination parent must exist and be non-symlink")
    # Approvals bind to case-specific observed states and fixture hashes.
    # Perform a complete batch preflight BEFORE creating a staging directory.
    for site, html in sites:
        receipt, _before, _after = inspect_local(
            html, fixture_sha256=site["reference_sha256"],
            case=site["case"], astra_root=astra_root,
        )
        if receipt["review_digest"] != site["approved_review_digest"]:
            raise WebsiteReviewError("Stale or forged SITECRAFT review digest")
        if receipt["implementation_ready"] is not False:
            raise WebsiteReviewError("Unexpected automatic implementation approval")
    with tempfile.TemporaryDirectory(prefix=".sitecraft-p70-", dir=out.parent) as temp:
        bundle = Path(temp) / "bundle"
        bundle.mkdir()
        evidence = {}
        for site, html in sites:
            case = site["case"]
            dest = bundle / case
            result = build_reviewed(
                html, owner, dest,
                fixture_sha256=site["reference_sha256"],
                owner_sha256=data["owner_sha256"],
                case=case, approved_review_digest=site["approved_review_digest"],
                id_field=data["mapping"]["id"],
                title_field=data["mapping"]["title"],
                category_field=data["mapping"]["category"],
                fixture_permission="YES_LOCAL_FIXTURE",
                owner_approval="APPROVE_SYNTHETIC_ONLY",
                fable_root=fable_root, astra_root=astra_root,
            )
            if (result["status"] != "P70_SYNTHETIC_BROWSER_HOLD"
                    or result["browser_parity"] != "MATCHED_OBSERVED_SYNTHETIC_BEHAVIOR"
                    or result["commercial_release"] != "HOLD"):
                raise WebsiteReviewError("Independent browser parity did not pass")
            evidence[case] = {
                "reference_sha256": site["reference_sha256"],
                "review_digest": site["approved_review_digest"],
                "browser_parity": result["browser_parity"],
                "owner_rows": result["owner_rows"],
                "reference_behavior_auto_approved": False,
            }
        # Verify all source pins again before publishing any folder.
        updated, owner_now, sites_now = read_scope(scope_path, require_approval=True)
        if updated != data or owner_now != owner or sites_now != sites:
            raise WebsiteReviewError("Source/permission changed during batch")
        report = {
            "schema": SCHEMA, "product": "SITECRAFT AX",
            "status": "P70_SYNTHETIC_BROWSER_REVIEW_HOLD",
            "case_results": evidence,
            "actual_browser_cases": len(evidence),
            "reference_site_assets_reused": False,
            "customer_identity_verified": False,
            "external_site_scanned": False,
            "commercial_release": "HOLD",
        }
        (bundle / "sitecraft_p70_report.json").write_text(
            json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        publish_directory(bundle, out)
    return {
        "product": "SITECRAFT AX",
        "gate": "P70_SYNTHETIC_BROWSER_REVIEW_HOLD",
        "verified_browser_cases": sorted(evidence),
        "commercial_release": "HOLD",
        "published": out.name,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="SITECRAFT AX isolated three-site synthetic Chromium acceptance")
    p.add_argument("action", choices=("inspect", "build"))
    p.add_argument("--scope", required=True, type=Path)
    p.add_argument("--astra-root", required=True, type=Path)
    p.add_argument("--fable-root", type=Path)
    p.add_argument("--out", type=Path)
    args = p.parse_args(argv)
    try:
        if args.action == "inspect":
            result = inspect_three(args.scope, astra_root=args.astra_root)
        else:
            if args.fable_root is None or args.out is None:
                p.error("build requires --fable-root and --out")
            result = build_three(args.scope, args.out,
                                 fable_root=args.fable_root, astra_root=args.astra_root)
    except (ValueError, OSError, RuntimeError, KeyError) as error:
        p.exit(2, "SITECRAFT_P70_HOLD: " + type(error).__name__ + ": " + str(error) + "\n")
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
