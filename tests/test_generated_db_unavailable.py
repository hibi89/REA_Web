"""Synthetic unavailable-database E2E for a generated local FastAPI app.

Customer data, remote hosting and commercial authorization are out of scope.
"""
from __future__ import annotations

import importlib.util
import sqlite3

from fastapi.testclient import TestClient

from rea.mvp import generate


def _generated(tmp_path):
    owner_source = tmp_path / "owner.csv"
    owner_source.write_text(
        "id,title,category\nA,Synthetic,Food\n",
        encoding="utf-8",
    )
    directory = tmp_path / "generated"
    generate(owner_source, directory, "Synthetic database failure case")
    spec = importlib.util.spec_from_file_location(
        "rea_db_unavailable_regression", directory / "app.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return directory, module.app


def _assert_db_endpoints_unavailable(client):
    for endpoint in (
        "/health", "/api/items", "/api/categories",
        "/api/summary", "/api/items/A",
    ):
        response = client.get(endpoint)
        assert response.status_code == 503, (endpoint, response.text)
        assert response.json() == {"detail": "Local catalog unavailable"}
    # Schema-only metadata remains independent of the unreadable SQLite DB.
    assert client.get("/api/schema").status_code == 200


def test_missing_database_is_not_created_and_all_db_endpoints_return_503(tmp_path):
    directory, app = _generated(tmp_path)
    database = directory / "data.sqlite"
    database.unlink()
    with TestClient(app) as client:
        _assert_db_endpoints_unavailable(client)
    assert not database.exists()


def test_dropped_items_table_returns_503_without_local_sql_error_details(tmp_path):
    directory, app = _generated(tmp_path)
    with sqlite3.connect(directory / "data.sqlite") as db:
        db.execute("DROP TABLE items")
    with TestClient(app) as client:
        _assert_db_endpoints_unavailable(client)


def test_healthy_generated_db_endpoints_keep_original_contract(tmp_path):
    _directory, app = _generated(tmp_path)
    with TestClient(app) as client:
        assert client.get("/health").json() == {
            "status": "ok", "mode": "local_readonly"
        }
        assert client.get("/api/items").json()["total"] == 1
        assert client.get("/api/items/A").status_code == 200
        assert client.get("/api/items/missing").status_code == 404
        assert client.get("/api/categories").status_code == 200
        assert client.get("/api/summary").json()["total_items"] == 1


def test_missing_schema_metadata_yields_safe_503_without_blocking_data_endpoints(tmp_path):
    directory, app = _generated(tmp_path)
    (directory / "schema_preview.json").unlink()
    with TestClient(app) as client:
        for path in ("/health", "/api/schema", "/api/summary"):
            response = client.get(path)
            assert response.status_code == 503, (path, response.text)
            assert response.json() == {"detail": "Local catalog unavailable"}
        assert client.get("/api/items").json()["total"] == 1
        assert client.get("/api/items/A").status_code == 200


def test_invalid_schema_metadata_fails_closed_and_keeps_owner_rows(tmp_path):
    directory, app = _generated(tmp_path)
    schema = directory / "schema_preview.json"
    original = (directory / "data.sqlite").read_bytes()
    for malformed in (b"not-json", b"{}", b"x" * (256 * 1024 + 1)):
        schema.write_bytes(malformed)
        with TestClient(app) as client:
            assert client.get("/health").status_code == 503
            assert client.get("/api/schema").status_code == 503
            assert client.get("/api/summary").status_code == 503
        assert (directory / "data.sqlite").read_bytes() == original
