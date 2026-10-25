"""D12 offline installed-environment dependency and legal-file evidence.

Developer CI artifact ONLY. Not a wheel hash lock, license determination, security scan,
customer ZIP component, or evidence of ownership/redistribution rights.
"""
from __future__ import annotations

import argparse
from collections import deque
import hashlib
from importlib import metadata
import json
from pathlib import Path
import sys

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT_REQUIREMENTS = ("fastapi>=0.110,<1", "uvicorn>=0.27,<1")
LEGAL_PREFIXES = ("LICENSE", "LICENCE", "NOTICE", "COPYING")
MAX_LEGAL_BYTES = 1_000_000
MAX_LEGAL_ENTRIES = 100


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _legal_evidence(dist) -> dict:
    """Hash only legal file bytes; never publish their contents or absolute paths."""
    meta = dist.metadata
    declared = [str(x) for x in (meta.get_all("License-File") or [])]
    files = dist.files
    candidates = []
    if files is not None:
        for item in files:
            item_path = Path(str(item))
            if item_path.name.upper().startswith(LEGAL_PREFIXES) or str(item) in declared:
                candidates.append(str(item))
    candidates = sorted(set(candidates))
    results = []
    for relative in candidates[:MAX_LEGAL_ENTRIES]:
        item = Path(relative)
        entry = {"relative_path": relative}
        if item.is_absolute() or ".." in item.parts:
            entry["status"] = "UNSAFE_RELATIVE_PATH"
        else:
            try:
                path = Path(dist.locate_file(relative))
                if path.is_symlink():
                    entry["status"] = "SYMLINK_NOT_READ"
                elif not path.is_file():
                    entry["status"] = "FILE_MISSING"
                elif path.stat().st_size > MAX_LEGAL_BYTES:
                    entry["status"] = "FILE_TOO_LARGE_NOT_READ"
                else:
                    data = path.read_bytes()
                    entry.update(status="SHA256_OBSERVED", sha256=_sha256(data),
                                 byte_count=len(data))
            except (OSError, ValueError, TypeError):
                entry["status"] = "READ_ERROR"
        results.append(entry)
    metadata_text = None
    try:
        metadata_text = dist.read_text("METADATA")
    except (OSError, ValueError, TypeError):
        pass
    return {
        "declared_license_expression": meta.get("License-Expression"),
        "declared_license_legacy": (meta.get("License") or "")[:160],
        "declared_license_files": sorted(set(declared)),
        "file_list_available": files is not None,
        "legal_paths_truncated": len(candidates) > MAX_LEGAL_ENTRIES,
        "legal_file_evidence": results,
        "installed_metadata_sha256": (
            _sha256(metadata_text.encode("utf-8")) if metadata_text is not None else None
        ),
        "legal_contents_copied_to_artifact": False,
        "license_compliance_verdict": "UNKNOWN_NOT_GRANTED",
    }


