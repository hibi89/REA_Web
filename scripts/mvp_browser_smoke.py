"""True Chromium loopback smoke for the generated CSV app (not a DOM mock)."""
from __future__ import annotations

import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rea.mvp import generate  # noqa: E402


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def run() -> None:
    with tempfile.TemporaryDirectory(prefix="rea-mvp-browser-") as temp:
        destination = Path(temp) / "generated"
        generate(ROOT / "samples" / "products.csv", destination, "Browser smoke")
        port = free_port()
        server = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1",
             "--port", str(port), "--log-level", "warning"],
            cwd=destination, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        try:
            base = f"http://127.0.0.1:{port}"
            for attempt in range(60):
                if server.poll() is not None:
                    raise RuntimeError("Uvicorn stopped before starting: " + server.stderr.read().decode(errors="replace"))
                try:
                    with urlopen(base + "/health", timeout=1) as response:
                        if response.status == 200:
                            break
                except (URLError, OSError):
                    time.sleep(0.2)
            else:
                raise TimeoutError("Generated server did not become healthy in time")
            errors, external = [], []
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
                context = browser.new_context()
                page = context.new_page()
                page.on("pageerror", lambda exc: errors.append(str(exc)))
                page.on("request", lambda request: external.append(request.url) if not request.url.startswith(base + "/") else None)
                page.goto(base + "/", wait_until="networkidle")
                expect(page.locator("#count")).to_have_text("5건")
                expect(page.locator(".item")).to_have_count(5)
                page.locator("#category").select_option(label="음료")
                expect(page.locator("#count")).to_have_text("2건")
                page.locator("#search").fill("카페")
                expect(page.locator("#count")).to_have_text("1건")
                expect(page.locator(".item")).to_have_count(1)
                page.locator(".item").click()
                expect(page.locator("#detail h3")).to_have_text("카페라떼")
                expect(page.locator("#detail")).to_contain_text("4000")
                page.reload(wait_until="networkidle")
                expect(page.locator("#count")).to_have_text("5건")
                assert not errors, f"JS console exceptions: {errors}"
                assert not external, f"Unexpected external requests: {external}"
                context.close()
                browser.close()
            print("PASS real Chromium: 5 rows; filter 2; search 1; detail; reload; zero JS/network errors")
        finally:
            server.terminate()
            try:
                server.communicate(timeout=6)
            except subprocess.TimeoutExpired:
                server.kill()
                server.communicate(timeout=6)


if __name__ == "__main__":
    run()
