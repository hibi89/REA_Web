"""REA_Web P85: multi-step, responsive, evidence-linked synthetic website audit.

Actual Playwright Chromium visits ONLY owner-authorized, SHA-pinned in-memory
loopback HTML; actual frozen Astra P4 validates observations; existing P50
invokes real frozen Fable 5.1 static scan + existing Pro app generator.
No external website, Fable --record, UI-source clone, or real customer consent.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen

from rea.mvp import source_sha256
from rea.safe_publish import publish_directory
from rea.website_rebuild import WebsiteReviewError, _fixture, rebuild_local_fixture
from rea.website_p70 import (_site_server, _port, _digest, APPROVAL_TOKEN,
                             PERMISSION_TOKEN)

VIEWPORTS = {"desktop": {"width": 1280, "height": 720},
             "mobile": {"width": 390, "height": 844}}
MAX_CAPTURE = 400_000
STEPS = ("search", "filter", "detail")
NETWORK_MARKERS = (b"https://", b"http://", b"//example.", b"//localhost")


def _validate_scope(html: bytes):
    lower = html.lower()
    if any(marker in lower for marker in NETWORK_MARKERS):
        raise WebsiteReviewError("Synthetic fixture may not contain external URL markers")
    if b"<iframe" in lower or b"<object" in lower or b"<embed" in lower:
        raise WebsiteReviewError("Embedded third-party documents forbidden in synthetic fixture")


def _browser_context(browser, base: str, viewport: dict):
    context = browser.new_context(viewport=viewport, accept_downloads=False,
                                  service_workers="block", is_mobile=viewport["width"] < 500,
                                  has_touch=viewport["width"] < 500)
    blocked = []
    def guard(route):
        from urllib.parse import urlsplit
        target = route.request.url
        parsed = urlsplit(target)
        allowed = target == base + "/" or (
            parsed.scheme == "http" and parsed.netloc == base[7:] and
            (parsed.path.startswith("/api/") or parsed.path.startswith("/static/"))
        )
        if allowed:
            route.continue_()
        else:
            blocked.append("blocked_non_loopback_or_unapproved_path")
            route.abort()
    context.route("**/*", guard)
    return context, blocked


def _live_state(page, generated=False):
    count = page.locator("#count").inner_text()
    if generated:
        detail = page.locator("#detail h3")
        name = detail.inner_text() if detail.count() else ""
    else:
        name = page.locator("#detail").inner_text().strip()
    return {"count": count, "detail": name,
            "search_value": page.locator("#search").input_value(),
            "category_value": page.locator("#category").input_value()}


def _make_sequence(page, generated=False):
    page.wait_for_function("document.querySelector('#count') && document.querySelector('#count').textContent === '3건'")
    state = _live_state(page, generated)
    if state != {"count": "3건", "detail": "", "search_value": "", "category_value": ""}:
        raise WebsiteReviewError("Unexpected baseline for synthetic test")
    steps = []
    snapshots = [page.screenshot()]
    previous = state
    for feature in STEPS:
        if feature == "search":
            page.locator("#search").fill("커피")
            page.wait_for_function("document.querySelector('#count').textContent === '1건'")
            expected = {"count": "1건", "detail": "", "search_value": "커피", "category_value": ""}
        elif feature == "filter":
            page.locator("#category").select_option("음료")
            page.wait_for_function("document.querySelector('#count').textContent === '1건'")
            expected = {"count": "1건", "detail": "", "search_value": "커피", "category_value": "음료"}
        else:
            if generated:
                page.locator(".item").filter(has_text="커피").click()
                page.wait_for_function("document.querySelector('#detail h3') && document.querySelector('#detail h3').textContent === '커피'")
            else:
                page.locator("#first-detail").click()
                page.wait_for_function("document.querySelector('#detail').textContent.trim() === '커피'")
            expected = {"count": "1건", "detail": "커피", "search_value": "커피", "category_value": "음료"}
        after = _live_state(page, generated)
        if after != expected or after == previous:
            raise WebsiteReviewError("Step state invalid; no approved transition")
        steps.append({"feature": feature, "before": previous, "after": after,
                      "action": "synthetic_browser_" + feature})
        previous = after
        snapshots.append(page.screenshot())
    metrics = page.evaluate("""() => ({
        width: window.innerWidth,
        document_width: document.documentElement.scrollWidth,
        title: document.title,
        navigation_count: document.querySelectorAll('nav').length,
        heading_count: document.querySelectorAll('h1,h2,h3').length,
        form_control_count: document.querySelectorAll('input,select,button').length
    })""")
    if metrics["document_width"] > metrics["width"] + 1:
        raise WebsiteReviewError("Responsive viewport overflow")
    if len(snapshots) != 4 or any(len(data) > MAX_CAPTURE for data in snapshots):
        raise WebsiteReviewError("Screenshot size/count exceeds bounded evidence")
    return steps, snapshots, metrics


def _capture_reference(html: bytes):
    from playwright.sync_api import sync_playwright
    observations = {}
    with _site_server(html) as (base, server):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                for label, viewport in VIEWPORTS.items():
                    context, blocked = _browser_context(browser, base, viewport)
                    try:
                        page = context.new_page()
                        errors = []
                        page.on("pageerror", lambda err: errors.append(type(err).__name__))
                        page.goto(base + "/", wait_until="domcontentloaded", timeout=12000)
                        steps, screenshots, metrics = _make_sequence(page)
                        if blocked or errors or len(context.pages) != 1:
                            raise WebsiteReviewError("Unexpected reference network/UI behavior")
                        observations[label] = {
                            "steps": steps, "snapshots": screenshots, "metrics": metrics,
                            "evidence_shas": [hashlib.sha256(s).hexdigest() for s in screenshots],
                        }
                    finally:
                        context.close()
            finally:
                browser.close()
        if server.calls != len(VIEWPORTS):
            raise WebsiteReviewError("Reference browser made additional fixture requests")
    return observations


def _astra_multistep(observations: dict, astra_root: Path):
    if (astra_root.is_symlink() or
            not (astra_root / "astra_contracts" / "functional_spec.py").is_file()):
        raise WebsiteReviewError("Frozen Astra P4 model checkout required")
    root = str(astra_root.resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    from astra_contracts.observation import ObservationBundle
    from astra_contracts.functional_spec import derive_spec
    now = datetime.now(timezone.utc).isoformat()
    evidence = []
    actions = []
    for viewport in VIEWPORTS:
        for i, sha in enumerate(observations[viewport]["evidence_shas"]):
            evidence.append({"id": f"ev_{viewport}_{i}",
                             "kind": "screenshot",
                             "source_ref": f"review/p85_{viewport}_{i}.png",
                             "captured_at": now,
                             "notes": "SHA256 " + sha})
        for i, step in enumerate(observations[viewport]["steps"]):
            actions.append({
                "id": f"ob_{viewport}_{i}", "feature": step["feature"],
                "title": "Synthetic local browser observed " + step["feature"],
                "claim": "Only the directly inspected DOM state transition is observed",
                "certainty": "observed",
                "evidence_ids": [f"ev_{viewport}_{i}", f"ev_{viewport}_{i+1}"],
                "action": step["action"],
                "before": step["before"], "after": step["after"],
            })
    bundle = ObservationBundle.model_validate({
        "schema_version": "1.0", "site_url": "http://127.0.0.1",
        "scope": "Owner synthetic localhost only, desktop/mobile, three steps",
        "recorded_at": now, "evidence": evidence, "observations": actions,
    })
    spec = derive_spec(bundle).model_dump(mode="json")
    if (len(spec["candidate_features"]) != 6 or
            any(x["review_status"] != "requires_review" for x in spec["candidate_features"]) or
            any(g["status"] != "pending" for g in spec["approval_gates"]) or
            spec["implementation_ready"] or spec["status"] != "draft_requires_review"):
        raise WebsiteReviewError("Astra granted unauthorized spec approval")
    return bundle.model_dump(mode="json"), spec


def _review_subject(fixture_sha: str, observations: dict):
    return {
        "fixture_sha256": fixture_sha, "viewports": {
            label: {"steps": observations[label]["steps"],
                    "screenshots_sha256": observations[label]["evidence_shas"],
                    "metrics": observations[label]["metrics"]}
            for label in VIEWPORTS
        },
        "site_use": "synthetic_local_only",
    }


def inspect_p85(fixture_html: Path, *, fixture_sha256: str, astra_root: Path):
    html, digest, _ = _fixture(Path(fixture_html), fixture_sha256)
    _validate_scope(html)
    observed = _capture_reference(html)
    bundle, spec = _astra_multistep(observed, Path(astra_root))
    subject = _review_subject(digest, observed)
    receipt = {
        "schema_version": "rea.website.p85.v1",
        "subject": subject, "review_digest": _digest(subject),
        "astra_observation_bundle": bundle, "astra_spec_draft": spec,
        "human_review": "PENDING_EXPLICIT_SYNTHETIC_OWNER_APPROVAL",
        "site_approval": False,
        "production_release": "HOLD",
    }
    return receipt, observed


def _generated_capture(app: Path):
    from playwright.sync_api import sync_playwright
    port = _port()
    base = "http://127.0.0.1:" + str(port)
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1",
         "--port", str(port), "--log-level", "error"],
        cwd=str(app), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    result = {}
    try:
        for _ in range(85):
            if process.poll() is not None:
                raise WebsiteReviewError("Generated app server stopped")
            try:
                with urlopen(base + "/health", timeout=1) as response:
                    if response.status == 200:
                        break
            except (URLError, OSError):
                time.sleep(.1)
        else:
            raise WebsiteReviewError("Generated local app server did not start")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                for label, viewport in VIEWPORTS.items():
                    context, blocked = _browser_context(browser, base, viewport)
                    try:
                        page = context.new_page()
                        errors = []
                        page.on("pageerror", lambda err: errors.append(type(err).__name__))
                        page.goto(base + "/", wait_until="domcontentloaded", timeout=12000)
                        steps, screenshots, metrics = _make_sequence(page, generated=True)
                        if errors or blocked or len(context.pages) != 1:
                            raise WebsiteReviewError("Generated app requested forbidden resource")
                        result[label] = {
                            "steps": steps, "snapshots": screenshots, "metrics": metrics,
                            "evidence_shas": [hashlib.sha256(s).hexdigest() for s in screenshots],
                        }
                    finally:
                        context.close()
            finally:
                browser.close()
        return result
    finally:
        process.terminate()
        try:
            process.communicate(timeout=6)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=6)


def _visual_difference(reference_png: bytes, generated_png: bytes):
    """Quantitative DIFFERENCE report, never claim recovered design parity."""
    from PIL import Image, ImageChops
    with Image.open(BytesIO(reference_png)) as reference:
        with Image.open(BytesIO(generated_png)) as output:
            a, b = reference.convert("RGB"), output.convert("RGB")
            if a.size != b.size:
                raise WebsiteReviewError("Screenshots have incompatible viewport dimensions")
            changed = ImageChops.difference(a, b)
            hist = changed.histogram()
            npx = a.width * a.height
            # Sum channel magnitudes / 3 -> mean absolute channel difference.
            mean_abs = sum((i % 256) * count for i, count in enumerate(hist)) / (3 * npx * 255)
            return {"width": a.width, "height": a.height,
                    "mean_absolute_rgb_difference": round(mean_abs, 6),
                    "verdict": "VISUAL_DIFFERENCE_REQUIRES_HUMAN_REVIEW"}


def _compare(reference, generated):
    differences = {}
    for label in VIEWPORTS:
        ref, out = reference[label], generated[label]
        if ref["steps"] != out["steps"]:
            raise WebsiteReviewError("Observed sequence parity mismatch")
        report = {
            "functional_states": "MATCHED_SYNTHETIC_3_STEP_SEQUENCE",
            "responsive_overflow": False,
            "source_structure": {
                "navigation_count_ref": ref["metrics"]["navigation_count"],
                "navigation_count_generated": out["metrics"]["navigation_count"],
                "heading_count_ref": ref["metrics"]["heading_count"],
                "heading_count_generated": out["metrics"]["heading_count"],
                "form_control_count_ref": ref["metrics"]["form_control_count"],
                "form_control_count_generated": out["metrics"]["form_control_count"],
            },
            "screenshots": [],
        }
        for i in range(4):
            report["screenshots"].append(_visual_difference(ref["snapshots"][i],
                                                            out["snapshots"][i]))
        differences[label] = report
    return differences


def build_p85(fixture_html: Path, owner_csv: Path, out: Path, *,
              fixture_sha256: str, owner_sha256: str,
              approved_review_digest: str, fixture_permission: str,
              owner_approval: str, fable_root: Path, astra_root: Path,
              id_field="id", title_field="title", category_field="category"):
    if fixture_permission != PERMISSION_TOKEN or owner_approval != APPROVAL_TOKEN:
        raise WebsiteReviewError("Owner synthetic permission and explicit review approval required")
    if not isinstance(approved_review_digest, str) or len(approved_review_digest) != 64:
        raise WebsiteReviewError("Exact review digest required")
    target = Path(out).absolute()
    if target.exists() or target.is_symlink() or not target.parent.is_dir() or target.parent.is_symlink():
        raise FileExistsError("Destination must be a new path in an existing real directory")
    if source_sha256(owner_csv) != owner_sha256:
        raise WebsiteReviewError("Owner CSV changed")
    reviewed, reference = inspect_p85(fixture_html, fixture_sha256=fixture_sha256,
                                       astra_root=astra_root)
    if reviewed["review_digest"] != approved_review_digest:
        raise WebsiteReviewError("Review digest mismatch/stale")
    with tempfile.TemporaryDirectory(prefix=".rea-p85-", dir=target.parent) as folder:
        stage = Path(folder) / "independent-app"
        rebuilt = rebuild_local_fixture(
            fixture_html, owner_csv, stage,
            fixture_sha256=fixture_sha256, owner_sha256=owner_sha256,
            id_field=id_field, title_field=title_field, category_field=category_field,
            fixture_permission=PERMISSION_TOKEN, owner_approval="APPROVE",
            fable_root=fable_root, astra_root=astra_root)
        output = _generated_capture(stage)
        differences = _compare(reference, output)
        if source_sha256(owner_csv) != owner_sha256 or _fixture(fixture_html, fixture_sha256)[1] != fixture_sha256:
            raise WebsiteReviewError("Original source changed before publish")
        review = stage / "review"
        for label in VIEWPORTS:
            for i, image in enumerate(reference[label]["snapshots"]):
                (review / f"p85_{label}_{i}.png").write_bytes(image)
            for i, image in enumerate(output[label]["snapshots"]):
                (review / f"p85_generated_{label}_{i}.png").write_bytes(image)
        reviewed["synthetic_owner_decision"] = "APPROVE_SYNTHETIC_ONLY"
        reviewed["source_visual_difference"] = differences
        reviewed["functional_parity"] = "PASS_ON_SYNTHETIC_SEQUENCES"
        (review / "p85_evidence_and_visual_diff.json").write_text(
            json.dumps(review, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8")
        manifest = stage / "manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["website_p85"] = {
            "scope": "local_synthetic_only",
            "review_digest": approved_review_digest,
            "responsive_browser_modes": list(VIEWPORTS),
            "three_step_states_per_mode": True,
            "functional_parity": "PASS_SYNTHETIC",
            "visual_parity": "UNVERIFIED_DIFFERENCE_REPORTED",
            "commercial_release": "HOLD"}
        manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                            encoding="utf-8")
        publish_directory(stage, target)
    return {"status": "P85_SYNTHETIC_REVIEW_HOLD", "rows": rebuilt["rows"],
            "browser_sequences": len(VIEWPORTS), "steps_per_sequence": 3,
            "functional_parity": "PASS_SYNTHETIC",
            "visual_parity": "UNVERIFIED_DIFFERENCE_REPORTED",
            "commercial_release": "HOLD"}
