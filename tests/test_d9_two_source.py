"""D9 deliberate two-source same-schema row append regression."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest
from fastapi.testclient import TestClient
from rea.mvp import DataError
from rea.provenance import AuditError, inspect_delivery
from rea.two_source import preflight_pair, build_pair, pack_pair

ROOT = Path(__file__).resolve().parents[1]
FIRST = ROOT/"samples/qa_guided.csv"
SECOND = ROOT/"samples/qa_pair_extra.json"
MAPPING = {"id":"sku","title":"display_name","category":"group_name"}


def arguments(first=FIRST, second=SECOND, mapping=MAPPING):
    doc=preflight_pair(first,second)
    return (first,second,mapping,doc["sources"][0]["sha256"],
            doc["sources"][1]["sha256"],"APPROVE","APPROVE","APPEND")


def client(folder):
    spec=importlib.util.spec_from_file_location("rea_d9_app",folder/"app.py")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return TestClient(mod.app)


def test_valid_two_file_append_and_local_app(tmp_path):
    first_before,second_before=FIRST.read_bytes(),SECOND.read_bytes()
    first,second,m,h1,h2,a1,a2,confirmation=arguments()
    out=tmp_path/"app"
    doc=build_pair(first,second,out,"Pair",m,h1,h2,a1,a2,confirmation)
    assert doc["rows"]==5 and doc["source_count"]==2
    assert doc["semantic_mapping_status"]=="owner_confirmed_same_schema_append_only"
    receipt=json.loads((out/"append_report.json").read_text(encoding="utf-8"))
    assert receipt==doc["two_file_append"]
    assert receipt["status"]=="OWNER_CONFIRMED_EXPLICIT_APPEND_ONLY"
    assert receipt["mode"]=="SAME_SCHEMA_ROW_APPEND_NO_JOIN"
    assert [x["sha256"] for x in receipt["sources"]]==[h1,h2]
    assert [x["row_count"] for x in receipt["sources"]]==[3,2]
    assert all(x["confirmed"]=="APPROVE" for x in receipt["sources"])
    assert receipt["external_join_or_lookup_used"] is False
    assert receipt["fable_inferred_mapping_used"] is False
    assert FIRST.read_bytes()==first_before and SECOND.read_bytes()==second_before
    web=client(out)
    assert web.get("/api/items").json()["total"]==5
    assert web.get("/api/items/S04").json()["attributes"]["price"]=="6900"
    assert web.get("/api/items?category=디저트").json()["total"]==1
    assert web.get("/api/schema").json()["approved_semantic_bindings"]==[]
    assert web.get("/append_report.json").status_code==404


def test_owner_preflight_only_header_metadata():
    preview=preflight_pair(FIRST,SECOND)
    assert preview["combined_rows"]==5 and preview["source_count"]==2
    dump=json.dumps(preview,ensure_ascii=False)
    assert "초코케이크" not in dump and "카페라떼" not in dump
    assert "S04" not in dump and str(ROOT) not in dump


@pytest.mark.parametrize("index,bad",[(5,"NO"),(6,""),(7,"approve")])
def test_separate_explicit_approvals(index,bad,tmp_path):
    args=list(arguments())
    args[index]=bad
    a,b,m,h1,h2,c1,c2,c3=args
    with pytest.raises(DataError):
        build_pair(a,b,tmp_path/"deny","N",m,h1,h2,c1,c2,c3)
    assert not (tmp_path/"deny").exists()


def test_changed_source_sha_rejected(tmp_path):
    a,b,m,h1,h2,c1,c2,c3=arguments()
    with pytest.raises(DataError,match="changed"):
        build_pair(a,b,tmp_path/"bad","N",m,"f"*64,h2,c1,c2,c3)
    with pytest.raises(DataError,match="changed"):
        build_pair(a,b,tmp_path/"bad","N",m,h1,"f"*64,c1,c2,c3)


def test_different_normalized_columns_rejected(tmp_path):
    other=tmp_path/"other.json"
    other.write_text(json.dumps([{"sku":"S08","display_name":"Other","group_name":"음료",
                                  "extra":"x"}]),encoding="utf-8")
    a,b,m,h1,h2,c1,c2,c3=arguments(FIRST,other)
    with pytest.raises(DataError,match="Different mapped schemas"):
        build_pair(a,b,tmp_path/"bad","N",m,h1,h2,c1,c2,c3)


def test_duplicate_id_across_inputs_rejected(tmp_path):
    other=tmp_path/"dup.csv"
    other.write_text("sku,display_name,group_name,price\nS01,new,음료,100\n",encoding="utf-8")
    a,b,m,h1,h2,c1,c2,c3=arguments(FIRST,other)
    with pytest.raises(DataError,match="Duplicate id across"):
        build_pair(a,b,tmp_path/"bad","N",m,h1,h2,c1,c2,c3)


def test_identical_input_hardlink_and_symlink_refused(tmp_path):
    with pytest.raises(DataError):
        preflight_pair(FIRST,FIRST)
    local=tmp_path/"local.csv"
    local.write_bytes(FIRST.read_bytes())
    hard=tmp_path/"hard.csv"
    hard.hardlink_to(local)
    with pytest.raises(DataError):
        preflight_pair(local,hard)
    link=tmp_path/"alias.json"
    link.symlink_to(SECOND)
    with pytest.raises(DataError):
        preflight_pair(FIRST,link)


def test_invalid_mapping_refused(tmp_path):
    a,b,_,h1,h2,c1,c2,c3=arguments()
    with pytest.raises(DataError):
        build_pair(a,b,tmp_path/"bad","N",
                   {"id":"sku","title":"sku","category":"group_name"},
                   h1,h2,c1,c2,c3)


def test_zip_has_two_source_provenance_and_no_original(tmp_path):
    a,b,m,h1,h2,c1,c2,c3=arguments()
    out=tmp_path/"pair.zip"
    pack_pair(a,b,out,"Pair",m,h1,h2,c1,c2,c3)
    audit=inspect_delivery(out)
    assert audit["two_file_append_receipt_present"] is True
    assert audit["overall_commercial_clearance"]=="NOT_GRANTED"
    with zipfile.ZipFile(out) as z:
        names=set(z.namelist())
        assert "app/append_report.json" in names
        assert "app/data.sqlite" in names
        assert "app/approved_combined.csv" not in names
        doc=json.loads(z.read("app/append_report.json"))
        assert doc["sources"][0]["sha256"]==h1
        assert doc["sources"][1]["sha256"]==h2


def test_no_overwrite_of_owner_folder_or_zip(tmp_path):
    a,b,m,h1,h2,c1,c2,c3=arguments()
    out=tmp_path/"owner"
    out.mkdir()
    (out/"keep").write_text("KEEP",encoding="utf-8")
    with pytest.raises(FileExistsError):
        build_pair(a,b,out,"Pair",m,h1,h2,c1,c2,c3)
    assert (out/"keep").read_text(encoding="utf-8")=="KEEP"
    z=tmp_path/"exists.zip"
    z.write_bytes(b"KEEP")
    with pytest.raises(FileExistsError):
        pack_pair(a,b,z,"Pair",m,h1,h2,c1,c2,c3)
    assert z.read_bytes()==b"KEEP"
