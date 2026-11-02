"""Latest detail click wins even if older detail API response arrives late."""
import json
import os
from playwright.sync_api import expect, sync_playwright
from rea.adapter.frontend_bridge import JS

HTML = '''<div id="connection"><span id="connection-text"></span></div>
<span id="kpi-total"></span><span id="kpi-completed"></span><span id="kpi-pending"></span>
<span id="count"></span><div id="empty" hidden></div><input id="search">
<table><tbody id="jobs"></tbody></table><div id="detail"></div>
<div id="error" hidden></div><button id="retry" hidden></button>'''
CONFIG = {'list': {'path':'/api/jobs','field':'items'},
          'metrics': {'path':'/api/metrics','field':'__root__'},
          'detail': {'path':'/api/jobs/{job_id}','field':'__root__'}}
FETCH = '''
window.delayed = new Set();window.resolveDetail={};
window.fetch = async (path, opts) => {
  if(path==='/api/jobs')return new Response(JSON.stringify({items:[
    {id:'A',name:'Alpha',category:'audit',status:'done'},
    {id:'B',name:'Beta',category:'audit',status:'pending'}]}),{headers:{'content-type':'application/json'}});
  if(path==='/api/metrics')return new Response(JSON.stringify({total:2,completed:1,pending:1}),{headers:{'content-type':'application/json'}});
  const id=path.split('/').at(-1);
  if(window.delayed.has(id))return new Promise(resolve=>{window.resolveDetail[id]=resolve});
  return new Response(JSON.stringify({id,name:id==='A'?'Alpha':'Beta',category:'audit',status:'done'}),{headers:{'content-type':'application/json'}});
};
'''


def test_latest_detail_selection_wins_over_stale_success_and_failure():
    errors = []
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.getenv('REA_CHROMIUM_PATH') or None,args=['--no-sandbox'])
        try:
            page=browser.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.set_content(HTML)
            page.add_script_tag(content=FETCH)
            page.add_script_tag(content=JS.replace('__API_JSON__',json.dumps(CONFIG)))
            expect(page.locator('#connection-text')).to_have_text('CONNECTED')
            page.evaluate("() => { window.delayed.add('A'); window.slowDetail = showDetail('A'); }")
            page.wait_for_function("typeof window.resolveDetail.A === 'function'")
            page.evaluate("() => { showDetail('B'); }")
            expect(page.locator('#detail')).to_contain_text('Beta')
            page.evaluate("async () => { window.resolveDetail.A(new Response(JSON.stringify({id:'A',name:'Alpha'}),{headers:{'content-type':'application/json'}})); await window.slowDetail; }")
            expect(page.locator('#detail')).to_contain_text('Beta')
            assert 'Alpha' not in page.locator('#detail').inner_text()
            page.evaluate("() => {window.delayed.delete('A');window.delayed.add('B');window.slowDetail=showDetail('B')}")
            page.wait_for_function("typeof window.resolveDetail.B === 'function'")
            page.evaluate("() => {showDetail('A')}")
            expect(page.locator('#detail')).to_contain_text('Alpha')
            page.evaluate("async () => {window.resolveDetail.B(new Response('{}',{status:404,headers:{'content-type':'application/json'}}));await window.slowDetail;}")
            assert page.locator('#connection-text').inner_text()=='CONNECTED'
            assert page.locator('#error').is_hidden()
            assert not errors, errors
        finally:
            browser.close()
