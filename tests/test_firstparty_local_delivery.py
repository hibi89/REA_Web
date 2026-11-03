"""Actual generated REA FastAPI/SQLite app packaged and integrity checked."""
from __future__ import annotations
import csv
import json
import subprocess
import sys
import zipfile

import pytest

from rea.adapter.local_product import build
from rea.adapter.local_delivery import pack, verify_archive, UnsafeLocalDelivery
from tests_static_fixture import FABLE

from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def _app(tmp_path):
    data=tmp_path/"owned.csv"
    with data.open("w",encoding="utf-8",newline="") as stream:
        writer=csv.writer(stream)
        writer.writerow(["id","title","category"])
        for i in range(130):
            writer.writerow([f"id-{i}",f"Title {i}","A" if i%2 else "B"])
    fable=tmp_path/"fable.json"
    fable.write_text(json.dumps(FABLE),encoding="utf-8")
    folder=tmp_path/"generated"
    build(data,fable,ROOT/"samples"/"rea_firstparty_bindings.json",
          folder,owner_authorized_data=True,owner_confirmed=True)
    return folder,data,fable


def test_real_app_zip_determinism_and_extracted_local_check(tmp_path):
    app,data,fable=_app(tmp_path)
    before=data.read_bytes(),fable.read_bytes()
    first=tmp_path/"first.zip"
    other=tmp_path/"second.zip"
    with pytest.raises(UnsafeLocalDelivery,match="owner-confirmed"):
        pack(app,first)
    assert not first.exists()
    result=pack(app,first,owner_confirmed=True)
    assert result["rows"]==130
    assert result["status"]=="ZIP_CREATED_NOT_COMMERCIAL"
    assert verify_archive(first)["zip_sha256"]==result["zip_sha256"]
    assert pack(app,other,owner_confirmed=True)["zip_sha256"]==result["zip_sha256"]
    with zipfile.ZipFile(first) as archive:
        assert all(path.startswith("REA_LOCAL_APP/") for path in archive.namelist())
        assert "REA_LOCAL_APP/data.sqlite" in archive.namelist()
        assert "REA_LOCAL_APP/owned.csv" not in archive.namelist()
        archive.extractall(tmp_path/"unzipped")  # verified test-owned ZIP only
    path=tmp_path/"unzipped"/"REA_LOCAL_APP"
    checked=subprocess.run([sys.executable,str(path/"SELF_CHECK.py"),"--check"],
                           cwd=path,text=True,capture_output=True,timeout=20)
    assert checked.returncode==0,checked.stderr
    assert "LOCAL_INTEGRITY_PASS" in checked.stdout
    if sys.platform=="win32":
        cmd=subprocess.run(["cmd","/d","/c",str(path/"RUN_LOCAL_WINDOWS.cmd"),"--check"],
                           cwd=path,text=True,capture_output=True,timeout=20)
        assert cmd.returncode==0,cmd.stderr
    assert (data.read_bytes(),fable.read_bytes())==before
    with pytest.raises(UnsafeLocalDelivery,match="NEW"):
        pack(app,first,owner_confirmed=True)


def test_modified_app_refused_before_zip_written(tmp_path):
    folder,_,_=_app(tmp_path)
    dest=tmp_path/"reject.zip"
    changed=folder/"dashboard"/"app.js"
    changed.write_bytes(changed.read_bytes()+b"\n// altered")
    with pytest.raises(UnsafeLocalDelivery,match="hash mismatch"):
        pack(folder,dest,owner_confirmed=True)
    assert not dest.exists()


def test_modified_zip_fails_independent_verify(tmp_path):
    folder,_,_=_app(tmp_path)
    src=tmp_path/"valid.zip"
    pack(folder,src,owner_confirmed=True)
    bad=tmp_path/"altered.zip"
    with zipfile.ZipFile(src) as source, zipfile.ZipFile(bad,"w") as output:
        for info in source.infolist():
            data=source.read(info)
            if info.filename.endswith("/dashboard/style.css"):
                data+=b"\n/* changed */"
            output.writestr(info,data)
    with pytest.raises(UnsafeLocalDelivery,match="hash mismatch"):
        verify_archive(bad)
