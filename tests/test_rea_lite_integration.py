"""REA Lite integration tests against the actual REA_Web Pro parser."""
import json
from pathlib import Path
import pytest

from rea.lite_builder import inspect, build, safe_json
from rea.mvp import DataError, parse_input, map_owner_fields


def source(tmp_path, data="item_code,item_name,group,price\nA001,가상상품,문구,2000\n", ext=".csv"):
    path = tmp_path / ("owner" + ext)
    path.write_text(data, encoding="utf-8")
    return path


def approved(src, dest, **kwargs):
    return build(
        src, dest,
        mapping={"id": "item_code", "title": "item_name", "category": "group"},
        approved_sha=inspect(src)["sha256"],
        confirmation="APPROVE",
        theme="inventory",
        title="품목 조회",
        **kwargs,
    )


def payload(html):
    a = '<script id="rea-payload" type="application/json">'
    return json.loads(html.split(a, 1)[1].split("</script>", 1)[0])


def test_real_pro_csv_mapping_and_self_contained_html(tmp_path):
    p = source(tmp_path)
    headers, rows = parse_input(p, require_semantics=False)
    actual_cols, actual_rows = map_owner_fields(
        headers, rows, {"id":"item_code","title":"item_name","category":"group"}
    )
    output = tmp_path / "product.html"
    created = approved(p, output)
    html = output.read_text(encoding="utf-8")
    data = payload(html)
    assert data["records"] == actual_rows
    assert data["columns"] == actual_cols
    assert data["sourceColumns"] == headers
    assert data["theme"] == "inventory"
    assert created["rows"] == 1
    assert created["status"] == "CREATED_UNAPPROVED_FOR_SALE"
    assert "http://" not in html and "https://" not in html


def test_json_pro_input_with_explicit_mapping(tmp_path):
    p = source(
        tmp_path,
        json.dumps([{"item_code":"001","item_name":"도구","group":"문구","price":"100"}],
                   ensure_ascii=False),
        ext=".json",
    )
    out = tmp_path / "out.html"
    approved(p, out)
    assert payload(out.read_text(encoding="utf-8"))["records"][0]["id"] == "001"


def test_stale_input_and_unapproved_refused_without_output(tmp_path):
    p = source(tmp_path)
    sha = inspect(p)["sha256"]
    mapping = {"id":"item_code","title":"item_name","category":"group"}
    out = tmp_path / "out.html"
    with pytest.raises(DataError):
        build(p, out, mapping=mapping, approved_sha=sha, confirmation="yes")
    p.write_text("item_code,item_name,group,price\nA001,changed,문구,1000\n", encoding="utf-8")
    with pytest.raises(DataError):
        build(p, out, mapping=mapping, approved_sha=sha, confirmation="APPROVE")
    assert not out.exists()


def test_no_overwrite_and_original_bytes_preserved(tmp_path):
    p = source(tmp_path)
    before = p.read_bytes()
    out = tmp_path / "out.html"
    approved(p, out)
    previous = out.read_bytes()
    with pytest.raises(DataError):
        approved(p, out)
    assert p.read_bytes() == before
    assert out.read_bytes() == previous


def test_script_injection_is_encoded_but_values_preserved(tmp_path):
    attack = '</script><img src=x onerror=alert(1)>'
    p = source(tmp_path, 'item_code,item_name,group,price\nA001,"'+attack+'",문구,1000\n')
    out = tmp_path / "out.html"
    approved(p, out)
    html = out.read_text(encoding="utf-8")
    assert attack not in html
    assert payload(html)["records"][0]["title"] == attack
    assert safe_json({"x":"</script>"}) == '{"x":"\\u003c/script\\u003e"}'


def test_duplicate_id_fails_through_real_pro_mapping(tmp_path):
    p = source(tmp_path, "item_code,item_name,group,price\nA001,a,z,2\nA001,b,z,3\n")
    with pytest.raises(DataError):
        approved(p, tmp_path / "out.html")


def test_rejected_unsafe_semantics_and_output_types(tmp_path):
    p = source(tmp_path)
    info = inspect(p)
    kwargs = dict(
        source=p,
        approved_sha=info["sha256"],
        confirmation="APPROVE",
        mapping={"id":"item_code","title":"item_name","category":"group"},
    )
    with pytest.raises(DataError):
        build(output=tmp_path/"out.txt", **kwargs)
    with pytest.raises(DataError):
        build(output=tmp_path/"out.html", theme="../invalid", **kwargs)
    with pytest.raises(DataError):
        build(output=tmp_path/"out.html", title="bad\nname", **kwargs)
    with pytest.raises(DataError):
        build(output=tmp_path/"out.html",
              mapping={"id":"item_code","title":"item_code","category":"group"},
              source=p, approved_sha=info["sha256"], confirmation="APPROVE")
    assert not (tmp_path/"out.html").exists()
