"""Genuine on-disk file:// Chromium and Windows Edge acceptance; synthetic data."""
import os
from pathlib import Path
import pytest
from rea.lite_builder import inspect, build

@pytest.mark.parametrize("theme", ["cafe", "inventory", "office"])
def test_file_url_update_reopen(tmp_path: Path, theme: str):
    from playwright.sync_api import sync_playwright, expect

    source = tmp_path / "source.csv"
    source.write_text("item_code,item_name,group,price\nA01,First,Alpha,100\nB02,Second,Beta,200\n", encoding="utf-8")
    output = tmp_path / "original.html"
    build(source, output, mapping={"id": "item_code", "title": "item_name", "category": "group"},
          approved_sha=inspect(source)["sha256"], confirmation="APPROVE", theme=theme, title="Synthetic catalog")
    malformed = tmp_path / "invalid.csv"
    malformed.write_text("item_code,item_name,group,price\nA01,first,A,1\nA01,duplicate,A,1\n", encoding="utf-8")
    replacement = tmp_path / "replacement.csv"
    replacement.write_text('group,price,item_name,item_code\nNew,50,"Updated, item",Z99\n', encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            **({"channel": "msedge"} if os.environ.get("REA_BROWSER_CHANNEL") == "msedge" else {}),
        )
        try:
            page = browser.new_page(accept_downloads=True)
            requests, errors = [], []
            page.on("request", lambda req: requests.append(req.url))
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.goto(output.resolve().as_uri())
            assert page.url.startswith("file://")
            assert page.locator("#total").inner_text() == "2"
            assert page.locator("body").get_attribute("data-theme") == theme
            page.locator("#search").fill("B02")
            assert page.locator("#matched").inner_text() == "1"
            page.locator("#search").fill("")

            page.locator("#csv-file").set_input_files(str(malformed))
            expect(page.locator("#status")).to_contain_text("갱신 실패")
            assert page.locator("#total").inner_text() == "2"

            page.locator("#csv-file").set_input_files(str(replacement))
            expect(page.locator("#total")).to_have_text("1")
            page.locator(".record").click()
            assert "Updated, item" in page.locator("#details").inner_text()

            with page.expect_download() as dl:
                page.locator("#export").click()
            saved = tmp_path / "reopened.html"
            dl.value.save_as(saved)
            assert saved.exists() and saved.stat().st_size < 2_000_000

            fresh = browser.new_page()
            fresh_errors = []
            fresh.on("pageerror", lambda err: fresh_errors.append(str(err)))
            fresh.goto(saved.resolve().as_uri())
            assert fresh.url.startswith("file://")
            assert fresh.locator("#total").inner_text() == "1"
            fresh.locator(".record").click()
            assert "Updated, item" in fresh.locator("#details").inner_text()
            assert not fresh_errors, fresh_errors
            assert not errors, errors
            assert not [u for u in requests if u.startswith(("https://", "http://"))], requests
        finally:
            browser.close()
