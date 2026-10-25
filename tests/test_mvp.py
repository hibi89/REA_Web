from __future__ import annotations

import csv
import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from rea.mvp import DataError, generate, parse_csv


def fixture_csv(tmp_path: Path, content: str) -> Path:
    file = tmp_path / "products.csv"
    file.write_text(content, encoding="utf-8-sig")
    return file


def test_generate_local_web_app(tmp_path):
    source = fixture_csv(tmp_path, "id,title,category,price\nA1,한글 상품,음료,1000\nA2,Coffee,음료,1500\nB1,Cake,디저트,2500\n")
    output = tmp_path / "built"
    metadata = generate(source, output, "My Store")
    assert metadata["rows"] == 3
    assert metadata["sha256"]
    assert (output / "data.sqlite").exists()
    assert (output / "static" / "app.js").exists()
    assert (output / "README.md").exists()
    spec = importlib.util.spec_from_file_location("rea_generated_app_test", output / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client = TestClient(module.app)
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/").status_code == 200
    assert "textContent" in client.get("/static/app.js").text
    assert client.get("/api/categories").json()["categories"] == ["디저트", "음료"]
    assert client.get("/api/items").json()["total"] == 3
    assert client.get("/api/items?q=한글").json()["total"] == 1
    assert client.get("/api/items?category=음료").json()["total"] == 2
    assert client.get("/api/items?category=음료&q=Coffee").json()["total"] == 1
    assert client.get("/api/items/A1").json()["attributes"]["price"] == "1000"
    assert client.get("/api/items/missing").status_code == 404
    assert client.get("/api/items?limit=99999").status_code == 422
    with sqlite3.connect(output / "data.sqlite") as db:
        assert db.execute("SELECT count(*) FROM items").fetchone()[0] == 3


@pytest.mark.parametrize("text", [
    "id,title,category\nA,x,food\nA,y,food\n",
    "id,title\nA,x\n",
    "id,title,category\nA,x,food,extra\n",
    "id,title,category\nA,,food\n",
    "id,title,category\n",
])
def test_bad_csv_rejected(tmp_path, text):
    source = fixture_csv(tmp_path, text)
    with pytest.raises(DataError):
        generate(source, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_never_overwrite_existing_output(tmp_path):
    source = fixture_csv(tmp_path, "id,title,category\nA,x,food\n")
    out = tmp_path / "out"
    out.mkdir()
    (out / "keep.txt").write_text("untouched")
    with pytest.raises(FileExistsError):
        generate(source, out)
    assert (out / "keep.txt").read_text() == "untouched"


def test_csv_wildcards_are_literal(tmp_path):
    source = fixture_csv(tmp_path, "id,title,category\nA,100% 좋음,group\nB,plain,group\n")
    out = tmp_path / "out"
    generate(source, out)
    spec = importlib.util.spec_from_file_location("rea_generated_app_wildcard", out / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client = TestClient(module.app)
    assert client.get("/api/items?q=%").json()["total"] == 1
    assert client.get("/api/items?q=_").json()["total"] == 0


def test_source_is_unchanged(tmp_path):
    source = fixture_csv(tmp_path, "id,title,category\nA,x,food\n")
    before = source.read_bytes()
    generate(source, tmp_path / "built")
    assert source.read_bytes() == before
