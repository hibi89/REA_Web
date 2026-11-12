"""Real headless file:// buyer-flow verification using synthetic local REA Lite data only.

A temporary test script drives the unmodified product UI and intercepts only
the browser-created download Blob. The actual bytes are saved, packaged and
reopened at file://. This is not a human/customer device acceptance test.
"""
from __future__ import annotations

import base64
import hashlib
import html as html_lib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from rea.lite_builder import build_lite
from rea.lite_delivery import package_lite, verify_lite_zip
from lite_file_browser_gate import browser_path


HARNESS = r"""
(() => {
  const testNode = document.currentScript;
  testNode.remove(); // ensure that saved buyer HTML does not contain this test
  const f = document.getElementById('csv-file');
  const message = document.getElementById('message');
  const count = () => document.querySelectorAll('#items tr').length;
  const check = (assertion, label) => { if (!assertion) throw Error(label); };
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const until = async predicate => {
    for (let i=0; i<100; i++) {if (predicate()) return; await sleep(25);}
    throw Error('CSV_UI_TIMEOUT');
  };
  async function replaceCSV(encoded, expected, statusText) {
    const bytes = Uint8Array.from(atob(encoded), c=>c.charCodeAt(0));
    const transfer = new DataTransfer();
    transfer.items.add(new File([bytes], 'owner-reviewed.csv', {type:'text/csv'}));
    f.files=transfer.files;
    f.dispatchEvent(new Event('change', {bubbles:true}));
    await until(() => message.textContent.includes(statusText));
    check(count()===expected, 'ROW_COUNT_AFTER_CSV_'+expected+'_ACTUAL_'+count()+'_MESSAGE_'+message.textContent);
  }
  function report(value) {
    const e=document.createElement('pre');
    e.id='rea-gate';
    e.textContent=value;
    document.body.appendChild(e);
  }
  (async () => {
    check(count()===3,'INITIAL_ITEMS_MISSING');
    const search=document.getElementById('search');
    search.value='사무';
    search.dispatchEvent(new Event('input',{bubbles:true}));
    check(count()===1,'SEARCH_NOT_APPLIED');
    search.value='';
    search.dispatchEvent(new Event('input',{bubbles:true}));
    const category=document.getElementById('category');
    category.value='문서';category.dispatchEvent(new Event('change',{bubbles:true}));
    check(count()===1,'CATEGORY_NOT_APPLIED');
    category.value='';category.dispatchEvent(new Event('change',{bubbles:true}));
    check(count()===3,'FILTER_NOT_RESTORED');
    await replaceCSV('__BAD_CSV_B64__',3,'이전 데이터는 유지');
    await replaceCSV('__GOOD_CSV_B64__',2,'검증 완료');
    check(document.getElementById('items').textContent.includes('카페업데이트'), 'SOURCE_HEADERS_NOT_MAPPED');
    await replaceCSV('__INJECT_CSV_B64__',1,'검증 완료');
    check(count()===1 && document.querySelectorAll('#items img').length===0,'HTML_INJECTION_EXECUTED');
    const originalCreate=URL.createObjectURL.bind(URL);
    let downloaded=null;
    URL.createObjectURL=blob=>{downloaded=blob;return originalCreate(blob)};
    document.getElementById('export').click();
    check(downloaded!==null,'BROWSER_EXPORT_NOT_CREATED');
    const bytes=new Uint8Array(await downloaded.arrayBuffer());
    check(bytes.length>2000 && bytes.length<16*1024*1024,'EXPORT_BYTES_INVALID');
    let binary='';
    for(let p=0;p<bytes.length;p+=8192) binary+=String.fromCharCode(...bytes.slice(p,p+8192));
    report('PASS:'+btoa(binary));
  })().catch(err=>report('FAIL:'+String(err.message||err)));
})();
"""


def chrome_dom(chrome: Path, target: Path, profile: Path, *, seconds: int = 50) -> str:
    flags = [str(chrome), '--headless=new', '--no-sandbox', '--disable-gpu',
             '--disable-dev-shm-usage', '--disable-extensions', '--no-first-run',
             '--disable-background-networking', '--no-default-browser-check',
             '--virtual-time-budget=8000', '--user-data-dir=' + str(profile),
             '--dump-dom', target.as_uri()]
    run = subprocess.run(flags, capture_output=True, text=True, encoding='utf-8',
                         errors='replace', timeout=seconds)
    if run.returncode:
        raise AssertionError('HEADLESS_BROWSER_EXIT_' + str(run.returncode))
    return run.stdout


