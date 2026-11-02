"""Real Chromium DOM and stream reader regression, no browser network required.

The test imports the generated JS constant. It is not evidence of FastAPI
localhost connectivity, source ZIP origin, or customer API authorization.
"""
import json
import os

from playwright.sync_api import expect, sync_playwright

from rea.adapter.frontend_bridge import JS

CONFIG = {
    "list": {"path": "/api/jobs", "field": "items"},
    "metrics": {"path": "/api/metrics", "field": "__root__"},
    "detail": {"path": "/api/jobs/{job_id}", "field": "__root__"},
}
HTML = """<!doctype html><html lang="ko"><body>
<div id="connection"><span id="connection-text"></span></div>
<span id="kpi-total"></span><span id="kpi-completed"></span><span id="kpi-pending"></span>
<span id="count"></span><span id="empty" hidden></span><input id="search">
<table><tbody id="jobs"></tbody></table><div id="detail"></div>
<div id="error" hidden></div><button id="retry" hidden>API 다시 연결</button>
</body></html>"""
FETCH_STUB = """window.mode='normal';window.calls=[];
window.fetch=async function(path,options){
 window.calls.push({path,method:options?.method||'GET',signal:!!options?.signal});
 if(window.mode==='fail'&&path==='/api/metrics')return new Response('{}',{status:503,headers:{'content-type':'application/json'}});
 if(window.mode==='html'&&path==='/api/jobs')return new Response('<html>bad</html>',{status:200,headers:{'content-type':'text/html'}});
 if(window.mode==='large'&&path==='/api/jobs')return new Response(JSON.stringify({items:[{name:'X'.repeat(1048576)}]}),{status:200,headers:{'content-type':'application/json'}});
 if(window.mode==='malformed'&&path==='/api/jobs')return new Response('{bad json}',{status:200,headers:{'content-type':'application/json'}});
 if(window.mode==='stream'&&path==='/api/jobs')return new Response(new ReadableStream({start(c){c.enqueue(new Uint8Array(700000));c.enqueue(new Uint8Array(400000));c.close()}}),{status:200,headers:{'content-type':'application/json'}});
 if(window.mode==='timeout'&&path==='/api/jobs')return new Promise((resolve,reject)=>{options.signal.addEventListener('abort',()=>reject(new DOMException('Aborted','AbortError')),{once:true})});
 const data=path==='/api/jobs'?{items:[{id:'A-1',name:'첫 작업',category:'audit',status:'done'},{id:'B-2',name:'검색 검증',category:'quality',status:'pending'}]}:path==='/api/metrics'?{total:2,completed:1,pending:1}:{id:decodeURIComponent(path.split('/').at(-1)),name:'상세'};
 return new Response(JSON.stringify(data),{status:200,headers:{'content-type':'application/json'}});
};"""


def test_browser_live_stream_refusal_and_recovery():
    """Actual browser UI with explicitly mocked responses; no local network."""
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True, executable_path=os.environ.get("REA_CHROMIUM_PATH") or None,
            args=["--no-sandbox"],
        )
        try:
            page = browser.new_page()
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.set_content(HTML)
            page.add_script_tag(content=FETCH_STUB)
            page.add_script_tag(content=JS.replace("__API_JSON__", json.dumps(CONFIG)))
            expect(page.locator("#connection-text")).to_have_text("CONNECTED")
            expect(page.locator("#kpi-total")).to_have_text("2")
            assert page.locator("#jobs tr").count() == 2
            page.locator("#search").fill("검색")
            assert page.locator("#jobs tr").count() == 1
            page.locator("button.link").click()
            expect(page.locator("#detail")).to_contain_text("B-2")
            for mode, expected in (
                ("fail", "HTTP 503"),
                ("large", "크기 초과"),
                ("html", "JSON이 아닙니다"),
                ("malformed", "백엔드 API 연결 실패"),
                ("stream", "크기 초과"),
                ("timeout", "API 응답 시간 초과"),
            ):
                page.evaluate("mode => {window.mode=mode; document.getElementById('retry').click()}", mode)
                expect(page.locator("#connection-text")).to_have_text("API ERROR", timeout=13000)
                expect(page.locator("#error")).to_contain_text(expected)
                assert page.locator("#retry").is_visible()
                page.evaluate("() => {window.mode='normal'; document.getElementById('retry').click()}")
                expect(page.locator("#connection-text")).to_have_text("CONNECTED")
                assert page.locator("#error").is_hidden()
                assert page.locator("#retry").is_hidden()
            calls = page.evaluate("window.calls")
            assert calls and all(x["method"] == "GET" and x["signal"] for x in calls)
            assert not errors, errors
        finally:
            browser.close()
