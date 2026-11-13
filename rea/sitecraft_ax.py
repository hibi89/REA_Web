"""SITECRAFT AX P50. Local synthetic-only Fable/Astra/REA Pro vertical slice.

A synthetic approval token is not proof of legal rights or a customer identity.
Never scan a public URL, copy reference assets, or grant production release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re

from rea.website_rebuild import WebsiteReviewError, rebuild_local_fixture

SCHEMA = "sitecraft.p50.synthetic.v1"
KEYS = frozenset(("schema", "product", "mode", "reference_html",
                  "reference_sha256", "owner_csv", "owner_sha256", "mapping",
                  "permission", "approval", "external_network_allowed",
                  "commercial_release_allowed"))
MAX_BYTES = 16384
SHA = re.compile(r"[0-9a-f]{64}\Z")


def _unique_pairs(pairs):
    value = {}
    for k, v in pairs:
        if k in value:
            raise WebsiteReviewError("Duplicate contract keys")
        value[k] = v
    return value


def _local_input(base: Path, name, suffix: str) -> Path:
    if not isinstance(name, str) or not 1 <= len(name) <= 200:
        raise WebsiteReviewError("Input path must be short and relative")
    if any(x in name for x in ("\\", ":", "\x00")):
        raise WebsiteReviewError("Windows paths and URL schemes forbidden")
    rel = PurePosixPath(name)
    if rel.is_absolute() or any(x in (".", "..", "") for x in name.split("/")):
        raise WebsiteReviewError("Path traversal forbidden")
    if rel.suffix.lower() != suffix:
        raise WebsiteReviewError("Input extension is not allowed")
    target = base / rel
    if target.is_symlink() or not target.is_file():
        raise WebsiteReviewError("Input must be an existing non-symlink file")
    if not target.resolve().is_relative_to(base.resolve()):
        raise WebsiteReviewError("Input escapes approved folder")
    return target


def read_contract(contract_path: Path) -> tuple[dict, Path, Path]:
    path = Path(contract_path)
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_BYTES:
        raise WebsiteReviewError("Invalid contract file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
    try:
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as handle:
            raw = handle.read(MAX_BYTES + 1)
    except OSError as error:
        raise WebsiteReviewError("Cannot open contract safely") from error
    if not raw or len(raw) > MAX_BYTES:
        raise WebsiteReviewError("Contract exceeds byte limit")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise WebsiteReviewError("Invalid UTF-8 JSON contract") from error
    if not isinstance(data, dict) or set(data) != KEYS:
        raise WebsiteReviewError("Contract schema keys mismatch")
    if (data["schema"] != SCHEMA or data["product"] != "SITECRAFT AX"
            or data["mode"] != "synthetic_local_static_only"
            or data["permission"] != "YES_OWNER_AUTHORIZED_LOCAL_FIXTURE"
            or data["approval"] != "APPROVE_SYNTHETIC_ONLY"
            or data["external_network_allowed"] is not False
            or data["commercial_release_allowed"] is not False):
        raise WebsiteReviewError("Only authorized synthetic scope and HOLD allowed")
    mapping = data["mapping"]
    if (not isinstance(mapping, dict) or set(mapping) != {"id", "title", "category"}
            or any(not isinstance(v, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,79}", v)
                   for v in mapping.values()) or len(set(mapping.values())) != 3):
        raise WebsiteReviewError("Three distinct owner-provided column mappings required")
    if any(not isinstance(data[k], str) or not SHA.fullmatch(data[k])
           for k in ("reference_sha256", "owner_sha256")):
        raise WebsiteReviewError("Both explicit SHA256 hashes required")
    html = _local_input(path.parent, data["reference_html"], ".html")
    csv = _local_input(path.parent, data["owner_csv"], ".csv")
    if hashlib.sha256(html.read_bytes()).hexdigest() != data["reference_sha256"]:
        raise WebsiteReviewError("Reference SHA mismatch")
    if hashlib.sha256(csv.read_bytes()).hexdigest() != data["owner_sha256"]:
        raise WebsiteReviewError("Owner CSV SHA mismatch")
    return data, html, csv


def build_p50(contract: Path, out: Path, *, fable_root: Path, astra_root: Path) -> dict:
    data, html, csv = read_contract(contract)
    out = Path(out)
    if out.exists() or out.is_symlink():
        raise FileExistsError("Output exists: no overwrite")
    result = rebuild_local_fixture(
        html, csv, out,
        fixture_sha256=data["reference_sha256"],
        owner_sha256=data["owner_sha256"],
        id_field=data["mapping"]["id"],
        title_field=data["mapping"]["title"],
        category_field=data["mapping"]["category"],
        fixture_permission="YES_LOCAL_FIXTURE",
        owner_approval="APPROVE",
        fable_root=Path(fable_root),
        astra_root=Path(astra_root),
    )
    if (result.get("status") != "P50_SYNTHETIC_REVIEW_HOLD"
            or result.get("fable_requests") != 1
            or result.get("astra_draft_unapproved") is not True):
        raise WebsiteReviewError("Upstream Fable/Astra/Pro gate changed; HOLD")
    return {"product": "SITECRAFT AX", "gate": "P50_SYNTHETIC_ONLY",
            "fable_local_get_count": 1, "approved_synthetic_rows": result["rows"],
            "site_behavior_approved": False, "customer_identity_verified": False,
            "commercial_release": "HOLD", "output": result["output"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description="SITECRAFT AX P50 safe synthetic local-only vertical slice")
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--fable-root", required=True, type=Path)
    parser.add_argument("--astra-root", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        value = build_p50(args.contract, args.out, fable_root=args.fable_root, astra_root=args.astra_root)
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        parser.exit(2, f"SITECRAFT HOLD: {error}\n")
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
