"""D8 local guided one-source review/approval, with no implicit mapping."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest
from fastapi.testclient import TestClient
from rea.guided import approved_selection, preflight
from rea.mvp import DataError, generate
from rea.orchestrator import build
from rea.delivery import create_delivery, verify_delivery
from rea.provenance import AuditError, inspect_delivery

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "samples" / "qa_guided.csv"
JSON = ROOT / "samples" / "qa_guided.json"
MAP_CSV = {"id":"sku","title":"display_name","category":"group_name"}
MAP_JSON = {"id":"item_code","title":"label","category":"region"}


def client(out: Path):
    spec = importlib.util.spec_from_file_location("rea_d8_local", out / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return TestClient(module.app)


@pytest.mark.parametrize("source,mapping,expected_id", [
    (CSV, MAP_CSV, "S01"), (JSON, MAP_JSON, "J01")
])
def test_preflight_and_user_confirmed_mapping_complete_source_unmodified(tmp_path, source, mapping, expected_id):
    original = source.read_bytes()
    info = preflight(source)
    assert len(info["source_sha256"]) == 64
    assert info["row_count"] == 3
    assert info["review_status"] == "UNAPPROVED"
    assert info["approved_semantic_bindings"] == []
    assert info["fields"][0]["name"] == list(mapping.values())[0]
    assert approved_selection(source, mapping, info["source_sha256"], "APPROVE") == mapping
    out = tmp_path / "app"
    manifest = build(source, out, approved_mapping=mapping,
                     expected_source_sha256=info["source_sha256"])
    assert source.read_bytes() == original
    assert manifest["rows"] == 3
    assert manifest["semantic_mapping_status"] == "owner_confirmed_single_source"
    receipt = json.loads((out / "mapping_report.json").read_text(encoding="utf-8"))
    assert receipt == manifest["owner_field_mapping"]
    assert receipt["source_fields"] == mapping
    assert receipt["confirmation_scope"] == "ONE_LOCAL_GENERATION_ONLY"
    assert receipt["fable_inferred_mapping_used"] is False
    web = client(out)
    assert web.get("/api/items").json()["total"] == 3
    assert web.get("/api/items/" + expected_id).status_code == 200
    assert web.get("/api/schema").json()["approved_semantic_bindings"] == []
    assert web.get("/mapping_report.json").status_code == 404
    assert web.post("/api/items").status_code == 405


@pytest.mark.parametrize("bad", [
    {"id":"sku","title":"sku","category":"group_name"},
    {"id":"sku","title":"display_name","category":"missing"},
    {"id":"sku","title":"display_name"},
    {"id":"sku","title":"display_name","category":"group_name","extra":"x"},
    {"id":1,"title":"display_name","category":"group_name"},
])
def test_bad_mappings_fail_without_creating_any_output(tmp_path, bad):
    report=preflight(CSV)
    with pytest.raises(DataError):
        approved_selection(CSV,bad,report["source_sha256"],"APPROVE")
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("confirmation", ["","yes","approve","APPROVE!","NO"])
def test_approval_is_not_default_or_case_insensitive(confirmation):
    report=preflight(CSV)
    with pytest.raises(DataError,match="APPROVE"):
        approved_selection(CSV,MAP_CSV,report["source_sha256"],confirmation)


def test_stale_fingerprint_rejected(tmp_path):
    source = tmp_path / "raw.csv"
    source.write_bytes(CSV.read_bytes())
    old = preflight(source)["source_sha256"]
    source.write_bytes(source.read_bytes().replace(b"S03",b"S04"))
    with pytest.raises(DataError,match="SHA changed"):
        approved_selection(source,MAP_CSV,old,"APPROVE")
    with pytest.raises(DataError,match="changed since"):
        build(source,tmp_path/"output",approved_mapping=MAP_CSV,expected_source_sha256=old)
    assert not (tmp_path/"output").exists()


def test_duplicate_ids_and_empty_required_after_mapping_rejected(tmp_path):
    src=tmp_path/"bad.csv"
    src.write_text("sku,display_name,group_name\nX,one,a\nX,two,b\n",encoding="utf-8")
    report=preflight(src)
    with pytest.raises(DataError,match="duplicate id"):
        approved_selection(src,MAP_CSV,report["source_sha256"],"APPROVE")
    src.write_text("sku,display_name,group_name\nY,one,a\nZ,,b\n",encoding="utf-8")
    report=preflight(src)
    with pytest.raises(DataError,match="missing title"):
        approved_selection(src,MAP_CSV,report["source_sha256"],"APPROVE")


def test_collision_with_unselected_reserved_field_is_rejected(tmp_path):
    src=tmp_path/"other.csv"
    src.write_text("sku,display_name,group_name,id\nS01,one,x,OLD\n",encoding="utf-8")
    report=preflight(src)
    with pytest.raises(DataError,match="collides"):
        approved_selection(src,MAP_CSV,report["source_sha256"],"APPROVE")


def test_legacy_exact_schema_still_requires_no_manual_mapping(tmp_path):
    source=ROOT/"samples/qa_cafe.csv"
    out=tmp_path/"legacy"
    result=build(source,out)
    assert result["rows"]==4
    assert result["semantic_mapping_status"]=="not_approved"
    assert "owner_field_mapping" not in result
    assert not (out/"mapping_report.json").exists()


@pytest.mark.parametrize("source,mapping",[(CSV,MAP_CSV),(JSON,MAP_JSON)])
def test_guided_zip_audited_and_preview_not_served(tmp_path,source,mapping):
    report=preflight(source)
    zip_path=tmp_path/"owner.zip"
    create_delivery(source,zip_path,approved_mapping=mapping,
                    expected_source_sha256=report["source_sha256"])
    verify_delivery(zip_path)
    audit=inspect_delivery(zip_path)
    assert audit["owner_mapping_receipt_present"] is True
    assert audit["overall_commercial_clearance"]=="NOT_GRANTED"
    with zipfile.ZipFile(zip_path) as zf:
        names=set(zf.namelist())
        assert "app/mapping_report.json" in names
        assert "app/data.sqlite" in names
        assert source.name not in names
        receipt=json.loads(zf.read("app/mapping_report.json"))
        assert receipt["source_fields"]==mapping


def test_mapping_receipt_removed_even_with_rehashed_archive_fails_audit(tmp_path):
    source=CSV
    good=tmp_path/"good.zip"
    create_delivery(source,good,approved_mapping=MAP_CSV,
                    expected_source_sha256=preflight(source)["source_sha256"])
    with zipfile.ZipFile(good) as zf:
        entries={n:zf.read(n) for n in zf.namelist()
                 if n not in {"delivery_manifest.json","app/mapping_report.json"}}
    changed=tmp_path/"bad.zip"
    mani={"schema_version":"rea.delivery.v0.1","files":[
        {"path":p,"sha256":hashlib.sha256(contents).hexdigest(),"bytes":len(contents)}
        for p,contents in sorted(entries.items())]}
    entries["delivery_manifest.json"]=json.dumps(mani).encode()
    with zipfile.ZipFile(changed,"x") as zf:
        for p,contents in entries.items():zf.writestr(p,contents)
    with pytest.raises(AuditError,match="report missing"):
        inspect_delivery(changed)


def test_inspect_cli_does_not_print_record_values(tmp_path):
    p=subprocess.run([sys.executable,"-m","rea.guided","inspect","--csv",str(CSV)],
                     cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    assert "LOCAL OWNER FILE -" in p.stdout
    assert "sku:" in p.stdout
    assert "S01" not in p.stdout and "아메리카노" not in p.stdout


def test_wizard_interactive_requires_owner_typing(tmp_path):
    out=tmp_path/"wizard"
    argv=[sys.executable,"-m","rea.guided","wizard","--csv",str(CSV),"--out",str(out)]
    denied=subprocess.run(argv,cwd=ROOT,input="sku\ndisplay_name\ngroup_name\nNO\n",
                          capture_output=True,text=True)
    assert denied.returncode!=0 and not out.exists()
    approved=subprocess.run(argv,cwd=ROOT,input="sku\ndisplay_name\ngroup_name\nAPPROVE\n",
                            capture_output=True,text=True)
    assert approved.returncode==0,approved.stderr
    assert (out/"mapping_report.json").exists()
    assert client(out).get("/api/items").json()["total"]==3


def test_noninteractive_build_cli_requires_fingerprint_and_approval(tmp_path):
    sha=preflight(JSON)["source_sha256"]
    argv=[sys.executable,"-m","rea.guided","build","--json",str(JSON),
          "--id-field","item_code","--title-field","label","--category-field","region",
          "--source-sha256",sha,"--confirm","APPROVE","--out",str(tmp_path/"app")]
    ok=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True)
    assert ok.returncode==0,ok.stderr
    assert (tmp_path/"app"/"mapping_report.json").is_file()
    bad=subprocess.run([*argv[:-3],"NO","--out",str(tmp_path/"never")],
                       cwd=ROOT,capture_output=True,text=True)
    assert bad.returncode!=0
    assert not (tmp_path/"never").exists()


def test_owner_source_symlink_and_nested_json_rejected(tmp_path):
    link=tmp_path/"linked.csv"
    link.symlink_to(CSV)
    with pytest.raises(DataError):
        preflight(link)
    j=tmp_path/"bad.json"
    j.write_text('[{"item_code":"X","label":"one","region":"r","complex":{"a":"x"}}]',
                 encoding="utf-8")
    with pytest.raises(DataError):
        preflight(j)
