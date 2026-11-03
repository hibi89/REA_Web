"""Schema hints are AST-only; no execution, auth, or response verification claims."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest
from rea.adapter.backend_schema import inspect_backend_schema, UnsafeSchema
from rea.adapter.backend_zip import UnsafeBackendZip


SOURCE = '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
app = FastAPI()
class Job(BaseModel):
    id: str
    name: str
    status: str = "pending"
    private_note: str = "TOKEN_MUST_NOT_EXPORT"
class PreviewRequest(BaseModel):
    job_id: str = Field(min_length=1)
    mode: Literal["dry_run"] = "dry_run"
@app.get("/api/jobs", response_model=list[Job])
def jobs(limit: int = 10):
    return []
@app.get("/api/jobs/{job_id}", response_model=Job)
def job(job_id: str):
    return Job(id=job_id, name="dummy")
@app.post("/api/preview")
def preview(request: PreviewRequest):
    return {"ok":True}
@app.get("/api/unknown")
def unknown():
    return {"secret": "DONT_RETAIN_RETURN_LITERAL"}
'''


def make_zip(path, source=SOURCE, extra=None):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("app.py", source)
        for key, val in (extra or {}).items():
            archive.writestr(key, val)
    return path


def route(contract, path):
    return next(e for e in contract['routes'] if e['path'] == path)


def test_pydantic_declarations_and_routes(tmp_path):
    z = make_zip(tmp_path/'fixture.zip')
    result = inspect_backend_schema(z)
    assert result == inspect_backend_schema(z)
    assert result['schema_version'] == 'rea.backend_schema.v0.1'
    assert result['generation_allowed'] is False and result['execution_performed'] is False
    assert result['backend_sha256'] == hashlib.sha256(z.read_bytes()).hexdigest()
    job = route(result, '/api/jobs')
    assert job['response']['type_hint'] == 'list[Job]'
    assert job['response']['source'] == 'response_model_declaration'
    assert job['response']['models'][0]['model'] == 'Job'
    assert job['response']['models'][0]['fields'][0] == {'name':'id','type':'str','required_hint':True}
    assert job['parameters'][0]['name'] == 'limit'
    assert job['parameters'][0]['location_hint'] == 'query_or_dependency'
    detail = route(result, '/api/jobs/{job_id}')
    assert detail['parameters'][0]['location_hint'] == 'path'
    assert detail['parameters'][0]['required_hint'] is True
    preview = route(result, '/api/preview')
    assert preview['request_body']['model'] == 'PreviewRequest'
    assert preview['request_body']['fields'][0]['name'] == 'job_id'
    assert preview['request_body']['fields'][0]['required_hint'] is True
    assert preview['request_body']['fields'][1]['type'] == 'unknown'  # Literal values excluded
    assert preview['response']['type_hint'] == 'unknown'
    assert route(result, '/api/unknown')['response']['type_hint'] == 'unknown'
    assert 'TOKEN_MUST_NOT_EXPORT' not in json.dumps(result)
    assert 'DONT_RETAIN_RETURN_LITERAL' not in json.dumps(result)


def test_no_import_execution_or_annotations_eval(tmp_path):
    marker = tmp_path/'LEAK_CREATED'
    snippet = f'''from fastapi import FastAPI
from pydantic import BaseModel
open({str(marker)!r},'w').write('leak')
app=FastAPI()
class Evil(BaseModel):
  key: __import__('os').system('touch BAD')
@app.get('/api/x')
def x() -> Evil: return Evil()
'''
    contract = inspect_backend_schema(make_zip(tmp_path/'test.zip',snippet))
    assert not marker.exists()
    assert route(contract, '/api/x')['response']['type_hint'] == 'Evil'
    assert route(contract, '/api/x')['response']['models'][0]['fields'][0]['type'] == 'unknown'


def test_bad_archives_reuse_original_security_gate(tmp_path):
    malicious = make_zip(tmp_path/'bad.zip',extra={'../escape.py':'evil'})
    with pytest.raises(UnsafeBackendZip):inspect_backend_schema(malicious)
    suspicious = tmp_path/'empty.zip'
    suspicious.write_bytes(b'not-a-zip')
    with pytest.raises(UnsafeBackendZip):inspect_backend_schema(suspicious)


def test_imported_model_unresolved_not_guessed(tmp_path):
    text = '''from fastapi import FastAPI
from some_module import Person
app = FastAPI()
@app.get('/api/profile',response_model=Person)
def profile() -> Person:
  return Person()
'''
    result = inspect_backend_schema(make_zip(tmp_path/'src.zip',text))
    assert route(result,'/api/profile')['response']['type_hint'] == 'unknown'
    assert route(result,'/api/profile')['response']['models'] == []


def test_routes_and_schema_source_correspond(tmp_path):
    source = '''from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
app=FastAPI()
r=APIRouter(prefix='/api')
class Summary(BaseModel):
    total: int
@r.get('/metrics',response_model=Summary)
def metrics():return {}
app.include_router(r,prefix='/v2')
'''
    result = inspect_backend_schema(make_zip(tmp_path/'src.zip',source))
    assert route(result,'/v2/api/metrics')['response']['models'][0]['fields'][0]['name']=='total'


def test_same_size_zip_rewrite_during_schema_ast_rejected(tmp_path, monkeypatch):
    # A stable ZIP fingerprint must not describe AST hints read from different
    # bytes, even when another handle rewrites the same-length file in place.
    from rea.adapter import backend_schema as schema
    original = tmp_path / "backend.zip"
    replacement = tmp_path / "replacement.zip"
    a = SOURCE
    b = SOURCE.replace("name: str", "kind: str")
    assert len(a) == len(b) and a != b
    for path, body in ((original, a), (replacement, b)):
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as writer:
            writer.writestr("app.py", body)
    before, after = original.read_bytes(), replacement.read_bytes()
    assert len(before) == len(after)
    assert hashlib.sha256(before).digest() != hashlib.sha256(after).digest()

    real_models = schema._models
    changed = []

    def mutate_after_ast_read(tree):
        if not changed:
            changed.append(True)
            with original.open("r+b") as handle:
                handle.write(after)
                handle.flush()
        return real_models(tree)

    monkeypatch.setattr(schema, "_models", mutate_after_ast_read)
    with pytest.raises(UnsafeSchema, match="ZIP changed during schema scan"):
        schema.inspect_backend_schema(original)
    assert changed and original.read_bytes() == after


def test_changed_zip_between_route_and_schema_rejected_before_parse(tmp_path, monkeypatch):
    from rea.adapter import backend_schema as schema
    original = make_zip(tmp_path / "backend.zip", SOURCE)
    replacement = make_zip(tmp_path / "replacement.zip", SOURCE.replace("name: str", "kind: str"))
    real_inspect = schema.inspect_backend_zip
    parsed = []
    real_models = schema._models

    def change_after_route_scan(path):
        result = real_inspect(path)
        original.write_bytes(replacement.read_bytes())
        return result

    def observe_models(tree):
        parsed.append(True)
        return real_models(tree)

    monkeypatch.setattr(schema, "inspect_backend_zip", change_after_route_scan)
    monkeypatch.setattr(schema, "_models", observe_models)
    with pytest.raises(UnsafeSchema, match="ZIP changed before schema scan"):
        schema.inspect_backend_schema(original)
    assert parsed == []


def test_cli_write_only_new(tmp_path):
    source = make_zip(tmp_path/'fixture.zip')
    target = tmp_path/'new.json'
    command = [sys.executable,'-m','rea.adapter.backend_schema',str(source),'--out',str(target)]
    first = subprocess.run(command,capture_output=True,text=True)
    assert first.returncode == 0, first.stderr
    contents = target.read_bytes()
    second = subprocess.run(command,capture_output=True,text=True)
    assert second.returncode == 2
    assert target.read_bytes() == contents


def test_schema_join_is_review_only(tmp_path):
    from rea.adapter.frontend_bridge import make_review, BridgeError
    from tests_static_fixture import FABLE
    from rea.adapter.backend_zip import inspect_backend_zip
    source = make_zip(tmp_path/'fixture.zip')
    backend = inspect_backend_zip(source)
    schema = inspect_backend_schema(source)
    review = make_review(FABLE, backend, schema=schema)
    assert review['schema_review']['route_hints']==4
    assert review['schema_review']['bindings_autoapproved'] is False
    assert review['bindings'] is None
    assert review['generation_allowed'] is False
    stale = json.loads(json.dumps(schema))
    stale['backend_sha256']='0'*64
    with pytest.raises(BridgeError):make_review(FABLE,backend,schema=stale)
    forged = json.loads(json.dumps(schema))
    forged['routes'][0]['path']='/api/admin'
    with pytest.raises(BridgeError):make_review(FABLE,backend,schema=forged)
    malformed = json.loads(json.dumps(schema))
    malformed['routes'][0]['methods']=[{}]
    with pytest.raises(BridgeError):make_review(FABLE,backend,schema=malformed)


def test_five_route_fixture_preview_request_type(tmp_path):
    source = '''from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Literal
app=FastAPI()
class PreviewRequest(BaseModel):
    job_id: str = Field(min_length=1, max_length=32)
    mode: Literal["dry_run"] = "dry_run"
@app.get("/api/health")
def health(): return {"ok":True}
@app.get("/api/jobs")
def jobs(): return {"items":[]}
@app.get("/api/jobs/{job_id}")
def job(job_id: str): return {"id":job_id}
@app.get("/api/metrics")
def metrics(): return {"total":3}
@app.post("/api/preview")
def preview(request: PreviewRequest): return {"executed":False}
'''
    result = inspect_backend_schema(make_zip(tmp_path/'backend.zip',source))
    assert len(result['routes']) == 5
    preview = route(result,'/api/preview')
    assert preview['request_body']['model']=='PreviewRequest'
    assert preview['request_body']['fields'][0]['name']=='job_id'


def test_stacked_routes_do_not_misattribute_response_models(tmp_path):
    source = '''from fastapi import FastAPI
from pydantic import BaseModel
app=FastAPI()
class One(BaseModel):
  a: str
class Two(BaseModel):
  b: str
@app.get('/api/one',response_model=One)
@app.get('/api/two',response_model=Two)
def shared(): return {}
'''
    review=inspect_backend_schema(make_zip(tmp_path/'backend.zip',source))
    assert route(review, '/api/one')['response']['type_hint'] == 'One'
    assert route(review, '/api/two')['response']['type_hint'] == 'Two'
