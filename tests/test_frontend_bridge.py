"""Fable+ZIP contract joining, approval gates, and original frontend source generation."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest
from rea.adapter.frontend_bridge import BridgeError, make_review, generate_frontend

FABLE = {
    'schema_version':'1.0',
    'target':{'input_url':'https://example.org/private/DO_NOT_LEAK?token=SECRET'},
    'scanned_at':'2026-11-01T12:00:00+00:00',
    'scan_mode':'static',
    'frontend':[], 'backend_inferred':[], 'infra':[],
    'api':{'endpoints':[], 'candidates':[], 'chart_candidates':[]},
    'charts':[], 'warnings':[],
}
SHA='a'*64
BACKEND = {
    'schema_version':'rea.backend_contract.v0.1', 'status':'REVIEW_REQUIRED',
    'generation_allowed':False, 'execution_performed':False,
    'input':{'sha256':SHA},
    'api':{'endpoints':[
        {'path':path,'methods':methods,'verification':'STATIC_DECLARATION_ONLY','mount':'app_declaration'}
        for path,methods in [('/api/jobs',['GET']),('/api/metrics',['GET']),('/api/jobs/{job_id}',['GET']),('/api/preview',['POST'])]
    ]}
}
BINDINGS={
    'list':{'path':'/api/jobs','field':'items'},
    'metrics':{'path':'/api/metrics','field':'__root__'},
    'detail':{'path':'/api/jobs/{job_id}','field':'__root__'},
}


def test_review_keeps_real_visual_unknown_and_scrubs_private_url():
    plan=make_review(FABLE,BACKEND)
    assert plan['reference']['origin']=='https://example.org'
    assert plan['reference']['visual_evidence']=='NOT_CAPTURED_BY_FABLE_STATIC_CONTRACT'
    assert plan['reference']['layout_similarity_to_reference']=='UNVERIFIED'
    assert plan['generation_allowed'] is False and plan['bindings'] is None
    assert 'SECRET' not in json.dumps(plan) and 'DO_NOT_LEAK' not in json.dumps(plan)


def test_explicit_bindings_match_get_and_generate(tmp_path):
    review=make_review(FABLE,BACKEND,BINDINGS)
    out=tmp_path/'dashboard'
    manifest=generate_frontend(review,out,owner_confirmed=True)
    assert sorted(p.name for p in out.iterdir())==['README_KO.md','app.js','index.html','manifest.json','style.css']
    assert manifest['status']=='FRONTEND_SOURCE_GENERATED_NOT_RUNTIME_VERIFIED'
    assert manifest['reference']['style_source']=='ORIGINAL_REA_NEUTRAL_DEFAULT'
    assert 'fetch(' in (out/'app.js').read_text(encoding='utf8')
    assert '/api/jobs/{job_id}' in (out/'app.js').read_text(encoding='utf8')
    assert "node('td'" in (out/'app.js').read_text(encoding='utf8')
    assert 'textContent' in (out/'app.js').read_text(encoding='utf8')
    assert 'innerHTML' not in (out/'app.js').read_text(encoding='utf8')
    assert 'connect-src \'self\'' in (out/'index.html').read_text(encoding='utf8')
    assert 'SECRET' not in ''.join(p.read_text(encoding='utf8') for p in out.iterdir())
    assert 'CHECKING API' in (out/'index.html').read_text(encoding='utf8')
    assert 'API ERROR' in (out/'app.js').read_text(encoding='utf8')
    before={p.name:p.read_bytes() for p in out.iterdir()}
    with pytest.raises(FileExistsError):generate_frontend(review,out,owner_confirmed=True)
    assert before=={p.name:p.read_bytes() for p in out.iterdir()}


def test_owner_review_is_required(tmp_path):
    review=make_review(FABLE,BACKEND,BINDINGS)
    with pytest.raises(BridgeError):generate_frontend(review,tmp_path/'missing',owner_confirmed=False)
    assert not (tmp_path/'missing').exists()
    with pytest.raises(BridgeError):generate_frontend(make_review(FABLE,BACKEND),tmp_path/'missing',owner_confirmed=True)


def test_prevent_false_preapproved_state(tmp_path):
    review=make_review(FABLE,BACKEND,BINDINGS)
    review['generation_allowed']=True
    with pytest.raises(BridgeError):generate_frontend(review,tmp_path/'bad',owner_confirmed=True)


@pytest.mark.parametrize('role,path',[
    ('list','https://evil.example/api/jobs'),('list','//evil/api'),
    ('list','/api/../jobs'),('list','/api/preview'),
    ('list','/api/jobs/{job_id}'),('detail','/api/jobs'),
    ('metrics','/api/unlisted'),
])
def test_unsafe_or_unverified_bindings_rejected(role,path):
    mapping=copy.deepcopy(BINDINGS)
    mapping[role]['path']=path
    with pytest.raises(BridgeError):make_review(FABLE,BACKEND,mapping)


def test_unmounted_router_rejected():
    b=copy.deepcopy(BACKEND)
    b['api']['endpoints'][0]['mount']='router_mount_unverified'
    with pytest.raises(BridgeError):make_review(FABLE,b,BINDINGS)


def test_nonstandard_fields_require_explicit_mapping():
    b=copy.deepcopy(BINDINGS)
    b['list']['field']='secret;alert(1)'
    with pytest.raises(BridgeError):make_review(FABLE,BACKEND,b)


def test_untrusted_backend_contract_rejected():
    for key,value in [('generation_allowed',True),('execution_performed',True),('status','APPROVED')]:
        b=copy.deepcopy(BACKEND);b[key]=value
        with pytest.raises(BridgeError):make_review(FABLE,b,BINDINGS)


def test_invalid_fable_rejected():
    f=copy.deepcopy(FABLE);f['target']['input_url']='file:///etc/passwd'
    with pytest.raises(BridgeError):make_review(f,BACKEND,BINDINGS)


def test_cli_review_and_explicit_generation(tmp_path):
    paths=[]
    for name,data in [('fable.json',FABLE),('backend.json',BACKEND),('bindings.json',BINDINGS)]:
        p=tmp_path/name;p.write_text(json.dumps(data),encoding='utf8');paths.append(p)
    args=[sys.executable,'-m','rea.adapter.frontend_bridge','--fable',str(paths[0]),'--backend',str(paths[1]),'--bindings',str(paths[2])]
    preview=subprocess.run(args,text=True,capture_output=True)
    assert preview.returncode==0,preview.stderr
    assert json.loads(preview.stdout)['status']=='OWNER_REVIEW_REQUIRED'
    unapproved=subprocess.run([*args,'--out',str(tmp_path/'fail')],text=True,capture_output=True)
    assert unapproved.returncode==2 and not (tmp_path/'fail').exists()
    approved=subprocess.run([*args,'--owner-confirmed','--out',str(tmp_path/'ok')],text=True,capture_output=True)
    assert approved.returncode==0,approved.stderr
    assert json.loads(approved.stdout)['frontend_path']=='/dashboard/'
