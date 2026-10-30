"""REA_Web fast MVP: isolated CSV or flat JSON -> working local web app.

No remote URLs or production DB access. Run: python -m rea.mvp --csv samples/products.csv --out /tmp/rea-products
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
import re
import hashlib
import json
import os
import shutil
import sqlite3
import stat
import tempfile
from pathlib import Path

from rea.safe_publish import publish_directory

MAX_BYTES = 10 * 1024 * 1024
MAX_ROWS = 10_000
MAX_COLUMNS = 20
REQUIRED = ("id", "title", "category")
TEMPLATES = Path(__file__).resolve().parent / "templates"


class DataError(ValueError):
    """Invalid customer-supplied file. The original is never changed."""

def source_sha256(source: Path) -> str:
    """Hash a bounded, regular owner input without unbounded read_bytes()."""
    source = Path(source)
    if (source.suffix.lower() not in (".csv", ".json")
            or source.is_symlink() or not source.is_file()):
        raise DataError("Provide a regular .csv or .json source (not a symlink)")
    if source.stat().st_size > MAX_BYTES:
        raise DataError("Source exceeds 10 MiB")
    digest = hashlib.sha256()
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(source, flags)
    except OSError as exc:
        raise DataError("Cannot safely open owner source") from exc
    with os.fdopen(fd, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise DataError("Owner source must be a regular file")
        total = 0
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            total += len(chunk)
            if total > MAX_BYTES:
                raise DataError("Source exceeds 10 MiB")
            digest.update(chunk)
    if source.is_symlink():
        raise DataError("Owner source changed into a symlink")
    return digest.hexdigest()


def _validate_records(headers: list[str], records, *, label: str = "Row", require_semantics: bool = True) -> tuple[list[str], list[dict[str, str]]]:
    """One bounded row validator for CSV and JSON, preserving CSV behaviour."""
    if (len(headers) > MAX_COLUMNS or len(headers) != len(set(headers))
            or (require_semantics and not set(REQUIRED).issubset(headers))
            or any(not key or "\x00" in key or len(key) > 2000 for key in headers)):
        raise DataError("Required unique columns: id, title, category (maximum 20)")
    seen: set[str] = set()
    entries: list[dict[str, str]] = []
    for number, row in enumerate(records, start=2):
        if len(entries) >= MAX_ROWS:
            raise DataError("Input exceeds 10,000 rows")
        if not isinstance(row, dict) or set(row) != set(headers):
            raise DataError(f"{label} {number}: wrong columns")
        if any(type(value) is not str for value in row.values()):
            raise DataError(f"{label} {number}: every value must be a string")
        clean = {key: row[key].strip() for key in headers}
        if any("\x00" in value or len(value) > 2000 for value in clean.values()):
            raise DataError(f"{label} {number}: invalid cell")
        if require_semantics:
            for key in REQUIRED:
                if not clean[key]:
                    raise DataError(f"{label} {number}: missing {key}")
            if clean["id"] in seen:
                raise DataError(f"{label} {number}: duplicate id")
            seen.add(clean["id"])
        entries.append(clean)
    if not entries:
        raise DataError("Input must have at least one record")
    return headers, entries


def parse_csv(source: Path, *, require_semantics: bool = True) -> tuple[list[str], list[dict[str, str]]]:
    source = Path(source)
    if not source.is_file() or source.suffix.lower() != ".csv" or source.is_symlink():
        raise DataError("Provide an existing regular .csv file (not a symlink)")
    if source.stat().st_size > MAX_BYTES:
        raise DataError("CSV exceeds 10 MiB")
    try:
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, restkey="__extra", strict=True)
            if not reader.fieldnames:
                raise DataError("CSV must have a header row")
            headers = [key.strip() for key in reader.fieldnames]
            reader.fieldnames = headers
            return _validate_records(headers, reader, require_semantics=require_semantics)
    except (UnicodeError, csv.Error) as exc:
        raise DataError("Invalid UTF-8 CSV format") from exc


def _json_pairs(pairs):
    """Refuse duplicate JSON object keys instead of silently overwriting."""
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise DataError("Duplicate JSON object field")
        obj[key] = value
    return obj


def _reject_constant(value):
    raise DataError("Non-finite JSON numbers are unsupported")


def parse_json(source: Path, *, require_semantics: bool = True) -> tuple[list[str], list[dict[str, str]]]:
    """Strict array-of-flat-string-objects; never guess nested structures."""
    source = Path(source)
    if not source.is_file() or source.suffix.lower() != ".json" or source.is_symlink():
        raise DataError("Provide an existing regular .json file (not a symlink)")
    if source.stat().st_size > MAX_BYTES:
        raise DataError("JSON exceeds 10 MiB")
    try:
        records = json.loads(source.read_text(encoding="utf-8-sig"),
                             object_pairs_hook=_json_pairs, parse_constant=_reject_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise DataError("Invalid UTF-8 JSON format") from exc
    if not isinstance(records, list) or not records or len(records) > MAX_ROWS:
        raise DataError("JSON must be an array of 1 to 10,000 objects")
    first = records[0]
    if not isinstance(first, dict):
        raise DataError("JSON array elements must be flat objects")
    headers = list(first)
    if any(not isinstance(key, str) or key != key.strip() for key in headers):
        raise DataError("JSON field names must be nonblank and unpadded")
    return _validate_records(headers, records, label="Object", require_semantics=require_semantics)


def parse_input(source: Path, *, require_semantics: bool = True) -> tuple[list[str], list[dict[str, str]]]:
    """One accepted owner data file. Multiple-file joining remains unsupported."""
    ext = Path(source).suffix.lower()
    if ext == ".csv":
        return parse_csv(source, require_semantics=require_semantics)
    if ext == ".json":
        return parse_json(source, require_semantics=require_semantics)
    raise DataError("Data input must be one .csv or .json file")


INTEGER_RE = re.compile(r"-?(?:0|[1-9][0-9]{0,17})")
DECIMAL_RE = re.compile(r"-?(?:0|[1-9][0-9]{0,17})\.[0-9]{1,12}")


def _classify(value: str) -> str:
    """Lexical-only hint, never automatic semantic field mapping."""
    if INTEGER_RE.fullmatch(value):
        return "integer"
    if DECIMAL_RE.fullmatch(value):
        return "decimal"
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        try:
            date.fromisoformat(value)
            return "date"
        except ValueError:
            pass
    return "text"


def preview_schema(columns: list[str], rows: list[dict[str, str]], *, source_kind: str = "customer_supplied_csv") -> dict:
    """Unapproved shape hints; no cell samples, secrets or source URLs."""
    fields = []
    for column in columns:
        filled = [row[column] for row in rows if row[column] != ""]
        kinds = {_classify(value) for value in filled}
        if not kinds:
            kind = "unknown"
        elif kinds <= {"integer", "decimal"}:
            kind = "decimal" if "decimal" in kinds else "integer"
        elif len(kinds) == 1:
            kind = next(iter(kinds))
        else:
            kind = "mixed"
        fields.append({
            "name": column, "inferred_type": kind,
            "present_count": len(filled),
            "missing_count": len(rows) - len(filled),
        })
    return {
        "schema_version": "rea.csv_schema_preview.v0.1",
        "review_status": "UNAPPROVED",
        "source_kind": source_kind,
        "row_count": len(rows),
        "fields": fields,
        "approved_semantic_bindings": [],
    }



def map_owner_fields(
    headers: list[str], rows: list[dict[str, str]], mapping: dict[str, str]
) -> tuple[list[str], list[dict[str, str]]]:
    """Honor exactly the owner-confirmed 1-to-1 source columns. Never infer."""
    if (not isinstance(mapping, dict) or set(mapping) != set(REQUIRED)
            or any(type(v) is not str for v in mapping.values())
            or len(set(mapping.values())) != 3
            or any(v not in headers for v in mapping.values())):
        raise DataError("Mapping must name three distinct existing source fields")
    # An unused source column named a reserved target must not be silently lost.
    remaining = [h for h in headers if h not in mapping.values()]
    if any(h in REQUIRED for h in remaining):
        raise DataError("Unselected source column collides with a reserved target")
    columns = [*REQUIRED, *remaining]
    translated = [
        {**{target: row[mapping[target]] for target in REQUIRED},
         **{extra: row[extra] for extra in remaining}}
        for row in rows
    ]
    return _validate_records(columns, translated, label="Mapped row")


def generate(csv_file: Path, output: Path, name: str = "REA sample web app",
             *, approved_mapping: dict[str, str] | None = None,
             expected_source_sha256: str | None = None) -> dict:
    source = Path(csv_file).absolute()
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Output already exists: {output}")
    if not name.strip() or len(name) > 100:
        raise DataError("App name must be 1 to 100 characters")
    source_digest = source_sha256(source)
    if expected_source_sha256 is not None and source_digest != expected_source_sha256:
        raise DataError("Owner source changed since the approved field preview")
    if approved_mapping is None:
        columns, rows = parse_input(source)
    else:
        candidate_headers, candidate_rows = parse_input(source, require_semantics=False)
        columns, rows = map_owner_fields(candidate_headers, candidate_rows, approved_mapping)
    source_kind = "customer_supplied_json" if source.suffix.lower() == ".json" else "customer_supplied_csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".rea-staging-", dir=output.parent))
    try:
        db = sqlite3.connect(stage / "data.sqlite")
        try:
            db.executescript(
                "CREATE TABLE items (id TEXT PRIMARY KEY, title TEXT NOT NULL, "
                "category TEXT NOT NULL, attributes_json TEXT NOT NULL);"
                "CREATE INDEX idx_category ON items(category);"
            )
            db.executemany(
                "INSERT INTO items VALUES (?, ?, ?, ?)",
                [(r["id"], r["title"], r["category"],
                  json.dumps({k: v for k, v in r.items() if k not in REQUIRED}, ensure_ascii=False))
                 for r in rows],
            )
            db.commit()
        finally:
            db.close()
        (stage / "schema_preview.json").write_text(
            json.dumps(preview_schema(columns, rows, source_kind=source_kind), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        shutil.copy2(TEMPLATES / "app.py", stage / "app.py")
        shutil.copytree(TEMPLATES / "static", stage / "static")
        (stage / "requirements.txt").write_text("fastapi>=0.110,<1\nstarlette>=1.3.1,<2\nuvicorn>=0.27,<1\n", encoding="utf-8")
        # Abort if the source changed after parsing; never publish inconsistent provenance.
        if source_sha256(source) != source_digest:
            raise DataError("Source changed during generation")
        manifest = {
            "generator": "REA_Web MVP 0.1", "source": source.name,
            "input_kind": source_kind,
            "sha256": source_digest,
            "name": name.strip(), "fields": columns, "rows": len(rows),
            "features": ["list", "search", "category_filter", "detail", "schema_preview", "category_summary"],
            "run": "python -m uvicorn app:app --host 127.0.0.1 --port 8000",
            "scope": "LOCAL_SYNTHETIC_OR_USER_SUPPLIED_DATA_ONLY",
        }
        if approved_mapping is not None:
            manifest["owner_field_mapping"] = {
                "status": "OWNER_CONFIRMED_FOR_THIS_LOCAL_BUILD",
                "source_fields": {key: approved_mapping[key] for key in REQUIRED},
                "confirmation_scope": "ONE_LOCAL_GENERATION_ONLY",
                "source_sha256": source_digest,
                "fable_inferred_mapping_used": False,
            }
            (stage / "mapping_report.json").write_text(
                json.dumps(manifest["owner_field_mapping"], ensure_ascii=False,
                           sort_keys=True, indent=2) + "\n", encoding="utf-8"
            )
        (stage / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (stage / "README.md").write_text(
            "# " + name.strip() + "\n\n"
            "Generated by REA_Web from one user-provided CSV or JSON input.\n\n"
            "Python 3.11+ required.\n\n"
            "1. python -m pip install -r requirements.txt\n"
            "2. python -m uvicorn app:app --host 127.0.0.1 --port 8000\n"
            "3. Open http://127.0.0.1:8000/\n\n"
            "API: /health, /api/items, /api/items/{id}, /api/categories, /api/schema, /api/summary.\n"
            "The app is local/read-only, with no login, internet synchronization or hosting.\n"
            "Use only non-sensitive data. Do not expose this server to the internet.\n",
            encoding="utf-8",
        )
        # Stage is on the same filesystem; never overwrite an existing project.
        publish_directory(stage, output)
        return manifest
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a working local web app from CSV or flat JSON")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--csv", type=Path, help="CSV with id,title,category columns")
    group.add_argument("--json", type=Path, help="Flat JSON array of string-value objects")
    parser.add_argument("--out", required=True, type=Path, help="New output directory, must not exist")
    parser.add_argument("--name", default="REA sample web app")
    args = parser.parse_args(argv)
    try:
        report = generate(args.csv or args.json, args.out, args.name)
    except (OSError, DataError, FileExistsError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
