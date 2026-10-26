"""D18 developer-CI-only: run a REAL Tk-generated synthetic delivery in the SAME fresh venv.

No customer files, public bind, automatic install, hosting, or retained ZIPs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import ProxyHandler, build_opener
import zipfile

from rea.delivery import verify_delivery
from rea.provenance import inspect_delivery

ROOT = Path(__file__).resolve().parents[1]
STATUS = "FRESH_VENV_TK_ZIP_LOCALHOST_HTTP_PASS"
EXPECTED_IDS = {"S01", "S02", "S03", "S04", "S05"}


def check_synthetic_archive(archive: Path, ui_report: Path) -> dict:
    """Reject a non-D18 fixture, stale UI receipt or an unsafe archive."""
    archive, ui_report = Path(archive), Path(ui_report)
    if not archive.is_file() or archive.is_symlink():
        raise ValueError("Only a real synthetic archive can be executed")
    proof = json.loads(ui_report.read_text(encoding="utf-8"))
    if (proof.get("status") != "ACTUAL_TK_TWO_FILE_WIDGETS_PASS"
            or proof.get("both_origins_sha_unchanged") is not True
            or proof.get("commercial_clearance") != "NOT_GRANTED"
            or proof.get("validated_zip_sha256") != hashlib.sha256(archive.read_bytes()).hexdigest()):
        raise ValueError("Real Tk GUI synthetic ZIP evidence mismatch")
    verify_delivery(archive)
    audit = inspect_delivery(archive)
    if (audit["two_file_append_receipt_present"] is not True
            or audit["overall_commercial_clearance"] != "NOT_GRANTED"):
        raise ValueError("Approved synthetic APPEND receipt missing")
    with zipfile.ZipFile(archive) as zf:
        manifest = json.loads(zf.read("app/manifest.json"))
        receipt = json.loads(zf.read("app/append_report.json"))
        if (manifest.get("rows") != 5 or manifest.get("source_count") != 2
                or receipt.get("mode") != "SAME_SCHEMA_ROW_APPEND_NO_JOIN"
                or receipt.get("combined_confirmation") != "APPEND"
                or [x.get("row_count") for x in receipt["sources"]] != [3, 2]
                or [x.get("confirmed") for x in receipt["sources"]] != ["APPROVE", "APPROVE"]):
            raise ValueError("Unexpected append dataset or approval scope")
        for i, name in enumerate(("qa_guided.csv", "qa_pair_extra.json")):
            expected = hashlib.sha256((ROOT / "samples" / name).read_bytes()).hexdigest()
            if receipt["sources"][i].get("sha256") != expected:
                raise ValueError("This archive is not generated from committed synthetic fixtures")
        # verify_delivery already bounds/validates member names and bytes.
        for member in zf.infolist():
            if stat.S_ISLNK(member.external_attr >> 16):
                raise ValueError("Symlink ZIP entries are forbidden")
    return {"zip_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            "sources": 2, "rows": 5}


def loopback_port() -> int:
    """Choose an ephemeral loopback port; reservation ends before launch."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def http_json(opener, base: str, endpoint: str) -> dict:
    with opener.open(base + endpoint, timeout=2) as response:
        if response.status != 200:
            raise ValueError("Unexpected HTTP status")
        return json.load(response)


