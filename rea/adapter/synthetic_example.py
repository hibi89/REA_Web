"""Reproducible self-authored REA v0.2 JSON preflight example (offline).

No customer artifacts, URL retrieval, backend execution, Docker, model calls,
frontend generation or real API activity. All example IDs are invented.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

from rea.adapter.frontend_bridge import SCHEMA as REVIEW_SCHEMA, make_review
from rea.adapter.response_preflight import INPUT_SCHEMA, review_synthetic_samples
from rea.safe_publish import publish_directory

# These small values are authored by this project; no real API or account data.
FAKE_FABLE = {
    "schema_version": "1.0",
    "target": {"input_url": "https://example.org/"},
    "scanned_at": "2026-11-03T00:00:00+00:00",
    "scan_mode": "static",
    "frontend": [], "backend_inferred": [], "infra": [],
    "api": {"endpoints": [], "candidates": [], "chart_candidates": []},
    "charts": [], "warnings": [],
}
FAKE_BACKEND = {
    "schema_version": "rea.backend_contract.v0.1",
    "status": "REVIEW_REQUIRED",
    "generation_allowed": False,
    "execution_performed": False,
    "input": {"sha256": "e" * 64},
    "api": {
        "endpoints": [
            {
                "path": path,
                "methods": ["GET"],
                "verification": "STATIC_DECLARATION_ONLY",
                "mount": "app_declaration",
            }
            for path in ("/api/jobs", "/api/metrics", "/api/jobs/{job_id}")
        ],
    },
}
FAKE_BINDINGS = {
    "list": {"path": "/api/jobs", "field": "items"},
    "metrics": {"path": "/api/metrics", "field": "__root__"},
    "detail": {"path": "/api/jobs/{job_id}", "field": "__root__"},
    "presentation": {
        "item": {"id": "id", "name": "name", "category": "category", "status": "status"},
        "metrics": {"total": "total", "completed": "completed", "pending": "pending"},
        "detail_fields": ["id", "name", "category", "status", "duration_ms"],
    },
}
FAKE_ROWS = [
    {"id": "EXAMPLE-001", "name": "Synthetic check", "category": "demo", "status": "done"},
    {"id": "EXAMPLE-002", "name": "Synthetic report", "category": "demo", "status": "pending"},
]


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True,
                       allow_nan=False) + "\n").encode("utf-8")


def make_example() -> tuple[bytes, bytes]:
    """Produce a deterministic review and versioned sample pair in memory."""
    review = make_review(FAKE_FABLE, FAKE_BACKEND, FAKE_BINDINGS)
    review_raw = _json_bytes(review)
    response_bodies = {
        "list": {"items": FAKE_ROWS},
        "metrics": {"total": 2, "completed": 1, "pending": 1},
        "detail": {**FAKE_ROWS[0], "duration_ms": 34},
    }
    sample = {
        "schema_version": INPUT_SCHEMA,
        "synthetic_only": True,
        "review_sha256": hashlib.sha256(review_raw).hexdigest(),
        "review_schema_version": REVIEW_SCHEMA,
        "backend_sha256": review["backend"]["sha256"],
        "selected_id": "EXAMPLE-001",
        "completed_statuses": ["done"],
        "pending_statuses": ["pending"],
        "list_coverage": "complete",
        "samples": {
            role: {
                "status": 200, "content_type": "application/json",
                "body": json.dumps(body, ensure_ascii=False, sort_keys=True,
                                   separators=(",", ":"), allow_nan=False),
            }
            for role, body in response_bodies.items()
        },
    }
    # Internal preflight is still review-only; never treat this as release.
    report = review_synthetic_samples(
        review, sample, review_sha256=sample["review_sha256"])
    if (report["status"] != "SYNTHETIC_PREFLIGHT_REVIEW_REQUIRED"
            or report["generation_allowed"] is not False
            or report["release_allowed"] is not False
            or report["customer_runtime_verified"] is not False):
        raise ValueError("synthetic preflight must remain review only")
    return review_raw, _json_bytes(sample)


def create_example(destination: Path) -> None:
    """Stage then publish exactly two new files; never overwrite a directory."""
    target = Path(destination).absolute()
    if not target.parent.is_dir() or target.parent.is_symlink():
        raise ValueError("existing regular parent directory required")
    if target.exists() or target.is_symlink():
        raise FileExistsError("output already exists")
    review_raw, sample_raw = make_example()
    with tempfile.TemporaryDirectory(prefix=".rea-v02-", dir=target.parent) as tmp:
        stage = Path(tmp) / "example"
        stage.mkdir()
        (stage / "review.json").write_bytes(review_raw)
        (stage / "synthetic_samples.json").write_bytes(sample_raw)
        publish_directory(stage, target)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate REA v0.2 synthetic-only offline sample")
    parser.add_argument("--out", type=Path, required=True,
                        help="NEW output directory for two self-authored JSON files")
    args = parser.parse_args(argv)
    try:
        create_example(args.out)
    except (OSError, ValueError):
        print("REA synthetic example refused: new local directory required", file=sys.stderr)
        return 2
    print(json.dumps({
        "status": "SELF_AUTHORED_SYNTHETIC_EXAMPLE_READY",
        "schema_version": INPUT_SCHEMA,
        "generated_files": ["review.json", "synthetic_samples.json"],
        "generation_allowed": False,
        "release_allowed": False,
        "customer_runtime_verified": False,
        "execution_performed": False,
        "network_performed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
