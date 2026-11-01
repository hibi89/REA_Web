"""REAL Chromium -> localhost FastAPI fixture API; never executes an owner ZIP."""
from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright
from rea.adapter.frontend_bridge import generate_frontend, make_review

FABLE = {
    'schema_version': '1.0', 'target': {'input_url':'https://example.org/public'},
    'scanned_at':'2026-11-01T12:00:00+00:00', 'scan_mode':'static',
    'frontend':[], 'backend_inferred':[], 'infra':[],
    'api':{'endpoints':[],'candidates':[],'chart_candidates':[]}, 'charts':[], 'warnings':[],
}
CONTRACT = {
    'schema_version':'rea.backend_contract.v0.1', 'status':'REVIEW_REQUIRED',
    'generation_allowed':False, 'execution_performed':False,
    'input':{'sha256':'f'*64}, 'api':{'endpoints':[
        {'path':p,'methods':['GET'],'verification':'STATIC_DECLARATION_ONLY', 'mount':'app_declaration'}
        for p in ['/api/jobs','/api/metrics','/api/jobs/{job_id}']
    ]},
}
BINDINGS = {
    'list':{'path':'/api/jobs','field':'items'},
    'metrics':{'path':'/api/metrics','field':'__root__'},
    'detail':{'path':'/api/jobs/{job_id}','field':'__root__'},
}

BACKEND_SOURCE = '''from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.staticfiles import StaticFiles
app=FastAPI()
ITEMS=[{"id":"A-1","name":"첫 작업","category":"analytics","status":"done","duration_ms":15},
       {"id":"B-2","name":"검색 검증","category":"quality","status":"done","duration_ms":30},
       {"id":"C-3","name":"보고서","category":"report","status":"pending","duration_ms":0}]
@app.get('/api/health')
def health():return {"ok":True}
@app.get('/api/jobs')
def jobs():return {"items":ITEMS}
@app.get('/api/metrics')
def metrics():return {"total":3,"completed":2,"pending":1}
@app.get('/api/jobs/{job_id}')
def detail(job_id:str):
    for item in ITEMS:
        if item['id']==job_id:return item
    raise HTTPException(status_code=404,detail='Not found')
app.mount('/dashboard',StaticFiles(directory=str(Path(__file__).parent/'dashboard'),html=True),name='frontend')
'''


def test_generated_frontend_real_http_chromium(tmp_path):
    """Only a trusted test-owned FastAPI fixture is imported/executed."""
    plan=make_review(FABLE,CONTRACT,BINDINGS)
    generate_frontend(plan,tmp_path/'dashboard',owner_confirmed=True)
    (tmp_path/'fixture_backend.py').write_text(BACKEND_SOURCE,encoding='utf8')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0))
        port=sock.getsockname()[1]
    args=[sys.executable,'-m','uvicorn','fixture_backend:app','--host','127.0.0.1',
          '--port',str(port),'--log-level','warning']
    env={**os.environ,'PYTHONPATH':str(tmp_path)}
    proc=subprocess.Popen(args,cwd=tmp_path,env=env,stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,text=True)
    try:
        address=f'http://127.0.0.1:{port}'
        for _ in range(70):
            if proc.poll() is not None:
                raise AssertionError('fixture backend terminated before readiness')
            try:
                with urlopen(address+'/api/health',timeout=.5) as response:
                    if response.status==200:
                        break
            except OSError:
                time.sleep(.15)
        else:
            raise AssertionError('fixture backend HTTP readiness timeout')
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            try:
                page=browser.new_page(viewport={'width':1280,'height':850})
                errors=[];failed=[];calls=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.on('requestfailed',lambda request:failed.append(request.url))
                page.on('response',lambda response:calls.append((response.status,response.url)))
                response=page.goto(address+'/dashboard/',wait_until='networkidle',timeout=25000)
                assert response is not None and response.status==200
                expect(page.locator('#kpi-total')).to_have_text('3')
                assert page.locator('#kpi-completed').inner_text()=='2'
                assert page.locator('#kpi-pending').inner_text()=='1'
                assert page.locator('#jobs tr').count()==3
                page.locator('#search').fill('검색')
                assert page.locator('#jobs tr').count()==1
                page.locator('button.link').first.click()
                expect(page.locator('#detail')).to_contain_text('B-2')
                assert len([u for status,u in calls if status==200 and '/api/' in u])>=3
                assert not errors and not failed, (errors,failed)
                assert page.locator('#error').is_hidden()
            finally:
                browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
