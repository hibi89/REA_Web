#!/usr/bin/env python3
"""Validate vendored files against upstream Git blob SHA manifests (stdlib only)."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "fable51": (88, "bbe72c0acd3a3e355062d6bd0d866af33e5274b0", 8),
    "astra_p4": (103, "b3166b67604381a9d2afd41667b65f9a9b103b37", 9),
}


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def check_vendor(vendor: str, *, allow_absent: bool = False) -> int:
    expected_count, source_commit, expected_batches = EXPECTED[vendor]
    folder = (ROOT / "engines" / vendor)
    if not folder.is_dir():
        if allow_absent:
            print(f"SKIP {vendor}: vendor not yet merged into this branch")
            return 0
        raise ValueError(f"{vendor}: missing vendor directory")
    archive = sorted((folder / "provenance").glob("BATCH_*.json"))
    if len(archive) != expected_batches:
        raise ValueError(f"{vendor}: expected {expected_batches} manifests, got {len(archive)}")
    seen: set[str] = set()
    base = folder.resolve()
    for manifest in archive:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        if payload.get("source_commit") != source_commit:
            raise ValueError(f"{manifest.name}: source commit mismatch")
        checks = payload.get("upstream_github_git_blob_sha")
        if not isinstance(checks, dict) or not checks:
            raise ValueError(f"{manifest.name}: missing blob mapping")
        for name, expected_sha in checks.items():
            sub = Path(name)
            if sub.is_absolute() or ".." in sub.parts or "\\" in name or name in seen:
                raise ValueError(f"unsafe or duplicate vendor path: {name}")
            seen.add(name)
            path = (folder / sub).resolve()
            if not path.is_relative_to(base) or not path.is_file():
                raise ValueError(f"missing or escaped vendor file: {name}")
            actual = git_blob_sha(path.read_bytes())
            if actual != expected_sha:
                raise ValueError(f"{vendor}/{name}: blob hash mismatch")
    if len(seen) != expected_count:
        raise ValueError(f"{vendor}: expected {expected_count} source files, found {len(seen)}")
    print(f"PASS {vendor}: {len(seen)}/{expected_count} pinned Git blobs match {source_commit[:12]}")
    return len(seen)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-absent", action="store_true")
    parser.add_argument("--vendor", choices=["fable51", "astra_p4"], action="append")
    args = parser.parse_args()
    for name in (args.vendor or list(EXPECTED)):
        check_vendor(name, allow_absent=args.allow_absent)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
