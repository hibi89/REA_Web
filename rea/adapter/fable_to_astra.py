"""Conservative Fable 5.1 -> Astra P4 review-only adapter.

Static/network/chart evidence is not proof of UI behavior. Record event
markers support inferred hypotheses only, never observed functional claims.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import urlsplit

MAX_BYTES = 2 * 1024 * 1024
MAX_MARKERS = 200
FILE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,99}$")
ID = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
TAG = re.compile(r"^[a-z][a-z0-9-]{0,30}$")


class InvalidFable(ValueError):
    """Unsupported or unsafe untrusted input."""


def obj(value: Any, name: str) -> dict:
    if not isinstance(value, dict):
        raise InvalidFable(f"{name} must be an object")
    return value


def arr(value: Any, name: str, limit: int = 10000) -> list:
    if not isinstance(value, list) or len(value) > limit:
        raise InvalidFable(f"{name} must be an array (maximum {limit})")
    return value


def origin(value: Any) -> str:
    if not isinstance(value, str) or len(value) > 2048:
        raise InvalidFable("invalid site URL")
    try:
        u = urlsplit(value)
        if (u.scheme not in ("https", "http") or not u.hostname
                or u.username is not None or u.password is not None
                or not u.netloc or any(c.isspace() for c in u.netloc)):
            raise InvalidFable("unsafe site URL")
        port = u.port
        host = u.hostname.lower()
        if ":" in host:
            host = f"[{host}]"
        # No URL path, query, fragment or credentials are retained.
        return f"{u.scheme}://{host}" + (f":{port}" if port is not None else "")
    except ValueError as exc:
        raise InvalidFable("unsafe site URL") from exc


def timestamp(value: Any) -> str:
    if not isinstance(value, str):
        raise InvalidFable("scanned_at missing")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.utcoffset() is None:
            raise ValueError("timezone required")
        return dt.isoformat()
    except ValueError as exc:
        raise InvalidFable("scanned_at requires timezone") from exc


def project_fable(source: dict, *, source_ref: str = "result.json") -> dict:
    """Generate unapproved hypotheses from real Fable 1.0 result structure.

    No metadata-only scan may yield an Astra UI observation. Record event
    markers are inferred navigation/filter possibilities without action effects.
    """
    if not FILE.fullmatch(source_ref) or source_ref.startswith("."):
        raise InvalidFable("source_ref requires a safe, non-hidden basename")
    d = obj(source, "result")
    if d.get("schema_version") != "1.0":
        raise InvalidFable("unsupported Fable schema_version")
    mode = d.get("scan_mode")
    if mode not in ("static", "runtime", "record"):
        raise InvalidFable("unsupported scan_mode")
    site = origin(obj(d.get("target"), "target").get("input_url"))
    scanned = timestamp(d.get("scanned_at"))
    api = obj(d.get("api"), "api")
    counts = {
        "observed_xhr_endpoints": len(arr(api.get("endpoints"), "api.endpoints")),
        "unverified_js_path_candidates": len(arr(api.get("candidates"), "api.candidates")),
        "chart_api_correlations_inferred": len(arr(api.get("chart_candidates", []), "api.chart_candidates")),
        "dom_chart_candidates": len(arr(d.get("charts"), "charts")),
    }
    record = obj(d.get("record"), "record") if mode == "record" else {}
    markers = arr(record.get("interactions", []), "record.interactions", MAX_MARKERS) if mode == "record" else []
    if mode == "record" and site not in arr(record.get("allowed_origins"), "record.allowed_origins", 20):
        raise InvalidFable("record scope excludes the scanned origin")

    observations, evidence, seen = [], [], set()
    ignored = 0
    for marker in markers:
        if not isinstance(marker, dict):
            ignored += 1
            continue
        kind, tag, ms = marker.get("type"), marker.get("tag"), marker.get("at_ms")
        pg, nav = marker.get("page_id"), marker.get("navigation_id")
        if (kind not in ("click", "change") or not isinstance(tag, str) or not TAG.fullmatch(tag)
                or type(ms) is not int or not (946684800000 <= ms <= 4102444800000)
                or not isinstance(pg, str) or not ID.fullmatch(pg)
                or not isinstance(nav, str) or not ID.fullmatch(nav)):
            ignored += 1
            continue
        key = pg, nav, kind, tag, ms
        if key in seen:
            ignored += 1
            continue
        seen.add(key)
        n = len(observations) + 1
        eid = f"ev_{n:04d}"
        evidence.append({
            "id": eid, "kind": "user_demonstration", "source_ref": source_ref,
            "captured_at": datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat(),
            "notes": "Fable marker only: no before/after UI state or causal effect was captured.",
        })
        observations.append({
            "id": f"ob_{n:04d}", "feature": "filter" if kind == "change" else "navigation",
            "title": "Unverified control effect",
            "claim": f"A {kind} marker on HTML {tag} was recorded; effect unknown. Feature category is a hypothesis.",
            "certainty": "inferred", "evidence_ids": [eid],
            "action": None, "before": {}, "after": {},
        })
    digest = hashlib.sha256(json.dumps(d, sort_keys=True, ensure_ascii=False,
                                       separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    bundle = ({
        "schema_version": "1.0", "site_url": site,
        "scope": "Fable authorized record markers; effects NOT observed",
        "recorded_at": scanned, "evidence": evidence, "observations": observations,
    } if observations else None)
    return {
        "schema_version": "rea.fable_astra.v0.1", "status": "REVIEW_REQUIRED",
        "source": {"engine": "fable51", "schema_version": "1.0", "scan_mode": mode,
                   "source_ref": source_ref, "sha256": digest, "site_origin": site},
        "technical_finding_counts": counts,
        "record_markers_accepted": len(observations), "record_markers_ignored": ignored,
        "astra_observation_bundle": bundle, "astra_functional_spec_draft": None,
        "astra_contract_validation": "NOT_RUN",
        "unknowns": ["actual_ui_effect", "real_chart_api_lineage", "original_metric_formulas",
                     "owner_db_api_mapping", "source_rights_review"],
        "approved_semantic_bindings": [], "generation_allowed": False,
        "implementation_ready": False, "db_api_mapping_status": "not_started",
    }


def verify_astra(projected: dict) -> dict:
    """Validate against the pinned *actual* Astra models, not lookalikes."""
    try:
        from astra_contracts.observation import ObservationBundle
        from astra_contracts.functional_spec import FunctionalSpecDraft, derive_spec
    except ImportError as exc:
        raise RuntimeError("Astra not importable; checkout pinned import/astra-p4-b3166b6 and add engines/astra_p4 to PYTHONPATH") from exc
    raw = projected["astra_observation_bundle"]
    if raw is None:
        projected["astra_contract_validation"] = "NO_UI_OBSERVATIONS"
        return projected
    bundle = ObservationBundle.model_validate(raw)
    spec = FunctionalSpecDraft.model_validate(derive_spec(bundle).model_dump(mode="json"))
    if spec.implementation_ready or spec.db_api_mapping_status != "not_started" or spec.candidate_features:
        raise RuntimeError("Astra unexpectedly approved/promoted an inferred feature")
    projected["astra_observation_bundle"] = bundle.model_dump(mode="json")
    projected["astra_functional_spec_draft"] = spec.model_dump(mode="json")
    projected["astra_contract_validation"] = "VALIDATED"
    return projected


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Fable 5.1 -> unapproved Astra evidence/spec proposal")
    p.add_argument("input", type=Path)
    p.add_argument("--astra-root", type=Path, help="pinned engines/astra_p4 directory")
    p.add_argument("--preview-only", action="store_true", help="unvalidated review preview; NO Astra spec")
    args = p.parse_args(argv)
    try:
        if args.input.is_symlink():
            raise InvalidFable("symlink input refused")
        if args.input.stat().st_size > MAX_BYTES:
            raise InvalidFable("input exceeds 2 MiB")
        d = json.loads(args.input.read_text(encoding="utf-8"))
        if args.astra_root:
            sys.path.insert(0, str(args.astra_root.resolve()))
        result = project_fable(d, source_ref=args.input.name)
        if not args.preview_only:
            verify_astra(result)
    except (OSError, UnicodeError, ValueError, RuntimeError, ImportError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
