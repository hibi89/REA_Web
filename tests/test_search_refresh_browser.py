"""Search query stays active when a trusted dashboard API refresh returns new rows."""
import json
import os
from playwright.sync_api import expect, sync_playwright
from rea.adapter.frontend_bridge import JS

HTML='''<div id="connection"><span id="connection-text"></span></div><span id="kpi-total"></span><span id="kpi-completed"></span><span id="kpi-pending"></span><span id="count"></span><span id="empty" hidden></span><input id="search"><table><tbody id="jobs"></tbody></table><div id="detail"></div><div id="error" hidden></div><button id="retry" hidden></button>'''
CONFIG={'list': {'path':'/api/jobs','field':'items'}, 'metrics': {'path':'/api/metrics','field':'__root__'}, 'detail': {'path':'/api/jobs/{job_id}','field':'__root__'}}
FETCH='''
window.revision=0;
window.fetch=async(path, opts)=>{
 const items = [{id:'a',name:'Alpha',category:'audit',status:'done'},{id:'b',name:'Beta',category:'audit',status:'pending'}];
 if(window.revision) items.push({id:'c',name:'Beta new',category:'quality',status:'pending'});
 const body=path==='/api/jobs'?{items}:{total:items.length,completed:1,pending:items.length-1};
 return new Response(JSON.stringify(body),{headers:{'content-type':'application/json'}});
};
'''

def test_reload_preserves_visible_search_query_and_new_matching_rows():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=os.environ.get('REA_CHROMIUM_PATH') or None,args=['--no-sandbox'])
        try:
            page=browser.new_page();page.set_content(HTML);page.add_script_tag(content=FETCH)
            page.add_script_tag(content=JS.replace('__API_JSON__',json.dumps(CONFIG)))
            expect(page.locator('#jobs tr')).to_have_count(2)
            page.locator('#search').fill('beta')
            expect(page.locator('#jobs tr')).to_have_count(1)
            page.evaluate("window.revision=1;load()")
            expect(page.locator('#kpi-total')).to_have_text('3')
            expect(page.locator('#jobs tr')).to_have_count(2)
            assert page.locator('#search').input_value()=='beta'
            assert 'Alpha' not in page.locator('#jobs').inner_text()
            assert 'Beta new' in page.locator('#jobs').inner_text()
        finally: browser.close()
