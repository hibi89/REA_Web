"""Generated local customer app must not invite browser storage of catalog data.

All observations use generated synthetic owner rows. This is a header policy
regression, NOT a human Windows acceptance or proof of secure data erasure.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from rea.mvp import generate


def _generated(tmp_path):
    source = tmp_path / "synthetic.csv"
    source.write_text("id,title,category\nA,Example,Food\n", encoding="utf-8")
    out = tmp_path / "generated"
    generate(source, out, "Synthetic privacy headers")
    spec = importlib.util.spec_from_file_location(
        "rea_generated_cache_headers_test", out / "app.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return out, module.app


@pytest.mark.parametrize("path,expected_status", [
    ("/", 200),
    ("/static/app.js", 200),
    ("/static/style.css", 200),
    ("/health", 200),
    ("/api/items", 200),
    ("/api/items/A", 200),
    ("/api/summary", 200),
    ("/api/categories", 200),
    ("/api/schema", 200),
    ("/api/items/NO_SUCH_SYNTHETIC_ID", 404),
    ("/api/items?limit=101", 422),
])
def test_browser_responses_refuse_cache_and_keep_contract(tmp_path, path, expected_status):
    out, app = _generated(tmp_path)
    original_db = (out / "data.sqlite").read_bytes()
    with TestClient(app) as client:
        response = client.get(path)
    assert response.status_code == expected_status
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert (out / "data.sqlite").read_bytes() == original_db


def test_error_responses_and_untrusted_hosts_also_not_cacheable(tmp_path):
    out, app = _generated(tmp_path)
    (out / "data.sqlite").unlink()  # synthetic generated copy only
    with TestClient(app) as client:
        missing_db = client.get("/api/items")
        untrusted = client.get("/api/items", headers={"host": "attacker.example"})
        post = client.post("/api/items", json={"id": "not-allowed"})
    assert missing_db.status_code == 503
    assert missing_db.json() == {"detail": "Local catalog unavailable"}
    assert untrusted.status_code == 400
    assert post.status_code == 405
    for response in (missing_db, untrusted, post):
        assert response.headers["cache-control"] == "no-store"
        assert response.headers["x-content-type-options"] == "nosniff"
    assert not (out / "data.sqlite").exists()
