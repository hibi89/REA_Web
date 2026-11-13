"""SITECRAFT AX P85: isolated three-site desktop/mobile synthetic QA batch.

This is a synthetic engineering gate. SHA-pinned localhost HTML and separate
owner CSV are tested with real Chromium, Astra, Fable STATIC and independent
Pro app creation. No real owner identity, site reuse right, or release approval.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from rea.safe_publish import publish_directory
from rea.sitecraft_p70 import read_scope, WebsiteReviewError
from rea.website_p85 import inspect_p85, build_p85, VIEWPORTS, STEPS

SCHEMA = "sitecraft.p85.synthetic.v1"
MODE = "three_synthetic_local_responsive_cases"


def read_p85_scope(scope: Path, *, require_approval: bool):
    # Reuse the exact P70 file-safety, SHA, mapping and no-external-source gates.
    # The new schema changes only product stage and the interpretation of the
    # review digest (desktop+mobile 3-step evidence rather than one P70 action).
    return read_scope(scope, require_approval=require_approval,
                      expected_schema=SCHEMA, expected_mode=MODE)


def _read_observed(site: dict, html: Path, astra_root: Path):
    receipt, observed = inspect_p85(
        html, fixture_sha256=site["reference_sha256"], astra_root=astra_root)
    if (receipt["schema_version"] != "rea.website.p85.v1"
            or receipt["site_approval"] is not False
            or receipt["production_release"] != "HOLD"
            or receipt["astra_spec_draft"]["implementation_ready"] is not False
            or any(x["review_status"] != "requires_review"
                   for x in receipt["astra_spec_draft"]["candidate_features"])
            or len(receipt["astra_observation_bundle"]["observations"]) != 6
            or len(receipt["astra_observation_bundle"]["evidence"]) != 8
            or set(observed) != set(VIEWPORTS)):
        raise WebsiteReviewError("Real Astra/Chromium P85 evidence gate changed")
    for name in VIEWPORTS:
        series = observed[name]
        if ([step["feature"] for step in series["steps"]] != list(STEPS)
                or len(series["snapshots"]) != 4
                or series["metrics"]["document_width"] > series["metrics"]["width"] + 1):
            raise WebsiteReviewError("Incomplete responsive 3-action evidence")
    return receipt


def inspect_three(scope: Path, *, astra_root: Path) -> dict:
    """Review three actual responsive site receipts before synthetic consent."""
    data, _owner, sites = read_p85_scope(scope, require_approval=False)
    results = {}
    for site, html in sites:
        receipt = _read_observed(site, html, astra_root)
        results[site["case"]] = {
            "reference_sha256": site["reference_sha256"],
            "review_digest": receipt["review_digest"],
            "desktop_mobile_evidence_count": len(receipt["astra_observation_bundle"]["evidence"]),
            "steps_per_viewport": len(STEPS),
            "observed_claims": len(receipt["astra_observation_bundle"]["observations"]),
            "status": "REVIEW_REQUIRED",
        }
    return {
        "product": data["product"],
        "gate": "P85_SYNTHETIC_INSPECTION_ONLY",
        "sites": results,
        "commercial_release": "HOLD",
        "customer_identity_verified": False,
        "real_external_website": False,
    }


def build_three(scope: Path, out: Path, *, fable_root: Path,
                astra_root: Path) -> dict:
    """P85 three-site bundle is published atomically only when all sites pass."""
    data, owner, sites = read_p85_scope(scope, require_approval=True)
    dest = Path(out).absolute()
    if dest.exists() or dest.is_symlink():
        raise FileExistsError("SITECRAFT package destination already exists")
    if not dest.parent.is_dir() or dest.parent.is_symlink():
        raise WebsiteReviewError("Output parent must be an existing non-symlink directory")
    # Match each review digest to complete desktop/mobile observed screenshots
    # BEFORE creating staging output. A synthetic token is not customer consent.
    for site, html in sites:
        receipt = _read_observed(site, html, astra_root)
        if receipt["review_digest"] != site["approved_review_digest"]:
            raise WebsiteReviewError("P85 review digest changed or forged")
    with tempfile.TemporaryDirectory(prefix=".sitecraft-p85-", dir=dest.parent) as tmp:
        bundle = Path(tmp) / "bundle"
        bundle.mkdir()
        results = {}
        for site, html in sites:
            case = site["case"]
            app = bundle / case
            outcome = build_p85(
                html, owner, app,
                fixture_sha256=site["reference_sha256"],
                owner_sha256=data["owner_sha256"],
                approved_review_digest=site["approved_review_digest"],
                fixture_permission="YES_LOCAL_FIXTURE",
                owner_approval="APPROVE_SYNTHETIC_ONLY",
                fable_root=fable_root, astra_root=astra_root,
                id_field=data["mapping"]["id"],
                title_field=data["mapping"]["title"],
                category_field=data["mapping"]["category"],
            )
            if (outcome["status"] != "P85_SYNTHETIC_REVIEW_HOLD"
                    or outcome["browser_sequences"] != len(VIEWPORTS)
                    or outcome["steps_per_sequence"] != len(STEPS)
                    or outcome["functional_parity"] != "PASS_SYNTHETIC"
                    or outcome["visual_parity"] != "UNVERIFIED_DIFFERENCE_REPORTED"
                    or outcome["commercial_release"] != "HOLD"):
                raise WebsiteReviewError("P85 synthetic responsive acceptance failed")
            audit = json.loads((app / "review/p85_evidence_and_visual_diff.json").read_text(encoding="utf-8"))
            if (audit["review_digest"] != site["approved_review_digest"]
                    or audit["astra_spec_draft"]["implementation_ready"] is not False
                    or len(audit["astra_observation_bundle"]["observations"]) != 6):
                raise WebsiteReviewError("P85 published evidence incompatible with review")
            visual = audit["source_visual_difference"]
            if set(visual) != set(VIEWPORTS):
                raise WebsiteReviewError("Missing viewport visual difference")
            for viewport in VIEWPORTS:
                diffs = visual[viewport]["screenshots"]
                if (len(diffs) != 4
                        or visual[viewport]["functional_states"] != "MATCHED_SYNTHETIC_3_STEP_SEQUENCE"
                        or any(d["verdict"] != "VISUAL_DIFFERENCE_REQUIRES_HUMAN_REVIEW"
                               or not 0 <= d["mean_absolute_rgb_difference"] <= 1
                               for d in diffs)):
                    raise WebsiteReviewError("P85 visual review differs from contract")
            results[case] = {
                "fixture_sha256": site["reference_sha256"],
                "review_digest": site["approved_review_digest"],
                "viewports": list(VIEWPORTS),
                "observed_steps": len(VIEWPORTS) * len(STEPS),
                "reference_screenshots": 8,
                "generated_screenshots": 8,
                "rgb_diff_reports": 8,
                "functional_parity": "PASS_SYNTHETIC",
                "visual_parity": "UNVERIFIED_DIFFERENCE_REPORTED",
                "rows": outcome["rows"],
                "auto_approved_site_rebuild": False,
            }
        # Check scope + all input bytes again after the last browser process.
        updated, owner_now, sites_now = read_p85_scope(scope, require_approval=True)
        if updated != data or owner_now != owner or sites_now != sites:
            raise WebsiteReviewError("Scope drifted before atomic publication")
        report = {
            "schema": SCHEMA,
            "product": "SITECRAFT AX",
            "status": "P85_SYNTHETIC_RESPONSIVE_REVIEW_HOLD",
            "sites": results,
            "total_observed_actions": sum(r["observed_steps"] for r in results.values()),
            "total_png_evidence": sum(r["reference_screenshots"] + r["generated_screenshots"] for r in results.values()),
            "total_rgb_difference_reports": sum(r["rgb_diff_reports"] for r in results.values()),
            "source_assets_reused": False,
            "original_websites_modified": False,
            "customer_identity_verified": False,
            "real_external_website": False,
            "commercial_release": "HOLD",
        }
        (bundle / "sitecraft_p85_report.json").write_text(
            json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8")
        publish_directory(bundle, dest)
    return {
        "product": "SITECRAFT AX",
        "gate": "P85_SYNTHETIC_RESPONSIVE_REVIEW_HOLD",
        "cases": sorted(results),
        "observed_browser_actions": report["total_observed_actions"],
        "visual_acceptance": "HUMAN_REVIEW_REQUIRED",
        "commercial_release": "HOLD",
        "published": dest.name,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="SITECRAFT P85 3 synthetic websites × 2 viewports × 3 actions")
    parser.add_argument("action", choices=("inspect", "build"))
    parser.add_argument("--scope", required=True, type=Path)
    parser.add_argument("--astra-root", required=True, type=Path)
    parser.add_argument("--fable-root", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.action == "inspect":
            result = inspect_three(args.scope, astra_root=args.astra_root)
        else:
            if args.fable_root is None or args.out is None:
                parser.error("build requires --fable-root and --out")
            result = build_three(args.scope, args.out, fable_root=args.fable_root,
                                 astra_root=args.astra_root)
    except (ValueError, OSError, RuntimeError, KeyError) as error:
        parser.exit(2, f"SITECRAFT_P85_HOLD: {type(error).__name__}: {error}\n")
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
