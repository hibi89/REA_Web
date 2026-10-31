"""Native file:// browser test. Run with installed Chromium/Playwright, no remote access."""
from __future__ import annotations
import base64
import json
import os
import re
from pathlib import Path
import pytest
_playwright = pytest.importorskip("playwright.sync_api")
sync_playwright = _playwright.sync_playwright
expect = _playwright.expect

TEMPLATE = Path(__file__).resolve().parents[1] / 'rea' / 'lite_assets' / 'template.html'

@pytest.fixture()
def local_html(tmp_path):
    data={'version':1,'name':'Cafe <safe>','theme':'cafe','headers':['id','title','category','price'],
          'records':[{'id':str(i),'title':('콜드브루' if i==5 else f'Item {i}'),'category':('음료' if i%2 else '디저트'),'price':'5000'} for i in range(1,126)],'sourceSha256':'abc'}
    encoded=base64.b64encode(json.dumps(data,ensure_ascii=False).encode('utf-8')).decode('ascii')
    html=TEMPLATE.read_text(encoding='utf-8').replace('REPLACE_WITH_DATA_BASE64',encoded)
    path=tmp_path/'store.html';path.write_text(html,encoding='utf-8')
    return path


def test_dom_and_update_export(local_html, tmp_path):
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, executable_path=os.getenv('REA_CHROME_PATH') or ('/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None),args=['--no-sandbox'])
        page=b.new_page(accept_downloads=True)
        errors=[]; page.on('pageerror',lambda e: errors.append(str(e)))
        page.set_content(local_html.read_text(encoding="utf-8"))
        assert page.locator('#summary').inner_text().startswith('125개')
        assert page.locator('#items tr').count()==60
        page.locator('#next').click()
        assert '2 / 3' in page.locator('#page-label').inner_text()
        page.locator('#search').fill('콜드브루')
        assert page.locator('#items tr').count()==1
        page.locator('#items tr button').click()
        assert page.locator('#details').is_visible()
        assert '콜드브루' in page.locator('#detail-list').inner_text()
        page.locator('#close-dialog').click()
        old_count=page.locator('#summary').inner_text()
        bad=tmp_path/'bad.csv';bad.write_text('id,title,category,price\n1,Good,음료,1000\n1,Duplicate,음료,1000\n',encoding='utf-8')
        page.locator('#csv-file').set_input_files(str(bad));page.locator('#apply').click()
        expect(page.locator('#status')).to_contain_text('기존 데이터 유지')
        assert page.locator('#summary').inner_text()==old_count
        good=tmp_path/'good.csv';good.write_text('id,title,category,price\n7,Fresh Coffee,음료,2300\n8,New Cake,디저트,4500\n',encoding='utf-8')
        page.locator('#csv-file').set_input_files(str(good));page.locator('#apply').click()
        expect(page.locator('#status')).to_contain_text('2개 항목 적용')
        with page.expect_download() as info:
            page.locator('#export').click()
        download=info.value
        download.save_as(tmp_path/'updated.html')
        page.set_content((tmp_path/'updated.html').read_text(encoding="utf-8"))
        assert '2개 항목' in page.locator('#summary').inner_text()
        assert 'Fresh Coffee' in page.locator('#items').inner_text()
        assert not errors, errors
        b.close()


def test_file_url_native_only(local_html, tmp_path):
    """Real on-disk file open, invalid CSV rollback, valid update and exported file reopen."""
    from playwright._impl._errors import Error as PlaywrightError
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, executable_path=os.getenv('REA_CHROME_PATH') or ('/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None), args=['--no-sandbox'])
        page = b.new_page(accept_downloads=True)
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        try:
            try:
                page.goto(local_html.as_uri())
            except PlaywrightError as exc:
                if 'ERR_BLOCKED_BY_ADMINISTRATOR' in str(exc) and not os.getenv('REA_REQUIRE_NATIVE_FILE'):
                    pytest.skip('Container policy blocks file://; native Windows acceptance unverified')
                raise
            assert page.locator('#items tr').count() == 60
            before = page.locator('#summary').inner_text()
            invalid = tmp_path / 'native-invalid.csv'
            invalid.write_text('id,title,category,price\n1,Tea,Drink,10\n1,Duplicate,Drink,20\n', encoding='utf-8')
            page.locator('#csv-file').set_input_files(str(invalid))
            page.locator('#apply').click()
            expect(page.locator('#status')).to_contain_text('기존 데이터 유지')
            assert page.locator('#summary').inner_text() == before
            updated = tmp_path / 'native-updated.csv'
            updated.write_text('id,title,category,price\nN1,Native Windows,Office,500\n', encoding='utf-8')
            page.locator('#csv-file').set_input_files(str(updated))
            page.locator('#apply').click()
            expect(page.locator('#status')).to_contain_text('1개 항목 적용')
            with page.expect_download() as handle:
                page.locator('#export').click()
            saved = tmp_path / 'native-export-reopen.html'
            handle.value.save_as(saved)
            page.goto(saved.as_uri())
            assert '1개 항목' in page.locator('#summary').inner_text()
            assert 'Native Windows' in page.locator('#items').inner_text()
            assert not errors, errors
        finally:
            b.close()


def test_csv_matches_pro_parser_for_blank_lines_embedded_quotes_and_escaped_cells(local_html, tmp_path):
    """CSV accepted by Python csv.DictReader(strict=True) must also work in Lite."""
    valid=(
        'id,title,category,price\r\n'
        '\r\n'
        'A,"Coffee, Tea",음료,1000\r\n'
        'B,Plain"Quote,디저트,2000\r\n'
        'C,"두 줄\r\n내용",음료,3000\r\n'
        '\r\n'
    )
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path=os.getenv('REA_CHROME_PATH') or ('/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None),args=['--no-sandbox'])
        page=b.new_page(accept_downloads=True)
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(local_html.read_text(encoding='utf-8'))
        csvfile=tmp_path/'valid.csv';csvfile.write_text(valid,encoding='utf-8')
        page.locator('#csv-file').set_input_files(str(csvfile));page.locator('#apply').click()
        expect(page.locator('#status')).to_contain_text('3개 항목 적용')
        assert '3개 항목' in page.locator('#summary').inner_text()
        page.locator('#search').fill('Plain"Quote')
        assert page.locator('#items tr').count()==1
        page.locator('#search').fill('Coffee, Tea')
        page.locator('#items tr button').first.click()
        assert 'Coffee, Tea' in page.locator('#detail-list').inner_text()
        page.locator('#close-dialog').click()
        with page.expect_download() as info:page.locator('#export').click()
        info.value.save_as(tmp_path/'csv-parity-export.html')
        page.set_content((tmp_path/'csv-parity-export.html').read_text(encoding='utf-8'))
        assert '3개 항목' in page.locator('#summary').inner_text()
        assert not errors,errors
        b.close()


def test_unsaved_csv_guard_survives_error_and_reopened_html_is_clean(local_html, tmp_path):
    """CSV apply is in-memory until export; warnings must survive later CSV errors."""
    with sync_playwright() as p:
        b = p.chromium.launch(
            headless=True,
            executable_path=os.getenv('REA_CHROME_PATH') or
            ('/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None),
            args=['--no-sandbox'],
        )
        page = b.new_page(accept_downloads=True)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        try:
            page.set_content(local_html.read_text(encoding='utf-8'))
            assert '변경사항 없음' in page.locator('#save-state').inner_text()

            def blocks_navigation():
                return page.evaluate("""() => {
                    const event = new Event('beforeunload', {cancelable: true});
                    window.dispatchEvent(event);
                    return event.defaultPrevented;
                }""")

            assert blocks_navigation() is False

            bad = tmp_path / 'bad-unsaved.csv'
            bad.write_text(
                'id,title,category,price\n1,First,Drink,100\n1,Duplicate,Drink,200\n',
                encoding='utf-8',
            )
            page.locator('#csv-file').set_input_files(str(bad))
            page.locator('#apply').click()
            expect(page.locator('#status')).to_contain_text('기존 데이터 유지')
            assert '변경사항 없음' in page.locator('#save-state').inner_text()
            assert blocks_navigation() is False

            good = tmp_path / 'valid-unsaved.csv'
            good.write_text('id,title,category,price\nN01,New Item,Office,500\n', encoding='utf-8')
            page.locator('#csv-file').set_input_files(str(good))
            page.locator('#apply').click()
            expect(page.locator('#status')).to_contain_text('1개 항목 적용')
            expect(page.locator('#save-state')).to_contain_text('저장 전 변경사항')
            assert blocks_navigation() is True

            page.locator('#csv-file').set_input_files(str(bad))
            page.locator('#apply').click()
            expect(page.locator('#status')).to_contain_text('기존 데이터 유지')
            assert '저장 전 변경사항' in page.locator('#save-state').inner_text()
            assert blocks_navigation() is True

            with page.expect_download() as item:
                page.locator('#export').click()
            target = tmp_path / 'unsaved-guard-export.html'
            item.value.save_as(target)
            # The original seller-source SHA must not appear as evidence that
            # newly imported browser CSV rows match that original source.
            saved_html = target.read_text(encoding='utf-8')
            match = re.search(
                r'<script id="rea-data" type="application/octet-stream">([^<]+)</script>',
                saved_html,
            )
            assert match is not None
            payload = json.loads(base64.b64decode(match.group(1)))
            assert payload['sourceSha256'] is None
            assert payload['originalSourceSha256'] == 'abc'
            assert payload['dataOrigin'] == 'BROWSER_CSV_UPDATED_HASH_UNVERIFIED'
            assert [record['id'] for record in payload['records']] == ['N01']
            # The browser cannot verify the OS has actually saved/reopened the
            # file, so download request must not silently clear the warning.
            expect(page.locator('#save-state')).to_contain_text('저장 전 변경사항')
            assert blocks_navigation() is True

            page.set_content(target.read_text(encoding='utf-8'))
            expect(page.locator('#save-state')).to_contain_text('변경사항 없음')
            assert page.locator('#summary').inner_text().startswith('1개')
            assert 'New Item' in page.locator('#items').inner_text()
            assert blocks_navigation() is False
            assert not errors, errors
        finally:
            b.close()


@pytest.mark.parametrize("key", ["Enter", "Space"])
def test_native_file_picker_keyboard_access(local_html, tmp_path, key):
    """Native visible input must open CSV chooser with keyboard, unlike stale PR #31 label."""
    replacement = tmp_path / "keyboard-replacement.csv"
    replacement.write_text(
        "id,title,category,price\nK01,Keyboard Accessible,Office,123\n",
        encoding="utf-8",
    )
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=os.getenv("REA_CHROME_PATH") or
            ("/usr/bin/chromium" if Path("/usr/bin/chromium").exists() else None),
            args=["--no-sandbox"],
        )
        page = browser.new_page(accept_downloads=True)
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        try:
            if os.getenv("REA_REQUIRE_NATIVE_FILE"):
                page.goto(local_html.resolve().as_uri())
            else:
                page.set_content(local_html.read_text(encoding="utf-8"))
            picker = page.locator("#csv-file")
            expect(picker).to_be_visible()
            picker.focus()
            assert picker.evaluate("(el) => document.activeElement === el")
            with page.expect_file_chooser(timeout=5000) as chooser:
                picker.press(key)
            chooser.value.set_files(str(replacement))
            page.locator("#apply").click()
            expect(page.locator("#status")).to_contain_text("1개 항목 적용")
            assert "Keyboard Accessible" in page.locator("#items").inner_text()
            assert not errors, errors
        finally:
            browser.close()
