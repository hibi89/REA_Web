"""Offline bridge from an existing reviewed frontend plan to SYNTHETIC JSON examples.

Inputs must be self-authored test fixtures. This does not verify actual customer
ZIPs, responses, source rights, authentication, or authorize a generated app.
Never imports/runs a backend, contacts a URL, or reflects input values/errors.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import stat
import sys

from rea.adapter.frontend_bridge import SCHEMA as REVIEW_SCHEMA
from rea.adapter.response_contract import (
    InvalidResponseContract, _no_constant, _unique_pairs,
    validate_synthetic_response_contract,
)

SCHEMA = "rea.synthetic_response_preflight.v0.2"
INPUT_SCHEMA = "rea.synthetic_response_samples.v0.2"
REVIEW_MAX_BYTES = 2 * 1024 * 1024
SAMPLES_MAX_BYTES = 4 * 1024 * 1024
SHA256 = re.compile(r"^[a-f0-9]{64}$")


class UnsafeSyntheticPreflight(ValueError):
    """An input, policy declaration, or sample was refused (no user data echoed)."""


def _read_json_file(path: Path, limit: int) -> tuple[dict, str]:
    """Read one bounded local regular file, never a ZIP/source or directory."""
    if path.is_symlink():
        raise UnsafeSyntheticPreflight("invalid local input")
    try:
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
                raise UnsafeSyntheticPreflight("invalid local input")
            data = stream.read(limit + 1)
            after = os.fstat(stream.fileno())
            if (len(data) > limit or before.st_size != after.st_size
                    or before.st_mtime_ns != after.st_mtime_ns):
                raise UnsafeSyntheticPreflight("invalid local input")
    except OSError as exc:
        raise UnsafeSyntheticPreflight("invalid local input") from exc
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_pairs,
                           parse_constant=_no_constant)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise UnsafeSyntheticPreflight("invalid local JSON") from exc
    if not isinstance(value, dict):
        raise UnsafeSyntheticPreflight("JSON root must be object")
    return value, hashlib.sha256(data).hexdigest()


def _reviewed_bindings(review: dict) -> dict:
    """Require review-only provenance, never treat a pasted plan as authorization."""
    if (review.get("schema_version") != REVIEW_SCHEMA
            or review.get("status") != "OWNER_REVIEW_REQUIRED"
            or review.get("generation_allowed") is not False):
        raise UnsafeSyntheticPreflight("static review is not in a safe review-only state")
    backend = review.get("backend")
    if (not isinstance(backend, dict)
            or not isinstance(backend.get("sha256"), str)
            or not SHA256.fullmatch(backend["sha256"])
            or backend.get("runtime_verified") is not False
            or backend.get("response_schema_verified") is not False):
        raise UnsafeSyntheticPreflight("unverified backend provenance required")
    schema_review = review.get("schema_review")
    if (schema_review is not None
            and (not isinstance(schema_review, dict)
                 or schema_review.get("status") != "STATIC_AST_HINT_ONLY_NOT_RUNTIME_VERIFIED"
                 or schema_review.get("backend_sha256") != backend["sha256"]
                 or schema_review.get("bindings_autoapproved") is not False)):
        raise UnsafeSyntheticPreflight("unsafe AST review provenance")
    reference = review.get("reference")
    if not isinstance(reference, dict) or not isinstance(reference.get("origin"), str):
        raise UnsafeSyntheticPreflight("missing static reference provenance")
    bindings = review.get("bindings")
    if not isinstance(bindings, dict):
        raise UnsafeSyntheticPreflight("explicit reviewed bindings required")
    return bindings


def review_synthetic_samples(review: dict, envelope: dict, *, review_sha256: str) -> dict:
    """Connect the existing make_review() result to bounded example validation.

    The returned object is a non-authorization summary with zero input values,
    source URLs, paths, selected IDs, body strings, hashes or credentials.
    """
    if not isinstance(review, dict) or not isinstance(envelope, dict):
        raise UnsafeSyntheticPreflight("invalid review or samples")
    bindings = _reviewed_bindings(review)
    if (set(envelope) != {"schema_version", "synthetic_only", "selected_id",
                          "completed_statuses", "pending_statuses",
                          "list_coverage", "samples", "review_sha256",
                          "review_schema_version", "backend_sha256"}
            or envelope.get("schema_version") != INPUT_SCHEMA
            or envelope.get("synthetic_only") is not True):
        raise UnsafeSyntheticPreflight("explicit versioned synthetic-only sample schema required")
    # Bind to the exact review FILE bytes used by this invocation, not a
    # separately re-read path or an approximation from the selected API fields.
    # A digest detects accidental replacement; it is not a signature or proof
    # that this reviewer or customer owned the source.
    supplied = envelope.get("review_sha256")
    if (not isinstance(review_sha256, str) or SHA256.fullmatch(review_sha256) is None
            or not isinstance(supplied, str) or SHA256.fullmatch(supplied) is None
            or not hmac.compare_digest(supplied, review_sha256)
            or envelope.get("review_schema_version") != REVIEW_SCHEMA
            or envelope.get("backend_sha256") != review["backend"]["sha256"]):
        raise UnsafeSyntheticPreflight("synthetic source review identity or version mismatch")
    try:
        accepted = validate_synthetic_response_contract(
            bindings, envelope["samples"], selected_id=envelope["selected_id"],
            completed_statuses=envelope["completed_statuses"],
            pending_statuses=envelope["pending_statuses"],
            list_coverage=envelope["list_coverage"],
        )
    except (InvalidResponseContract, TypeError, KeyError) as exc:
        raise UnsafeSyntheticPreflight("synthetic response contract rejected") from exc
    return {
        "schema_version": SCHEMA,
        "status": "SYNTHETIC_PREFLIGHT_REVIEW_REQUIRED",
        "review_status": "OWNER_REVIEW_REQUIRED",
        "sample_contract_status": accepted["status"],
        "sample_rows": accepted["sample_rows"],
        "checked_roles": ["list", "metrics", "detail"],
        "generation_allowed": False,
        "release_allowed": False,
        "customer_runtime_verified": False,
        "source_rights_verified": False,
        "execution_performed": False,
        "network_performed": False,
        "limitations": [
            "synthetic_fixture_only",
            "source_rights_auth_and_runtime_unverified",
            "no_customer_zip_execution_or_docker",
            "no_deployment_or_commercial_approval",
        ],
    }


def _write_new_report(path: Path, report: dict) -> None:
    """Never overwrite any existing path; restrict report permissions on POSIX."""
    if path.is_symlink():
        raise UnsafeSyntheticPreflight("report destination unavailable")
    raw = (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2,
                      allow_nan=False) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    try:
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
    except OSError as exc:
        raise UnsafeSyntheticPreflight("report destination unavailable") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="REA self-authored SYNTHETIC JSON preflight; never customer acceptance")
    parser.add_argument("--review", type=Path, required=True,
                        help="existing frontend_bridge review JSON (preview mode)")
    parser.add_argument("--samples", type=Path, required=True,
                        help="bounded self-authored JSON body-string fixture")
    parser.add_argument("--synthetic-only", action="store_true", required=True,
                        help="mandatory explicit assertion: not real customer data")
    parser.add_argument("--out", type=Path, help="optional NEW non-secret report JSON")
    args = parser.parse_args(argv)
    try:
        if not args.synthetic_only or args.review == args.samples:
            raise UnsafeSyntheticPreflight("explicit separate synthetic input files required")
        reviewed, review_digest = _read_json_file(args.review, REVIEW_MAX_BYTES)
        samples, _ = _read_json_file(args.samples, SAMPLES_MAX_BYTES)
        report = review_synthetic_samples(
            reviewed, samples, review_sha256=review_digest,
        )
        if args.out is not None:
            _write_new_report(args.out, report)
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, allow_nan=False))
        return 0
    except UnsafeSyntheticPreflight:
        # Never echo a submitted field/value, absolute path or parser exception.
        print(json.dumps({
            "schema_version": SCHEMA,
            "status": "SYNTHETIC_PREFLIGHT_REFUSED",
            "generation_allowed": False,
            "release_allowed": False,
            "customer_runtime_verified": False,
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
