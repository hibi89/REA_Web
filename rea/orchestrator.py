"""REA_Web Day2: customer CSV -> independent local app, optional Fable review.

The application is generated *only* from the owner-provided CSV. The Fable
artifact is never a mapping authority, source of app data, or generation gate.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

from rea.adapter.fable_to_astra import MAX_BYTES, InvalidFable, project_fable, verify_astra
from rea.mvp import DataError, generate, parse_input
from rea.safe_publish import publish_directory


def _fable_review(source: Path, astra_root: Path | None) -> dict:
    if source.is_symlink() or not source.is_file() or source.stat().st_size > MAX_BYTES:
        raise InvalidFable("Fable input must be an existing regular JSON file, max 2 MiB, not a symlink")
    if astra_root is not None:
        root = astra_root.resolve()
        if not (root / "astra_contracts" / "observation.py").is_file():
            raise InvalidFable("Invalid --astra-root: expected pinned astra_contracts directory")
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
    data = json.loads(source.read_text(encoding="utf-8"))
    review = verify_astra(project_fable(data, source_ref=source.name))
    if (review["status"] != "REVIEW_REQUIRED"
            or review["generation_allowed"] or review["implementation_ready"]
            or review["approved_semantic_bindings"]
            or review["db_api_mapping_status"] != "not_started"):
        raise RuntimeError("Unsafe Fable/Astra approval state")
    return review


def build(csv_file: Path, output: Path, name: str = "REA local app",
          *, fable_result: Path | None = None, astra_root: Path | None = None) -> dict:
    """Build with no production network, DB/API access, or source mutations.

    Parse both inputs before touching destination. Stage full deliverable on
    the destination filesystem; publish at the end without intentional overwrite.
    """
    csv_file = Path(csv_file)
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Output already exists: {output}")
    if not name.strip() or len(name) > 100:
        raise DataError("App name must be 1 to 100 characters")
    # Validate before creating a staging directory (also bounds CSV size/rows).
    parse_input(csv_file)
    review = _fable_review(Path(fable_result), astra_root) if fable_result is not None else None
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".rea-orchestrator-", dir=output.parent) as temp:
        project = Path(temp) / "app"
        manifest = generate(csv_file, project, name)
        # Report is sibling to the executable app and not mounted as a web route.
        manifest["generation_input"] = "customer_supplied_json_only" if csv_file.suffix.lower() == ".json" else "customer_supplied_csv_only"
        manifest["semantic_mapping_status"] = "not_approved"
        manifest["fable_review"] = {
            "status": "REVIEW_REQUIRED", "used_for_generation": False,
            "validation": review["astra_contract_validation"],
            "source_sha256": review["source"]["sha256"],
        } if review is not None else {
            "status": "NOT_REQUESTED", "used_for_generation": False,
        }
        (project / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        if review is not None:
            folder = project / "review"
            folder.mkdir()
            (folder / "fable_review.json").write_text(
                json.dumps(review, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                encoding="utf-8",
            )
            (folder / "README.md").write_text(
                "# Reference evidence — REVIEW_REQUIRED\n\n"
                "Offline sanitized proposal from a separate Fable result. "
                "It was NOT used to generate or map the customer app. "
                "No observed UI effects, backend, metric formula or customer "
                "ownership can be concluded from these hints. Keep the input "
                "JSON privately for future provenance checks; it is not shipped.\n",
                encoding="utf-8",
            )
        with (project / "README.md").open("a", encoding="utf-8") as readme:
            readme.write(
                "\nREA Day5: generated solely from one supplied CSV or JSON file. No reference "
                "website information was used for app data or business logic.\n"
                "Any Fable review is stored in ./review (not served by FastAPI), "
                "remains REVIEW_REQUIRED and is not an approved mapping.\n"
            )
        # Never intentionally replace a file/directory supplied by the owner.
        if output.exists() or output.is_symlink():
            raise FileExistsError(f"Output already exists: {output}")
        publish_directory(project, output)
        return manifest


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build read-only localhost app from one CSV or JSON owner input")
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--csv", type=Path)
    source.add_argument("--json", type=Path)
    p.add_argument("--out", type=Path, required=True, help="New output directory; cannot exist")
    p.add_argument("--name", default="REA local app")
    p.add_argument("--fable-result", type=Path, help="Existing Fable 1.0 JSON (never a live URL)")
    p.add_argument("--astra-root", type=Path, help="Pinned Astra contracts checkout for optional Fable validation")
    args = p.parse_args(argv)
    try:
        result = build(args.csv or args.json, args.out, args.name,
                       fable_result=args.fable_result, astra_root=args.astra_root)
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        p.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
