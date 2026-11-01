"""Playwright -> trusted FastAPI loopback E2E with nonstandard JSON field names."""
from __future__ import annotations

import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

import pytest
from playwright.sync_api import expect, sync_playwright
from rea.adapter.frontend_bridge import make_review, generate_frontend
from tests_static_fixture import FABLE, BACKEND


TRUSTED_FIXTURE = '''from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
app=FastAPI()
TASKS=[{"ticket":"T-11","task":"검사 결과","department":"quality","phase":"done"},
       {"ticket":"T-12","task":"월간 보고서","department":"report","phase":"pending"},
       {"ticket":"T-13","task":"정산 작업","department":"finance","phase":"done"}]
@app.get('/api/health')
def health():return {"ok":True}
@app.get('/api/tasks')
def tasks():return {"results":TASKS}
@app.get('/api/insights')
def insights():return {"summary":{"all_count":3,"success_count":2,"queued_count":1}}
@app.get('/api/tasks/{ticket_id}')
def detail(ticket_id:str):
 for x in TASKS:
  if x['ticket']==ticket_id:return {"result":x}
 raise HTTPException(status_code=404)
app.mount('/dashboard',StaticFiles(directory=str(Path(__file__).parent/'dashboard'),html=True),name='ui')
'''


def test_nonstandard_fields_and_detail_param_real_http(tmp_path):
    backend = {**BACKEND, 'api':{'endpoints': [
        {'path':path,'methods':['GET'],'verification':'STATIC_DECLARATION_ONLY','mount':'app_declaration'}
        for path in ['/api/tasks','/api/insights','/api/tasks/{ticket_id}']
    ]}}
    bindings = {
        'list':{'path':'/api/tasks','field':'results'},
        'metrics':{'path':'/api/insights','field':'summary'},
        'detail':{'path':'/api/tasks/{ticket_id}','field':'result','path_param':'ticket_id'},
        'presentation':{
            'item':{'id':'ticket','name':'task','category':'department','status':'phase'},
            'metrics':{'total':'all_count','completed':'success_count','pending':'queued_count'},
            'detail_fields':['ticket','task','department','phase'],
        },
    }
    review = make_review(FABLE,backend,bindings)
    generate_frontend(review,tmp_path/'dashboard',owner_confirmed=True)
    (tmp_path/'trusted_backend.py').write_text(TRUSTED_FIXTURE,encoding='utf-8')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0))
        port=sock.getsockname()[1]
    address=f'http://127.0.0.1:{port}'
    env={**os.environ,'PYTHONPATH':str(tmp_path)}
    proc=subprocess.Popen([sys.executable,'-m','uvicorn','trusted_backend:app',
                           '--host','127.0.0.1','--port',str(port),'--log-level','warning'],
                          cwd=tmp_path,env=env,stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,text=True)
    try:
        for _ in range(60):
            if proc.poll() is not None:
                raise AssertionError('test server failed')
            try:
                with urlopen(address+'/api/health',timeout=.6) as response:
                    if response.status == 200:
                        break
            except OSError:
                time.sleep(.15)
        else:
            raise AssertionError('HTTP readiness timeout')
        with sync_playwright() as pw:
            try:
                browser=pw.chromium.launch(headless=True)
            except Exception as exc:
                if 'Executable doesn\'t exist' in str(exc):
                    pytest.skip('Local Playwright browser not installed; GitHub runner installs Chromium')
                raise
            try:
                page=browser.new_page(viewport={'width':1280,'height':800})
                errors=[]; failed=[]; calls=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.on('requestfailed',lambda request:failed.append(request.url))
                page.on('response',lambda response:calls.append((response.status,response.url)))
                assert page.goto(address+'/dashboard/',wait_until='networkidle').status==200
                expect(page.locator('#connection-text')).to_have_text('CONNECTED')
                expect(page.locator('#kpi-total')).to_have_text('3')
                expect(page.locator('#kpi-completed')).to_have_text('2')
                assert page.locator('#jobs tr').count()==3
                page.locator('#search').fill('보고서')
                assert page.locator('#jobs tr').count()==1
                page.locator('#jobs button').click()
                expect(page.locator('#detail')).to_contain_text('T-12')
                expect(page.locator('#detail')).to_contain_text('report')
                assert not errors and not failed, (errors,failed)
                assert len([x for x in calls if x[0]==200 and '/api/' in x[1]])>=3
            finally:
                browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill();proc.wait(timeout=5)
