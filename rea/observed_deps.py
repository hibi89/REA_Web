"""Record CI-observed Python environment and reported license metadata only.

This is NOT a license compliance verdict, exact runtime lock, security or SPDX
audit. No network or customer data. Python packages are NOT bundled in REA ZIP.
"""
from __future__ import annotations

import argparse
from importlib import metadata
import json
from pathlib import Path
import sys

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

DIRECT = ("fastapi", "uvicorn")


def inventory() -> dict:
    encountered: dict[str, dict] = {}
    outstanding = list(DIRECT)
    while outstanding:
        name = canonicalize_name(outstanding.pop(0))
        if name in encountered:
            continue
        try:
            dist = metadata.distribution(name)
        except metadata.PackageNotFoundError:
            encountered[name] = {"name": name, "status": "MISSING", "version": None}
            continue
        meta = dist.metadata
        licenses = [
            x for x in (meta.get_all("Classifier") or [])
            if x.startswith("License ::")
        ]
        files = dist.files or []
        legal_files = [
            str(p) for p in files
            if any(z in str(p).upper() for z in ("LICENSE", "LICENCE", "NOTICE", "COPYING"))
        ][:30]
        encountered[name] = {
            "name": name,
            "version": dist.version,
            "status": "OBSERVED_METADATA_ONLY_NOT_LICENSE_CLEARED",
            "declared_license_expression": meta.get("License-Expression"),
            "declared_license_legacy": (meta.get("License") or "")[:160],
            "declared_license_classifiers": licenses[:20],
            "observed_legal_file_paths": legal_files,
            "legal_contents_reviewed": False,
        }
        for raw in dist.requires or []:
            try:
                requirement = Requirement(raw)
                if requirement.marker is None or requirement.marker.evaluate({"extra": ""}):
                    other = canonicalize_name(requirement.name)
                    if other not in encountered:
                        outstanding.append(other)
            except (ValueError, TypeError):
                # Leave a known uncertainty rather than silently claiming completeness.
                encountered[name]["requirement_parse_uncertain"] = True
    return {
        "schema_version": "rea.rc.python_environment.v0.1",
        "python_runtime": ".".join(map(str, sys.version_info[:3])),
        "platform": sys.platform,
        "direct_declared_ranges": {"fastapi": ">=0.110,<1", "uvicorn": ">=0.27,<1"},
        "exact_installed_versions_are_observations_not_customer_lock": True,
        "classification": "CI_ENVIRONMENT_ONLY",
        "commercial_license_clearance": "NOT_GRANTED",
        "wheels_bundled_in_delivery_zip": False,
        "transitive_licensing_and_vulnerabilities_reviewed": False,
        "distributions": [encountered[k] for k in sorted(encountered)],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Offline observed Python package metadata")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    report = inventory()
    with args.out.open("x", encoding="utf-8") as f:
        f.write(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "classification": report["classification"],
        "count": len(report["distributions"]),
        "direct": [
            {"name": x["name"], "version": x["version"]}
            for x in report["distributions"] if x["name"] in DIRECT
        ],
        "commercial_license_clearance": report["commercial_license_clearance"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
