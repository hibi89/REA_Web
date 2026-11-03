"""Actual native Windows CMD launcher smoke, unpacked synthetic ZIP -> HTTP."""
from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rea.delivery import create_delivery  # noqa: E402


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    if os.name != "nt":
        raise SystemExit("NOT_RUN: native Windows host required")
    with tempfile.TemporaryDirectory(prefix="rea-win-qa-") as location:
        root = Path(location)
        package = root / "sample.zip"
        create_delivery(ROOT / "samples/qa_cafe.csv", package)
        extracted = root / "extracted"
        extracted.mkdir()
        with zipfile.ZipFile(package) as zf:
            zf.extractall(extracted)
        script = extracted / "launch_windows.cmd"
        assert script.exists()
        port = free_port()
        env = dict(os.environ, REA_WEB_PORT=str(port))
        # This is a real cmd.exe invocation, not emulation.
        runner = subprocess.Popen(["cmd.exe", "/d", "/c", str(script)],
                                  cwd=extracted, env=env,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            base = f"http://127.0.0.1:{port}"
            for _ in range(120):
                if runner.poll() is not None:
                    raise RuntimeError(f"Windows launcher stopped early: {runner.returncode}")
                try:
                    with urlopen(base + "/health", timeout=1) as r:
                        if r.status == 200:
                            break
                except (URLError, OSError):
                    time.sleep(0.15)
            else:
                raise TimeoutError("Windows launcher did not start")
            with urlopen(base + "/api/items", timeout=3) as r:
                assert json.load(r)["total"] == 4
            print("PASS native Windows: ZIP extraction -> .cmd launcher -> localhost API 4 rows")
        finally:
            if runner.poll() is None:
                subprocess.run(["taskkill", "/PID", str(runner.pid), "/T", "/F"],
                               capture_output=True, check=False)
            try:
                runner.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                runner.kill()
                runner.communicate(timeout=5)


if __name__ == "__main__":
    main()
