"""Offline, review-only Docker image evidence inventory. Never contacts Docker or a registry.

Artifact hashes and Python lock/SBOM consistency are checked; cryptographic
signature validity, package licenses and runtime isolation are NOT established.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

SCHEMA = "rea.docker_image_evidence.v0.1"
IMAGE = re.compile(r"^[a-z0-9][a-z0-9._/-]*@sha256:[a-f0-9]{64}$")
IMAGE_SEGMENT = re.compile(r"^[a-z0-9]+(?:(?:[._]|__|-+)[a-z0-9]+)*$")
HEX = re.compile(r"^[a-f0-9]{64}$")
NAME = re.compile(r"^[a-z0-9][a-z0-9._-]{0,99}$")
REQUIRED = ("dockerfile", "wheel_lock", "spdx_sbom", "signature_receipt",
            "vulnerability_report", "license_review")
MAX_FILE = 2 * 1024 * 1024
MAX_WHEELS = 512
MAX_SPDX_PACKAGES = 4096


class UnsafeEvidence(ValueError):
    """Missing, unbound, unsafe or internally inconsistent supplied evidence."""


def _bytes(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_FILE:
        raise UnsafeEvidence("missing, symlinked or oversized local evidence")
    with path.open("rb") as file:
        data = file.read(MAX_FILE + 1)
    if len(data) > MAX_FILE:
        raise UnsafeEvidence("oversized local evidence")
    return data


def _json(data: bytes) -> object:
    # The manifest digest binds bytes, not their interpretation. Duplicate keys
    # or non-JSON constants can be interpreted differently by review tools.
    # Refuse ambiguous JSON at every nesting depth before trusting any fields.
    def unique_object(pairs: list[tuple[str, object]]) -> dict:
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError("duplicate JSON object key")
            obj[key] = value
        return obj

    def no_nonfinite(value: str) -> object:
        raise ValueError("nonstandard JSON numeric constant")

    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=no_nonfinite)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise UnsafeEvidence("invalid UTF-8 evidence JSON") from exc


def _normal(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.lower())


def _lock(data: bytes) -> dict[str, str]:
    obj = _json(data)
    if not isinstance(obj, dict) or set(obj) != {"wheels"} or not isinstance(obj["wheels"], list) or len(obj["wheels"]) > MAX_WHEELS:
        raise UnsafeEvidence("invalid pinned wheel lock format")
    wheels = {}
    for entry in obj["wheels"]:
        if (not isinstance(entry, dict) or set(entry) != {"name", "version", "sha256"}
                or not all(isinstance(entry[k], str) for k in entry)):
            raise UnsafeEvidence("invalid wheel lock entry")
        name = _normal(entry["name"])
        if (not NAME.fullmatch(name) or not entry["version"]
                or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.+!_-]{0,79}", entry["version"])
                or not HEX.fullmatch(entry["sha256"]) or name in wheels):
            raise UnsafeEvidence("unpinned or duplicate wheel entry")
        wheels[name] = entry["version"]
    if not {"fastapi", "uvicorn"}.issubset(wheels):
        raise UnsafeEvidence("FastAPI/Uvicorn runtime wheel lock missing")
    return wheels


def _sbom(data: bytes) -> dict[str, str]:
    obj = _json(data)
    if (not isinstance(obj, dict) or obj.get("spdxVersion") != "SPDX-2.3"
            or not isinstance(obj.get("packages"), list) or not obj["packages"]
            or len(obj["packages"]) > MAX_SPDX_PACKAGES):
        raise UnsafeEvidence("invalid SPDX package inventory")
    found = {}
    for entry in obj["packages"]:
        if not isinstance(entry, dict):
            raise UnsafeEvidence("invalid SPDX package entry")
        name, version, license_id = (entry.get("name"), entry.get("versionInfo"),
                                     entry.get("licenseConcluded"))
        if not all(isinstance(value, str) and value for value in (name, version, license_id)):
            raise UnsafeEvidence("SPDX package version/license evidence missing")
        normalized = _normal(name)
        if not NAME.fullmatch(normalized):
            raise UnsafeEvidence("invalid SPDX package name")
        # SPDX can include OS and Python packages; a repeated name with
        # conflicting versions is ambiguous and must be manually resolved.
        if normalized in found:
            raise UnsafeEvidence("duplicate or ambiguous SPDX package")
        found[normalized] = version
    return found


def _valid_image_ref(image: str) -> bool:
    if not isinstance(image, str) or len(image) > 256 or not IMAGE.fullmatch(image):
        return False
    repository = image.split("@sha256:", 1)[0]
    return all(IMAGE_SEGMENT.fullmatch(part) for part in repository.split("/"))


def inspect_local_evidence(evidence_dir: Path, manifest: Path, *,
                           expected_manifest_sha256: str) -> dict:
    """Validate local evidence references only. No call can grant runtime approval."""
    if not isinstance(expected_manifest_sha256, str) or not HEX.fullmatch(expected_manifest_sha256):
        raise UnsafeEvidence("independently supplied manifest SHA256 required")
    root = Path(evidence_dir)
    if root.is_symlink() or not root.is_dir():
        raise UnsafeEvidence("real evidence directory required")
    root = root.resolve(strict=True)
    manifest = Path(manifest)
    if manifest.is_symlink() or manifest.resolve(strict=True).parent != root:
        raise UnsafeEvidence("manifest must be a direct local evidence file")
    manifest_bytes = _bytes(manifest)
    if hashlib.sha256(manifest_bytes).hexdigest() != expected_manifest_sha256:
        raise UnsafeEvidence("manifest digest mismatch")
    obj = _json(manifest_bytes)
    if (not isinstance(obj, dict) or set(obj) != {"schema", "image_ref", "platform", "artifacts"}
            or obj["schema"] != SCHEMA or not _valid_image_ref(obj["image_ref"])
            or obj["platform"] not in ("linux/amd64", "linux/arm64")
            or not isinstance(obj["artifacts"], dict)
            or set(obj["artifacts"]) != set(REQUIRED)):
        raise UnsafeEvidence("invalid immutable image evidence manifest")
    evidence = {}
    used = {manifest.name}
    for kind in REQUIRED:
        detail = obj["artifacts"][kind]
        if (not isinstance(detail, dict) or set(detail) != {"file", "sha256"}
                or not isinstance(detail["file"], str)
                or not isinstance(detail["sha256"], str)
                or not HEX.fullmatch(detail["sha256"])):
            raise UnsafeEvidence("invalid evidence artifact descriptor")
        name = detail["file"]
        if (not name or name in used or name in (".", "..")
                or Path(name).name != name or "/" in name or "\\" in name
                or any(ord(char) < 32 for char in name)):
            raise UnsafeEvidence("duplicate or unsafe evidence file")
        used.add(name)
        path = root / name
        if path.is_symlink() or path.resolve(strict=True).parent != root:
            raise UnsafeEvidence("artifact must remain inside local evidence directory")
        data = _bytes(path)
        if hashlib.sha256(data).hexdigest() != detail["sha256"]:
            raise UnsafeEvidence("evidence artifact SHA256 mismatch")
        evidence[kind] = data
    wheels = _lock(evidence["wheel_lock"])
    spdx = _sbom(evidence["spdx_sbom"])
    unmatched = sorted(name for name, version in wheels.items() if spdx.get(name) != version)
    if unmatched:
        raise UnsafeEvidence("wheel lock and SPDX package inventory mismatch")
    return {
        "schema": SCHEMA,
        "status": "EVIDENCE_INVENTORY_REVIEW_REQUIRED",
        "image_ref": obj["image_ref"],
        "platform": obj["platform"],
        "evidence_files_sha256_checked": len(REQUIRED) + 1,
        "wheel_sbom_versions_consistent": True,
        "locked_python_packages": len(wheels),
        "sbom_packages_listed": len(spdx),
        "signature_cryptographically_verified": False,
        "complete_dependency_closure_verified": False,
        "license_rights_approved": False,
        "vulnerability_report_independently_verified": False,
        "docker_engine_isolation_tested": False,
        "image_execution_authorized": False,
        "customer_zip_execution_authorized": False,
        "commercial_release_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="REA Docker image evidence offline pre-review")
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.out.is_symlink() or args.out.exists():
            raise UnsafeEvidence("output already exists; never overwrite")
        report = inspect_local_evidence(args.evidence_dir, args.manifest,
                    expected_manifest_sha256=args.expected_manifest_sha256)
        with args.out.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, sort_keys=True, indent=2)
            stream.write("\n")
    except (UnsafeEvidence, OSError, TypeError) as exc:
        parser.exit(2, "[REA] REFUSED: " + str(exc) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
