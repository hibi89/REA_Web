"""Local generated app Host validation, including DNS rebinding regression.

All requests and owner fixtures are synthetic and local only.
"""
from __future__ import annotations

import importlib.util

import pytest
from fastapi.testclient import TestClient

from rea.mvp import generate


def _build(tmp_path):
    source = tmp_path / "synthetic.csv"
    source.write_text("id,title,category\nA,Example,Food\n", encoding="utf-8")
    out = tmp_path / "generated"
    generate(source, out)
    spec = importlib.util.spec_from_file_location("rea_local_host_guard_test", out / "app.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("host", [
    "127.0.0.1:8765", "localhost:8000", "testserver",
])
def test_approved_local_hosts_remain_usable(tmp_path, host):
    generated = _build(tmp_path)
    with TestClient(generated.app) as client:
        assert client.get("/health", headers={"host": host}).status_code == 200
        assert client.get("/api/items", headers={"host": host}).json()["total"] == 1
        assert client.get("/", headers={"host": host}).status_code == 200


@pytest.mark.parametrize("host", [
    "attacker.example", "attacker.example:8765",
    "127.0.0.1.attacker.example", "localhost.attacker.example",
])
@pytest.mark.parametrize("endpoint", [
    "/health", "/api/items", "/api/items/A", "/api/summary",
    "/api/schema", "/api/categories", "/", "/static/app.js",
])
def test_untrusted_host_rejected_before_response(tmp_path, host, endpoint):
    generated = _build(tmp_path)
    with TestClient(generated.app) as client:
        response = client.get(endpoint, headers={"host": host})
    assert response.status_code == 400, (endpoint, host, response.status_code)
    assert "Example" not in response.text
    assert "app/data.sqlite" not in response.text


def test_untrusted_host_does_not_enter_generated_database_api(tmp_path, monkeypatch):
    generated = _build(tmp_path)
    def should_not_open_database():
        raise AssertionError("Untrusted Host reached SQLite")
    monkeypatch.setattr(generated, "connection", should_not_open_database)
    with TestClient(generated.app) as client:
        response = client.get("/api/items", headers={"host": "attacker.example"})
    assert response.status_code == 400
