"""Generated, standalone read-only FastAPI/SQLite application."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="REA generated app", version="0.1.0", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


def connection():
    db = sqlite3.connect(f"file:{ROOT / 'data.sqlite'}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    return db


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
        "source_kind": "customer_supplied_csv_snapshot",
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
