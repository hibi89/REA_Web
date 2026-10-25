"""D15 optional Tk pair controller: only owner-approved same-schema ROW APPEND."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import zipfile

import pytest

from rea.mvp import DataError
from rea.pair_creator import PairCreatorController
from rea.provenance import inspect_delivery

ROOT = Path(__file__).resolve().parents[1]
FIRST = ROOT / "samples/qa_guided.csv"
SECOND = ROOT / "samples/qa_pair_extra.json"
MAPPING = {"id": "sku", "title": "display_name", "category": "group_name"}


def allowed(controller, out, first=FIRST, second=SECOND, mapping=MAPPING):
    return controller.export(first, second, out, "Two-file owner app", mapping,
                             True, True, "APPROVE", "APPROVE", "APPEND")


def test_real_two_file_zip_and_immutable_originals(tmp_path):
    old_a, old_b = FIRST.read_bytes(), SECOND.read_bytes()
    c = PairCreatorController()
    p = c.inspect(FIRST, SECOND)
    assert (p.first_rows, p.second_rows) == (3, 2)
    assert p.first_sha == hashlib.sha256(old_a).hexdigest()
    assert p.second_sha == hashlib.sha256(old_b).hexdigest()
    zip_path = tmp_path / "merged.zip"
    allowed(c, zip_path)
    assert c.inspected is None
    assert FIRST.read_bytes() == old_a and SECOND.read_bytes() == old_b
    audit = inspect_delivery(zip_path)
    assert audit["two_file_append_receipt_present"] is True
    assert audit["overall_commercial_clearance"] == "NOT_GRANTED"
    with zipfile.ZipFile(zip_path) as z:
        manifest = json.loads(z.read("app/manifest.json"))
        receipt = json.loads(z.read("app/append_report.json"))
        assert manifest["rows"] == 5 and manifest["source_count"] == 2
        assert receipt["mode"] == "SAME_SCHEMA_ROW_APPEND_NO_JOIN"
        assert receipt["combined_confirmation"] == "APPEND"
        assert all(x["confirmed"] == "APPROVE" for x in receipt["sources"])
        assert "app/data.sqlite" in z.namelist()


@pytest.mark.parametrize("a,b,c,d,e", [
    (False,True,"APPROVE","APPROVE","APPEND"),
    (True,False,"APPROVE","APPROVE","APPEND"),
    (True,True,"approve","APPROVE","APPEND"),
    (True,True,"APPROVE","approve","APPEND"),
    (True,True,"APPROVE","APPROVE","append"),
    (True,True,"APPROVE","APPROVE",""),
])
def test_independent_rights_and_confirmations_required(tmp_path,a,b,c,d,e):
    ctl = PairCreatorController()
    ctl.inspect(FIRST,SECOND)
    with pytest.raises(DataError):
        ctl.export(FIRST,SECOND,tmp_path/"no.zip","No",MAPPING,a,b,c,d,e)
    assert not (tmp_path/"no.zip").exists()
    assert ctl.inspected is not None


def test_no_export_without_both_file_inspections(tmp_path):
    with pytest.raises(DataError,match="BOTH"):
        allowed(PairCreatorController(),tmp_path/"no.zip")


def test_changed_file_selection_clears_preview(tmp_path):
    ctl=PairCreatorController()
    ctl.inspect(FIRST,SECOND)
    with pytest.raises(DataError,match="changed"):
        ctl.export(SECOND,FIRST,tmp_path/"no.zip","No",MAPPING,
                   True,True,"APPROVE","APPROVE","APPEND")
    assert ctl.inspected is None


@pytest.mark.parametrize("which",["first","second"])
def test_stale_sha_denied_no_output(tmp_path,which):
    a=tmp_path/"a.csv"
    b=tmp_path/"b.json"
    a.write_bytes(FIRST.read_bytes())
    b.write_bytes(SECOND.read_bytes())
    ctl=PairCreatorController()
    ctl.inspect(a,b)
    target = a if which=="first" else b
    data=target.read_bytes()
    assert len(data)>0
    # Change a valid CSV cell, or legal insignificant JSON trailing space,
    # so source digest drift is the only rejection under test.
    target.write_bytes(data.replace(b"S01", b"S99", 1) if which=="first"
                       else data+b" ")
    with pytest.raises(DataError,match="changed"):
        allowed(ctl,tmp_path/"no.zip",a,b)
    assert not (tmp_path/"no.zip").exists()


def test_differing_schema_rejected(tmp_path):
    bad=tmp_path/"bad.json"
    bad.write_text('[{"sku":"S30","display_name":"value","group_name":"x","extra":"y"}]',
                   encoding="utf-8")
    ctl=PairCreatorController()
    ctl.inspect(FIRST,bad)
    with pytest.raises(DataError,match="identical column"):
        allowed(ctl,tmp_path/"no.zip",FIRST,bad)
    assert not (tmp_path/"no.zip").exists()


def test_duplicate_id_across_files_denied(tmp_path):
    dup=tmp_path/"dup.csv"
    dup.write_text("sku,display_name,group_name,price\nS01,duplicate,x,100\n",
                   encoding="utf-8")
    ctl=PairCreatorController()
    ctl.inspect(FIRST,dup)
    with pytest.raises(DataError,match="Duplicate id"):
        allowed(ctl,tmp_path/"no.zip",FIRST,dup)


@pytest.mark.parametrize("mapping", [
    {"id":"sku","title":"sku","category":"group_name"},
    {"id":"sku","title":"display_name","category":"missing"},
    {"id":"sku","title":"display_name"},
])
def test_guessed_or_duplicate_mapping_denied(tmp_path,mapping):
    ctl=PairCreatorController()
    ctl.inspect(FIRST,SECOND)
    with pytest.raises(DataError):
        allowed(ctl,tmp_path/"no.zip",mapping=mapping)


def test_samefile_and_symlink_rejected(tmp_path):
    ctl=PairCreatorController()
    with pytest.raises(DataError):
        ctl.inspect(FIRST,FIRST)
    link=tmp_path/"linked.csv"
    try:
        link.symlink_to(FIRST)
    except (NotImplementedError,OSError):
        pytest.skip("No symlink permission on this Windows runner")
    with pytest.raises(DataError):
        ctl.inspect(link,SECOND)
    assert ctl.inspected is None


def test_existing_zip_no_overwrite_and_no_reuse_after_success(tmp_path):
    existing=tmp_path/"keep.zip"
    existing.write_bytes(b"KEEP")
    c=PairCreatorController()
    c.inspect(FIRST,SECOND)
    with pytest.raises(FileExistsError):
        allowed(c,existing)
    assert existing.read_bytes()==b"KEEP"
    out=tmp_path/"good.zip"
    allowed(c,out)
    with pytest.raises(DataError,match="Inspect"):
        allowed(c,tmp_path/"second.zip")
    assert not (tmp_path/"second.zip").exists()


def test_pair_import_does_not_require_display():
    import rea.pair_creator_window as gui
    assert callable(gui.build_pair_window)
    assert "pair_button" in (ROOT/"rea/creator_gui.py").read_text(encoding="utf-8")


def test_empty_name_and_non_zip_path_denied(tmp_path):
    c=PairCreatorController()
    c.inspect(FIRST,SECOND)
    with pytest.raises(DataError,match="name"):
        c.export(FIRST,SECOND,tmp_path/"no.zip"," ",MAPPING,
                 True,True,"APPROVE","APPROVE","APPEND")
    with pytest.raises(DataError,match="ZIP"):
        allowed(c,tmp_path/"no.csv")