def audit_environment(root_requirements=ROOT_REQUIREMENTS, lookup=None) -> dict:
    """Resolve currently active *base* metadata edges; report skipped/uncertain edges."""
    if lookup is None:
        lookup = metadata.distribution
    queue = deque()
    for raw in root_requirements:
        req = Requirement(raw)
        if req.marker is not None or req.extras:
            raise ValueError("Direct roots must be unconditional base distributions")
        queue.append((None, raw))
    observed = {}
    edges = []
    while queue:
        parent, raw = queue.popleft()
        edge = {"from": parent, "requirement": raw}
        try:
            req = Requirement(raw)
            name = canonicalize_name(req.name)
            edge["to"] = name
            edge["requested_extras"] = sorted(req.extras)
        except (ValueError, TypeError):
            edge["status"] = "UNPARSEABLE_REQUIREMENT"
            edges.append(edge)
            continue
        if req.marker is not None:
            try:
                active = req.marker.evaluate({"extra": ""})
            except (ValueError, TypeError, KeyError):
                edge["status"] = "UNKNOWN_MARKER_SEMANTICS"
                edges.append(edge)
                continue
            if not active:
                edge["status"] = ("SKIPPED_OPTIONAL_EXTRA" if "extra" in str(req.marker)
                                  else "SKIPPED_ENVIRONMENT_MARKER")
                edges.append(edge)
                continue
        edge["status"] = "ACTIVE_NEEDS_VERSION_CHECK"
        if req.extras:
            edge["extras_resolution"] = "NOT_RECURSIVELY_AUDITED_REVIEW_REQUIRED"
        edges.append(edge)
        if name in observed:
            continue
        try:
            dist = lookup(name)
        except metadata.PackageNotFoundError:
            observed[name] = {"name": name, "version": None, "status": "MISSING"}
            continue
        version = str(dist.version)
        record = {
            "name": name,
            "version": version,
            "status": "INSTALLED_METADATA_OBSERVED_ONLY",
            **_legal_evidence(dist),
        }
        observed[name] = record
        for dependency in dist.requires or []:
            queue.append((name, str(dependency)))

    for edge in edges:
        if edge["status"] != "ACTIVE_NEEDS_VERSION_CHECK":
            continue
        target = observed[edge["to"]]
        if target["version"] is None:
            edge["status"] = "MISSING"
        else:
            try:
                spec = Requirement(edge["requirement"]).specifier
                edge["status"] = ("VERSION_SATISFIES_DECLARATION"
                                  if spec.contains(target["version"], prereleases=True)
                                  else "VERSION_CONFLICT")
            except (ValueError, TypeError):
                edge["status"] = "VERSION_UNCERTAIN"
    unresolved = sorted(set(
        entry["status"] for entry in edges
        if entry["status"] in ("MISSING", "VERSION_CONFLICT", "VERSION_UNCERTAIN",
                               "UNPARSEABLE_REQUIREMENT", "UNKNOWN_MARKER_SEMANTICS")
    ))
    if any(e.get("requested_extras") for e in edges):
        unresolved.append("EXTRAS_NOT_FULLY_EXPANDED")
    if any(not record.get("legal_file_evidence") for record in observed.values()
           if record.get("status") == "INSTALLED_METADATA_OBSERVED_ONLY"):
        unresolved.append("NO_LEGAL_FILES_DISCOVERED")
    if any(not record.get("declared_license_expression")
           and not record.get("declared_license_legacy")
           for record in observed.values()
           if record.get("status") == "INSTALLED_METADATA_OBSERVED_ONLY"):
        unresolved.append("NO_LICENSE_DECLARATION")
    if any(not record.get("file_list_available", True)
           or record.get("legal_paths_truncated", False)
           or any(f["status"] != "SHA256_OBSERVED"
                  for f in record.get("legal_file_evidence", []))
           for record in observed.values()):
        unresolved.append("LEGAL_FILE_METADATA_INCOMPLETE")
    return {
        "schema_version": "rea.dependency_evidence.v0.1",
        "classification": "DEVELOPER_CI_INSTALLED_ENVIRONMENT_ONLY",
        "python_runtime": ".".join(map(str, sys.version_info[:3])),
        "platform": sys.platform,
        "root_requirements": list(root_requirements),
        "installed_distributions": [observed[k] for k in sorted(observed)],
        "requirement_edges": sorted(edges, key=lambda e: (
            str(e.get("from")), str(e.get("to")), e["requirement"])),
        "candidate_constraints": [
            name + "==" + record["version"]
            for name, record in sorted(observed.items())
            if record["version"] is not None
        ],
        "candidate_constraints_status": "NOT_A_LOCK_UNPINNED_WHEEL_HASHES_AND_MARKERS",
        "installed_metadata_hashes_are_not_wheel_archive_hashes": True,
        "wheel_downloads_or_hash_verification": "NOT_RUN_NO_NETWORK",
        "security_or_vulnerability_audit": "NOT_RUN",
        "source_redistribution_permission": "NOT_GRANTED",
        "commercial_license_clearance": "NOT_GRANTED",
        "legal_compliance_status": "UNKNOWN",
        "unresolved_resolution_issues": sorted(set(unresolved)),
        "customer_zip_unchanged": True,
        "network_calls_made_by_auditor": 0,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="No-network developer dependency evidence")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    report = audit_environment()
    # Exclusive open prevents accidental overwrite, including existing symlinks.
    with args.out.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({
        "classification": report["classification"],
        "distributions": len(report["installed_distributions"]),
        "unresolved_resolution_issues": report["unresolved_resolution_issues"],
        "commercial_license_clearance": report["commercial_license_clearance"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
