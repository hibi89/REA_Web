"""Real Chromium checks against the EXTRACTED THREE delivery ZIPs, not source mocks.

Network is loopback 127.0.0.1 only; input fixtures are synthetic. Does not
provide signed customer/human acceptance or approve the broader G0-G6 gates.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen
import zipfile

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rea.provenance import inspect_delivery  # noqa: E402
from scripts.d11_rehearsal import CASES  # noqa: E402


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def run_case(spec: dict, archive: Path, working: Path, report: Path, pw) -> dict:
    audit = inspect_delivery(archive)
    if audit["overall_commercial_clearance"] != "NOT_GRANTED":
        raise ValueError("Unexpected commercial clearance")
    extracted = working / spec["case_id"]
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(extracted)
    app = extracted / "app"
    port = free_port()
    base = f"http://127.0.0.1:{port}"
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app",
         "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
        cwd=app, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    try:
        for _ in range(75):
            if proc.poll() is not None:
                raise RuntimeError("Extracted delivery HTTP server quit unexpectedly")
            try:
                with urlopen(base + "/health", timeout=1) as result:
                    if result.status == 200:
                        break
            except (URLError, OSError):
                time.sleep(0.15)
        else:
            raise TimeoutError("Extracted delivery server did not start")
        errors, external, dialogs = [], [], []
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context()
        try:
            page = context.new_page()
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))
            page.on("request", lambda request: external.append(request.url)
                    if not request.url.startswith(base + "/") else None)
            page.goto(base, wait_until="networkidle")
            verified = []
            features = spec["selected_features"]
            if "list" in features:
                expect(page.locator(".item")).to_have_count(spec["expected_rows"])
                expect(page.locator("#count")).to_have_text(f'{spec["expected_rows"]}건')
                verified.append("list")
            if "simple_summary" in features:
                expect(page.locator("#overview-total")).to_have_text(
                    f'{spec["expected_rows"]}건')
                assert page.request.get(base + "/api/summary").status == 200
                verified.append("simple_summary")
            if "category_filter" in features:
                page.locator("#category").select_option(label=spec["filter_category"])
                expect(page.locator("#count")).to_have_text(f'{spec["filter_count"]}건')
                verified.append("category_filter")
            if "search" in features:
                page.locator("#category").select_option("")
                page.locator("#search").fill(spec["search"])
                expect(page.locator("#count")).to_have_text("1건")
                verified.append("search")
            if "detail" in features:
                page.locator("#search").fill(spec["search"])
                page.locator("#category").select_option("")
                expect(page.locator(".item")).to_have_count(1)
                page.locator(".item").click()
                expect(page.locator("#detail h3")).to_have_text(spec["detail_title"])
                assert page.locator("#detail script").count() == 0
                verified.append("detail")
            assert set(verified) == set(features)
            page.screenshot(path=str(report / (spec["case_id"] + ".png")), full_page=True)
            page.reload(wait_until="networkidle")
            expect(page.locator("#count")).to_have_text(f'{spec["expected_rows"]}건')
            assert page.request.get(base + "/review/fable_review.json").status == 404
            assert page.request.get(base + "/manifest.json").status == 404
            assert page.request.get(base + "/append_report.json").status == 404
            assert page.request.get(base + "/mapping_report.json").status == 404
            assert not errors, f"JS errors: {errors}"
            assert not external, f"Nonlocal network calls: {external}"
            assert not dialogs, f"JS dialogs: {dialogs}"
        finally:
            context.close()
            browser.close()
        return {
            "case_id": spec["case_id"], "status": "PASS_SYNTHETIC_EXTRACTED_ZIP_BROWSER",
            "browser": "Chromium", "contracted_features_verified": verified,
            "reload_verified": True, "unexpected_external_requests": 0,
            "javascript_errors": 0, "dialogs": 0,
            "real_customer_acceptance": "NOT_RUN",
        }
    finally:
        proc.terminate()
        try:
            proc.communicate(timeout=6)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate(timeout=6)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--rehearsal", type=Path, required=True)
    p.add_argument("--report-dir", type=Path, required=True)
    args = p.parse_args(argv)
    source, out = args.rehearsal.absolute(), args.report_dir.absolute()
    if out.exists() or out.is_symlink():
        raise FileExistsError("Browser report destination exists")
    score = json.loads((source / "acceptance_scorecard.json").read_text(encoding="utf-8"))
    if score.get("classification") != "SYNTHETIC_THREE_CASE_REHEARSAL_ONLY":
        raise ValueError("Only approved synthetic rehearsal fixtures")
    out.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="rea-d11-browser-") as folder:
        with sync_playwright() as pw:
            results = [
                run_case(spec, source / (spec["case_id"] + ".zip"), Path(folder), out, pw)
                for spec in CASES
            ]
    if len(results) != 3 or {item["case_id"] for item in results} != {
            item["case_id"] for item in score["three_cases"]}:
        raise ValueError("Missing browser rehearsal case")
    per_case = {item["case_id"]: item for item in results}
    for item in score["three_cases"]:
        evidence = per_case[item["case_id"]]
        if set(evidence["contracted_features_verified"]) != set(item["selected_features"]):
            raise ValueError("Quote-to-browser feature parity failure")
        item["browser_acceptance"] = evidence["status"]
        item["gates"]["G4"] = {
            "status": "PASS_SYNTHETIC_SUBCHECK",
            "evidence": "Real Chromium against extracted customer ZIP for this quoted scope",
        }
        assert item["gates"]["G5"]["status"] == "BLOCKED"
        assert item["gates"]["G6"]["status"] == "BLOCKED"
        assert item["manual_labor_minutes"] is None
    score["browser_in_delivery_archive_proof"] = "PASS_THREE_SYNTHETIC_ZIP_BROWSER_CASES"
    assert score["overall_g0_g6_release"] == "BLOCKED"
    (out / "browser_acceptance.json").write_text(
        json.dumps({"schema_version": "rea.rehearsal.browser.v0.1",
                    "three_case_count": 3, "results": results,
                    "real_customer_acceptance": "NOT_RUN"}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out / "combined_acceptance_scorecard.json").write_text(
        json.dumps(score, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print("PASS D11: 3 real Chromium tests of extracted synthetic delivery ZIPs; G5/G6 blocked")


if __name__ == "__main__":
    raise SystemExit(main())
