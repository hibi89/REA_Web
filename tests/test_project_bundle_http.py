"""Real TCP HTTP smoke for a clean extracted, trusted self-authored synthetic bundle.

This test does not use Chromium, and does not run unknown customer sources.
Browser CSP enforcement and Javascript rendering are separate tests.
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import zipfile

from test_project_bundle import package


def _get(url: str) -> tuple[int, str, bytes]:
    try:
        with urlopen(Request(url, method="GET"), timeout=2) as response:
            return response.status, response.headers.get("content-type", ""), response.read()
    except HTTPError as exc:
        return exc.code, exc.headers.get("content-type", ""), exc.read()


def test_clean_synthetic_bundle_real_http_assets_get_only_and_source_identity(tmp_path):
    packed, _ = package(tmp_path)
    clean = tmp_path / "HTTP_CLEAN"
    clean.mkdir()
    with zipfile.ZipFile(packed) as archive:
        archive.extractall(clean)
        expected = {name: (clean / name).read_bytes() for name in
                    ("dashboard/index.html", "dashboard/style.css", "dashboard/app.js")}

    integrity = subprocess.run(
        [sys.executable, "runtime_entry.py", "--check"], cwd=clean,
        capture_output=True, text=True, timeout=15,
    )
    assert integrity.returncode == 0, integrity.stderr
    with socket.socket() as reserved:
        reserved.bind(("127.0.0.1", 0))
        port = reserved.getsockname()[1]

    server = subprocess.Popen(
        [sys.executable, "runtime_entry.py", "--run-trusted-synthetic", "--port", str(port)],
        cwd=clean, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(80):
            assert server.poll() is None, "trusted synthetic server exited before HTTP readiness"
            try:
                status, mime, body = _get(base + "/api/jobs")
                if status == 200:
                    break
            except (URLError, OSError):
                time.sleep(0.1)
        else:
            raise AssertionError("trusted synthetic HTTP server readiness timeout")

        assert "application/json" in mime
        assert len(json.loads(body)["items"]) == 2
        status, mime, body = _get(base + "/api/metrics")
        assert status == 200 and "application/json" in mime
        assert json.loads(body) == {"total": 2, "completed": 1, "pending": 1}
        status, mime, body = _get(base + "/api/jobs/X1")
        assert status == 200 and json.loads(body)["id"] == "X1"
        status, mime, body = _get(base + "/api/jobs/missing")
        assert status == 404 and "application/json" in mime
        for pathname, content_type in (
            ("dashboard/", "text/html"),
            ("dashboard/style.css", "text/css"),
            ("dashboard/app.js", "javascript"),
        ):
            status, mime, body = _get(base + "/" + pathname)
            assert status == 200 and content_type in mime, (pathname, mime)
            expected_name = "dashboard/index.html" if pathname.endswith("/") else pathname
            assert body == expected[expected_name], f"HTTP asset differs from packaged ZIP: {pathname}"
        assert b"connect-src 'self'" in expected["dashboard/index.html"]
        assert b"/dashboard/app.js" in expected["dashboard/index.html"]
        try:
            with urlopen(Request(base + "/api/jobs", data=b"{}", method="POST"), timeout=2):
                raise AssertionError("synthetic API unexpectedly accepted POST")
        except HTTPError as exc:
            assert exc.code == 405
    finally:
        server.terminate()
        try:
            server.communicate(timeout=8)
        except subprocess.TimeoutExpired:
            server.kill()
            server.communicate(timeout=8)
