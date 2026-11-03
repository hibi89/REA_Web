"""End-to-end one-command user workflow with only self-authored source ZIP/JSON."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

from rea.adapter.offline_compose import compose
from rea.adapter.frontend_bridge import BridgeError
from tests_static_fixture import FABLE, BINDINGS

SELF_AUTHORED_FASTAPI = '''from fastapi import FastAPI
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


def fixture(tmp_path):
    backend = tmp_path / "trusted_synthetic.zip"
    with zipfile.ZipFile(backend, "w", compression=zipfile.ZIP_DEFLATED) as writer:
        writer.writestr("app.py", SELF_AUTHORED_FASTAPI)
    fable = tmp_path / "fable.json"
    fable.write_text(json.dumps(FABLE), encoding="utf-8")
    bindings = tmp_path / "bindings.json"
    bindings.write_text(json.dumps(BINDINGS), encoding="utf-8")
    return backend, fable, bindings


def cmd(*args):
    return subprocess.run(
        [sys.executable, "-m", "rea.adapter.offline_compose", *map(str,args)],
        capture_output=True, text=True,
    )


def test_preview_then_generate_one_command_without_running_backend(tmp_path):
    backend, fable, bindings = fixture(tmp_path)
    preview = cmd("--backend-zip",backend,"--fable",fable,
                  "--owner-authorized-source")
    assert preview.returncode == 0, preview.stderr
    data = json.loads(preview.stdout)
    assert data["status"] == "OWNER_REVIEW_REQUIRED"
    assert data["frontend_source_generated"] is False
    assert data["candidate_get_paths"] == [
        "/api/jobs","/api/jobs/{job_id}","/api/metrics"]
    assert data["network_performed"] is False and data["backend_executed"] is False
    assert data["release_allowed"] is False
    assert not any(p.is_dir() for p in tmp_path.iterdir())

    out = tmp_path / "dashboard"
    approved = cmd("--backend-zip",backend,"--fable",fable,"--bindings",bindings,
                   "--out",out,"--owner-authorized-source","--owner-confirmed")
    assert approved.returncode == 0, approved.stderr
    report = json.loads(approved.stdout)
    assert report["frontend_source_generated"] is True
    assert report["status"] == "FRONTEND_SOURCE_GENERATED_NOT_RUNTIME_VERIFIED"
    assert report["customer_runtime_verified"] is False
    assert report["release_allowed"] is False
    assert {p.name for p in out.iterdir()} == {
        "index.html", "app.js", "style.css", "manifest.json", "README_KO.md"}
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["backend"]["runtime_verified"] is False
    assert manifest["bindings"] == BINDINGS
    assert "fetch(" in (out / "app.js").read_text(encoding="utf-8")
    previous = {p.name: p.read_bytes() for p in out.iterdir()}

    rejected = cmd("--backend-zip",backend,"--fable",fable,"--bindings",bindings,
                   "--out",out,"--owner-authorized-source","--owner-confirmed")
    assert rejected.returncode == 2
    assert previous == {p.name:p.read_bytes() for p in out.iterdir()}


def test_source_permission_and_mapping_confirmation_are_separate(tmp_path):
    backend, fable, bindings = fixture(tmp_path)
    out = tmp_path / "new"
    for args in (
        ("--backend-zip",backend,"--fable",fable),
        ("--backend-zip",backend,"--fable",fable,"--out",out,
         "--bindings",bindings,"--owner-authorized-source"),
        ("--backend-zip",backend,"--fable",fable,"--out",out,
         "--owner-authorized-source","--owner-confirmed"),
        ("--backend-zip",backend,"--fable",fable,
         "--owner-authorized-source","--owner-confirmed"),
    ):
        response = cmd(*args)
        assert response.returncode == 2
        assert not out.exists()


def test_nonexistent_and_incompatible_bindings_fail_without_output(tmp_path):
    backend, fable, bindings = fixture(tmp_path)
    bad = json.loads(bindings.read_text(encoding="utf-8"))
    bad["list"]["path"] = "/api/preview"  # POST is not a GET candidate.
    bindings.write_text(json.dumps(bad),encoding="utf-8")
    out = tmp_path / "output"
    rejected = cmd("--backend-zip",backend,"--fable",fable,"--bindings",bindings,
                   "--out",out,"--owner-authorized-source","--owner-confirmed")
    assert rejected.returncode == 2 and not out.exists()
    assert "list: GET declaration not found" in rejected.stderr


def test_composer_function_returns_review_only_for_authorized_preview(tmp_path):
    backend, fable, _ = fixture(tmp_path)
    with pytest.raises(BridgeError,match="owner-authorized-source"):
        compose(backend,fable)
    review = compose(backend,fable,source_authorized=True)
    assert review["status"] == "OWNER_REVIEW_REQUIRED"
    assert review["bindings_present"] is False
    assert review["source_rights_verified"] is False
    assert review["backend_executed"] is False
