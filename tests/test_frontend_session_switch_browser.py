"""A delayed detail response from session A must not repaint session B's dashboard.

Self-authored, browser-only fake read-only API. No customer source or network.
"""
import json
import os

from playwright.sync_api import expect, sync_playwright

from rea.adapter.frontend_bridge import JS

HTML = """<div id="connection"><span id="connection-text"></span></div>
<span id="kpi-total"></span><span id="kpi-completed"></span><span id="kpi-pending"></span>
<span id="count"></span><div id="empty" hidden></div><input id="search">
<table><tbody id="jobs"></tbody></table><div id="detail"></div>
<div id="error" hidden></div><button id="retry" hidden></button>"""
CONFIG = {
    "list": {"path": "/api/jobs", "field": "items"},
    "metrics": {"path": "/api/metrics", "field": "__root__"},
    "detail": {"path": "/api/jobs/{job_id}", "field": "__root__"},
}
FETCH = """
window.session = 'A';
window.finishOldDetail = null;
window.fetch = async (path) => {
  const session = window.session;
  const headers = {'content-type': 'application/json'};
  if (path === '/api/jobs') {
    const item = session === 'A'
      ? {id:'A',name:'Old Alpha',category:'prior',status:'done'}
      : {id:'B',name:'New Beta',category:'current',status:'done'};
    return new Response(JSON.stringify({items:[item]}),{headers});
  }
  if (path === '/api/metrics') {
    return new Response(JSON.stringify({
      total:session==='A'?1:2,completed:1,pending:0
    }),{headers});
  }
  if (path === '/api/jobs/A') {
    return new Promise(resolve => { window.finishOldDetail=resolve; });
  }
  if (path === '/api/jobs/B') {
    return new Response(JSON.stringify({id:'B',name:'New Beta'}),{headers});
  }
  throw new Error('unexpected fake endpoint: '+path);
};
"""


def test_cross_session_reload_discards_stale_detail_success_and_denial():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            executable_path=os.getenv("REA_CHROMIUM_PATH") or None,
            args=["--no-sandbox"],
        )
        try:
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.set_content(HTML)
            page.add_script_tag(content=FETCH)
            page.add_script_tag(content=JS.replace("__API_JSON__", json.dumps(CONFIG)))
            expect(page.locator("#connection-text")).to_have_text("CONNECTED")

            for old_status in (200, 401):
                page.evaluate("async () => { window.session='A'; await load(); }")
                expect(page.locator("#jobs")).to_contain_text("Old Alpha")
                page.evaluate("() => { window.oldRequest=showDetail('A'); }")
                page.wait_for_function("typeof window.finishOldDetail === 'function'")
                page.evaluate("async () => { window.session='B'; await load(); }")
                expect(page.locator("#kpi-total")).to_have_text("2")
                expect(page.locator("#jobs")).to_contain_text("New Beta")
                assert "Old Alpha" not in page.locator("#jobs").inner_text()
                assert "Old Alpha" not in page.locator("#detail").inner_text()
                page.evaluate("""async status => {
                  const headers={'content-type':'application/json'};
                  window.finishOldDetail(new Response(
                    status === 200 ? JSON.stringify({id:'A',name:'Old Alpha'}) : '{}',
                    {status,headers}));
                  await window.oldRequest;
                  window.finishOldDetail=null;
                }""", old_status)
                expect(page.locator("#connection-text")).to_have_text("CONNECTED")
                assert page.locator("#error").is_hidden()
                assert "Old Alpha" not in page.locator("#detail").inner_text()

            page.evaluate("showDetail('B')")
            expect(page.locator("#detail")).to_contain_text("New Beta")
            assert not errors, errors
        finally:
            browser.close()
