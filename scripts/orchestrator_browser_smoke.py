"""Day2 real Chromium E2E: optional reviewed Fable + independent CSV web app."""
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
from rea.orchestrator import build  # noqa: E402


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    with tempfile.TemporaryDirectory(prefix="rea-d2-browser-") as tmp:
        out = Path(tmp) / "site"
        manifest = build(ROOT / "samples/products.csv", out,
                         fable_result=ROOT / "samples/fable_record_redacted.json")
        assert manifest["fable_review"]["validation"] == "VALIDATED"
        port = free_port()
        server = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1",
             "--port", str(port), "--log-level", "warning"],
            cwd=out, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        try:
            base = f"http://127.0.0.1:{port}"
            for _ in range(60):
                if server.poll() is not None:
                    raise RuntimeError(server.stderr.read().decode(errors="replace"))
                try:
                    with urlopen(base + "/health", timeout=1) as response:
                        if response.status == 200:
                            break
                except (URLError, OSError):
                    time.sleep(0.2)
            else:
                raise TimeoutError("Server did not become healthy")
            errors, external = [], []
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
                ctx = browser.new_context()
                page = ctx.new_page()
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.on("request", lambda q: external.append(q.url) if not q.url.startswith(base + "/") else None)
                page.goto(base + "/", wait_until="networkidle")
                expect(page.locator("#count")).to_have_text("5건")
                page.locator("#category").select_option(label="음료")
                expect(page.locator("#count")).to_have_text("2건")
                page.locator("#search").fill("카페")
                expect(page.locator("#count")).to_have_text("1건")
                page.locator(".item").click()
                expect(page.locator("#detail h3")).to_have_text("카페라떼")
                expect(page.locator("#detail")).to_contain_text("4000")
                page.reload(wait_until="networkidle")
                expect(page.locator("#count")).to_have_text("5건")
                assert not errors, errors
                assert not external, external
                assert page.request.get(base + "/review/fable_review.json").status == 404
                ctx.close()
                browser.close()
            print("PASS D2 real Chromium: optional Fable review + independent app, filter/search/detail/reload, no JS/external network")
        finally:
            server.terminate()
            try:
                server.communicate(timeout=6)
            except subprocess.TimeoutExpired:
                server.kill()
                server.communicate(timeout=6)


if __name__ == "__main__":
    main()
