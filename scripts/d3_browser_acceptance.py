"""D3 real loopback Chromium acceptance for three independent synthetic apps."""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rea.orchestrator import build  # noqa: E402
from rea.guided import preflight  # noqa: E402
from rea.two_source import preflight_pair, build_pair  # noqa: E402

CASES = [
    {"name": "cafe", "csv": "qa_cafe.csv", "total": 4, "category": "음료",
     "category_total": 2, "search": "카페라떼", "title": "카페라떼", "detail": "4000", "fable": True, "fields": 5},
    {"name": "inventory", "csv": "qa_inventory.csv", "total": 5, "category": "저장장치",
     "category_total": 2, "search": "NAS", "title": "NAS HDD", "detail": "<script>alert(1)</script>", "fable": False, "fields": 6},
    {"name": "json_products", "csv": "qa_products.json", "total": 4, "category": "음료",
     "category_total": 2, "search": "블렌드", "title": "블렌드 커피", "detail": "4900",
     "fable": False, "fields": 5},
    {"name": "formulas", "csv": "qa_formula.csv", "total": 4, "category": "공식",
     "category_total": 2, "search": "=1+1", "title": "=1+1", "detail": "=CMD",
     "fable": False, "fields": 4},
    {"name": "owner_csv", "csv": "qa_guided.csv", "total": 3, "category": "음료",
     "category_total": 2, "search": "카페라떼", "title": "카페라떼", "detail": "4000",
     "fable": False, "fields": 4, "category_count": 2,
     "mapping": {"id": "sku", "title": "display_name", "category": "group_name"}},
    {"name": "owner_json", "csv": "qa_guided.json", "total": 3, "category": "JP",
     "category_total": 2, "search": "실버", "title": "실버", "detail": "95",
     "fable": False, "fields": 4, "category_count": 2,
     "mapping": {"id": "item_code", "title": "label", "category": "region"}},
    {"name": "approved_two", "csv": "qa_guided.csv", "second": "qa_pair_extra.json",
     "total": 5, "category": "디저트", "category_total": 1,
     "search": "초코케이크", "title": "초코케이크", "detail": "6900",
     "fable": False, "fields": 4, "category_count": 3,
     "mapping": {"id": "sku", "title": "display_name", "category": "group_name"}},
    {"name": "trends", "csv": "qa_trends.csv", "total": 5, "category": "JP",
     "category_total": 2, "search": "실버", "title": "JP 실버", "detail": "90", "fable": False, "fields": 6},
]


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def run_one(case: dict, work: Path, pw, report_dir: Path) -> dict:
    out = work / case["name"]
    if case.get("second"):
        a, second = ROOT / "samples" / case["csv"], ROOT / "samples" / case["second"]
        preview = preflight_pair(a, second)
        manifest = build_pair(
            a, second, out, "REA synthetic same-schema append",
            case["mapping"], preview["sources"][0]["sha256"],
            preview["sources"][1]["sha256"], "APPROVE", "APPROVE", "APPEND")
        assert manifest["source_count"] == 2
    else:
        manifest = build(
            ROOT / "samples" / case["csv"], out,
            fable_result=(ROOT / "samples/fable_record_redacted.json") if case["fable"] else None,
            approved_mapping=case.get("mapping"),
            expected_source_sha256=(preflight(ROOT / "samples" / case["csv"])["source_sha256"]
                                    if case.get("mapping") else None),
        )
    assert manifest["rows"] == case["total"]
    assert manifest["fable_review"]["status"] == ("REVIEW_REQUIRED" if case["fable"] else "NOT_REQUESTED")
    port = free_port()
    base = f"http://127.0.0.1:{port}"
    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "app:app",
                               "--host", "127.0.0.1", "--port", str(port),
                               "--log-level", "warning"],
                              cwd=out, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for _ in range(80):
            if server.poll() is not None:
                raise RuntimeError(server.stderr.read().decode(errors="replace"))
            try:
                with urlopen(base + "/health", timeout=1) as response:
                    if response.status == 200:
                        break
            except (URLError, OSError):
                time.sleep(0.15)
        else:
            raise TimeoutError("Generated app did not become healthy")
        errors, external, dialogs = [], [], []
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context()
        try:
            page = context.new_page()
            page.set_default_timeout(15_000)
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))
            page.on("request", lambda request: external.append(request.url)
                    if not request.url.startswith(base + "/") else None)
            # Wait for the document, then let assertions wait for API data.
            # networkidle is brittle when the local app has in-flight fetches.
            page.goto(base, wait_until="domcontentloaded")
            expect(page.locator("#count")).to_have_text(f'{case["total"]}건')
            expect(page.locator(".item")).to_have_count(case["total"])
            expect(page.locator("#overview-total")).to_have_text(f'{case["total"]}건')
            expect(page.locator("#category-stats li")).to_have_count(case.get("category_count", 3))
            page.locator("#schema-panel summary").click()
            expect(page.locator("#schema-fields li")).to_have_count(case["fields"])
            expect(page.locator("#schema-status")).to_have_text("검토 전")
            page.locator("#category").select_option(label=case["category"])
            expect(page.locator("#count")).to_have_text(f'{case["category_total"]}건')
            page.locator("#search").fill(case["search"])
            expect(page.locator("#count")).to_have_text("1건")
            expect(page.locator(".item")).to_have_count(1)
            page.locator(".item").click()
            expect(page.locator("#detail h3")).to_have_text(case["title"])
            expect(page.locator("#detail")).to_contain_text(case["detail"])
            if case["name"] in {"inventory", "formulas"}:
                assert page.locator("#detail script").count() == 0
            page.screenshot(path=str(report_dir / f"{case['name']}.png"), full_page=True)
            page.reload(wait_until="domcontentloaded")
            expect(page.locator("#count")).to_have_text(f'{case["total"]}건')
            assert page.request.get(base + "/review/fable_review.json").status == 404
            assert page.request.get(base + "/manifest.json").status == 404
            assert page.request.get(base + "/schema_preview.json").status == 404
            assert page.request.get(base + "/mapping_report.json").status == 404
            assert page.request.get(base + "/append_report.json").status == 404
            assert not errors, f"JS errors: {errors}"
            assert not external, f"Unexpected requests: {external}"
            assert not dialogs, f"Unexpected dialogs: {dialogs}"
        finally:
            context.close()
            browser.close()
        return {"case": case["name"], "rows": case["total"],
                "category_results": case["category_total"], "search_results": 1,
                "detail_verified": True, "reload_verified": True,
                "schema_preview_verified": True, "category_summary_verified": True,
                "explicit_mapping_verified": bool(case.get("mapping")),
                "two_file_explicit_append_verified": bool(case.get("second")),
                "unexpected_network_calls": len(external), "js_errors": len(errors),
                "dialogs": len(dialogs), "fable_review": manifest["fable_review"]["status"],
                "browser": "Chromium", "status": "PASS"}
    finally:
        server.terminate()
        try:
            server.communicate(timeout=6)
        except subprocess.TimeoutExpired:
            server.kill()
            server.communicate(timeout=6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument(
        "--skip-fable-review", action="store_true",
        help="Run local CSV/JSON/browser cases when pinned Astra contracts are unavailable",
    )
    args = parser.parse_args()
    report = args.report_dir.absolute()
    report.mkdir(parents=True, exist_ok=False)
    skipped = ([{"case": case["name"], "status": "BLOCKED_MISSING_LOCAL_ASTRA_CONTRACTS"}
                for case in CASES if case["fable"]]
               if args.skip_fable_review else [])
    cases_to_run = ([case for case in CASES if not case["fable"]]
                    if args.skip_fable_review else CASES)
    with tempfile.TemporaryDirectory(prefix="rea-d3-browser-") as folder:
        with sync_playwright() as pw:
            cases = [run_one(case, Path(folder), pw, report) for case in cases_to_run]
    summary = {"schema_version": "rea.qa.v0.1",
               "environment": f"{platform.system()} {platform.release()} / Python {platform.python_version()}",
               "fixture_kind": "synthetic_only",
               "windows_native": "NOT_TESTED_BY_THIS_SCRIPT",
               "case_count": len(cases), "cases": cases,
               "skipped_cases": skipped,
               "status": "PASS" if not skipped else "PARTIAL"}
    (report / "qa_report.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{summary['status']} D9 real Chromium: {len(cases)} synthetic apps; safe search/filter/detail/reload")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
