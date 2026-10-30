"""Private local one-file guided intake. No web uploads or implicit mapping.

Commands:
  python -m rea.guided inspect --csv samples/cafe_raw.csv
  python -m rea.guided wizard --csv samples/cafe_raw.csv --out ./out/demo
  python -m rea.guided build --csv ... --id-field ... --title-field ...
    --category-field ... --source-sha256 <preview hash> --confirm APPROVE --out ...
  python -m rea.guided pack --json ... [mapping fields] --out ./out/demo.zip
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from rea.mvp import DataError, REQUIRED, map_owner_fields, parse_input, preview_schema, source_sha256
from rea.orchestrator import build
from rea.delivery import create_delivery


def preflight(source: Path) -> dict:
    """No record values exported, only field names, counts, shape hints and SHA."""
    source = Path(source)
    first_digest = source_sha256(source)
    columns, rows = parse_input(source, require_semantics=False)
    digest = source_sha256(source)
    if digest != first_digest:
        raise DataError("Owner source changed during preview; inspect again")
    result = preview_schema(
        columns, rows,
        source_kind=("customer_supplied_json" if source.suffix.lower() == ".json"
                     else "customer_supplied_csv"),
    )
    result["source_sha256"] = digest
    result["guidance"] = (
        "Lexical types are unapproved. Select id/title/category from three "
        "different columns; owner must explicitly confirm. "
        "Never supply sensitive/private source data without permission."
    )
    return result


def approved_selection(source: Path, mapping: dict[str, str],
                       digest: str, confirmation: str) -> dict[str, str]:
    if confirmation != "APPROVE":
        raise DataError("Owner must explicitly type APPROVE; no default approval")
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise DataError("Expected exact SHA256 from preflight")
    report = preflight(source)
    if report["source_sha256"] != digest:
        raise DataError("Source SHA changed after preview; re-inspect and approve")
    columns, rows = parse_input(source, require_semantics=False)
    map_owner_fields(columns, rows, mapping)  # checks unique fields/ids/nonblank
    return mapping


def _source_parser(p: argparse.ArgumentParser) -> None:
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--csv", type=Path, help="One UTF-8 CSV")
    src.add_argument("--json", type=Path, help="One flat UTF-8 JSON array")


def _explicit_parser(p: argparse.ArgumentParser) -> None:
    p.add_argument("--id-field", required=True)
    p.add_argument("--title-field", required=True)
    p.add_argument("--category-field", required=True)
    p.add_argument("--source-sha256", required=True)
    p.add_argument("--confirm", required=True, help="Literal APPROVE after reviewing all fields")


def _print_preview(report: dict) -> None:
    print("LOCAL OWNER FILE - only header metadata shown; cell values omitted")
    print(f"Records: {report['row_count']}, SHA256: {report['source_sha256']}")
    for field in report["fields"]:
        print(f"  {field['name']}: {field['inferred_type']} "
              f"(values {field['present_count']}; empty {field['missing_count']})")
    print(report["guidance"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local owner-guided single CSV/JSON app generation")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "wizard", "build", "pack"):
        p = commands.add_parser(name)
        _source_parser(p)
        if name != "inspect":
            p.add_argument("--out", required=True, type=Path)
            p.add_argument("--name", default="REA owner-reviewed app")
        if name in {"build", "pack"}:
            _explicit_parser(p)
    args = parser.parse_args(argv)
    source = args.csv or args.json
    try:
        info = preflight(source)
        if args.command == "inspect":
            _print_preview(info)
            return 0
        if args.command == "wizard":
            _print_preview(info)
            print("Select exact column names. No suggestion is automatically approved.")
            mapping = {
                target: input(f"{target} source column: ").strip()
                for target in REQUIRED
            }
            print("Requested mapping:", json.dumps(mapping, ensure_ascii=False))
            print("Only use owner-authorized, nonsensitive data; no public hosting.")
            confirmation = input("Type APPROVE to create a local app (anything else cancels): ").strip()
            approved_selection(source, mapping, info["source_sha256"], confirmation)
            result = build(source, args.out, args.name, approved_mapping=mapping,
                           expected_source_sha256=info["source_sha256"])
        else:
            mapping = {
                "id": args.id_field, "title": args.title_field,
                "category": args.category_field,
            }
            approved_selection(source, mapping, args.source_sha256, args.confirm)
            if args.command == "build":
                result = build(source, args.out, args.name, approved_mapping=mapping,
                               expected_source_sha256=args.source_sha256)
            else:
                result = create_delivery(source, args.out, args.name,
                                         approved_mapping=mapping,
                                         expected_source_sha256=args.source_sha256)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, UnicodeError, ValueError, EOFError) as exc:
        parser.exit(2, f"OWNER_GUIDED_ERROR: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
