"""REA_Web fast MVP: an isolated CSV -> working local web app generator.

No remote URLs or production DB access. Run: python -m rea.mvp --csv samples/products.csv --out /tmp/rea-products
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from pathlib import Path

MAX_BYTES = 10 * 1024 * 1024
MAX_ROWS = 10_000
MAX_COLUMNS = 20
REQUIRED = ("id", "title", "category")
TEMPLATES = Path(__file__).resolve().parent / "templates"


class DataError(ValueError):
    """Invalid customer-supplied file. The original is never changed."""


def parse_csv(source: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not source.is_file() or not source.name.lower().endswith(".csv"):
        raise DataError("Provide an existing .csv file")
    if source.stat().st_size > MAX_BYTES:
        raise DataError("CSV exceeds 10 MiB")
    try:
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, restkey="__extra", strict=True)
            if not reader.fieldnames:
                raise DataError("CSV must have a header row")
            headers = [name.strip() for name in reader.fieldnames]
            if len(headers) > MAX_COLUMNS or len(headers) != len(set(headers)):
                raise DataError("Too many or duplicate columns")
            if not set(REQUIRED).issubset(headers) or any(not key or "\x00" in key for key in headers):
                raise DataError("Required columns: id, title, category")
            # DictReader keys use the original header text unless replaced.
            reader.fieldnames = headers
            entries: list[dict[str, str]] = []
            seen: set[str] = set()
            for number, row in enumerate(reader, start=2):
                if len(entries) >= MAX_ROWS:
                    raise DataError("CSV exceeds 10,000 rows")
                if "__extra" in row or any(value is None for value in row.values()):
                    raise DataError(f"Row {number}: wrong column count")
                clean = {key: value.strip() for key, value in row.items()}
                if any("\x00" in value or len(value) > 2000 for value in clean.values()):
                    raise DataError(f"Row {number}: invalid cell")
                for key in REQUIRED:
                    if not clean[key]:
                        raise DataError(f"Row {number}: missing {key}")
                if clean["id"] in seen:
                    raise DataError(f"Row {number}: duplicate id")
                seen.add(clean["id"])
                entries.append(clean)
    except (UnicodeError, csv.Error) as exc:
        raise DataError("Invalid UTF-8 CSV format") from exc
    if not entries:
        raise DataError("CSV must have at least one record")
    return headers, entries


def generate(csv_file: Path, output: Path, name: str = "REA sample web app") -> dict:
    source = Path(csv_file).resolve()
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}")
    if not name.strip() or len(name) > 100:
        raise DataError("App name must be 1 to 100 characters")
    columns, rows = parse_csv(source)
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
        shutil.copy2(TEMPLATES / "app.py", stage / "app.py")
        shutil.copytree(TEMPLATES / "static", stage / "static")
        (stage / "requirements.txt").write_text("fastapi>=0.110,<1\nuvicorn>=0.27,<1\n", encoding="utf-8")
        manifest = {
            "generator": "REA_Web MVP 0.1", "source": source.name,
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "name": name.strip(), "fields": columns, "rows": len(rows),
            "features": ["list", "search", "category_filter", "detail"],
            "run": "python -m uvicorn app:app --host 127.0.0.1 --port 8000",
            "scope": "LOCAL_SYNTHETIC_OR_USER_SUPPLIED_DATA_ONLY",
        }
        (stage / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (stage / "README.md").write_text(
            "# " + name.strip() + "\n\n"
            "Generated by REA_Web from a user-provided CSV.\n\n"
            "Python 3.11+ required.\n\n"
            "1. python -m pip install -r requirements.txt\n"
            "2. python -m uvicorn app:app --host 127.0.0.1 --port 8000\n"
            "3. Open http://127.0.0.1:8000/\n\n"
            "API: /health, /api/items, /api/items/{id}, /api/categories.\n"
            "The app is local/read-only, with no login, internet synchronization or hosting.\n"
            "Use only non-sensitive data. Do not expose this server to the internet.\n",
            encoding="utf-8",
        )
        # Stage is on the same filesystem; never overwrite an existing project.
        if output.exists():
            raise FileExistsError(f"Output already exists: {output}")
        os.rename(stage, output)
        return manifest
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a working local web app from a CSV")
    parser.add_argument("--csv", required=True, type=Path, help="CSV with id,title,category columns")
    parser.add_argument("--out", required=True, type=Path, help="New output directory, must not exist")
    parser.add_argument("--name", default="REA sample web app")
    args = parser.parse_args(argv)
    try:
        report = generate(args.csv, args.out, args.name)
    except (OSError, DataError, FileExistsError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
