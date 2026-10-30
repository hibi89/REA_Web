"""Real Pro parser integration checks for offline Lite output."""
import json
from pathlib import Path
import pytest
from rea.lite_builder import inspect, build, safe_json
from rea.mvp import DataError


def make_source(tmp_path, text="item_code,item_name,group,price\nA001,가상상품,문구,2000\n"):
    p = tmp_path / "input.csv"
    p.write_text(text, encoding="utf-8")
    return p


def make_html(tmp_path, text=None):
    p = make_source(tmp_path) if text is None else make_source(tmp_path, text)
    info = inspect(p)
    dest = tmp_path / "customer.html"
    result = build(
        p, dest, mapping={"id": "item_code", "title": "item_name", "category": "group"},
        approved_sha=info["sha256"], confirmation="APPROVE",
        theme="inventory", title="품목 조회",
    )
    return p, dest, result


def test_real_owner_mapping_and_self_contained_html(tmp_path):
    p, out, result = make_html(tmp_path)
    html = out.read_text(encoding="utf-8")
    assert '<script id="rea-payload" type="application/json">' in html
    payload = json.loads(html.split('<script id="rea-payload" type="application/json">')[1].split("</script>")[0])
    assert payload["records"][0]["id"] == "A001"
    assert payload["records"][0]["title"] == "가상상품"
    assert payload["sourceColumns"] == ["item_code", "item_name", "group", "price"]
    assert payload["theme"] == "inventory"
    assert result["rows"] == 1
    assert "https://" not in html and "http://" not in html


def test_unapproved_and_changed_input_refused(tmp_path):
    p = make_source(tmp_path)
    sha = inspect(p)["sha256"]
    out = tmp_path / "out.html"
    mapping = {"id": "item_code", "title": "item_name", "category": "group"}
    with pytest.raises(DataError):
        build(p, out, mapping=mapping, approved_sha=sha, confirmation="yes")
    p.write_text("item_code,item_name,group,price\nA001,changed,문구,1000\n", encoding="utf-8")
    with pytest.raises(DataError):
        build(p, out, mapping=mapping, approved_sha=sha, confirmation="APPROVE")
    assert not out.exists()


def test_no_overwrite_even_if_existing(tmp_path):
    p, out, _ = make_html(tmp_path)
    old = out.read_bytes()
    with pytest.raises(DataError):
        build(p, out, mapping={"id": "item_code", "title": "item_name", "category": "group"},
              approved_sha=inspect(p)["sha256"], confirmation="APPROVE")
    assert out.read_bytes() == old


def test_html_script_escaping(tmp_path):
    source = 'item_code,item_name,group,price\nA001,"</script><img src=x>",문구,1000\n'
    p, out, _ = make_html(tmp_path, source)
    html = out.read_text(encoding="utf-8")
    assert "</script><img" not in html
    payload = json.loads(html.split('<script id="rea-payload" type="application/json">')[1].split("</script>")[0])
    assert payload["records"][0]["title"] == "</script><img src=x>"
    assert safe_json({"x": "</script>"}) == '{"x":"\\u003c/script\\u003e"}'


def test_duplicate_ids_rejected(tmp_path):
    p = make_source(tmp_path, "item_code,item_name,group,price\nA001,a,z,2\nA001,b,z,3\n")
    with pytest.raises(DataError):
        build(p, tmp_path / "out.html",
              mapping={"id": "item_code", "title": "item_name", "category": "group"},
              approved_sha=inspect(p)["sha256"], confirmation="APPROVE")
