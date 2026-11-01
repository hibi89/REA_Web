"""Real Chromium file:// acceptance for REA Lite generated from rea.mvp.

This is an automated browser test, NOT a human Windows acceptance.
"""
from pathlib import Path
import pytest
from rea.lite_builder import inspect, build

THEMES = ("cafe", "inventory", "office")


def make_html(tmp_path, theme):
    csv = tmp_path / "owner.csv"
    csv.write_text(
        "item_code,item_name,group,price\n"
        "A001,아메리카노,커피,4500\n"
        "A002,카페라테,커피,5000\n"
        "B001,레몬에이드,음료,5500\n", encoding="utf-8")
    html = tmp_path / (theme + ".html")
    build(
        csv, html,
        mapping={"id":"item_code", "title":"item_name", "category":"group"},
        approved_sha=inspect(csv)["sha256"], confirmation="APPROVE",
        theme=theme, title="합성 테스트 카탈로그",
    )
    return html


@pytest.mark.parametrize("theme", THEMES)
def test_real_file_navigation_search_filter_details_and_no_network(tmp_path, theme):
    from playwright.sync_api import sync_playwright
    html = make_html(tmp_path, theme)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(accept_downloads=True)
            errors, external = [], []
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.on("request", lambda req:
                    external.append(req.url) if req.url.startswith(("http://", "https://")) else None)
            page.goto(html.as_uri(), wait_until="load")
            assert page.locator("#total").inner_text() == "3"
            assert page.locator("body").get_attribute("data-theme") == theme
            page.locator("#search").fill("B001")
            assert page.locator("#matched").inner_text() == "1"
            page.locator(".record").click()
            assert "레몬에이드" in page.locator("#details").inner_text()
            page.locator("#search").fill("")
            page.locator("#category").select_option(label="커피")
            assert page.locator("#matched").inner_text() == "2"
            assert not errors, errors
            assert not external, external
        finally:
            browser.close()


def test_bad_csv_preserves_original_and_export_reopens_on_file(tmp_path):
    from playwright.sync_api import sync_playwright
    html = make_html(tmp_path, "inventory")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(accept_downloads=True)
            errors, external = [], []
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.on("request", lambda req:
                    external.append(req.url) if req.url.startswith(("http://", "https://")) else None)
            page.goto(html.as_uri())
            bad = tmp_path / "duplicate.csv"
            bad.write_text("item_code,item_name,group,price\nX1,가,테스트,1\nX1,나,테스트,2\n", encoding="utf-8")
            page.locator("#csv-file").set_input_files(str(bad))
            assert "갱신 실패" in page.locator("#status").inner_text()
            assert page.locator("#total").inner_text() == "3"
            update = tmp_path / "new.csv"
            payload = '</script><img src=x onerror=alert(1)>'
            update.write_text(
                'group,price,item_name,item_code\n'
                '새분류,100,"'+payload+'",Z001\n', encoding="utf-8")
            page.locator("#csv-file").set_input_files(str(update))
            assert page.locator("#total").inner_text() == "1"
            page.locator(".record").click()
            assert payload in page.locator("#details").inner_text()
            assert page.locator("img").count() == 0
            with page.expect_download() as download:
                page.locator("#export").click()
            saved = tmp_path / "rea_exported.html"
            download.value.save_as(saved)
            assert saved.is_file()
            assert payload not in saved.read_text(encoding="utf-8")
            reread = browser.new_page()
            reread.on("pageerror", lambda exc: errors.append(str(exc)))
            reread.goto(saved.as_uri())
            assert reread.locator("#total").inner_text() == "1"
            reread.locator(".record").click()
            assert payload in reread.locator("#details").inner_text()
            assert not errors, errors
            assert not external, external
            assert html.read_text(encoding="utf-8") != saved.read_text(encoding="utf-8")
        finally:
            browser.close()


def test_unsaved_csv_changes_warn_without_browser_persistence(tmp_path):
    """No localStorage/cookies/autosave; navigating away must warn only after edit."""
    from playwright.sync_api import sync_playwright
    html = make_html(tmp_path, "office")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(accept_downloads=True)
            errors = []
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.goto(html.as_uri())
            def warning_status():
                return page.evaluate("""() => {
                    const event = new Event('beforeunload', {cancelable:true});
                    window.dispatchEvent(event);
                    return event.defaultPrevented;
                }""")
            assert warning_status() is False
            initial = page.locator("#total").inner_text()
            bad = tmp_path / "bad.csv"
            bad.write_text("item_code,item_name,group,price\nX1,가,z,1\nX1,나,z,2\n", encoding="utf-8")
            page.locator("#csv-file").set_input_files(str(bad))
            assert "갱신 실패" in page.locator("#status").inner_text()
            assert warning_status() is False
            assert page.locator("#total").inner_text() == initial
            update = tmp_path / "update.csv"
            update.write_text("item_code,item_name,group,price\nX9,업데이트,분류,777\n", encoding="utf-8")
            page.locator("#csv-file").set_input_files(str(update))
            assert page.locator("#total").inner_text() == "1"
            assert warning_status() is True
            assert page.evaluate("() => localStorage.length") == 0
            assert page.evaluate("() => sessionStorage.length") == 0
            with page.expect_download() as incoming:
                page.locator("#export").click()
            saved = tmp_path / "exported.html"
            incoming.value.save_as(saved)
            # A requested download does not prove the user retained the file.
            assert warning_status() is True
            reopened = browser.new_page()
            reopened.goto(saved.as_uri())
            assert reopened.locator("#total").inner_text() == "1"
            assert reopened.locator(".record").inner_text().find("업데이트") >= 0
            assert reopened.evaluate("""() => {
                const event = new Event('beforeunload', {cancelable:true});
                window.dispatchEvent(event);
                return event.defaultPrevented;
            }""") is False
            assert not errors, errors
        finally:
            browser.close()
