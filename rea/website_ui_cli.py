"""REA_Web P95: safe read-only observation preview / owner-approved local build.

Usage:
 python -m rea.website_ui_cli inspect --reference-html ... --fixture-sha256 ... --p85-receipt ...
 python -m rea.website_ui_cli build --reference-html ... --fixture-sha256 ... --p85-receipt ... --existing-app ... --decision ... --approved-ui-contract-sha256 ... --owner-approval APPROVE_SYNTHETIC_LAYOUT_ONLY --out NEW_DIR
Records from original frozen Fable 5.1 are optional, paired with original SHA.
Never connects to public websites or grants rights/production authorization.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rea.website_component_builder import observed_contract, build_evidence_ui
from rea.website_p95 import inspect_fable_record, _json_file


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="REA original website: Astra observed UI -> independent reviewed Pro components")
    parser.add_argument("action", choices=["inspect", "build"])
    parser.add_argument("--reference-html", type=Path, required=True)
    parser.add_argument("--fixture-sha256", required=True)
    parser.add_argument("--p85-receipt", type=Path, required=True)
    parser.add_argument("--fable-record", type=Path)
    parser.add_argument("--fable-record-sha256")
    parser.add_argument("--existing-app", type=Path)
    parser.add_argument("--decision", type=Path)
    parser.add_argument("--approved-ui-contract-sha256")
    parser.add_argument("--owner-approval", default="")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if bool(args.fable_record) != bool(args.fable_record_sha256):
        parser.error("Fable Record and exact SHA256 must be supplied together")
    try:
        record = (inspect_fable_record(args.fable_record,
                                      expected_sha256=args.fable_record_sha256)
                  if args.fable_record else None)
        receipt = _json_file(args.p85_receipt)
        contract, semantic = observed_contract(
            args.reference_html, fixture_sha256=args.fixture_sha256,
            p85_receipt=receipt, fable_record_summary=record)
        if args.action == "inspect":
            result = {"status": "REVIEW_REQUIRED",
                      "contract": contract, "proposed_layout": semantic["proposed_preset"]}
        else:
            if not (args.existing_app and args.decision and args.out
                    and args.approved_ui_contract_sha256):
                parser.error("build requires existing app, owner opinion, new destination and approved SHA")
            result = build_evidence_ui(
                args.existing_app, args.out, reference_html=args.reference_html,
                fixture_sha256=args.fixture_sha256, p85_receipt=receipt,
                decision_record=args.decision,
                approved_ui_contract_sha256=args.approved_ui_contract_sha256,
                owner_approval=args.owner_approval, fable_record_summary=record)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (ValueError, OSError, RuntimeError) as exc:
        parser.exit(2, f"REA_SITE_HOLD: {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
