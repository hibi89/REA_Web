"""Offline D2-02 vertical slice / regression, no external sites."""
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient
from rea.orchestrator import build

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "samples" / "products.csv"
FABLE = ROOT / "samples" / "fable_record_redacted.json"


def load_client(out):
    spec = importlib.util.spec_from_file_location("generated_rea_d2", out / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return TestClient(module.app)


def test_csv_only_vertical(tmp_path):
    out = tmp_path / "site"
    manifest = build(CSV, out, "내 상품")
    assert manifest["rows"] == 5
    assert manifest["generation_input"] == "customer_supplied_csv_only"
    assert manifest["fable_review"]["status"] == "NOT_REQUESTED"
    assert not (out / "review").exists()
    client = load_client(out)
    assert client.get("/health").json()["mode"] == "local_readonly"
    assert client.get("/").status_code == 200
    assert client.get("/api/items").json()["total"] == 5
    assert client.get("/api/items?category=음료").json()["total"] == 2
    assert client.get("/api/items?q=카페").json()["total"] == 1
    assert client.get("/api/items/P002").json()["attributes"]["price"] == "4000"
    assert client.get("/api/items/unknown").status_code == 404
    with sqlite3.connect(out / "data.sqlite") as conn:
        assert conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 5


def test_optional_fable_actual_astra_contract(tmp_path):
    pytest.importorskip("astra_contracts.observation")
    out = tmp_path / "site"
    manifest = build(CSV, out, fable_result=FABLE)
    assert manifest["fable_review"]["status"] == "REVIEW_REQUIRED"
    assert not manifest["fable_review"]["used_for_generation"]
    assert manifest["fable_review"]["validation"] == "VALIDATED"
    review = json.loads((out / "review" / "fable_review.json").read_text(encoding="utf-8"))
    assert review["astra_contract_validation"] == "VALIDATED"
    assert review["status"] == "REVIEW_REQUIRED"
    assert not review["generation_allowed"] and not review["implementation_ready"]
    assert review["astra_functional_spec_draft"]["candidate_features"] == []
    assert len(review["astra_functional_spec_draft"]["unresolved"]) == 2
    assert all(ob["certainty"] == "inferred" for ob in review["astra_observation_bundle"]["observations"])
    assert load_client(out).get("/api/items").json()["total"] == 5


def test_fable_does_not_modify_application_data(tmp_path):
    pytest.importorskip("astra_contracts.observation")
    a, b = tmp_path / "csvonly", tmp_path / "reviewed"
    build(CSV, a)
    build(CSV, b, fable_result=FABLE)
    assert (a / "data.sqlite").read_bytes() == (b / "data.sqlite").read_bytes()
    assert (a / "static" / "app.js").read_bytes() == (b / "static" / "app.js").read_bytes()


def test_reference_details_not_served(tmp_path):
    pytest.importorskip("astra_contracts.observation")
    out = tmp_path / "site"
    build(CSV, out, fable_result=FABLE)
    client = load_client(out)
    assert client.get("/review/fable_review.json").status_code == 404
    assert client.get("/manifest.json").status_code == 404


@pytest.mark.parametrize("bad", [
    "garbage",
    '{"schema_version":"999"}',
    '{"schema_version":"1.0","target":{"input_url":"file:///etc/passwd"}}'
])
def test_bad_fable_refused_no_output(tmp_path, bad):
    f = tmp_path / "fable.json"
    f.write_text(bad, encoding="utf-8")
    with pytest.raises((ValueError, RuntimeError)):
        build(CSV, tmp_path / "site", fable_result=f)
    assert not (tmp_path / "site").exists()


def test_no_astra_validation_no_build(tmp_path, monkeypatch):
    # Production code MUST fail closed rather than fall back to unvalidated review.
    pytest.importorskip("astra_contracts.observation")
    with pytest.raises(ValueError, match="Invalid --astra-root"):
        build(CSV, tmp_path / "site", fable_result=FABLE, astra_root=tmp_path / "absent")
    assert not (tmp_path / "site").exists()


def test_existing_folder_preserved(tmp_path):
    out = tmp_path / "site"
    out.mkdir()
    (out / "do-not-delete.txt").write_text("OWNER", encoding="utf-8")
    with pytest.raises(FileExistsError):
        build(CSV, out)
    assert (out / "do-not-delete.txt").read_text() == "OWNER"


def test_csv_invalid_refused_without_output(tmp_path):
    source = tmp_path / "bad.csv"
    source.write_text("id,title,category\nx,one,A\nx,two,B\n", encoding="utf-8")
    with pytest.raises(ValueError):
        build(source, tmp_path / "site")
    assert not (tmp_path / "site").exists()


def test_fable_secret_paths_not_in_export(tmp_path):
    pytest.importorskip("astra_contracts.observation")
    d = json.loads(FABLE.read_text(encoding="utf-8"))
    d["target"]["input_url"] = "https://example.org/private/PERSON_NAME?token=TOP_SECRET_TOKEN"
    f = tmp_path / "fable.json"
    f.write_text(json.dumps(d), encoding="utf-8")
    out = tmp_path / "site"
    build(CSV, out, fable_result=f)
    review = (out / "review" / "fable_review.json").read_text(encoding="utf-8")
    assert all(word not in review for word in ("PERSON_NAME", "TOP_SECRET_TOKEN", "/api/items"))


def test_csv_original_remains_same(tmp_path):
    before = CSV.read_bytes()
    build(CSV, tmp_path / "site")
    assert CSV.read_bytes() == before


def test_original_fable_remains_same(tmp_path):
    pytest.importorskip("astra_contracts.observation")
    before = FABLE.read_bytes()
    build(CSV, tmp_path / "site", fable_result=FABLE)
    assert FABLE.read_bytes() == before


def test_no_original_fable_copied(tmp_path):
    pytest.importorskip("astra_contracts.observation")
    out = tmp_path / "site"
    build(CSV, out, fable_result=FABLE)
    assert not (out / "result.json").exists()
    assert not (out / "samples").exists()
    assert not (out / FABLE.name).exists()


def test_manifest_disk_equals_cli_return(tmp_path):
    out = tmp_path / "site"
    manifest = build(CSV, out)
    assert json.loads((out / "manifest.json").read_text(encoding="utf-8")) == manifest


@pytest.mark.parametrize("cli_args", [
    [],
    ["--fable-result", "samples/fable_record_redacted.json"],
])
def test_cli_build(tmp_path, cli_args):
    pytest.importorskip("astra_contracts.observation")
    out = tmp_path / "site"
    p = subprocess.run([sys.executable, "-m", "rea.orchestrator", "--csv", str(CSV),
                        "--out", str(out), *cli_args], cwd=ROOT, text=True, capture_output=True)
    assert p.returncode == 0, p.stderr
    response = json.loads(p.stdout)
    assert response["rows"] == 5
    assert out.exists()


def test_cli_rejects_url_switch(tmp_path):
    cmd = [sys.executable, "-m", "rea.orchestrator", "--csv", str(CSV),
           "--out", str(tmp_path / "site"), "--url", "https://example.org"]
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    assert p.returncode != 0
    assert not (tmp_path / "site").exists()
