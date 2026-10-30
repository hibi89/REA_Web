"""Keyboard-only offline CSV picker regression, actual seller-built file:// HTML.

Chrome/Edge users must be able to open the native chooser with Enter and Space.
Synthetic data. Headless CI automation, not a nondeveloper human acceptance.
"""
import os
from pathlib import Path

import pytest
from rea.lite_builder import build, inspect


@pytest.mark.parametrize("key", ["Enter", "Space"])
def test_file_picker_works_from_keyboard(tmp_path: Path, key: str) -> None:
    from playwright.sync_api import expect, sync_playwright

    csv_path = tmp_path / "source.csv"
    csv_path.write_text(
        "code,name,group,price\nA01,Original,Inventory,100\n",
        encoding="utf-8",
    )
    replacement = tmp_path / "replacement.csv"
    replacement.write_text(
        "price,group,name,code\n200,Inventory,Updated,B02\n"
        "300,Inventory,Third,C03\n", encoding="utf-8",
    )
    html = tmp_path / "output.html"
    build(
        csv_path, html,
        mapping={"id": "code", "title": "name", "category": "group"},
        approved_sha=inspect(csv_path)["sha256"], confirmation="APPROVE",
        theme="cafe", title="Keyboard accessibility test",
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            **({"channel": "msedge"} if os.environ.get("REA_BROWSER_CHANNEL") == "msedge" else {}),
        )
        try:
            page = browser.new_page(accept_downloads=True)
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.goto(html.resolve().as_uri())
            expect(page.locator("#total")).to_have_text("1")
            label = page.locator("label.file-button")
            expect(label).to_have_attribute("role", "button")
            expect(label).to_have_attribute("tabindex", "0")
            label.focus()
            assert label.evaluate("(el) => document.activeElement === el")
            with page.expect_file_chooser(timeout=3500) as chooser:
                label.press(key)
            chooser.value.set_files(str(replacement))
            expect(page.locator("#total")).to_have_text("2")
            expect(page.locator("#status")).to_contain_text("CSV 2건")
            assert not errors, errors
        finally:
            browser.close()
