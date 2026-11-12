"""P70 local synthetic web observation + Astra evidence -> approved Pro app.

Real Fable 5.1 static scan is preserved by the P50 builder. This separate
Playwright observer records actual DOM state changes on an explicit local HTML
fixture. Observations stay review-gated, NOT automatic reference-site copying.
No external URL, customer data, LLM, or deployment is supported by this module.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
from threading import Thread
import time

from rea.mvp import source_sha256
from rea.safe_publish import publish_directory
from rea.website_rebuild import WebsiteReviewError, _fixture, rebuild_local_fixture

CASES = ("search", "filter", "detail")
APPROVAL_TOKEN = "APPROVE_SYNTHETIC_ONLY"
PERMISSION_TOKEN = "YES_LOCAL_FIXTURE"
MAX_SCREENSHOT_BYTES = 350_000


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


@contextmanager
def _site_server(html: bytes):
    """One in-memory HTML page, loopback only, no filesystem directory serving."""
    class Handler(BaseHTTPRequestHandler):
        calls = 0

        def do_GET(self):
            type(self).calls += 1
            if self.path != "/":
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy",
                             "default-src 'none'; script-src 'unsafe-inline'; "
                             "style-src 'unsafe-inline'; connect-src 'none'; "
                             "img-src 'none'; frame-src 'none'; form-action 'none'")
            self.end_headers()
            self.wfile.write(html)

        def log_message(self, *_args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:" + str(server.server_port), Handler
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _restricted_context(browser, base: str):
    context = browser.new_context(
        viewport={"width": 1080, "height": 720},
        service_workers="block", accept_downloads=False,
    )
    denied = []
    def route_handler(route):
        url = route.request.url
        if url == base + "/" or url.startswith(base + "/static/") or url.startswith(base + "/api/"):
            route.continue_()
        else:
            denied.append(url.split("?", 1)[0][:120])
            route.abort()
    context.route("**/*", route_handler)
    return context, denied


def _step(page, case: str):
    """A known public synthetic control and its bounded before/after state."""
    if case not in CASES:
        raise WebsiteReviewError("Unsupported synthetic interaction case")
    page.locator("#count").wait_for()
    before = {"count": page.locator("#count").inner_text()}
    if before["count"] != "3건":
        raise WebsiteReviewError("Reference fixture has unexpected baseline")
    if case == "search":
        page.locator("#search").fill("커피")
        page.wait_for_function("document.querySelector('#count').textContent === '1건'")
        after = {"count": page.locator("#count").inner_text()}
        action = "fill synthetic search control"
        feature = "search"
    elif case == "filter":
        page.locator("#category").select_option("음료")
        page.wait_for_function("document.querySelector('#count').textContent === '2건'")
        after = {"count": page.locator("#count").inner_text()}
        action = "select synthetic category option"
        feature = "filter"
    else:
        page.locator("#first-detail").click()
        page.wait_for_function("document.querySelector('#detail').textContent.trim() === '커피'")
        after = {"count": page.locator("#count").inner_text(),
                 "detail": page.locator("#detail").inner_text().strip()}
        before["detail"] = ""
        action = "click synthetic detail button"
        feature = "detail"
    if before == after:
        raise WebsiteReviewError("No observed UI state change")
    return {"feature": feature, "action": action, "before": before, "after": after}


def _observe_html(html: bytes, case: str):
    from playwright.sync_api import sync_playwright, Error as PlaywrightError
    with _site_server(html) as (base, server):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context, denied = _restricted_context(browser, base)
                try:
                    page = context.new_page()
                    errors = []
                    page.on("pageerror", lambda e: errors.append(str(e)[:150]))
                    page.goto(base + "/", wait_until="domcontentloaded", timeout=10000)
                    before_image = page.screenshot()
                    observation = _step(page, case)
                    after_image = page.screenshot()
                    if (errors or denied or server.calls != 1 or
                            len(before_image) > MAX_SCREENSHOT_BYTES or
                            len(after_image) > MAX_SCREENSHOT_BYTES):
                        raise WebsiteReviewError("Unsafe/non-deterministic browser observation")
                    observation["screenshots_sha256"] = {
                        "before": hashlib.sha256(before_image).hexdigest(),
                        "after": hashlib.sha256(after_image).hexdigest(),
                    }
                    return observation, before_image, after_image
                finally:
                    context.close()
            finally:
                browser.close()


def _astra_observed(observation, astra_root: Path):
    if (astra_root.is_symlink() or
            not (astra_root / "astra_contracts" / "observation.py").is_file()):
        raise WebsiteReviewError("Actual pinned Astra contracts required")
    root = str(astra_root.resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    from astra_contracts.observation import ObservationBundle
    from astra_contracts.functional_spec import derive_spec

    now = datetime.now(timezone.utc).isoformat()
    bundle = ObservationBundle.model_validate({
        "schema_version": "1.0", "site_url": "http://127.0.0.1",
        "scope": "Authorized synthetic local fixture, Chromium DOM before/after",
        "recorded_at": now,
        "evidence": [
            {"id": "ev_before", "kind": "screenshot",
             "source_ref": "review/p70_before.png", "captured_at": now,
             "notes": "Actual synthetic local Chromium screenshot before action"},
            {"id": "ev_after", "kind": "screenshot",
             "source_ref": "review/p70_after.png", "captured_at": now,
             "notes": "Actual synthetic local Chromium screenshot after action"},
        ],
        "observations": [{
            "id": "ob_action", "feature": observation["feature"],
            "title": "Synthetic local UI changed after direct browser action",
            "claim": "Recorded DOM count/detail transition for the declared synthetic action",
            "certainty": "observed",
            "evidence_ids": ["ev_before", "ev_after"],
            "action": observation["action"],
            "before": observation["before"], "after": observation["after"],
        }],
    })
    spec = derive_spec(bundle).model_dump(mode="json")
    if (len(spec["candidate_features"]) != 1
            or spec["candidate_features"][0]["review_status"] != "requires_review"
            or spec["implementation_ready"]
            or any(g["status"] != "pending" for g in spec["approval_gates"])):
        raise WebsiteReviewError("Astra behavior promotion violated human approval gate")
    return bundle.model_dump(mode="json"), spec


def inspect_local(fixture_html: Path, *, fixture_sha256: str, case: str,
                  astra_root: Path) -> dict:
    """Generate a review receipt before owner decides whether to build."""
    if case not in CASES:
        raise WebsiteReviewError("Unknown interaction")
    html, digest, _ = _fixture(Path(fixture_html), fixture_sha256)
    ob, before, after = _observe_html(html, case)
    bundle, spec = _astra_observed(ob, Path(astra_root))
    # Exclude timestamps, browser port and actual screenshot bytes from the
    # approval digest; retain screenshot hashes in the review evidence instead.
    approved_subject = {"fixture_sha256": digest, "case": case,
                        "feature": ob["feature"], "action": ob["action"],
                        "before": ob["before"], "after": ob["after"]}
    receipt = {
        "schema_version": "rea.website.p70.v1",
        "site_kind": "synthetic_local_fixture_only",
        "subject": approved_subject,
        "review_digest": _digest(approved_subject),
        "observation": ob, "astra_observation_bundle": bundle,
        "astra_functional_spec": spec,
        "status": "REVIEW_REQUIRED",
        "implementation_ready": False,
        "external_site_scanned": False,
        "commercial_release": "HOLD",
    }
    return receipt, before, after


def _port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _validate_generated_browser(app: Path, case: str, expected: dict) -> dict:
    """Run the freshly generated independent FastAPI app in actual Chromium."""
    from playwright.sync_api import sync_playwright
    port = _port()
    base = "http://127.0.0.1:" + str(port)
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1",
         "--port", str(port), "--log-level", "error"],
        cwd=str(app), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    try:
        from urllib.request import urlopen
        from urllib.error import URLError
        for _ in range(75):
            if proc.poll() is not None:
                raise WebsiteReviewError("Generated server exited before /health")
            try:
                with urlopen(base + "/health", timeout=1) as response:
                    if response.status == 200:
                        break
            except (URLError, OSError):
                time.sleep(0.1)
        else:
            raise WebsiteReviewError("Generated server not ready")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context, denied = _restricted_context(browser, base)
                try:
                    page = context.new_page()
                    errors = []
                    page.on("pageerror", lambda e: errors.append(str(e)[:150]))
                    page.goto(base + "/", wait_until="domcontentloaded", timeout=10000)
                    page.wait_for_function("document.querySelector('#count').textContent === '3건'")
                    before = {"count": page.locator("#count").inner_text()}
                    if case == "search":
                        page.locator("#search").fill("커피")
                        page.wait_for_function("document.querySelector('#count').textContent === '1건'")
                        after = {"count": page.locator("#count").inner_text()}
                    elif case == "filter":
                        page.locator("#category").select_option("음료")
                        page.wait_for_function("document.querySelector('#count').textContent === '2건'")
                        after = {"count": page.locator("#count").inner_text()}
                    elif case == "detail":
                        page.locator(".item").filter(has_text="커피").click()
                        page.wait_for_function("document.querySelector('#detail h3') && document.querySelector('#detail h3').textContent === '커피'")
                        before["detail"] = ""
                        after = {"count": page.locator("#count").inner_text(),
                                 "detail": page.locator("#detail h3").inner_text()}
                    else:
                        raise WebsiteReviewError("Invalid case")
                    if (errors or denied or before != expected["before"]
                            or after != expected["after"]):
                        raise WebsiteReviewError("Browser parity mismatch or external request")
                    return {"status": "MATCHED_OBSERVED_SYNTHETIC_BEHAVIOR",
                            "case": case, "before": before, "after": after}
                finally:
                    context.close()
            finally:
                browser.close()
    finally:
        proc.terminate()
        try:
            proc.communicate(timeout=6)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate(timeout=6)


def build_reviewed(fixture_html: Path, owner_csv: Path, out: Path, *,
                   fixture_sha256: str, owner_sha256: str,
                   case: str, approved_review_digest: str,
                   id_field: str, title_field: str, category_field: str,
                   fixture_permission: str, owner_approval: str,
                   fable_root: Path, astra_root: Path) -> dict:
    """New target only, signed-source-like SHA + human-selected receipt digest.

    The user's explicit approval is solely for this synthetic demo case and
    customer-owned CSV mapping; no site feature is automatically approved
    for commercial reproduction or website-content copying.
    """
    if fixture_permission != PERMISSION_TOKEN or owner_approval != APPROVAL_TOKEN:
        raise WebsiteReviewError("Explicit synthetic owner permission and review approval required")
    if (len(approved_review_digest) != 64 or
            any(c not in "0123456789abcdef" for c in approved_review_digest)):
        raise WebsiteReviewError("A precise review digest is required")
    out = Path(out).absolute()
    if out.exists() or out.is_symlink():
        raise FileExistsError("Target exists")
    if not out.parent.is_dir() or out.parent.is_symlink():
        raise WebsiteReviewError("Output parent directory not safe")
    if source_sha256(owner_csv) != owner_sha256:
        raise WebsiteReviewError("Owner CSV changed")
    review, before, after = inspect_local(
        fixture_html, fixture_sha256=fixture_sha256, case=case,
        astra_root=astra_root)
    if review["review_digest"] != approved_review_digest:
        raise WebsiteReviewError("Owner review digest is stale or mismatched")
    with tempfile.TemporaryDirectory(prefix=".rea-p70-", dir=out.parent) as temp:
        stage = Path(temp) / "app"
        result = rebuild_local_fixture(
            fixture_html, owner_csv, stage,
            fixture_sha256=fixture_sha256, owner_sha256=owner_sha256,
            id_field=id_field, title_field=title_field, category_field=category_field,
            fixture_permission=PERMISSION_TOKEN, owner_approval="APPROVE",
            fable_root=fable_root, astra_root=astra_root,
        )
        comparison = _validate_generated_browser(stage, case, review["observation"])
        if source_sha256(owner_csv) != owner_sha256:
            raise WebsiteReviewError("Owner CSV modified before delivery")
        if _fixture(fixture_html, fixture_sha256)[1] != fixture_sha256:
            raise WebsiteReviewError("Fixture modified before delivery")
        internal = stage / "review"
        (internal / "p70_before.png").write_bytes(before)
        (internal / "p70_after.png").write_bytes(after)
        review["generated_app_browser"] = comparison
        review["owner_mapping_approval"] = "APPROVE_SYNTHETIC_ONLY"
        (internal / "p70_browser_evidence.json").write_text(
            json.dumps(review, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        manifest_file = stage / "manifest.json"
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        manifest["website_p70"] = {
            "status": "SYNTHETIC_BROWSER_PARITY_REVIEW_HOLD",
            "case": case, "approval_digest": approved_review_digest,
            "reference_behavior_auto_approved": False,
            "browser_check": "MATCHED_OBSERVED_SYNTHETIC_BEHAVIOR",
        }
        manifest_file.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        publish_directory(stage, out)
    return {"status": "P70_SYNTHETIC_BROWSER_HOLD", "case": case,
            "owner_rows": result["rows"], "browser_parity": comparison["status"],
            "reference_human_review_required": True,
            "commercial_release": "HOLD"}


def main(argv=None):
    parser = __import__("argparse").ArgumentParser(description="Local synthetic browser site observation and independent app")
    parser.add_argument("action", choices=["inspect", "build"])
    parser.add_argument("--fixture-html", type=Path, required=True)
    parser.add_argument("--fixture-sha256", required=True)
    parser.add_argument("--case", required=True, choices=CASES)
    parser.add_argument("--astra-root", type=Path, required=True)
    parser.add_argument("--owner-csv", type=Path)
    parser.add_argument("--owner-sha256")
    parser.add_argument("--approved-review-digest")
    parser.add_argument("--id-field", default="id")
    parser.add_argument("--title-field", default="title")
    parser.add_argument("--category-field", default="category")
    parser.add_argument("--fixture-permission")
    parser.add_argument("--owner-approval")
    parser.add_argument("--fable-root", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.action == "inspect":
            receipt, _, _ = inspect_local(args.fixture_html, fixture_sha256=args.fixture_sha256,
                                          case=args.case, astra_root=args.astra_root)
            print(json.dumps({"status": receipt["status"],
                              "review_digest": receipt["review_digest"],
                              "subject": receipt["subject"]}, ensure_ascii=False))
        else:
            if not args.owner_csv or not args.owner_sha256 or not args.fable_root or not args.out:
                parser.error("build requires CSV, source SHA, fable checkout and output")
            print(json.dumps(build_reviewed(
                args.fixture_html, args.owner_csv, args.out,
                fixture_sha256=args.fixture_sha256, owner_sha256=args.owner_sha256,
                case=args.case, approved_review_digest=args.approved_review_digest or "",
                id_field=args.id_field, title_field=args.title_field, category_field=args.category_field,
                fixture_permission=args.fixture_permission or "",
                owner_approval=args.owner_approval or "",
                fable_root=args.fable_root, astra_root=args.astra_root),
                ensure_ascii=False))
    except (ValueError, OSError, RuntimeError) as exc:
        parser.exit(2, "P70_REVIEW_HOLD: " + type(exc).__name__ + ": " + str(exc) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
