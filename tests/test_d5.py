"""D5 strict one-file JSON intake and CSV regression / safety contract tests."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest
from fastapi.testclient import TestClient

from rea.mvp import DataError, MAX_BYTES, MAX_ROWS, MAX_COLUMNS, parse_csv, parse_input, parse_json
from rea.orchestrator import build
from rea.delivery import create_delivery, verify_delivery

ROOT = Path(__file__).resolve().parents[1]
JSON_SAMPLE = ROOT / "samples" / "qa_products.json"
CSV_SAMPLE = ROOT / "samples" / "qa_cafe.csv"


def client(folder):
    spec = importlib.util.spec_from_file_location("rea_d5_generated", folder / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return TestClient(module.app)


def make_json(tmp_path, data, filename="data.json"):
    file = tmp_path / filename
    file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return file


def rows(*items):
    return list(items)


def test_json_real_generated_webapp_unchanged_original(tmp_path):
    before = JSON_SAMPLE.read_bytes()
    fields, records = parse_json(JSON_SAMPLE)
    assert fields == ["id", "title", "category", "price", "status"]
    assert records[0]["title"] == "블렌드 커피"
    out = tmp_path / "app"
    manifest = build(JSON_SAMPLE, out, "JSON cafe")
    assert JSON_SAMPLE.read_bytes() == before
    assert manifest["input_kind"] == "customer_supplied_json"
    assert manifest["generation_input"] == "customer_supplied_json_only"
    assert manifest["source"] == "qa_products.json"
    assert manifest["rows"] == 4
    app = client(out)
    assert app.get("/api/items").json()["total"] == 4
    assert app.get("/api/items?q=블렌드").json()["total"] == 1
    assert app.get("/api/items?category=음료").json()["total"] == 2
    assert app.get("/api/items/J01").json()["attributes"]["price"] == "4900"
    assert app.get("/api/summary").json()["total_categories"] == 3
    schema = app.get("/api/schema").json()
    assert schema["source_kind"] == "customer_supplied_json"
    assert schema["review_status"] == "UNAPPROVED"
    assert schema["approved_semantic_bindings"] == []
    assert app.get("/schema_preview.json").status_code == 404


def test_json_and_csv_each_standalone(tmp_path):
    csv_out = tmp_path / "csv"
    json_out = tmp_path / "json"
    assert build(CSV_SAMPLE, csv_out)["generation_input"] == "customer_supplied_csv_only"
    assert build(JSON_SAMPLE, json_out)["generation_input"] == "customer_supplied_json_only"
    assert client(csv_out).get("/api/items").json()["total"] == 4
    assert client(json_out).get("/api/items").json()["total"] == 4


@pytest.mark.parametrize("invalid", [
    {}, "text", [], None, 12,
    [{"id": "1", "title": "One", "category": "x"}, {"id": "1", "title": "Two", "category": "y"}],
    [{"id": "1", "title": "One"}],
    [{"id": "1", "title": "One", "category": "x", "extra": None}],
    [{"id": "1", "title": "One", "category": "x", "extra": 0}],
    [{"id": "1", "title": "One", "category": "x", "extra": True}],
    [{"id": "1", "title": "One", "category": "x", "extra": [1]}],
    [{"id": "1", "title": "One", "category": "x", "extra": {"nested": "bad"}}],
    [{"id": "", "title": "One", "category": "x"}],
    [{"id": "1", "title": "", "category": "x"}],
    [{"id": "1", "title": "One", "category": "x"}, {"id": "2", "title": "Two", "category": "y", "other": "a"}],
    [{"id": "1", "title": "One", "category": "x"}, {"id": "2", "title": "Two"}],
])
def test_json_invalid_shape_fail_closed(tmp_path, invalid):
    source = make_json(tmp_path, invalid)
    out = tmp_path / "out"
    with pytest.raises(DataError):
        build(source, out)
    assert not out.exists()


def test_duplicate_object_key_not_silently_overwritten(tmp_path):
    source = tmp_path / "duplicate.json"
    source.write_text('[{"id":"x","title":"Safe","title":"Overwritten","category":"c"}]', encoding="utf-8")
    with pytest.raises(DataError, match="Duplicate JSON object"):
        parse_json(source)


@pytest.mark.parametrize("invalid", [
    "{invalid", '[{"id":"x","title":"One","category":"a"}] trailing',
    '[{"id":"x","title":"One","category":"a","v":NaN}]',
    '{"items":[{"id":"x","title":"One","category":"a"}]}',
])
def test_bad_json_text_rejected(tmp_path, invalid):
    source = tmp_path / "invalid.json"
    source.write_text(invalid, encoding="utf-8")
    with pytest.raises(DataError):
        parse_input(source)


def test_json_bom_accepted(tmp_path):
    source = tmp_path / "bom.JSON"
    source.write_text('\ufeff[{"id":"1","title":"A","category":"B"}]', encoding="utf-8")
    assert parse_json(source)[1][0]["id"] == "1"


def test_json_oversize_bytes_and_rows(tmp_path):
    source = make_json(tmp_path, [{"id": "x", "title": "y", "category": "a"}])
    with source.open("ab") as handle:
        handle.write(b" " * (MAX_BYTES + 1))
    with pytest.raises(DataError, match="10 MiB"):
        parse_json(source)
    arr = [{"id": str(i), "title": "T", "category": "C"} for i in range(MAX_ROWS + 1)]
    many = make_json(tmp_path, arr, "many.json")
    with pytest.raises(DataError, match="10,000"):
        parse_json(many)


def test_json_too_many_columns_and_cell_length(tmp_path):
    row = {"id": "1", "title": "a", "category": "b"}
    row.update({f"field_{i}": "x" for i in range(MAX_COLUMNS)})
    with pytest.raises(DataError):
        parse_json(make_json(tmp_path, [row], "manycolumns.json"))
    with pytest.raises(DataError):
        parse_json(make_json(tmp_path, [{"id": "1", "title": "a"*2001, "category": "b"}], "long.json"))


def test_no_empty_extra_or_wrong_extension(tmp_path):
    source = make_json(tmp_path, [{"id": "1", "title": "A", "category": "B"}], "file.txt")
    with pytest.raises(DataError):
        parse_input(source)
    with pytest.raises(DataError):
        parse_json(source)
    with pytest.raises(DataError):
        parse_csv(source)


def test_symlink_json_refused(tmp_path):
    source = make_json(tmp_path, [{"id": "1", "title": "A", "category": "B"}])
    symlink = tmp_path / "reference.json"
    symlink.symlink_to(source)
    with pytest.raises(DataError, match="symlink"):
        parse_json(symlink)


def test_json_zip_manifest_and_windows_guide(tmp_path):
    out = tmp_path / "json.zip"
    manifest = create_delivery(JSON_SAMPLE, out)
    assert manifest == verify_delivery(out)
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
        assert "app/schema_preview.json" in names
        assert "app/data.sqlite" in names
        assert "launch_windows.cmd" in names
        app_manifest = json.loads(zf.read("app/manifest.json"))
        assert app_manifest["input_kind"] == "customer_supplied_json"
        assert app_manifest["generation_input"] == "customer_supplied_json_only"
        assert "J01" not in json.dumps(app_manifest)
        assert "app/qa_products.json" not in names


def test_json_cli_and_csv_cli_independent(tmp_path):
    for mode, source in (("--json", JSON_SAMPLE), ("--csv", CSV_SAMPLE)):
        out = tmp_path / mode.replace("--", "")
        proc = subprocess.run(
            [sys.executable, "-m", "rea.orchestrator", mode, str(source), "--out", str(out)],
            cwd=ROOT, text=True, capture_output=True,
        )
        assert proc.returncode == 0, proc.stderr
        assert json.loads(proc.stdout)["rows"] == 4
    zipped = tmp_path / "standalone.zip"
    proc = subprocess.run(
        [sys.executable, "-m", "rea.delivery", "pack",
         "--json", str(JSON_SAMPLE), "--out", str(zipped)],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert verify_delivery(zipped)["runtime_binding"] == "127.0.0.1"


def test_two_inputs_must_be_explicitly_rejected(tmp_path):
    output = tmp_path / "not-created"
    proc = subprocess.run(
        [sys.executable, "-m", "rea.orchestrator", "--csv", str(CSV_SAMPLE),
         "--json", str(JSON_SAMPLE), "--out", str(output)],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert proc.returncode != 0 and not output.exists()


def test_json_fable_optional_still_unapproved(tmp_path):
    pytest.importorskip("astra_contracts.observation")
    out = tmp_path / "app"
    manifest = build(JSON_SAMPLE, out,
                     fable_result=ROOT / "samples/fable_record_redacted.json")
    assert manifest["fable_review"]["status"] == "REVIEW_REQUIRED"
    assert not manifest["fable_review"]["used_for_generation"]
    assert manifest["generation_input"] == "customer_supplied_json_only"
    app = client(out)
    assert app.get("/api/schema").json()["approved_semantic_bindings"] == []
    assert app.get("/api/summary").json()["total_items"] == 4
    assert app.get("/review/fable_review.json").status_code == 404


def test_existing_output_and_original_json_preserved(tmp_path):
    data_before = JSON_SAMPLE.read_bytes()
    out = tmp_path / "owner"
    out.mkdir()
    (out / "sentinel.txt").write_text("owner")
    with pytest.raises(FileExistsError):
        build(JSON_SAMPLE, out)
    assert JSON_SAMPLE.read_bytes() == data_before
    assert (out / "sentinel.txt").read_text() == "owner"

def test_generate_direct_rejects_symlink(tmp_path):
    from rea.mvp import generate
    link = tmp_path / "data.json"
    link.symlink_to(JSON_SAMPLE)
    out = tmp_path / "app"
    with pytest.raises(DataError, match="symlink"):
        generate(link, out)
    assert not out.exists()
