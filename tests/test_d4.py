"""D4 owner CSV schema and category summary tests."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import zipfile
import pytest
from fastapi.testclient import TestClient
from rea.mvp import preview_schema, parse_csv
from rea.orchestrator import build
from rea.delivery import create_delivery, verify_delivery

ROOT = Path(__file__).resolve().parents[1]

def client(folder):
    spec = importlib.util.spec_from_file_location("rea_d4_app", folder / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return TestClient(module.app)

@pytest.mark.parametrize("name,count,categories", [
    ("qa_cafe.csv", 4, {"베이커리": 1, "디저트": 1, "음료": 2}),
    ("qa_inventory.csv", 5, {"메모리": 1, "저장장치": 2, "주변기기": 2}),
    ("qa_trends.csv", 5, {"JP": 2, "KR": 2, "US": 1}),
])
def test_api_schema_summary_three_domains(tmp_path, name, count, categories):
    original = ROOT / "samples" / name
    original_bytes = original.read_bytes()
    out = tmp_path / "site"
    manifest = build(original, out)
    assert original.read_bytes() == original_bytes
    assert manifest["rows"] == count
    assert "category_summary" in manifest["features"]
    assert "schema_preview" in manifest["features"]
    web = client(out)
    schema = web.get("/api/schema").json()
    assert schema["review_status"] == "UNAPPROVED"
    assert schema["approved_semantic_bindings"] == []
    assert schema["row_count"] == count
    assert schema["source_kind"] == "customer_supplied_csv"
    assert schema["fields"][0]["name"] == "id"
    summary = web.get("/api/summary").json()
    assert summary["source_kind"] == "customer_supplied_csv_snapshot"
    assert summary["total_items"] == count
    assert summary["total_categories"] == len(categories)
    assert not summary["categories_truncated"]
    assert {x["category"]: x["count"] for x in summary["category_counts"]} == categories
    assert web.get("/api/items").json()["total"] == count
    assert web.get("/schema_preview.json").status_code == 404
    assert web.post("/api/summary").status_code == 405

def test_lexical_types_and_missing_are_unapproved(tmp_path):
    source = tmp_path / "mixed.csv"
    source.write_text(
        "id,title,category,amount,date,blank,mixed,code\n"
        "a,One,A,3.5,2026-10-25,,9,0001\n"
        "b,Two,B,3,2026-10-26,,word,0002\n", encoding="utf-8")
    columns, rows = parse_csv(source)
    report = preview_schema(columns, rows)
    fields = {x["name"]: x for x in report["fields"]}
    assert fields["amount"]["inferred_type"] == "decimal"
    assert fields["date"]["inferred_type"] == "date"
    assert fields["blank"]["inferred_type"] == "unknown"
    assert fields["blank"]["missing_count"] == 2
    assert fields["mixed"]["inferred_type"] == "mixed"
    assert fields["code"]["inferred_type"] == "text"
    assert report["approved_semantic_bindings"] == []
    assert "2026-10-25" not in json.dumps(report)

def test_header_xss_is_data_and_samples_not_exposed(tmp_path):
    csvfile = tmp_path / "safe.csv"
    csvfile.write_text("id,title,category,<img src=x onerror=alert(1)>\nX,Safe,C,SECRET_VALUE\n",
                       encoding="utf-8")
    out = tmp_path / "site"
    build(csvfile, out)
    schema = client(out).get("/api/schema").json()
    assert schema["fields"][-1]["name"] == "<img src=x onerror=alert(1)>"
    assert "SECRET_VALUE" not in json.dumps(schema)
    js = (out / "static" / "app.js").read_text(encoding="utf-8")
    assert "textContent" in js and "innerHTML" not in js

def test_summary_category_cap(tmp_path):
    csvfile = tmp_path / "groups.csv"
    csvfile.write_text(
        "id,title,category\n" + "".join(f"{n},item{n},group{n:03d}\n" for n in range(105)),
        encoding="utf-8")
    out = tmp_path / "site"
    build(csvfile, out)
    summary = client(out).get("/api/summary").json()
    assert summary["total_items"] == 105
    assert summary["total_categories"] == 105
    assert summary["categories_truncated"]
    assert len(summary["category_counts"]) == 100

def test_optional_fable_cannot_approve_mapping(tmp_path):
    pytest.importorskip("astra_contracts.observation")
    out = tmp_path / "site"
    build(ROOT / "samples/qa_cafe.csv", out,
          fable_result=ROOT / "samples/fable_record_redacted.json")
    web = client(out)
    assert web.get("/api/summary").json()["total_items"] == 4
    assert web.get("/api/schema").json()["approved_semantic_bindings"] == []
    assert web.get("/review/fable_review.json").status_code == 404

def test_zip_contains_schema_file_and_verifies(tmp_path):
    zippath = tmp_path / "preview.zip"
    create_delivery(ROOT / "samples/qa_trends.csv", zippath)
    verify_delivery(zippath)
    with zipfile.ZipFile(zippath) as archive:
        assert "app/schema_preview.json" in archive.namelist()
        schema = json.loads(archive.read("app/schema_preview.json"))
        assert schema["review_status"] == "UNAPPROVED"
        assert schema["row_count"] == 5

def test_source_and_existing_path_preserved(tmp_path):
    source = ROOT / "samples/qa_cafe.csv"
    data = source.read_bytes()
    out = tmp_path / "site"
    out.mkdir()
    (out / "keep.txt").write_text("owner", encoding="utf-8")
    with pytest.raises(FileExistsError):
        build(source, out)
    assert source.read_bytes() == data
    assert (out / "keep.txt").read_text(encoding="utf-8") == "owner"
