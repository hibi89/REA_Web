"""Computed CSS captures and reference-to-owner-API design adaptation regression."""
from __future__ import annotations

import copy
import json

import pytest
from rea.adapter.visual_reference import VisualError, sanitize_observation, validate_visual, capture_page, _safe_public_target
from rea.adapter.frontend_bridge import BridgeError, make_review, generate_frontend

ORIGIN = "https://reference.example.test"
FABLE = {
    "schema_version": "1.0", "target": {"input_url": ORIGIN + "/private?a=DO_NOT_LEAK"},
    "scanned_at": "2026-11-01T10:00:00+00:00", "scan_mode": "static",
    "frontend": [], "backend_inferred": [], "infra": [],
    "api": {"endpoints": [], "candidates": [], "chart_candidates": []},
    "charts": [], "warnings": [],
}
BACKEND = {
    "schema_version": "rea.backend_contract.v0.1", "status": "REVIEW_REQUIRED",
    "generation_allowed": False, "execution_performed": False,
    "input": {"sha256": "a"*64},
    "api": {"endpoints": [
        {"path": path, "methods": ["GET"], "verification": "STATIC_DECLARATION_ONLY", "mount": "app_declaration"}
        for path in ("/api/jobs", "/api/metrics", "/api/jobs/{job_id}")
    ]},
}
BINDINGS = {
    "list": {"path": "/api/jobs", "field": "items"},
    "metrics": {"path": "/api/metrics", "field": "__root__"},
    "detail": {"path": "/api/jobs/{job_id}", "field": "__root__"},
}

def raw(origin=ORIGIN, layout="sidebar"):
    return {
        "origin": origin, "layout": layout, "viewport": {"width": 1365, "height": 900},
        "colors": {"canvas": "rgb(249, 250, 253)", "surface": "#ffffff", "ink": "rgb(20,30,40)",
                   "navigation": "rgb(31, 52, 90)", "accent": "rgb(191, 64, 72)"},
        "components": {"navigation":1, "buttons":1, "tables":1, "forms":0, "inputs":1, "card_like":3},
        "evidence": {"navigation_visible":True, "panel_visible":True, "button_visible":True},
        "secret":"never copy this", "html":"<script>never include</script>", "cookies":["DO_NOT_LEAK"],
    }


def test_normalizes_css_into_minimal_hashed_whitelist():
    visual = sanitize_observation(raw())
    assert visual["colors"]["accent"] == "#bf4048"
    assert visual["colors"]["navigation"] == "#1f345a"
    assert visual["components"]["card_like"] == 3
    assert "DO_NOT_LEAK" not in json.dumps(visual) and "<script>" not in json.dumps(visual)
    assert validate_visual(visual, expected_origin=ORIGIN) == visual
    assert len(json.dumps(visual).encode()) < 3000


def test_visual_source_controls_generated_original_css(tmp_path):
    v=sanitize_observation(raw())
    review=make_review(FABLE,BACKEND,BINDINGS,visual=v)
    assert review["reference"]["visual_evidence"] == "BROWSER_COMPUTED_STYLE_OBSERVED"
    assert review["reference"]["visual_sha256"] == v["sha256"]
    assert review["reference"]["layout_similarity_to_reference"] == "UNVERIFIED"
    assert review["generation_allowed"] is False
    path=tmp_path/"frontend"
    manifest=generate_frontend(review,path,owner_confirmed=True)
    css=(path/"style.css").read_text(encoding='utf-8')
    assert ".sidebar{background-color:#1f345a;}" in css
    assert ".glyph{background-color:#bf4048;}" in css
    assert "reference_visual_hints_not_pixel_replication" in manifest["limitations"]
    assert "DO_NOT_LEAK" not in "".join(x.read_text(encoding='utf-8') for x in path.iterdir())
    assert (path/"app.js").is_file() and (path/"index.html").is_file()


def test_topbar_layout_hint_changes_original_arrangement(tmp_path):
    visual=sanitize_observation(raw(layout="topbar"))
    review=make_review(FABLE,BACKEND,BINDINGS,visual=visual)
    generate_frontend(review,tmp_path/"app",owner_confirmed=True)
    assert '.shell{display:block}.sidebar{display:flex;flex-direction:row;' in (tmp_path/"app"/"style.css").read_text(encoding='utf-8')


def test_visual_mismatch_and_tampering_refused(tmp_path):
    visual=sanitize_observation(raw())
    wrong=copy.deepcopy(visual);wrong["origin"]="https://wrong.example.test"
    with pytest.raises(BridgeError):make_review(FABLE,BACKEND,BINDINGS,visual=wrong)
    corrupt=copy.deepcopy(visual);corrupt["colors"]["accent"]="red; background:url(https://evil.test)"
    with pytest.raises(BridgeError):make_review(FABLE,BACKEND,BINDINGS,visual=corrupt)
    plan=make_review(FABLE,BACKEND,BINDINGS,visual=visual)
    plan["reference"]["visual_sha256"]="b"*64
    with pytest.raises(BridgeError):generate_frontend(plan,tmp_path/"no",owner_confirmed=True)
    assert not (tmp_path/"no").exists()


