"""Real hosted Chrome/Edge file:// download and independent offline REA Lite delivery.

Three synthetic product sectors; no customer data, network or permission changes.
Unlike the CI Blob harness, this invokes the real anchor click and saves the actual
browser Download object to disk, then independently verifies its package and reopens.
"""
from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

from lite_file_browser_gate import browser_path
from rea.lite_owner_kit import build_owner_kit, HTML_NAME, ZIP_NAME
from rea.lite_delivery import package_lite, verify_lite_zip


VERTICALS = (
    ("cafe", "아이스 커피", "따뜻한 차", "새 메뉴"),
    ("inventory", "재고 제품 A", "재고 제품 B", "새 재고"),
    ("office", "사무 문서 A", "사무 문서 B", "새 문서"),
)


def create_sector(root: Path, theme: str, first: str, second: str):
    root.mkdir()
    source = root / "approved.csv"
    source.write_text("식별자,이름,분류,비고\nA01," + first + ",영역,합성\nA02," +
                      second + ",영역,합성\n", encoding="utf-8")
    output = root / "customer"
    output.mkdir()
    receipt = build_owner_kit(
        source, output, mapping={"id": "식별자", "title": "이름", "category": "분류"},
        expected_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        confirm="APPROVE", acknowledge_plaintext="ACK_PLAINTEXT_LOCAL_DATA",
        theme=theme, name="REA 검증용")
    if receipt["sale_approved"] or receipt["buyer_accepted"]:
        raise AssertionError("SYNTHETIC_RECEIPT_FALSE_APPROVAL")
    return source, output


def main() -> None:
    chrome = browser_path()
    with tempfile.TemporaryDirectory(prefix="rea-lite-native-download-") as temp:
        root = Path(temp)
        with sync_playwright() as runner:
            browser = runner.chromium.launch(
                executable_path=str(chrome), headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage",
                      "--disable-background-networking", "--no-first-run"])
            try:
                for theme, first, second, updated in VERTICALS:
                    source, delivery = create_sector(root / theme, theme, first, second)
                    html = delivery / HTML_NAME
                    packed = delivery / ZIP_NAME
                    if verify_lite_zip(packed)["rows"] != 2:
                        raise AssertionError("INITIAL_ZIP_BROKEN")
                    original_hash = hashlib.sha256(html.read_bytes()).hexdigest()
                    ctx = browser.new_context(accept_downloads=True)
                    try:
                        page = ctx.new_page()
                        errors = []
                        requests = []
                        page.on("pageerror", lambda err: errors.append(str(err)))
                        page.on("request", lambda req: requests.append(req.url)
                                if req.url.startswith(("http://", "https://")) else None)
                        response = page.goto(html.as_uri(), wait_until="domcontentloaded")
                        # Local file URLs may not produce a conventional HTTP response.
                        page.locator("#items tr").first.wait_for(timeout=15000)
                        if page.locator("#items tr").count() != 2:
                            raise AssertionError("INITIAL_RENDER_BAD")
                        page.locator("#search").fill(first)
                        if page.locator("#items tr").count() != 1:
                            raise AssertionError("SEARCH_FAILED")
                        page.locator("#search").fill("")
                        page.locator("#category").select_option("영역")
                        if page.locator("#items tr").count() != 2:
                            raise AssertionError("CATEGORY_FAILED")
                        page.locator("#category").select_option("")
                        # Invalid source does not destroy the previous data.
                        page.locator("#csv-file").set_input_files({
                            "name": "invalid.csv", "mimeType": "text/csv",
                            "buffer": b"unexpected,columns\nX,not-valid\n"})
                        page.wait_for_function("document.getElementById('message').textContent.includes('이전 데이터는 유지됩니다.')", timeout=10000)
                        if page.locator("#items tr").count() != 2:
                            raise AssertionError("INVALID_CSV_OLD_DATA_LOST")
                        update = ("식별자,이름,분류,비고\nB01," + updated + ",영역,합성\n" +
                                  "B02,보관 항목,영역,합성\n").encode("utf-8")
                        page.locator("#csv-file").set_input_files({
                            "name": "owner-reviewed.csv", "mimeType": "text/csv",
                            "buffer": update})
                        page.wait_for_function("document.getElementById('message').textContent.includes('검증 완료')", timeout=10000)
                        if page.locator("#items tr").count() != 2:
                            raise AssertionError("APPROVED_MAPPING_FAILED")
                        if updated not in page.locator("#items").inner_text():
                            raise AssertionError("NEW_CONTENT_NOT_VISIBLE")
                        # True native HTML download, with no click suppression or Blob monkeypatch.
                        with page.expect_download(timeout=25000) as download_wait:
                            page.locator("#export").click()
                        download = download_wait.value
                        if download.suggested_filename != "REA_Lite_Updated.html":
                            raise AssertionError("UNEXPECTED_BUYER_FILE_NAME")
                        saved = root / (theme + "_actual_browser_download.html")
                        download.save_as(str(saved))
                        actual = saved.read_bytes()
                        if not actual.startswith(b"<!doctype html>") or updated.encode("utf-8") not in actual:
                            raise AssertionError("BROWSER_DOWNLOAD_CONTENT_MISMATCH")
                        if hashlib.sha256(html.read_bytes()).hexdigest() != original_hash:
                            raise AssertionError("ORIGINAL_BUYER_HTML_WAS_MODIFIED")
                        new_package = root / (theme + "_actual_download.zip")
                        receipt = package_lite(saved, new_package,
                                               expected_html_sha256=hashlib.sha256(actual).hexdigest(),
                                               acknowledge="ACK_PLAINTEXT_LOCAL_DATA")
                        if verify_lite_zip(new_package) != receipt or receipt["sale_approved"]:
                            raise AssertionError("DOWNLOADED_FILE_ZIP_RECHECK_FAILED")
                        reopened = ctx.new_page()
                        reopened.on("pageerror", lambda err: errors.append(str(err)))
                        reopened.on("request", lambda req: requests.append(req.url)
                                    if req.url.startswith(("http://", "https://")) else None)
                        reopened.goto(saved.as_uri(), wait_until="domcontentloaded")
                        reopened.locator("#items tr").first.wait_for(timeout=15000)
                        if reopened.locator("#items tr").count() != 2 or updated not in reopened.locator("#items").inner_text():
                            raise AssertionError("DOWNLOADED_FILE_REOPEN_MISMATCH")
                        if errors or requests:
                            raise AssertionError("BROWSER_ERRORS_OR_REMOTE_REQUESTS")
                        print("REA_LITE_REAL_BROWSER_DOWNLOAD_PASS theme=" + theme +
                              " rows=2 OS=" + sys.platform +
                              " buyer=synthetic release=HOLD")
                    finally:
                        ctx.close()
            finally:
                browser.close()
    print("REA_LITE_THREE_SYNTHETIC_NATIVE_DOWNLOADS_PASS; customer PC and legal authorization NOT_VERIFIED")


if __name__ == "__main__":
    main()