def main():
    chrome = browser_path()
    with tempfile.TemporaryDirectory(prefix='rea-lite-export-file-') as workspace:
        root=Path(workspace)
        source=root/'owner.csv'
        source.write_text('식별자,이름,분류,설명\nC01,카페 상품,음료,합성\nC02,노트북 재고,재고,합성\nC03,사무 문서,문서,합성\n',
                          encoding='utf-8')
        initial=root/'source.html'
        receipt=build_lite(source, initial, mapping={'id':'식별자','title':'이름','category':'분류'},
                           expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                           confirmation='APPROVE',theme='office',name='REA 테스트 전용')
        prepared=root/'prepared.zip'
        package_lite(initial,prepared,expected_html_sha256=receipt['html_sha256'],
                     acknowledge='ACK_PLAINTEXT_LOCAL_DATA')
        verify_lite_zip(prepared)

        good='식별자,이름,분류,설명\nN01,카페업데이트,음료,"인용 ""따옴표"""\nN02,두번째,문서,합성\n'
        bad='unexpected,columns\nD01,invalid\n'
        injection='id,title,category,설명\nZ01,"</script><img src=x onerror=alert(1)>",테스트,안전\n'
        def as_b64(s: str) -> str:
            return base64.b64encode(s.encode('utf-8')).decode('ascii')
        harness=(HARNESS.replace('__BAD_CSV_B64__',as_b64(bad))
                        .replace('__GOOD_CSV_B64__',as_b64(good))
                        .replace('__INJECT_CSV_B64__',as_b64(injection)))
        original=initial.read_text(encoding='utf-8')
        if original.count('</body></html>') != 1:
            raise AssertionError('TEMPLATE_HTML_END_MISMATCH')
        annotated=original.replace('</body></html>','<script>'+harness+'</script></body></html>')
        annotated_path=root/'tester.html'
        annotated_path.write_text(annotated,encoding='utf-8')
        dom=chrome_dom(chrome,annotated_path,root/'test-chrome-profile')
        result=re.search(r'<pre id="rea-gate">([^<]+)</pre>',dom,re.S)
        if not result:
            raise AssertionError('OWNER_FLOW_NO_RESULT_MARKER')
        value=html_lib.unescape(result.group(1))
        if not value.startswith('PASS:'):
            raise AssertionError('OWNER_FLOW_FAILED_' + value[:200].replace('\n',' '))
        saved=base64.b64decode(value[5:],validate=True)
        text=saved.decode('utf-8','strict')
        if '<script>'+harness+'</script>' in text:
            raise AssertionError('TEST_SCRIPT_LEAKED_IN_EXPORT')
        if '</script><img' in text or 'rea-gate' in text:
            raise AssertionError('SCRIPT_ESCAPE_OR_TEST_MARKER_LEAK')
        saved_path=root/'saved.html'
        saved_path.write_bytes(saved)
        saved_zip=root/'saved.zip'
        verify=package_lite(saved_path,saved_zip,
                            expected_html_sha256=hashlib.sha256(saved).hexdigest(),
                            acknowledge='ACK_PLAINTEXT_LOCAL_DATA')
        if verify['rows']!=1 or verify['columns']!=4:
            raise AssertionError('EXPORTED_HTML_INVALID_DATA_CONTRACT')

        reopened=chrome_dom(chrome,saved_path,root/'reopen-chrome-profile')
        table=re.search(r'<tbody id="items">(.*?)</tbody>',reopened,re.I|re.S)
        if table is None or len(re.findall(r'<tr\b',table.group(1),re.I)) != 1:
            raise AssertionError('BUYER_REOPEN_BAD_ROW_COUNT')
        if 'onerror=alert(1)' not in table.group(1):
            raise AssertionError('BUYER_REOPEN_LOST_SAFE_TEXT')
        if re.search(r'<img\b',table.group(1),re.I):
            raise AssertionError('BUYER_REOPEN_INJECTION_CREATED_ELEMENT')
        if "connect-src 'none'" not in reopened:
            raise AssertionError('BUYER_REOPEN_CSP_MISSING')
        print('REA_LITE_OWNER_FILE_FLOW_PASS: original browser file://; search/category; ' +
              'reject bad CSV; map owner CSV headers; reject active HTML; export blob; ' +
              'package+verify saved HTML; reopen file:// with 1 inert row; OS=' + sys.platform +
              '; human/legal customer acceptance NOT_VERIFIED')


if __name__ == '__main__':
    main()
