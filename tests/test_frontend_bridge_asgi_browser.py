"""FastAPI TestClient responses -> real Chromium DOM, without browser networking.

Only self-authored synthetic routes are called. This is a tested ASGI-to-browser
response contract, not evidence of network, customer-ZIP isolation, CSP, or
production auth. The emitted frontend source is unchanged.
"""
from __future__ import annotations

import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from playwright.sync_api import expect, sync_playwright

from rea.adapter.frontend_bridge import JS


HTML = '''<!doctype html><html lang="ko"><body>
<div id="connection"><span id="connection-text"></span></div>
<strong id="kpi-total"></strong><strong id="kpi-completed"></strong><strong id="kpi-pending"></strong>
<span id="count"></span><span id="empty" hidden></span><input id="search">
<table><tbody id="jobs"></tbody></table><div id="detail"></div>
<div id="error" hidden></div><button id="retry" hidden>API 다시 연결</button>
</body></html>'''
CONFIG = {
    'list': {'path': '/api/jobs', 'field': 'items'},
    'metrics': {'path': '/api/metrics', 'field': '__root__'},
    'detail': {'path': '/api/jobs/{job_id}', 'field': '__root__'},
}


def test_synthetic_fastapi_asgi_response_to_real_chromium_dom():
    app = FastAPI()
    records = [
        {'id': 'A-1', 'name': '첫 작업', 'category': 'audit', 'status': 'done'},
        {'id': 'B-2', 'name': '검색 검증', 'category': 'quality', 'status': 'pending'},
    ]
    state = {'fail_metrics': False}
    @app.get('/api/jobs')
    def list_jobs():
        return {'items': records}
    @app.get('/api/metrics')
    def metrics():
        if state['fail_metrics']:
            raise HTTPException(503, 'trusted synthetic outage')
        return {'total': len(records), 'completed': 1, 'pending': 1}
    @app.get('/api/jobs/{job_id}')
    def detail(job_id: str):
        for item in records:
            if item['id'] == job_id:
                return item
        raise HTTPException(404, 'not found')

    browser_errors = []
    traffic = []
    with TestClient(app) as client, sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            executable_path=os.environ.get('REA_CHROMIUM_PATH') or None,
            args=['--no-sandbox'],
        )
        try:
            page = browser.new_page()
            page.on('pageerror', lambda error: browser_errors.append(str(error)))
            def trusted_asgi_bridge(source, path, method):
                # The JS browser cannot access localhost in this environment.
                # Bridge only the test-owned GET API over the Python ASGI client.
                assert method == 'GET' and path.startswith('/api/')
                assert len(path) <= 250
                reply = client.get(path, follow_redirects=False)
                traffic.append((path, reply.status_code))
                return {'status': reply.status_code,
                        'content_type': reply.headers.get('content-type', ''),
                        'body': reply.text}
            page.expose_binding('reaSyntheticApi', trusted_asgi_bridge)
            page.set_content(HTML)
            page.add_script_tag(content='''
window.fetch=async (path, options) => {
 const r=await window.reaSyntheticApi(path, options?.method||'GET');
 return new Response(r.body, {status:r.status,headers:{'Content-Type':r.content_type}});
};''')
            page.add_script_tag(content=JS.replace('__API_JSON__', json.dumps(CONFIG)))
            expect(page.locator('#connection-text')).to_have_text('CONNECTED')
            expect(page.locator('#kpi-total')).to_have_text('2')
            expect(page.locator('#kpi-completed')).to_have_text('1')
            assert page.locator('#jobs tr').count() == 2
            page.locator('#search').fill('검색')
            assert page.locator('#jobs tr').count() == 1
            page.locator('button.link').click()
            expect(page.locator('#detail')).to_contain_text('B-2')
            assert ('/api/jobs/B-2', 200) in traffic
            # Real 404 detail and 503 metrics failures must surface, then recover.
            page.evaluate("showDetail('missing')")
            expect(page.locator('#error')).to_contain_text('HTTP 404')
            page.locator('#retry').click()
            expect(page.locator('#connection-text')).to_have_text('CONNECTED')
            state['fail_metrics'] = True
            page.evaluate('load()')
            expect(page.locator('#connection-text')).to_have_text('API ERROR')
            expect(page.locator('#error')).to_contain_text('HTTP 503')
            assert ('/api/metrics', 503) in traffic
            state['fail_metrics'] = False
            page.locator('#retry').click()
            expect(page.locator('#connection-text')).to_have_text('CONNECTED')
            assert page.locator('#error').is_hidden()
            assert page.locator('#jobs tr').count() == 2
            assert not browser_errors, browser_errors
            assert all(path.startswith('/api/') for path, _ in traffic)
        finally:
            browser.close()
