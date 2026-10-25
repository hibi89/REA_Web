"""Extra D9 failure boundary and ZIP provenance tests."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest
from rea.mvp import DataError
from rea.provenance import AuditError, inspect_delivery
from rea.two_source import preflight_pair, build_pair, pack_pair

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/"samples/qa_guided.csv"
B=ROOT/"samples/qa_pair_extra.json"
M={"id":"sku","title":"display_name","category":"group_name"}


def inputs(a=A,b=B):
    p=preflight_pair(a,b)
    return (a,b,M,p["sources"][0]["sha256"],p["sources"][1]["sha256"],
            "APPROVE","APPROVE","APPEND")


def test_10001_combined_rows_refused(tmp_path):
    a,b=tmp_path/"one.csv",tmp_path/"two.csv"
    head="sku,display_name,group_name,price\n"
    a.write_text(head+"".join(f"A{i},item,cat,1\n" for i in range(5001)),encoding="utf-8")
    b.write_text(head+"".join(f"B{i},item,cat,1\n" for i in range(5000)),encoding="utf-8")
    with pytest.raises(DataError,match="10,000"):
        preflight_pair(a,b)


def test_combined_10mb_refused_even_individually_under_limit(tmp_path):
    a,b=tmp_path/"one.csv",tmp_path/"two.csv"
    for p,c in ((a,"A"),(b,"B")):
        with p.open("w",encoding="utf-8") as f:
            f.write("sku,display_name,group_name,price,note\n")
            for i in range(3350):
                f.write(f"{c}{i},name,cat,1,{('z'*1600)}\n")
    assert a.stat().st_size < 10*1024*1024 and b.stat().st_size < 10*1024*1024
    with pytest.raises(DataError,match="10 MiB"):
        preflight_pair(a,b)


def test_unselected_reserved_column_rejected(tmp_path):
    b=tmp_path/"bad.csv"
    b.write_text("sku,display_name,group_name,price,id\nS20,x,c,2,extra\n",encoding="utf-8")
    params=inputs(A,b)
    with pytest.raises(DataError,match="collides"):
        build_pair(params[0],params[1],tmp_path/"not_created","N",*params[2:])


def test_tampered_archive_with_recomputed_sha_without_receipt_fails(tmp_path):
    a,b,m,h1,h2,c1,c2,c3=inputs()
    good=tmp_path/"good.zip"
    pack_pair(a,b,good,"P",m,h1,h2,c1,c2,c3)
    with zipfile.ZipFile(good) as f:
        raw={n:f.read(n) for n in f.namelist()
             if n not in {"delivery_manifest.json","app/append_report.json"}}
    manifest={"schema_version":"rea.delivery.v0.1","files":[
        {"path":n,"sha256":hashlib.sha256(v).hexdigest(),"bytes":len(v)}
        for n,v in sorted(raw.items())]}
    raw["delivery_manifest.json"]=json.dumps(manifest).encode()
    other=tmp_path/"tampered.zip"
    with zipfile.ZipFile(other,"x") as f:
        for n,v in raw.items():f.writestr(n,v)
    with pytest.raises(AuditError,match="Missing two-file"):
        inspect_delivery(other)


def test_command_build_pack_and_inspect_with_owner_confirmation(tmp_path):
    sha=preflight_pair(A,B)
    common=["--first",str(A),"--second",str(B),
            "--id-field","sku","--title-field","display_name",
            "--category-field","group_name",
            "--first-sha256",sha["sources"][0]["sha256"],
            "--second-sha256",sha["sources"][1]["sha256"],
            "--approve-first","APPROVE","--approve-second","APPROVE",
            "--confirm-append","APPEND"]
    command=[sys.executable,"-m","rea.two_source"]
    pre=subprocess.run(command+["inspect","--first",str(A),"--second",str(B)],
                       cwd=ROOT,capture_output=True,text=True)
    assert pre.returncode==0,pre.stderr
    assert "초코케이크" not in pre.stdout and "S01" not in pre.stdout
    for mode,output in (("build","app"),("pack","app.zip")):
        out=tmp_path/output
        p=subprocess.run(command+[mode,*common,"--out",str(out)],
                         cwd=ROOT,capture_output=True,text=True)
        assert p.returncode==0,p.stderr
        assert out.exists()
        if mode=="pack":
            assert inspect_delivery(out)["two_file_append_receipt_present"] is True
