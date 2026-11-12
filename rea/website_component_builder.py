"""REA_Web: evidence-bound independent component tree, not CSS-only site mimicry.

This is a strict, reproducible synthetic/local workflow. Real Chromium P85
observations + actual frozen Astra P4 feature/evidence output + SHA-pinned
owner HTML semantic structure -> reviewer-selected, independent HTML component
tree and its own styling. Existing approved customer CSV supplies ALL data.
No reference scripts, CSS, HTML, content, visual assets or hidden logic copied.
External live sites, legal permission and commercial release remain unsupported.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from bs4 import BeautifulSoup

from rea.website_rebuild import WebsiteReviewError
from rea.website_site_layout import (
    OWNER_LAYOUT_APPROVAL, observe_layout_contract, apply_owner_layout,
)
from rea.website_p95 import _hash, _json_file
from rea.safe_publish import publish_directory

FEATURES = ("search", "filter", "detail")
STRUCTURES = {"top_navigation", "side_inventory", "article_directory"}
CHROME_ORDER = {"desktop", "mobile"}
SELF_OWNED_COPY = {
    "top_navigation": ("데이터 살펴보기", "카탈로그 구성"),
    "side_inventory": ("현황 및 분류", "재고형 탐색 구성"),
    "article_directory": ("항목 탐색", "상세 정보형 구성"),
}
SHELL_CSS = """
/* REA-created independent component tree; zero reference-site source content. */
.rea-scope-links{display:flex;gap:12px;flex-wrap:wrap;padding:10px 0 16px}
.rea-scope-links a{color:#2763a7;font-weight:700;line-height:1.8}
.rea-side-workspace{display:grid;grid-template-columns:minmax(180px,260px) minmax(0,1fr);
gap:16px;align-items:start}
.rea-side-workspace .rea-scope-links{display:flex;flex-direction:column;gap:4px}
.rea-side-workspace .rea-side-rail{border:1px solid #e1e7f0;border-radius:12px;padding:16px}
.rea-side-workspace .rea-app-area{min-width:0}
.rea-article-workspace{border-top:3px solid #3a2949;padding-top:14px}
.rea-article-workspace .shell{grid-template-columns:1fr 1fr}
.rea-screen-provenance{font-size:12px;color:#53687e}
@media(max-width:740px){.rea-side-workspace{grid-template-columns:1fr}
.rea-side-workspace .rea-side-rail{padding:10px}
.rea-side-workspace .rea-scope-links{flex-direction:row}
.rea-article-workspace .shell{grid-template-columns:1fr}}
"""


def observed_contract(fixture_html: Path, *, fixture_sha256: str,
                      p85_receipt: dict) -> dict:
    """Bind actual Astra observed search/filter/detail states to a UI proposal."""
    layout = observe_layout_contract(
        fixture_html, fixture_sha256=fixture_sha256, p85_receipt=p85_receipt)
    subject = p85_receipt.get("subject", {})
    viewports = subject.get("viewports")
    spec = p85_receipt.get("astra_spec_draft", {})
    bundle = p85_receipt.get("astra_observation_bundle", {})
    if not isinstance(viewports, dict) or set(viewports) != CHROME_ORDER:
        raise WebsiteReviewError("Both actual Chromium P85 viewports required")
    if (not isinstance(spec, dict) or spec.get("implementation_ready") is not False
            or not isinstance(bundle, dict)):
        raise WebsiteReviewError("Actual unapproved Astra feature contract required")
    if not isinstance(bundle.get("evidence"), list):
        raise WebsiteReviewError("Astra evidence missing")
    evidence = {e.get("id"): e for e in bundle["evidence"]
                if isinstance(e, dict) and isinstance(e.get("id"), str)}
    if len(evidence) != 8:
        raise WebsiteReviewError("Exactly eight P85 viewport screenshots expected")
    allowed = {"search", "filter", "detail"}
    features = spec.get("candidate_features", [])
    if not isinstance(features, list) or len(features) != 6:
        raise WebsiteReviewError("Expected six Astra observed candidate features")
    trace = []
    observations = bundle.get("observations", [])
    if not isinstance(observations, list) or len(observations) != 6:
        raise WebsiteReviewError("Astra observed state count mismatch")
    for viewport, record in viewports.items():
        steps = record.get("steps")
        shas = record.get("screenshots_sha256")
        if (not isinstance(steps, list) or [s.get("feature") for s in steps] != list(FEATURES)
                or not isinstance(shas, list) or len(shas) != 4):
            raise WebsiteReviewError("Broken recorded Chromium state sequence")
        for index, step in enumerate(steps):
            observation_id = f"ob_{viewport}_{index}"
            match = next((o for o in observations if o.get("id") == observation_id), None)
            if (match is None or match.get("certainty") != "observed"
                    or match.get("feature") != step["feature"]
                    or match.get("before") != step.get("before")
                    or match.get("after") != step.get("after")):
                raise WebsiteReviewError("Astra observation does not match browser state")
            expected_refs = [f"ev_{viewport}_{index}",
                             f"ev_{viewport}_{index+1}"]
            if match.get("evidence_ids") != expected_refs:
                raise WebsiteReviewError("Astra evidence chain changed")
            for offset, eid in enumerate(expected_refs):
                ref = evidence.get(eid)
                if not ref or shas[index + offset] not in str(ref.get("notes", "")):
                    raise WebsiteReviewError("Screenshot evidence SHA mismatch")
            trace.append({"viewport": viewport, "feature": step["feature"],
                          "observation_id": observation_id,
                          "before_sha256": shas[index],
                          "after_sha256": shas[index+1],
                          "result": "BROWSER_OBSERVED_NOT_APPROVED"})
    for f in features:
        if (f.get("feature") not in allowed or
                f.get("review_status") != "requires_review" or
                not f.get("evidence")):
            raise WebsiteReviewError("Astra candidate has no review-bound evidence")
    data = {
        "schema_version": "rea.website.ui.contract.v1",
        "source_fixture_sha256": fixture_sha256,
        "p85_review_digest": p85_receipt["review_digest"],
        "semantic_layout_sha256": layout["contract_sha256"],
        "semantic_layout": layout["proposed_preset"],
        "app_owned_features": list(FEATURES),
        "traceability": trace,
        "component_structure": "CUSTOM_REA_INDEPENDENT_HTML",
        "original_assets_code_or_text_copied": False,
        "status": "REQUIRES_HUMAN_PROPOSAL_APPROVAL",
        "commercial_release": "HOLD",
    }
    data["contract_sha256"] = _hash(data)
    return data, layout


def _expect(soup: BeautifulSoup, selector: str):
    matches = soup.select(selector)
    if len(matches) != 1:
        raise WebsiteReviewError(f"Generated REA template missing/duplicate component: {selector}")
    return matches[0]


def _create_links(soup: BeautifulSoup):
    nav = soup.new_tag("nav", attrs={"class": "rea-scope-links",
                                     "aria-label": "REA 신규 데이터 탐색"})
    for target, label in [("rea-overview", "현황"),
                          ("rea-list", "목록"), ("rea-detail", "상세")]:
        a = soup.new_tag("a", href="#" + target)
        a.string = label
        nav.append(a)
    return nav


def _rebuild_components(soup: BeautifulSoup, preset: str):
    if preset not in STRUCTURES:
        raise WebsiteReviewError("Unsupported independent component arrangement")
    main = _expect(soup, "main.layout")
    intro = _expect(soup, "section.intro")
    overview = _expect(soup, "section.overview")
    shell = _expect(soup, "div.shell")
    list_section = _expect(soup, ".shell > section.panel")
    detail = _expect(soup, ".shell > aside.detail")
    _expect(soup, "input#search")
    _expect(soup, "select#category")
    _expect(soup, "#results")
    _expect(soup, "#count")
    _expect(soup, "#overview-total")
    _expect(soup, ".pagination")
    # DOM ids are stable for the independently authored Pro JS; all reference
    # source tags/text/CSS/scripts stay outside the new app.
    overview["id"] = "rea-overview"
    list_section["id"] = "rea-list"
    detail["id"] = "rea-detail"
    links = _create_links(soup)
    heading = soup.new_tag("h2", attrs={"class": "rea-screen-provenance"})
    heading.string = SELF_OWNED_COPY[preset][0]

    if preset == "top_navigation":
        intro.insert_after(links)
        overview.insert_before(heading)
    elif preset == "side_inventory":
        workspace = soup.new_tag("div", attrs={"class": "rea-side-workspace"})
        rail = soup.new_tag("aside", attrs={"class": "rea-side-rail",
                                            "aria-label": "REA 독립 작업영역"})
        area = soup.new_tag("section", attrs={"class": "rea-app-area"})
        intro.insert_after(workspace)
        workspace.append(rail)
        workspace.append(area)
        rail.append(heading)
        rail.append(links)
        # Move *existing independently authored app* components into the
        # newly owned structure; no source-site HTML is imported.
        rail.append(overview.extract())
        area.append(shell.extract())
    else:
        article = soup.new_tag("article", attrs={"class": "rea-article-workspace"})
        article["aria-label"] = "REA 자체 상세 탐색 구조"
        intro.insert_after(article)
        article.append(heading)
        article.append(links)
        article.append(overview.extract())
        article.append(shell.extract())
    # Validate no duplicate selectors introduced by DOM rewrite.
    for selector in ("#search", "#category", "#count", "#detail",
                     "#overview-total", ".pagination", "#results"):
        _expect(soup, selector)
    return str(soup)


def build_evidence_ui(existing_app: Path, output: Path, *,
                      reference_html: Path, fixture_sha256: str,
                      p85_receipt: dict, decision_record: Path,
                      approved_ui_contract_sha256: str,
                      owner_approval: str) -> dict:
    """Generate a new, browser-testable component tree with review traceability.

    P95 reviewer opinion is explicitly synthetic; a generated proposal cannot
    be mistaken for licensed real-site implementation or owner identity check.
    """
    if owner_approval != OWNER_LAYOUT_APPROVAL:
        raise WebsiteReviewError("Synthetic local owner approval required")
    ui_contract, layout = observed_contract(
        reference_html, fixture_sha256=fixture_sha256, p85_receipt=p85_receipt)
    if approved_ui_contract_sha256 != ui_contract["contract_sha256"]:
        raise WebsiteReviewError("Wrong/stale observed UI contract digest")
    decision = _json_file(decision_record)
    if (decision.get("schema_version") != "rea.website.p95.record.v1"
            or decision.get("decision") != "approve_synthetic_proposal"
            or decision.get("layout_preset") != ui_contract["semantic_layout"]
            or decision.get("review_digest") != ui_contract["p85_review_digest"]
            or decision.get("commercial_release") != "HOLD"
            or decision.get("site_use_license_verified") is not False
            or decision.get("code_generation_authorized") is not False):
        raise WebsiteReviewError("No matching owner-synthetic proposal approval")
    output = Path(output).absolute()
    if (output.exists() or output.is_symlink() or not output.parent.is_dir()
            or output.parent.is_symlink()):
        raise FileExistsError("Target must be a new directory in an existing real parent")
    with tempfile.TemporaryDirectory(prefix=".rea-evidence-ui-", dir=output.parent) as temp:
        stage = Path(temp)
        preset_app = stage / "preset"
        apply_owner_layout(
            existing_app, preset_app, contract=layout,
            decision_record=decision_record,
            approved_contract_sha256=layout["contract_sha256"],
            owner_layout_approval=OWNER_LAYOUT_APPROVAL)
        candidate = stage / "component"
        shutil.copytree(preset_app, candidate,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
        html_path = candidate / "static/index.html"
        css_path = candidate / "static/style.css"
        manifest_path = candidate / "manifest.json"
        soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
        restructured = _rebuild_components(soup, ui_contract["semantic_layout"])
        html_path.write_text(restructured + "\n", encoding="utf-8")
        with css_path.open("a", encoding="utf-8") as stream:
            stream.write(SHELL_CSS)
        (candidate / "review/p95_evidence_ui_contract.json").write_text(
            json.dumps(ui_contract, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["website_p95_component"] = {
            "ui_contract_sha256": ui_contract["contract_sha256"],
            "applied_semantic_layout": ui_contract["semantic_layout"],
            "traced_viewport_states": len(ui_contract["traceability"]),
            "reviewer_identity_verified": False,
            "actual_reference_site_license_verified": False,
            "reference_design_parity_verified": False,
            "commercial_release": "HOLD",
        }
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8")
        if output.exists() or output.is_symlink():
            raise FileExistsError("Another output occupied the target")
        publish_directory(candidate, output)
    return {
        "status": "P95_OBSERVED_SYNTHETIC_COMPONENT_WORKFLOW_HOLD",
        "observed_states": len(ui_contract["traceability"]),
        "applied_layout": ui_contract["semantic_layout"],
        "ui_contract_sha256": ui_contract["contract_sha256"],
        "reference_design_or_copyright_approved": False,
        "commercial_release": "HOLD",
    }
