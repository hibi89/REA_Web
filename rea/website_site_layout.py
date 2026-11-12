"""REA_Web: owner-selected, independently implemented reference-guided layout.

Extract ONLY semantic tag counts from an owner-supplied, SHA-pinned local HTML
fixture. Source HTML/CSS/JS/text/images are never copied into the generated app.
Existing Pro functions and data originate solely from approved customer CSV.
Reviewer selects a bounded independently authored layout preset; the result
is NOT visual clone, copyright permission or commercial approval.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
import os
from pathlib import Path
import shutil
import tempfile

from rea.safe_publish import publish_directory
from rea.website_rebuild import WebsiteReviewError, _fixture
from rea.website_p95 import _hash, _json_file

PRESETS = {"top_navigation", "side_inventory", "article_directory"}
OWNER_LAYOUT_APPROVAL = "APPROVE_SYNTHETIC_LAYOUT_ONLY"
STYLE = {
    "top_navigation": """/* REA owned preset: catalog navigation, original source not copied */
body.rea-preset-top_navigation .top{background:#162a45}
body.rea-preset-top_navigation .shell{grid-template-columns:minmax(0,1.5fr) minmax(0,1fr)}
body.rea-preset-top_navigation .panel{border-radius:12px}
@media(max-width:740px){body.rea-preset-top_navigation .shell{grid-template-columns:1fr}}
""",
    "side_inventory": """/* REA owned preset: inventory workspace, original source not copied */
body.rea-preset-side_inventory .top{background:#153a35}
body.rea-preset-side_inventory .shell{grid-template-columns:minmax(0,1fr) minmax(0,1.1fr)}
body.rea-preset-side_inventory .panel{border-left:4px solid #287f70;border-radius:8px}
body.rea-preset-side_inventory .controls{grid-template-columns:1fr 1fr}
@media(max-width:740px){body.rea-preset-side_inventory .shell{grid-template-columns:1fr}
body.rea-preset-side_inventory .controls{grid-template-columns:1fr}}
""",
    "article_directory": """/* REA owned preset: reference directory, original source not copied */
body.rea-preset-article_directory .top{background:#3a2949}
body.rea-preset-article_directory .shell{grid-template-columns:1fr}
body.rea-preset-article_directory .panel{border-radius:4px}
body.rea-preset-article_directory .detail{min-height:200px}
body.rea-preset-article_directory .intro{border-bottom:2px solid #d1c3df}
""",
}


class _Structure(HTMLParser):
    """Never record attributes or source content; count semantic tags only."""

    def __init__(self):
        super().__init__()
        self.counts = {name: 0 for name in
                       ("nav", "aside", "article", "main", "h1", "table",
                        "form", "input", "select", "button")}

    def handle_starttag(self, tag, attrs):
        if tag in self.counts:
            self.counts[tag] += 1


def observe_layout_contract(reference_html: Path, *, fixture_sha256: str,
                            p85_receipt: dict) -> dict:
    """A limited structural hint linked to P85 verified synthetic observations."""
    html, sha, _ = _fixture(Path(reference_html), fixture_sha256)
    if (p85_receipt.get("schema_version") != "rea.website.p85.v1" or
            p85_receipt.get("production_release") != "HOLD" or
            p85_receipt.get("site_approval") is not False):
        raise WebsiteReviewError("P85 evidence in unsafe state")
    if p85_receipt.get("subject", {}).get("fixture_sha256") != sha:
        raise WebsiteReviewError("HTML and P85 observation source mismatch")
    if p85_receipt.get("review_digest") != _hash(p85_receipt["subject"]):
        raise WebsiteReviewError("P85 evidence digest mismatch")
    parser = _Structure()
    try:
        parser.feed(html.decode("utf-8-sig"))
        parser.close()
    except UnicodeError as exc:
        raise WebsiteReviewError("Local HTML must be UTF-8") from exc
    c = parser.counts
    if c["aside"] > 0:
        proposal = "side_inventory"
    elif c["article"] > 0:
        proposal = "article_directory"
    elif c["nav"] > 0:
        proposal = "top_navigation"
    else:
        raise WebsiteReviewError("No supported semantic layout; owner review required")
    contract = {
        "schema_version": "rea.website.layout.contract.v1",
        "fixture_sha256": sha,
        "p85_review_digest": p85_receipt["review_digest"],
        "semantic_tag_counts": c,
        "proposed_preset": proposal,
        "proposed_reason": "bounded_semantic_structure_only",
        "source_html_css_js_copied": False,
        "status": "REVIEW_REQUIRED",
        "commercial_release": "HOLD",
    }
    contract["contract_sha256"] = _hash(contract)
    return contract


def apply_owner_layout(existing_app: Path, output: Path, *, contract: dict,
                       decision_record: Path, approved_contract_sha256: str,
                       owner_layout_approval: str) -> dict:
    """Copy-on-write Pro app refinement; never modify source or reference."""
    if owner_layout_approval != OWNER_LAYOUT_APPROVAL:
        raise WebsiteReviewError("Explicit synthetic-only layout consent required")
    if not isinstance(contract, dict):
        raise WebsiteReviewError("Layout contract required")
    preset = contract.get("proposed_preset")
    if preset not in PRESETS or contract.get("status") != "REVIEW_REQUIRED":
        raise WebsiteReviewError("Unsupported/inferred layout preset")
    digest = contract.get("contract_sha256")
    if (not isinstance(digest, str) or digest != approved_contract_sha256 or
            digest != _hash({k: v for k, v in contract.items() if k != "contract_sha256"})):
        raise WebsiteReviewError("Approved structural observation fingerprint mismatch")
    decision = _json_file(decision_record)
    if (decision.get("schema_version") != "rea.website.p95.record.v1"
            or decision.get("decision") != "approve_synthetic_proposal"
            or decision.get("layout_preset") != preset
            or decision.get("review_digest") != contract["p85_review_digest"]
            or decision.get("site_use_license_verified") is not False
            or decision.get("commercial_release") != "HOLD"):
        raise WebsiteReviewError("Missing matching owner proposal opinion")
    app = Path(existing_app)
    target = Path(output).absolute()
    if app.is_symlink() or not app.is_dir():
        raise WebsiteReviewError("Existing independent app folder required")
    if target.exists() or target.is_symlink() or not target.parent.is_dir() or target.parent.is_symlink():
        raise FileExistsError("Only new output paths in existing real folder")
    for entry in app.rglob("*"):
        if entry.is_symlink():
            raise WebsiteReviewError("Symlink forbidden in source app")
    index = app / "static/index.html"
    css = app / "static/style.css"
    manifest = app / "manifest.json"
    if not index.is_file() or not css.is_file() or not manifest.is_file():
        raise WebsiteReviewError("Missing generated Pro app assets")
    html = index.read_text(encoding="utf-8")
    if ('<body>' not in html or '<main class="layout">' not in html or
            html.count('<body>') != 1 or html.count('<main class="layout">') != 1):
        raise WebsiteReviewError("Unexpected generated independent layout source")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("website_p85", {}).get("commercial_release") != "HOLD":
        raise WebsiteReviewError("Only P85 held apps can be styled")
    with tempfile.TemporaryDirectory(prefix=".rea-layout-", dir=target.parent) as temp:
        destination = Path(temp) / "owned-app"
        shutil.copytree(app, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
        own_html = html.replace('<body>', f'<body class="rea-preset-{preset}">')
        (destination / "static/index.html").write_text(own_html, encoding="utf-8")
        with (destination / "static/style.css").open("a", encoding="utf-8") as styles:
            styles.write("\n" + STYLE[preset])
        review = destination / "review"
        review.mkdir(exist_ok=True)
        (review / "p95_owner_site_layout_contract.json").write_text(
            json.dumps(contract, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8")
        data["website_p95_layout"] = {
            "preset": preset, "contract_sha256": digest,
            "provenance": "semantic_structure_from_owned_local_fixture",
            "site_layout_reconstructed_exactly": False,
            "source_html_css_js_copied": False,
            "human_opinion_recorded_not_identity_verified": True,
            "commercial_release": "HOLD",
        }
        (destination / "manifest.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8")
        if target.exists() or target.is_symlink():
            raise FileExistsError("Target changed while preparing output")
        publish_directory(destination, target)
    return {
        "status": "SYNTHETIC_LAYOUT_PRESET_REBUILT_WITH_REVIEW_HOLD",
        "preset": preset, "contract_sha256": digest,
        "original_site_design_reproduced": False,
        "customer_rights_verified": False,
        "commercial_release": "HOLD",
    }
