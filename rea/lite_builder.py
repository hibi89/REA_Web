"""REA WEB Lite: approved owner input -> one offline self-contained HTML file.

Uses the Pro parser and explicit mapping rules. Never alters a source or Pro app.
Do not run on private/customer data without permission.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

from rea.mvp import (
    DataError, MAX_BYTES, MAX_COLUMNS, MAX_ROWS,
    parse_input, map_owner_fields, source_sha256,
)

VERSION = "rea-lite-v1"
THEMES = ("cafe", "inventory", "office")
TEMPLATE = Path(__file__).with_name("lite_assets") / "template.html"


def safe_json(data: dict) -> str:
    """Safe inside application/json script, including end-tag and U+2028/2029."""
    return (json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            .replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026").replace("\u2028", "\\u2028")
            .replace("\u2029", "\\u2029"))


def inspect(source: Path) -> dict:
    """Report schema and SHA, no record values or absolute source path."""
    first = source_sha256(source)
    columns, rows = parse_input(source, require_semantics=False)
    if source_sha256(source) != first:
        raise DataError("Source changed during inspection")
    return {"sha256": first, "columns": columns, "row_count": len(rows),
            "limits": {"max_bytes": MAX_BYTES, "max_rows": MAX_ROWS,
                       "max_columns": MAX_COLUMNS}}


def build(source: Path, output: Path, *, mapping: dict[str, str],
          approved_sha: str, confirmation: str, theme: str = "cafe",
          title: str = "내 데이터 카탈로그") -> dict:
    source, output = Path(source), Path(output)
    if theme not in THEMES:
        raise DataError("Unknown theme")
    if not title or len(title) > 100 or any(ord(c) < 32 for c in title):
        raise DataError("Title must be 1..100 printable characters")
    if confirmation != "APPROVE" or len(approved_sha) != 64 or any(c not in "0123456789abcdef" for c in approved_sha):
        raise DataError("Explicit APPROVE and inspected SHA256 required")
    if output.suffix.lower() != ".html" or output.exists() or output.is_symlink():
        raise DataError("Output must be a new .html file; overwrite refused")
    start_sha = source_sha256(source)
    if start_sha != approved_sha:
        raise DataError("Source changed since inspection")
    source_columns, raw = parse_input(source, require_semantics=False)
    canonical_columns, records = map_owner_fields(source_columns, raw, mapping)
    if source_sha256(source) != approved_sha:
        raise DataError("Source changed during processing")
    payload = {
        "version": VERSION, "title": title, "theme": theme,
        "sourceColumns": source_columns,
        "mapping": {field: mapping[field] for field in ("id", "title", "category")},
        "columns": canonical_columns, "records": records,
        "limits": {"bytes": MAX_BYTES, "rows": MAX_ROWS, "columns": MAX_COLUMNS},
    }
    source_html = TEMPLATE.read_text(encoding="utf-8")
    if source_html.count("__REA_PAYLOAD_JSON__") != 1:
        raise RuntimeError("Invalid immutable Lite HTML template")
    result = source_html.replace("__REA_PAYLOAD_JSON__", safe_json(payload))
    if output.parent.exists() and not output.parent.is_dir():
        raise DataError("Output parent is not a directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, staged = tempfile.mkstemp(prefix=".rea-lite-", suffix=".tmp", dir=output.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(result)
            handle.flush()
            os.fsync(handle.fileno())
        # Exclusive file creation: never race-overwrite a customer HTML.
        try:
            os.link(staged, output)
        except FileExistsError as exc:
            raise DataError("Output appeared during generation; overwrite refused") from exc
        except OSError as exc:
            raise DataError("Cannot publish Lite HTML safely") from exc
    finally:
        Path(staged).unlink(missing_ok=True)
    return {"status": "CREATED_UNAPPROVED_FOR_SALE", "path": str(output),
            "rows": len(records), "theme": theme, "source_sha256": approved_sha}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="REA Lite offline HTML generator")
    sub = parser.add_subparsers(dest="action", required=True)
    i = sub.add_parser("inspect")
    i.add_argument("--source", type=Path, required=True)
    b = sub.add_parser("build")
    b.add_argument("--source", type=Path, required=True)
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--id-field", required=True)
    b.add_argument("--title-field", required=True)
    b.add_argument("--category-field", required=True)
    b.add_argument("--source-sha256", required=True)
    b.add_argument("--confirm", required=True)
    b.add_argument("--theme", choices=THEMES, default="cafe")
    b.add_argument("--name", default="내 데이터 카탈로그")
    args = parser.parse_args(argv)
    try:
        if args.action == "inspect":
            print(json.dumps(inspect(args.source), ensure_ascii=False, indent=2))
        else:
            result = build(args.source, args.out,
                mapping={"id": args.id_field, "title": args.title_field,
                         "category": args.category_field},
                approved_sha=args.source_sha256, confirmation=args.confirm,
                theme=args.theme, title=args.name)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (DataError, OSError, ValueError) as exc:
        print(f"REA_LITE_ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
