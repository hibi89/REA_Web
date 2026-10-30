"""Generated, standalone read-only FastAPI/SQLite application."""
from __future__ import annotations

from contextlib import contextmanager
import json
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="REA generated app", version="0.1.0", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


@contextmanager
def connection():
    """Every endpoint closes SQLite handles, including on query exceptions.

    sqlite3.Connection.__exit__ commits or rolls back, but does not close it.
    The generated Windows app must release its read-only file handle.
    """
    db = sqlite3.connect((ROOT / "data.sqlite").as_uri() + "?mode=ro", uri=True)
    try:
        db.execute("PRAGMA query_only=ON")
        db.row_factory = sqlite3.Row
        yield db
    finally:
        db.close()


def as_item(record):
    value = dict(record)
    value["attributes"] = json.loads(value.pop("attributes_json"))
    return value


def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/health")
def health():
    """Report readiness only when the actual read-only catalog is usable."""
    try:
        with connection() as db:
            # Check all table/index pages, including unused user tables. Merely
            # SELECTing from items can succeed when another B-tree is corrupt.
            integrity = db.execute("PRAGMA quick_check(1)").fetchone()
            if integrity is None or integrity[0] != "ok":
                raise sqlite3.DatabaseError("SQLite quick_check failed")
            db.execute("SELECT 1 FROM items LIMIT 1").fetchone()
    except (sqlite3.Error, OSError) as exc:
        # Never disclose the customer's local DB path to the HTTP caller.
        raise HTTPException(503, "Local catalog unavailable") from exc
    return {"status": "ok", "mode": "local_readonly"}


@app.get("/api/categories")
def categories():
    with connection() as db:
        rows = db.execute("SELECT DISTINCT category FROM items ORDER BY category").fetchall()
    return {"categories": [row["category"] for row in rows]}


@app.get("/api/schema")
def schema_preview():
    """Read-only unapproved field shape; sample cell data is excluded."""
    return json.loads((ROOT / "schema_preview.json").read_text(encoding="utf-8"))


@app.get("/api/summary")
def summary():
    """Counts derived only from local customer CSV, never business formulas."""
    with connection() as db:
        total = db.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        categories = db.execute("SELECT COUNT(DISTINCT category) FROM items").fetchone()[0]
        rows = db.execute(
            "SELECT category, COUNT(*) AS count FROM items "
            "GROUP BY category ORDER BY category LIMIT 100"
        ).fetchall()
    return {
        "source_kind": json.loads((ROOT / "schema_preview.json").read_text(encoding="utf-8"))["source_kind"] + "_snapshot",
        "total_items": total, "total_categories": categories,
        "categories_truncated": categories > 100,
        "category_counts": [{"category": row["category"], "count": row["count"]}
                            for row in rows],
    }


@app.get("/api/items")
def items(q: str = Query("", max_length=200), category: str = Query("", max_length=200),
          limit: int = Query(100, ge=1, le=100), offset: int = Query(0, ge=0, le=100_000)):
    where, params = [], []
    if q.strip():
        where.append("(title LIKE ? ESCAPE '\\' OR id LIKE ? ESCAPE '\\')")
        like = "%" + escape_like(q.strip()) + "%"
        params.extend([like, like])
    if category:
        where.append("category=?")
        params.append(category)
    condition = " WHERE " + " AND ".join(where) if where else ""
    with connection() as db:
        total = db.execute("SELECT COUNT(*) FROM items" + condition, params).fetchone()[0]
        data = db.execute(
            "SELECT * FROM items" + condition + " ORDER BY title, id LIMIT ? OFFSET ?",
            [*params, limit, offset],
        ).fetchall()
    return {"total": total, "items": [as_item(row) for row in data]}


@app.get("/api/items/{item_id}")
def detail(item_id: str):
    with connection() as db:
        record = db.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
    if record is None:
        raise HTTPException(404, "Item not found")
    return as_item(record)
