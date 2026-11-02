"""The newest dashboard reload must own its final UI status and KPIs."""
import json
import os
from playwright.sync_api import sync_playwright, expect
from rea.adapter.frontend_bridge import JS

HTML='''<div id="connection"><span id="connection-text"></span></div>
<span id="kpi-total"></span><span id="kpi-completed"></span><span id="kpi-pending"></span>
<span id="count"></span><div id="empty" hidden></div><input id="search"><table><tbody id="jobs"></tbody></table>
<div id="detail"></div><div id="error" hidden></div><button id="retry" hidden></button>'''
CONFIG={'list':{'path':'/api/jobs','field':'items'},'metrics':{'path':'/api/metrics','field':'__root__'},'detail':{'path':'/api/jobs/{job_id}','field':'__root__'}}
FETCH='''
window.phase='normal';
window.fetch=async (path,opts)=>{
 if(path.includes('/jobs')) return new Response(JSON.stringify({items:[]}),{headers:{'content-type':'application/json'}});
 if(window.phase==='slow-fail') return new Promise(resolve=>{window.finishSlowFailure=()=>resolve(new Response('{}',{status:503,headers:{'content-type':'application/json'}}));});
 if(window.phase==='slow-success') return new Promise(resolve=>{window.finishSlowSuccess=()=>resolve(new Response(JSON.stringify({total:99,completed:0,pending:0}),{headers:{'content-type':'application/json'}}));});
 if(window.phase==='fast-fail') return new Response('{}',{status:503,headers:{'content-type':'application/json'}});
 return new Response(JSON.stringify({total:window.phase==='fast-success'?7:2,completed:1,pending:1}),{headers:{'content-type':'application/json'}});
};
'''

def test_latest_reload_wins_on_stale_error_and_stale_success():
  with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path=os.getenv('REA_CHROMIUM_PATH') or None,args=['--no-sandbox'])
    try:
      page=browser.new_page();page.set_content(HTML);page.add_script_tag(content=FETCH)
      page.add_script_tag(content=JS.replace('__API_JSON__',json.dumps(CONFIG)))
      expect(page.locator('#connection-text')).to_have_text('CONNECTED')
      page.evaluate("window.phase='slow-fail';window.slowRequest=load();void 0")
      page.wait_for_function('typeof window.finishSlowFailure === "function"')
      page.evaluate("window.phase='fast-success';load()")
      expect(page.locator('#kpi-total')).to_have_text('7')
      page.evaluate('async () => {window.finishSlowFailure();await window.slowRequest;}')
      assert page.locator('#connection-text').inner_text()=='CONNECTED'
      assert page.locator('#error').is_hidden()
      page.evaluate("window.phase='slow-success';window.slowRequest=load();void 0")
      page.wait_for_function('typeof window.finishSlowSuccess === "function"')
      page.evaluate("window.phase='fast-fail';load()")
      expect(page.locator('#connection-text')).to_have_text('API ERROR')
      page.evaluate('async () => {window.finishSlowSuccess();await window.slowRequest;}')
      assert page.locator('#connection-text').inner_text()=='API ERROR'
      assert page.locator('#kpi-total').inner_text()=='7'
    finally:
      browser.close()