@pytest.mark.parametrize("color", ["red", "url(https://evil.test)", "#abc", "rgb(300,1,2)", "rgba(2,4,6,0.1)"])
def test_bad_colors_not_injected(color):
    r=raw();r["colors"]["accent"]=color
    assert sanitize_observation(r)["colors"]["accent"] is None


@pytest.mark.parametrize("host", ["http://127.0.0.1/", "https://localhost/", "file:///etc/passwd", "https://example.org/?secret=x", "https://example.org:8080/"])
def test_public_url_gate_rejects_unsafe_without_network(host):
    with pytest.raises(VisualError): _safe_public_target(host)


def test_reference_capture_in_real_chromium_from_intercepted_synthetic_url():
    """Browser computes actual CSS. The route is fulfilled locally: zero outbound network."""
    sync_api = pytest.importorskip("playwright.sync_api")
    markup='''<!doctype html><html><head><style>
body{margin:0;color:#243449;background:#f9fafd;font-family:Arial}
aside{height:900px;width:245px;background:#20355b;position:absolute;left:0;top:0}
nav{height:760px;width:220px;}main{margin-left:260px}
article{background:#fff;padding:40px;}button{background:#bb4064;color:#fff}
</style></head><body><aside><nav><a href="#">Menu</a></nav></aside>
<main><article><h1>Example</h1><button>Open</button><table><tr><td>1</td></tr></table></article></main>
</body></html>'''
    try:
        with sync_api.sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            try:
                context=browser.new_context(viewport={"width":1365,"height":900},java_script_enabled=True)
                context.route("**/*",lambda route: route.fulfill(body=markup,content_type="text/html") if route.request.url.startswith(ORIGIN) else route.abort())
                page=context.new_page(); page.goto(ORIGIN+"/",wait_until="domcontentloaded")
                v=capture_page(page)
                assert v["origin"]==ORIGIN
                assert v["layout"]=="sidebar"
                assert v["colors"]["navigation"]=="#20355b"
                assert v["colors"]["accent"]=="#bb4064"
                assert v["components"]["tables"]==1
                # The real browser consumes the extracted style hint on a
                # separately generated original frontend (no copied HTML/CSS).
                import tempfile
                from pathlib import Path
                with tempfile.TemporaryDirectory() as temporary:
                    path=Path(temporary)/"generated"
                    review=make_review(FABLE,BACKEND,BINDINGS,visual=v)
                    generate_frontend(review,path,owner_confirmed=True)
                    def render_generated(route):
                        url=route.request.url
                        if url.endswith("/dashboard/"):
                            route.fulfill(body=(path/"index.html").read_text(encoding='utf-8'),content_type="text/html")
                        elif url.endswith("/dashboard/style.css"):
                            route.fulfill(body=(path/"style.css").read_text(encoding='utf-8'),content_type="text/css")
                        elif url.endswith("/dashboard/app.js"):
                            route.fulfill(body=(path/"app.js").read_text(encoding='utf-8'),content_type="text/javascript")
                        elif url.endswith("/api/jobs"):
                            route.fulfill(json={"items": []})
                        elif url.endswith("/api/metrics"):
                            route.fulfill(json={"total":0,"completed":0,"pending":0})
                        else:
                            route.abort()
                    context.route("https://preview.example.test/**", render_generated)
                    rendered=context.new_page()
                    rendered.goto("https://preview.example.test/dashboard/",wait_until="load")
                    rendered.wait_for_load_state("networkidle")
                    actual=rendered.locator(".sidebar").evaluate("el => getComputedStyle(el).backgroundColor")
                    assert actual=="rgb(32, 53, 91)"
                    accent=rendered.locator(".glyph").evaluate("el => getComputedStyle(el).backgroundColor")
                    assert accent=="rgb(187, 64, 100)"
            finally:browser.close()
    except Exception as exc:
        if "Executable doesn't exist" in str(exc):
            pytest.skip("Chromium binary unavailable on this local machine")
        raise


def test_public_url_cli_never_fetches_without_opt_in(tmp_path):
    import subprocess, sys
    dest=tmp_path/'visual.json'
    process=subprocess.run(
        [sys.executable,'-m','rea.adapter.visual_reference',
         '--url','https://example.org/','--out',str(dest)],
        text=True,capture_output=True,
    )
    assert process.returncode==2
    assert 'requires --allow-network' in process.stderr
    assert not dest.exists()


def test_missing_visual_is_neutral_and_does_not_claim_observed(tmp_path):
    plan=make_review(FABLE,BACKEND,BINDINGS)
    assert plan['visual_contract'] is None
    assert plan['reference']['style_source']=='ORIGINAL_REA_NEUTRAL_DEFAULT'
    generate_frontend(plan,tmp_path/'neutral',owner_confirmed=True)
    assert 'Sanitized reference computed-style hints' not in (tmp_path/'neutral'/'style.css').read_text(encoding='utf-8')
