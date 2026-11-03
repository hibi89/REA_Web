"""Operator input to independent frontend using self-authored ZIP/Fable only."""
from __future__ import annotations

import json
import subprocess
import sys
import zipfile

import pytest

from rea.adapter.offline_compose import compose
from rea.adapter.frontend_bridge import BridgeError
from tests_static_fixture import FABLE

SOURCE = '''
from fastapi import FastAPI
app=FastAPI()
@app.get("/api/jobs")
def jobs(): return {"items":[]}
@app.get("/api/metrics")
def metrics(): return {"total":0}
@app.get("/api/jobs/{job_id}")
def detail(job_id:str): return {"id":job_id}
@app.post("/api/preview")
def preview(): return {}
'''


def files(tmp_path):
    archive = tmp_path / "self_authored.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("app.py", SOURCE)
    fable = tmp_path / "fable.json"
    fable.write_text(json.dumps(FABLE), encoding="utf-8")
    return archive, fable


def invoke(archive, fable, dest, choices, *args):
    return subprocess.run(
        [sys.executable, "-m", "rea.adapter.offline_wizard",
         "--backend-zip", str(archive), "--fable", str(fable),
         "--out", str(dest), *args],
        input=choices, capture_output=True, text=True, timeout=25)


# Plain GET: /api/jobs (1), /api/metrics (2). Detail: /api/jobs/{job_id} (1).
OK = "1\nitems\n2\n__root__\n1\n__root__\nAPPROVE\n"


def test_wizard_interactive_flow_generates_frontend_only(tmp_path):
    archive, fable = files(tmp_path)
    dest = tmp_path / "dashboard"
    result = invoke(archive, fable, dest, OK, "--owner-authorized-source")
    assert result.returncode == 0, result.stderr
    assert "ZIP SHA256:" in result.stdout
    assert {p.name for p in dest.iterdir()} == {
        "index.html", "style.css", "app.js", "manifest.json", "README_KO.md"}
    manifest = json.loads((dest / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["bindings"]["detail"]["path_param"] == "job_id"
    assert manifest["bindings"]["list"]["field"] == "items"
    assert manifest["backend"]["runtime_verified"] is False
    assert archive.is_file()
    again = invoke(archive, fable, dest, OK, "--owner-authorized-source")
    assert again.returncode == 2
    assert "already exists" in again.stderr


@pytest.mark.parametrize("text", [
    "1\nitems\n2\n__root__\n1\n__root__\nDECLINE\n",
    "1\nitems\n2\n__root__\n1\n__root__\n",
    "3\nitems\n2\n__root__\n1\n__root__\nAPPROVE\n",
    "1\nitems\n2\nbad.field\n1\n__root__\nAPPROVE\n",
])
def test_decline_eof_bad_route_or_field_fails_closed(tmp_path, text):
    archive, fable = files(tmp_path)
    dest = tmp_path / "new"
    response = invoke(archive, fable, dest, text, "--owner-authorized-source")
    assert response.returncode == 2
    assert not dest.exists()


def test_no_permission_rejects_before_zip_read(tmp_path):
    dest = tmp_path / "new"
    response = invoke(tmp_path / "absent.zip", tmp_path / "absent.json", dest, OK)
    assert response.returncode == 2
    assert "owner-authorized-source" in response.stderr
    assert not dest.exists()


def test_sha_drift_rejects_static_output(tmp_path):
    archive, fable = files(tmp_path)
    preview = compose(archive, fable, source_authorized=True)
    assert len(preview["backend_sha256"]) == 64
    with pytest.raises(BridgeError, match="ZIP SHA changed"):
        compose(archive, fable, source_authorized=True,
                expected_backend_sha256="0" * 64)


def test_optional_owner_presentation_map(tmp_path):
    archive, fable = files(tmp_path)
    pres = tmp_path / "presentation.json"
    pres.write_text(json.dumps({
        "item":{"id":"code","name":"title","category":"group","status":"state"},
        "metrics":{"total":"count_all","completed":"count_ok","pending":"count_wait"},
        "detail_fields":["code","title","group","state"],
    }),encoding="utf-8")
    dest = tmp_path / "dashboard"
    response = invoke(archive,fable,dest,OK,"--owner-authorized-source",
                      "--presentation",str(pres))
    assert response.returncode == 0,response.stderr
    manifest = json.loads((dest/"manifest.json").read_text(encoding="utf-8"))
    assert manifest["bindings"]["presentation"]["item"]["id"] == "code"


def test_paginated_wizard_accepts_explicit_query_and_total_mapping(tmp_path):
    archive, fable = files(tmp_path)
    dest = tmp_path / 'paged'
    choices = '1\nitems\n2\n__root__\ntotal\nlimit\noffset\n100\n1\n__root__\nAPPROVE\n'
    outcome = invoke(archive, fable, dest, choices, '--owner-authorized-source', '--paginated-list')
    assert outcome.returncode == 0, outcome.stderr
    manifest = json.loads((dest / 'manifest.json').read_text(encoding='utf-8'))
    assert manifest['bindings']['list']['pagination'] == {
        'total_field':'total','limit_param':'limit',
        'offset_param':'offset','page_size':100}


@pytest.mark.parametrize('size', ['0', '101', 'not-a-number'])
def test_bad_pagination_size_fails_without_output(tmp_path,size):
    archive,fable=files(tmp_path)
    dest=tmp_path/'no_output'
    choices='1\nitems\n2\n__root__\ntotal\nlimit\noffset\n'+size+'\n1\n__root__\nAPPROVE\n'
    outcome=invoke(archive,fable,dest,choices,'--owner-authorized-source','--paginated-list')
    assert outcome.returncode == 2
    assert not dest.exists()
