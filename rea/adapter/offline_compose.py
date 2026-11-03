"""One local command: owner-authorized static ZIP + existing Fable report -> reviewed frontend.

Never imports/executes/extracts ZIP Python, fetches a URL, or serves a backend.
The explicit source-authorization and field-mapping confirmations are not
evidence of runtime behavior, IP rights, deployment safety, or sale approval.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from rea.adapter.backend_zip import UnsafeBackendZip, inspect_backend_zip
from rea.adapter.backend_schema import UnsafeSchema, inspect_backend_schema
from rea.adapter.frontend_bridge import (
    BridgeError, _read_json, generate_frontend, make_review,
)


def compose(backend_zip: Path, fable_report: Path, *, bindings: Path | None = None,
            visual: Path | None = None, destination: Path | None = None,
            source_authorized: bool = False,
            owner_confirmed: bool = False) -> dict:
    """Offline static inspection and optional source-only frontend publication.

    Passing source_authorized means the invoker has separate permission to
    inspect the exact local file; this function does not establish that right.
    """
    if not source_authorized:
        raise BridgeError("explicit --owner-authorized-source required before ZIP read")
    if destination is not None and not owner_confirmed:
        raise BridgeError("output requires explicit --owner-confirmed")
    if owner_confirmed and (destination is None or bindings is None):
        raise BridgeError("frontend generation requires --out and --bindings")
    if destination is None and owner_confirmed:
        raise BridgeError("--owner-confirmed requires output path")

    # All inputs are owner-selected local files. All operations remain offline.
    # Schema scan independently verifies the same ZIP hash as the initial
    # declaration scan; a changed archive is rejected before publication.
    backend = inspect_backend_zip(backend_zip)
    schema = inspect_backend_schema(backend_zip)
    review = make_review(
        _read_json(fable_report),
        backend,
        _read_json(bindings) if bindings is not None else None,
        visual=_read_json(visual) if visual is not None else None,
        schema=schema,
    )
    # Only app/router declarations with a statically visible mount are
    # candidates; static code cannot prove actual runtime endpoints.
    candidates = sorted({
        entry["path"] for entry in backend["api"]["endpoints"]
        if "GET" in entry["methods"] and entry["verification"] == "STATIC_DECLARATION_ONLY"
        and entry["mount"] in ("app_declaration", "local_router_mount_declaration")
    })
    result = {
        "schema_version": "rea.offline_frontend_composition.v0.1",
        "status": "OWNER_REVIEW_REQUIRED",
        "backend_sha256": backend["input"]["sha256"],
        "reference_origin": review["reference"]["origin"],
        "candidate_get_paths": candidates,
        "unresolved_backend_declarations": backend["api"]["unresolved_declarations"],
        "bindings_present": review["bindings"] is not None,
        "frontend_source_generated": False,
        "customer_runtime_verified": False,
        "source_rights_verified": False,
        "release_allowed": False,
        "network_performed": False,
        "backend_executed": False,
    }
    if destination is not None:
        generated = generate_frontend(review, destination, owner_confirmed=owner_confirmed)
        result["status"] = generated["status"]
        result["frontend_source_generated"] = True
        result["owner_bindings_confirmed"] = generated["owner_bindings_confirmed"]
        result["output_directory"] = str(Path(destination).absolute())
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="REA read-only, offline backend ZIP to independent frontend source"
    )
    parser.add_argument("--backend-zip", type=Path, required=True,
                        help="exact owner-authorized local FastAPI source ZIP")
    parser.add_argument("--fable", type=Path, required=True,
                        help="previously saved Fable 1.0 JSON; no URL is fetched")
    parser.add_argument("--bindings", type=Path,
                        help="manually confirmed three GET role/field mapping JSON")
    parser.add_argument("--visual", type=Path,
                        help="optional previously saved, origin-matched visual hints")
    parser.add_argument("--out", type=Path, help="NEW frontend-only output directory")
    parser.add_argument("--owner-authorized-source", action="store_true",
                        help="explicit permission for inspecting this exact local ZIP")
    parser.add_argument("--owner-confirmed", action="store_true",
                        help="explicit confirmation of these bindings for frontend generation")
    args = parser.parse_args(argv)
    try:
        result = compose(
            args.backend_zip, args.fable, bindings=args.bindings,
            visual=args.visual, destination=args.out,
            source_authorized=args.owner_authorized_source,
            owner_confirmed=args.owner_confirmed,
        )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    except (BridgeError, UnsafeBackendZip, UnsafeSchema, OSError, ValueError) as exc:
        # Never print raw ZIP contents or JSON response bodies on refusal.
        print("REA offline composition refused: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
