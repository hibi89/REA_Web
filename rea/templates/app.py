"""Generated, standalone read-only FastAPI/SQLite application."""
from __future__ import annotations

from contextlib import contextmanager
import json
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="REA generated app", version="0.1.0", docs_url=None, redoc_url=None)
# The shipped app is loopback-only. Reject arbitrary Host values as a defense
# against DNS rebinding through browser requests to an unprotected local API.
# "testserver" is the fixed default of FastAPI's local TestClient regression suite.
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["127.0.0.1", "localhost", "testserver"],
)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


@app.exception_handler(sqlite3.Error)
async def database_unavailable(_request, _error):
    """Fail closed without disclosing local database paths or SQL details."""
    return JSONResponse(status_code=503, content={"detail": "Local catalog unavailable"})


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


def read_schema():
    """Bounded generated metadata read; do not leak local filesystem errors."""
    try:
        schema_file = ROOT / "schema_preview.json"
        if schema_file.is_symlink():
            raise ValueError("Unsafe metadata alias")
        with schema_file.open("rb") as handle:
            content = handle.read(256 * 1024 + 1)
        if len(content) > 256 * 1024:
            raise ValueError("Oversized generated metadata")
        value = json.loads(content.decode("utf-8"))
        if (not isinstance(value, dict)
                or value.get("review_status") != "UNAPPROVED"
                or not isinstance(value.get("source_kind"), str)
                or not isinstance(value.get("fields"), list)):
            raise ValueError("Invalid generated metadata")
        return value
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise HTTPException(503, "Local catalog unavailable") from exc


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
    """Report readiness only when both catalog and metadata are usable."""
    read_schema()
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
    return read_schema()


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
        "source_kind": read_schema()["source_kind"] + "_snapshot",
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
