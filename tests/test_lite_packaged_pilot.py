"""Pro-built, published ZIP members must work offline after extraction.

This covers the actual CI artifact contents, unlike standalone builder tests.
Run after: python scripts/lite_delivery_rehearsal.py --out-dir lite_delivery_output
Tests use synthetic inputs only, and do not assert human Windows acceptance.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from zipfile import ZipFile

import pytest


PILOT = Path("lite_delivery_output")
CASE_ROWS = {"cafe": 3, "inventory": 3, "office": 2}
EXPECTED_NAMES = {
    *(f"{theme}_DEMO.html" for theme in CASE_ROWS),
    *(f"{theme}_SOURCE.csv" for theme in CASE_ROWS),
    "cafe_VALID_update.csv",
    "cafe_INVALID_duplicate_id.csv",
    "WINDOWS_HUMAN_PILOT_README.txt",
    "SHA256SUMS.txt",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.fixture(scope="module")
def unpacked_pilot(tmp_path_factory: pytest.TempPathFactory) -> Path:
    package_path = PILOT / "REA_WEB_Lite_Synthetic_Pilot.zip"
    report_path = PILOT / "rehearsal_report.json"
    assert package_path.is_file(), "First run scripts/lite_delivery_rehearsal.py"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "SYNTHETIC_AUTOMATED_DELIVERY_PASS"
    assert report["not_human"] is True
    assert report["not_customer_data"] is True
    assert report["not_windows_human_acceptance"] is True
    package_bytes = package_path.read_bytes()
    assert sha256(package_bytes) == report["package"]["sha256"]

    folder = tmp_path_factory.mktemp("delivered-pilot")
    with ZipFile(package_path) as archive:
        assert archive.testzip() is None
        assert len(archive.infolist()) == len(EXPECTED_NAMES)
        assert set(archive.namelist()) == EXPECTED_NAMES
        manifest_lines = archive.read("SHA256SUMS.txt").decode("ascii").splitlines()
        assert len(manifest_lines) == len(EXPECTED_NAMES) - 1
        manifest = {}
        for line in manifest_lines:
            h, delim, name = line.partition("  ")
            assert delim == "  "
            assert len(h) == 64
            assert name not in manifest
            manifest[name] = h
        assert set(manifest) == EXPECTED_NAMES - {"SHA256SUMS.txt"}

        for name in EXPECTED_NAMES:
            contents = archive.read(name)
            if name in manifest:
                assert sha256(contents) == manifest[name]
            # Explicit flat, allowlisted filenames only; no ZIP path extraction.
            (folder / name).write_bytes(contents)

    for case in report["cases"]:
        theme = case["theme"]
        assert theme in CASE_ROWS
        assert case["rows"] == CASE_ROWS[theme]
        assert sha256((folder / f"{theme}_DEMO.html").read_bytes()) == case["html_sha256"]
        assert sha256((folder / f"{theme}_SOURCE.csv").read_bytes()) == case["input_sha256"]
        assert case["unchanged_input"] and case["no_overwrite"]
    assert len(report["cases"]) == len(CASE_ROWS)
    return folder


@pytest.mark.parametrize("theme", ["cafe", "inventory", "office"])
def test_delivered_zip_html_file_browser(
    unpacked_pilot: Path, tmp_path: Path, theme: str
) -> None:
    from playwright.sync_api import expect, sync_playwright

    html = unpacked_pilot / f"{theme}_DEMO.html"
    source = unpacked_pilot / f"{theme}_SOURCE.csv"
    before_html, before_csv = sha256(html.read_bytes()), sha256(source.read_bytes())

    with sync_playwright() as playwright:
        launch_kwargs = {"headless": True}
        if os.environ.get("REA_BROWSER_CHANNEL") == "msedge":
            launch_kwargs["channel"] = "msedge"
        browser = playwright.chromium.launch(**launch_kwargs)
        try:
            page = browser.new_page(accept_downloads=True)
            errors, requests = [], []
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.on("request", lambda req: requests.append(req.url))
            page.goto(html.resolve().as_uri())
            assert page.url.startswith("file://")
            expect(page.locator("body")).to_have_attribute("data-theme", theme)
            expect(page.locator("#total")).to_have_text(str(CASE_ROWS[theme]))
            assert page.locator(".record").count() == CASE_ROWS[theme]
            first = page.locator(".record").first
            title = first.locator("strong").inner_text()
            page.locator("#search").fill(title)
            expect(page.locator("#matched")).not_to_have_text("0")
            page.locator("#search").fill("")
            first = page.locator(".record").first
            first.click()
            assert title in page.locator("#details").inner_text()

            if theme == "cafe":
                page.locator("#csv-file").set_input_files(
                    str(unpacked_pilot / "cafe_INVALID_duplicate_id.csv")
                )
                expect(page.locator("#status")).to_contain_text("갱신 실패")
                expect(page.locator("#total")).to_have_text("3")
                page.locator("#csv-file").set_input_files(
                    str(unpacked_pilot / "cafe_VALID_update.csv")
                )
                expect(page.locator("#total")).to_have_text("5")
                expect(page.locator("#status")).to_contain_text("CSV 5건")
                with page.expect_download() as download:
                    page.locator("#export").click()
                saved = tmp_path / "newly_saved.html"
                download.value.save_as(saved)
                assert saved.is_file() and sha256(saved.read_bytes()) != before_html
                reopened = browser.new_page()
                reopened_errors, reopened_requests = [], []
                reopened.on("pageerror", lambda err: reopened_errors.append(str(err)))
                reopened.on("request", lambda req: reopened_requests.append(req.url))
                reopened.goto(saved.resolve().as_uri())
                assert reopened.url.startswith("file://")
                expect(reopened.locator("#total")).to_have_text("5")
                reopened.locator(".record").first.click()
                assert "아이스, 아메리카노" in reopened.locator("#details").inner_text()
                assert not reopened_errors, reopened_errors
                assert not [url for url in reopened_requests if url.startswith(("http://", "https://"))]
                reopened.close()

            assert not errors, errors
            assert not [url for url in requests if url.startswith(("http://", "https://"))], requests
        finally:
            browser.close()
    assert sha256(html.read_bytes()) == before_html
    assert sha256(source.read_bytes()) == before_csv
