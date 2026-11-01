"""Trusted synthetic OpenAPI reconciliation; never execute an uploaded ZIP."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import zipfile

import pytest

from rea.adapter.backend_zip import inspect_backend_zip
from rea.adapter.backend_schema import inspect_backend_schema
from rea.adapter.runtime_contract import InvalidRuntimeEvidence, reconcile

from pydantic import BaseModel
class Item(BaseModel):
    ticket: str
    task: str
class Preview(BaseModel):
    job_id: str

FIXTURE = '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
app = FastAPI()
class Item(BaseModel):
    ticket: str
    task: str
class Preview(BaseModel):
    job_id: str
@app.get("/api/items", response_model=list[Item])
def items():
    return []
@app.get("/api/items/{ticket}", response_model=Item)
def detail(ticket: str):
    return Item(ticket=ticket, task="sample")
@app.post("/api/preview")
def preview(request: Preview):
    return {"dry_run": True}
'''


def evidence(tmp_path):
    path = tmp_path / 'owner.zip'
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as f:
        f.writestr('app.py', FIXTURE)
    contract = inspect_backend_zip(path)
    static = inspect_backend_schema(path)
    # This fixture is deliberately self-authored and trusted in the test runner.
    # No code is imported or executed from the ZIP itself.
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    app = FastAPI()
    @app.get('/api/items',response_model=list[Item])
    def items(): return []
    @app.get('/api/items/{ticket}',response_model=Item)
    def detail(ticket:str): return Item(ticket=ticket,task='sample')
    @app.post('/api/preview')
    def preview(request:Preview): return {'dry_run':True}
    with TestClient(app) as client:
        doc = client.get('/openapi.json').json()
        assert client.get('/api/items').status_code == 200
    return contract,static,doc


def test_trusted_fixture_openapi_declared_methods_match(tmp_path):
    a,b,c=evidence(tmp_path)
    result=reconcile(a,b,c)
    assert result['status']=='DECLARATIONS_MATCH_REVIEW_REQUIRED'
    assert result['summary']=={'declared_operations':3,'matched':3,'mismatched':0,'unverified_response_shapes':1}
    assert result['runtime_origin_attested'] is False
    assert result['generation_allowed'] is False
    assert result['runtime_code_executed_by_reconciler'] is False
    assert result==reconcile(a,b,c)


def test_missing_runtime_route_blocks(tmp_path):
    a,b,c=evidence(tmp_path)
    c['paths'].pop('/api/items/{ticket}')
    r=reconcile(a,b,c)
    assert r['status']=='MISMATCH'
    assert any(x['code']=='OPENAPI_OPERATION_MISSING' for x in r['issues'])


def test_wrong_runtime_method_blocks(tmp_path):
    a,b,c=evidence(tmp_path)
    c['paths']['/api/preview']['get']=c['paths']['/api/preview'].pop('post')
    r=reconcile(a,b,c)
    assert any(x['code']=='OPENAPI_OPERATION_MISSING' for x in r['issues'])


def test_missing_path_parameter_blocks(tmp_path):
    a,b,c=evidence(tmp_path)
    c['paths']['/api/items/{ticket}']['get']['parameters']=[]
    assert any(x['code']=='PATH_PARAMETERS_MISMATCH' for x in reconcile(a,b,c)['issues'])


def test_missing_request_model_field_blocks(tmp_path):
    a,b,c=evidence(tmp_path)
    op=c['paths']['/api/preview']['post']
    ref=op['requestBody']['content']['application/json']['schema']['$ref']
    c['components']['schemas'][ref.split('/')[-1]]['properties'].pop('job_id')
    assert any(x['code']=='REQUEST_FIELDS_MISMATCH' for x in reconcile(a,b,c)['issues'])


def test_missing_response_model_field_blocks(tmp_path):
    a,b,c=evidence(tmp_path)
    name=next(name for name in c['components']['schemas'] if name.startswith('Item'))
    c['components']['schemas'][name]['properties'].pop('task')
    assert any(x['code']=='RESPONSE_MODEL_FIELDS_MISMATCH' for x in reconcile(a,b,c)['issues'])


def test_zip_mismatch_is_rejected(tmp_path):
    a,b,c=evidence(tmp_path)
    b['backend_sha256']='a'*64
    with pytest.raises(InvalidRuntimeEvidence,match='SHA mismatch'):reconcile(a,b,c)


def test_unmounted_router_not_promoted(tmp_path):
    a,b,c=evidence(tmp_path)
    a['api']['endpoints'][0]['mount']='router_mount_unverified'
    assert 'ROUTER_MOUNT_UNVERIFIED' in [x['code'] for x in reconcile(a,b,c)['issues']]


def test_no_secret_values_in_report(tmp_path):
    a,b,c=evidence(tmp_path)
    c['info']['description']='SECRET_SHOULD_NOT_ESCAPE'
    c['servers']=[{'url':'https://private.example.org/secret'}]
    c['components']['schemas']['Preview']['properties']['job_id']['example']='PRIVATE_PASSWORD'
    s=json.dumps(reconcile(a,b,c))
    for secret in ('SECRET_SHOULD_NOT_ESCAPE','private.example.org','PRIVATE_PASSWORD'):
        assert secret not in s


def test_unsafe_openapi_raises(tmp_path):
    a,b,c=evidence(tmp_path)
    c['paths']['https://evil.example.org/api/p']={'get':{}}
    with pytest.raises(InvalidRuntimeEvidence,match='unsafe OpenAPI path'):reconcile(a,b,c)


def test_cli_never_overwrites_and_fails_on_mismatch(tmp_path):
    a,b,c=evidence(tmp_path)
    inputs=[]
    for name,obj in [('backend.json',a),('schema.json',b),('openapi.json',c)]:
        p=tmp_path/name;p.write_text(json.dumps(obj),encoding='utf8');inputs.append(p)
    out=tmp_path/'out.json'
    command=[sys.executable,'-m','rea.adapter.runtime_contract','--backend',str(inputs[0]),'--schema',str(inputs[1]),'--openapi',str(inputs[2]),'--out',str(out)]
    first=subprocess.run(command,capture_output=True,text=True)
    assert first.returncode==0,first.stderr
    result=json.loads(out.read_text(encoding='utf8'))
    assert result['summary']['matched']==3
    saved=out.read_bytes()
    assert subprocess.run(command,capture_output=True).returncode==2
    assert out.read_bytes()==saved
    c['paths'].pop('/api/items')
    inputs[2].write_text(json.dumps(c),encoding='utf8')
    command[-1]=str(tmp_path/'mismatch.json')
    assert subprocess.run(command,capture_output=True).returncode==3
    assert json.loads((tmp_path/'mismatch.json').read_text())['status']=='MISMATCH'


def test_response_field_type_mismatch_blocks(tmp_path):
    a,b,c=evidence(tmp_path)
    c['components']['schemas']['Item']['properties']['ticket']['type']='integer'
    assert any(x['code']=='RESPONSE_MODEL_FIELDS_MISMATCH' for x in reconcile(a,b,c)['issues'])


def test_request_required_field_change_blocks(tmp_path):
    a,b,c=evidence(tmp_path)
    c['components']['schemas']['Preview']['required']=[]
    assert any(x['code']=='REQUEST_FIELDS_MISMATCH' for x in reconcile(a,b,c)['issues'])


def test_empty_static_contract_rejected(tmp_path):
    a,b,c=evidence(tmp_path)
    a['api']['endpoints']=[]
    with pytest.raises(InvalidRuntimeEvidence,match='empty static API'):
        reconcile(a,b,c)


def test_cli_rejects_secret_path_and_bounded_file(tmp_path):
    a,b,c=evidence(tmp_path)
    target=tmp_path/'sensitive.json'
    target.write_text('x'*(2*1024*1024+1),encoding='utf8')
    from rea.adapter.runtime_contract import _read_json
    with pytest.raises(InvalidRuntimeEvidence,match='2 MiB'):
        _read_json(target)
    with pytest.raises(InvalidRuntimeEvidence):
        _read_json(tmp_path/'not_found.json')
