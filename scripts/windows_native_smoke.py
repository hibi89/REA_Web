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
    with tempfile.TemporaryDirectory(prefix="rea-win-qa-", ignore_cleanup_errors=True) as location:
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
        log_path = root / "launcher.log"
        launcher_log = log_path.open("w", encoding="utf-8", errors="replace")
        # This is a real cmd.exe invocation, not emulation.
        runner = subprocess.Popen(
            ["cmd.exe", "/d", "/c", str(script)], cwd=extracted, env=env,
            stdout=launcher_log, stderr=subprocess.STDOUT,
        )
        failure = None
        last_health_error = "no health request attempted"
        rows = None
        try:
            base = f"http://127.0.0.1:{port}"
            ready = False
            for _ in range(120):
                if runner.poll() is not None:
                    failure = RuntimeError(
                        f"Windows launcher stopped early: {runner.returncode}"
                    )
                    break
                try:
                    with urlopen(base + "/health", timeout=1) as r:
                        if r.status == 200:
                            ready = True
                            break
                        last_health_error = f"unexpected HTTP status {r.status}"
                except (URLError, OSError) as exc:
                    last_health_error = f"{type(exc).__name__}: {exc}"
                    time.sleep(0.15)
            if failure is None and not ready:
                failure = TimeoutError("Windows launcher did not start")
            if failure is None:
                with urlopen(base + "/api/items", timeout=3) as r:
                    rows = json.load(r).get("total")
                if rows != 4:
                    failure = AssertionError(
                        f"Expected 4 synthetic rows from /api/items; received {rows!r}"
                    )
        except Exception as exc:
            failure = exc
        finally:
            if runner.poll() is None:
                stopped = subprocess.run(
                    ["taskkill", "/PID", str(runner.pid), "/T", "/F"],
                    capture_output=True, text=True, errors="replace", check=False,
                )
            else:
                stopped = None
            try:
                runner.wait(timeout=5)
            except subprocess.TimeoutExpired as exc:
                runner.kill()
                runner.wait(timeout=5)
                if failure is None:
                    failure = RuntimeError(f"Windows launcher process did not stop: {exc}")
            launcher_log.close()
        output = log_path.read_text(encoding="utf-8", errors="replace").strip()
        if failure is not None:
            launcher_output = output or "<launcher produced no captured output>"
            if len(launcher_output) > 12000:
                launcher_output = launcher_output[-12000:]
            kill_output = (
                ""
                if stopped is None
                else f"\nProcess-tree stop command exited {stopped.returncode}: "
                     f"{(stopped.stdout or stopped.stderr or '').strip()}"
            )
            raise RuntimeError(
                f"Native Windows smoke failed: {type(failure).__name__}: {failure}\n"
                f"Last /health result: {last_health_error}\n"
                f"Launcher output:\n{launcher_output}{kill_output}\n"
                f"Diagnostic workspace: {root}"
            ) from failure
        print("PASS native Windows: ZIP extraction -> .cmd launcher -> localhost API 4 rows")


if __name__ == "__main__":
    main()

