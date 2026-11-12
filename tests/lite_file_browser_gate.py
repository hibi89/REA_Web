"""Synthetic REA Lite real file:// browser gate for CI Windows/Ubuntu.

No buyer data is used. Opens the *packaged* catalog from a safe exact-name
read, not an arbitrary ZIP extraction. Does not prove customer device acceptance.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from rea.lite_builder import build_lite
from rea.lite_delivery import package_lite, verify_lite_zip


def browser_path() -> Path:
    locations = [
        shutil.which("google-chrome"), shutil.which("chromium"),
        shutil.which("chromium-browser"), shutil.which("chrome"),
    ]
    if sys.platform == "win32":
        roots = [os.environ.get("PROGRAMFILES", ""), os.environ.get("PROGRAMFILES(X86)", ""),
                 os.environ.get("LOCALAPPDATA", "")]
        for root in roots:
            if root:
                locations.extend([
                    str(Path(root) / "Google" / "Chrome" / "Application" / "chrome.exe"),
                    str(Path(root) / "Microsoft" / "Edge" / "Application" / "msedge.exe"),
                ])
    for candidate in locations:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    raise RuntimeError("NO_CHROMIUM_BROWSER_AVAILABLE")


def main():
    chrome = browser_path()
    with tempfile.TemporaryDirectory(prefix="rea-lite-file-gate-") as temp:
        root = Path(temp)
        source = root / "synthetic.csv"
        source.write_text("식별자,이름,분류,설명\nC01,카페 상품,음료,합성\nC02,노트북 재고,재고,합성\nC03,사무 문서,문서,합성\n",
                          encoding="utf-8")
        html = root / "catalog.html"
        receipt = build_lite(source, html, mapping={"id": "식별자", "title": "이름", "category": "분류"},
                             expected_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                             confirmation="APPROVE", theme="office", name="REA 로컬 검수")
        package = root / "delivery.zip"
        package_lite(html, package, expected_html_sha256=receipt["html_sha256"],
                     acknowledge="ACK_PLAINTEXT_LOCAL_DATA")
        result = verify_lite_zip(package)
        if result["rows"] != 3:
            raise AssertionError("PACKAGED_ROWS_MISMATCH")
        with zipfile.ZipFile(package) as archive:
            # Only the exact, allowlisted HTML member is read after verifier.
            delivered = archive.read("catalog.html")
        target = root / "buyer-open.html"
        target.write_bytes(delivered)
        profile = root / "chrome-profile"
        cmd = [str(chrome), "--headless=new", "--no-sandbox", "--disable-gpu",
               "--disable-dev-shm-usage", "--disable-extensions", "--no-first-run",
               "--disable-background-networking", "--no-default-browser-check",
               "--virtual-time-budget=4000", "--user-data-dir=" + str(profile),
               "--dump-dom", target.as_uri()]
        run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             encoding="utf-8", errors="replace", timeout=55)
        if run.returncode:
            raise RuntimeError("BROWSER_HEADLESS_FAILED_" + str(run.returncode))
        if not re.search(r'<tbody id="items">\s*<tr\b', run.stdout, re.I):
            raise AssertionError("FILE_URL_LITE_DOM_NOT_RENDERED")
        match = re.search(r'<tbody id="items">(.*?)</tbody>', run.stdout, re.I | re.S)
        if match is None or len(re.findall(r'<tr\b', match.group(1), re.I)) != 3:
            raise AssertionError("FILE_URL_THREE_ROWS_NOT_RENDERED")
        for title in ("카페 상품", "노트북 재고", "사무 문서"):
            if title not in match.group(1):
                raise AssertionError("FILE_URL_EXPECTED_SYNTHETIC_TITLE_MISSING")
        if "connect-src 'none'" not in run.stdout:
            raise AssertionError("FILE_URL_CSP_MISSING")
        print("REA_LITE_FILE_URL_BROWSER_PASS: 3 synthetic rows; generated ZIP HTML; " +
              ("Windows" if sys.platform == "win32" else "non-Windows") +
              "; customer device and commercial acceptance NOT VERIFIED")


if __name__ == "__main__":
    main()