def assert_http_contract(opener, base: str) -> None:
    health = http_json(opener, base, "/health")
    if health != {"status": "ok", "mode": "local_readonly"}:
        raise AssertionError("Local health mismatch")
    listed = http_json(opener, base, "/api/items?limit=100")
    if (listed["total"] != 5 or len(listed["items"]) != 5
            or {x["id"] for x in listed["items"]} != EXPECTED_IDS):
        raise AssertionError("APPEND total/IDs mismatch")
    search = http_json(opener, base, "/api/items?" + urlencode({"q": "콜드브루"}))
    if (search["total"] != 1 or len(search["items"]) != 1
            or search["items"][0]["id"] != "S05"):
        raise AssertionError("Unicode query did not find appended JSON row")
    filtered = http_json(opener, base, "/api/items?" + urlencode({"category": "음료"}))
    if filtered["total"] != 3 or {x["id"] for x in filtered["items"]} != {"S01", "S02", "S05"}:
        raise AssertionError("Category filter differs from two-source fixture")
    item = http_json(opener, base, "/api/items/S04")
    if item["id"] != "S04" or item["title"] != "초코케이크":
        raise AssertionError("Detail should return appended JSON item")
    summary = http_json(opener, base, "/api/summary")
    if summary["total_items"] != 5:
        raise AssertionError("Synthetic summary row count mismatch")
    schema = http_json(opener, base, "/api/schema")
    if schema.get("review_status") != "UNAPPROVED":
        raise AssertionError("Non-approved semantic fields falsely approved")
    try:
        http_json(opener, base, "/api/items/ABSENT_D18")
    except HTTPError as error:
        if error.code != 404:
            raise AssertionError("Unexpected missing-detail status") from error
    else:
        raise AssertionError("Missing-detail lookup should return HTTP 404")


def stop_server(server: subprocess.Popen) -> None:
    """Do not let a local test server outlive the developer CI test."""
    if server.poll() is None:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(server.pid), "/T", "/F"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=8, check=False)
        else:
            server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait(timeout=5)
    if server.poll() is None:
        raise RuntimeError("Loopback server cleanup was not confirmed")


def serve_archive(archive: Path, ui_report: Path) -> dict:
    check_synthetic_archive(archive, ui_report)
    # Scratch has no user files, and the ZIP is fully allowlisted and verified.
    with tempfile.TemporaryDirectory(prefix="rea-d18-http-") as tmp:
        target = Path(tmp) / "unzipped"
        target.mkdir()
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(target)
        generated = target / "app"
        if not (generated / "app.py").is_file():
            raise RuntimeError("Extracted generated app not found")
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        env["PYTHONIOENCODING"] = "utf-8"
        port = loopback_port()
        # Only the invoking isolated .venv interpreter may host this process.
        command = [sys.executable, "-m", "uvicorn", "app:app",
                   "--host", "127.0.0.1", "--port", str(port), "--no-access-log"]
        server = subprocess.Popen(
            command, cwd=generated, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            opener = build_opener(ProxyHandler({}))  # never use a proxy for local smoke
            base = "http://127.0.0.1:" + str(port)
            for _ in range(100):
                if server.poll() is not None:
                    raise RuntimeError("Generated server exited before HTTP readiness")
                try:
                    response = http_json(opener, base, "/health")
                    if response == {"status": "ok", "mode": "local_readonly"}:
                        break
                except (OSError, ValueError, URLError):
                    time.sleep(0.1)
            else:
                raise TimeoutError("No 127.0.0.1 HTTP readiness before deadline")
            assert_http_contract(opener, base)
        finally:
            stop_server(server)
    return {
        "status": STATUS,
        "source": "ACTUAL_TWO_FILE_TK_SYNTHETIC_ZIP",
        "venv_interpreter": "INVOKING_PYTHON_ONLY",
        "binding": "127.0.0.1",
        "health": "HTTP_200",
        "rows": 5,
        "query": "PASS",
        "category_filter": "PASS",
        "detail": "PASS",
        "missing_detail_404": "PASS",
        "schema_not_autoapproved": True,
        "server_cleanup": "CONFIRMED",
        "temporary_extraction": "REMOVED",
        "commercial_clearance": "NOT_GRANTED",
        "human_non_developer_acceptance": "NOT_RUN",
        "customer_data": "NOT_USED",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="D18 synthetic-only fresh venv localhost proof")
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--ui-report", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out.exists() or args.out.is_symlink():
        print("D18_HTTP_NOT_VERIFIED: ExistingOutput", file=sys.stderr)
        return 2
    try:
        result = serve_archive(args.archive, args.ui_report)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8") as file:
            json.dump(result, file, ensure_ascii=False, sort_keys=True, indent=2)
            file.write("\n")
    except Exception as exc:
        print("D18_HTTP_NOT_VERIFIED: " + type(exc).__name__, file=sys.stderr)
        return 2
    print(json.dumps({"status": STATUS, "rows": 5, "http": "PASS",
                      "cleanup": "CONFIRMED", "human": "NOT_RUN"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
