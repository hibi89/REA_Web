"""Detail 404 must not make a healthy list and metrics dashboard disconnected."""
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
window.fetch = async path => {
  if(path==='/api/jobs') return new Response(JSON.stringify({items:[{id:'A',name:'Alpha',category:'audit',status:'done'}]}),{headers:{'content-type':'application/json'}});
  if(path==='/api/metrics') return new Response(JSON.stringify({total:1,completed:1,pending:0}),{headers:{'content-type':'application/json'}});
  if(path==='/api/jobs/missing') return new Response(JSON.stringify({detail:'not found'}),{status:404,headers:{'content-type':'application/json'}});
  if(path==='/api/jobs/A') return new Response(JSON.stringify({id:'A',name:'Alpha',category:'audit',status:'done'}),{headers:{'content-type':'application/json'}});
  throw new Error('not expected: '+path);
};
'''

def test_detail_404_is_local_error_and_success_recovers():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.getenv('REA_CHROMIUM_PATH') or None,args=['--no-sandbox'])
        try:
            page=browser.new_page();errors=[]
            page.on('pageerror',lambda x:errors.append(str(x)))
            page.set_content(HTML);page.add_script_tag(content=FETCH)
            page.add_script_tag(content=JS.replace('__API_JSON__',json.dumps(CONFIG)))
            expect(page.locator('#connection-text')).to_have_text('CONNECTED')
            page.evaluate("showDetail('missing')")
            expect(page.locator('#detail')).to_contain_text('404')
            assert page.locator('#connection-text').inner_text()=='CONNECTED'
            assert page.locator('#retry').is_hidden()
            assert page.locator('#error').is_hidden()
            page.evaluate("showDetail('A')")
            expect(page.locator('#detail')).to_contain_text('Alpha')
            assert '실패' not in page.locator('#detail').inner_text()
            assert page.locator('#connection-text').inner_text()=='CONNECTED'
            assert not errors,errors
        finally:
            browser.close()
