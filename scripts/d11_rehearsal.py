"""Three synthetic quote-to-delivery trials; neither orders nor customers.

This generates REAL zipped apps and runs their standalone extracted self-checks.
It does not invent human preparation hours or claim real customer acceptance.
Browser results are a separate evidence phase (scripts/d11_browser_rehearsal.py).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

from rea.delivery import create_delivery
from rea.provenance import inspect_delivery
from rea.safe_publish import publish_directory

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_FEATURES = frozenset({"list", "search", "category_filter", "detail", "simple_summary"})
UNSUPPORTED = ("cross_table_join", "customer_login", "payment", "live_sync",
               "production_hosting", "pixel_perfect_site_clone", "unlimited_support")
CASES = (
    {"case_id": "cafe", "domain": "local_cafe", "source": "qa_cafe.csv",
     "source_type": "CSV", "screen_count": 1,
     "selected_features": ("list", "search", "category_filter"),
     "expected_rows": 4, "filter_category": "음료", "filter_count": 2,
     "search": "카페라떼", "detail_title": "카페라떼"},
    {"case_id": "inventory", "domain": "local_inventory", "source": "qa_inventory.csv",
     "source_type": "CSV", "screen_count": 1,
     "selected_features": ("list", "search", "detail"),
     "expected_rows": 5, "filter_category": "저장장치", "filter_count": 2,
     "search": "NAS", "detail_title": "NAS HDD"},
    {"case_id": "trends", "domain": "local_trends", "source": "qa_trends.csv",
     "source_type": "CSV", "screen_count": 1,
     "selected_features": ("list", "category_filter", "simple_summary"),
     "expected_rows": 5, "filter_category": "JP", "filter_count": 2,
     "search": "실버", "detail_title": "JP 실버"},
)
LABOR_FIELDS = (
    "case_id", "operator", "prep_start", "prep_end", "prep_minutes",
    "build_start", "build_end", "build_minutes",
    "correction_start", "correction_end", "correction_minutes",
    "qa_start", "qa_end", "qa_minutes",
    "delivery_start", "delivery_end", "delivery_minutes",
    "total_manual_minutes", "notes", "actual_owner_signoff",
)


def validate_case(case: dict) -> None:
    features = case.get("selected_features")
    if (not isinstance(features, (list, tuple)) or len(features) > 3
            or len(features) < 1 or len(set(features)) != len(features)
            or not set(features) <= ALLOWED_FEATURES):
        raise ValueError("Offer contract permits at most three distinct supported features")
    screens = case.get("screen_count")
    if type(screens) is not int or screens not in (1, 2):
        raise ValueError("Offer contract permits 1-2 screens only")
    if case.get("source_type") != "CSV" or case.get("source") not in {
            "qa_cafe.csv", "qa_inventory.csv", "qa_trends.csv"}:
        raise ValueError("Synthetic fixture only; external customer data not allowed")
    if case.get("expected_rows", 0) <= 0:
        raise ValueError("Positive synthetic fixture row count required")


def _run_selfcheck(folder: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(folder / "self_check.py"), "--root", str(folder)],
        cwd=folder, capture_output=True, text=True, timeout=25,
    )
    if proc.returncode != 0:
        raise ValueError("Extracted delivery self-check failed (details retained locally)")
    result = json.loads(proc.stdout)
    if result.get("status") != "PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE":
        raise ValueError("Customer prerequisite self-check was not a safe PASS")
    return {
        "status": "PASS_SYNTHETIC_PREREQUISITES_ONLY",
        "database": result.get("database"),
        "integrity": result.get("integrity"),
        "row_count": result.get("row_count_only"),
    }


def _gate_matrix(case_id: str, evidence: dict) -> dict:
    """Subchecks are distinct from complete G0–G6 release-gate approvals."""
    return {
        "G0": {"status": "PARTIAL", "evidence": "Pinned vendor bytes checked in CI separately; rights unresolved"},
        "G1": {"status": "PARTIAL", "evidence": "Review-only adapter has synthetic regression; site rights not evaluated"},
        "G2": {"status": "PARTIAL", "evidence": "Synthetic UTF-8 source validated, not signed customer authorization"},
        "G3": {"status": "PASS_SYNTHETIC_SUBCHECK", "evidence": evidence["app_build"]},
        "G4": {"status": "PARTIAL_AWAITING_BROWSER", "evidence": "ZIP self-check PASS; extracted actual Chromium pending"},
        "G5": {"status": "BLOCKED", "evidence": "No authorized real reference, customer sign-off or timed manual labor"},
        "G6": {"status": "BLOCKED", "evidence": "Automated Windows diagnostics only; legal, clean human Windows and disaster recovery missing"},
    }


def make(out: Path) -> dict:
    """Safely publish precisely three independently validated synthetic orders."""
    out = Path(out).absolute()
    if out.exists() or out.is_symlink():
        raise FileExistsError("Rehearsal output already exists")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".rea-d11-", dir=out.parent) as temp:
        stage = Path(temp) / "rehearsal"
        stage.mkdir()
        cases = []
        for spec in CASES:
            validate_case(spec)
            source = ROOT / "samples" / spec["source"]
            sha = hashlib.sha256(source.read_bytes()).hexdigest()
            archive = stage / (spec["case_id"] + ".zip")
            create_delivery(source, archive, "Synthetic " + spec["case_id"])
            with zipfile.ZipFile(archive) as zf:
                built = json.loads(zf.read("app/manifest.json"))
            audit = inspect_delivery(archive)
            if (built["rows"] != spec["expected_rows"]
                    or audit["overall_commercial_clearance"] != "NOT_GRANTED"
                    or audit["source_kind"] != "customer_supplied_csv"):
                raise ValueError("Synthetic receipt/row integrity mismatch")
            with tempfile.TemporaryDirectory(prefix="rea-d11-extracted-") as extracted:
                root = Path(extracted)
                with zipfile.ZipFile(archive) as zf:
                    zf.extractall(root)
                checked = _run_selfcheck(root)
                if checked["row_count"] != spec["expected_rows"]:
                    raise ValueError("Extracted package row count mismatch")
            safe_record = {
                "case_id": spec["case_id"],
                "synthetic_customer": "FIXTURE_ONLY_NOT_REAL_PERSON",
                "data_ownership": "TEST_FIXTURE_ONLY",
                "authorization": "SYNTHETIC_FIXTURE_NO_CUSTOMER_PERMISSION_CLAIM",
                "price_krw_hypothesis": 300000,
                "quote_is_binding": False,
                "screen_count": spec["screen_count"],
                "selected_features": list(spec["selected_features"]),
                "available_extra_functions_not_contracted": sorted(
                    ALLOWED_FEATURES - set(spec["selected_features"])),
                "unsupported": list(UNSUPPORTED),
                "input_file_count": 1,
                "fixture_name": spec["source"],
                "fixture_sha256": sha,
                "data_rows": spec["expected_rows"],
                "customer_acceptance": "NOT_RUN",
                "manual_labor_minutes": None,
                "manual_correction_round": "NOT_RUN",
                "browser_acceptance": "NOT_RUN_IN_PACKAGING_PHASE",
                "output_zip": archive.name,
                "output_zip_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "evidence": {
                    "app_build": "PASS_SYNTHETIC_ROWS_AND_READONLY_ZIP",
                    "zip_sha256": audit["delivery_integrity"],
                    "unexpected_delivery_file_count": 0,
                    "extracted_selfcheck": checked,
                },
            }
            safe_record["gates"] = _gate_matrix(spec["case_id"], safe_record["evidence"])
            cases.append(safe_record)
        doc = {
            "schema_version": "rea.rehearsal.v0.1",
            "classification": "SYNTHETIC_THREE_CASE_REHEARSAL_ONLY",
            "commercial_clearance": "NOT_GRANTED",
            "reference_site_authorization": "NOT_RUN",
            "real_windows_non_developer": "NOT_RUN",
            "measured_manual_hours": None,
            "three_cases": cases,
            "three_case_count": len(cases),
            "overall_g0_g6_release": "BLOCKED",
            "browser_in_delivery_archive_proof": "NOT_RUN_IN_PACKAGING_PHASE",
            "human_log_required": True,
        }
        (stage / "acceptance_scorecard.json").write_text(
            json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        (stage / "MANUAL_TIME_LOG_BLANK.csv").write_text(
            ",".join(LABOR_FIELDS) + "\n", encoding="utf-8",
        )
        (stage / "README_KO.md").write_text(
            "# REA_Web 합성 주문 3건의 견적부터 납품까지 검증 (판매 금지)\n\n"
            "cafe.zip, inventory.zip, trends.zip은 각각 독립적인 로컬 웹앱입니다.\n"
            "acceptance_scorecard.json에 합성 자료의 기계적 테스트 근거가 있습니다.\n"
            "단일 화면과 사례별 계약 기능 3개만 견적 범위로 기재했습니다.\n"
            "생성된 앱이 기타 기능을 제공하더라도 계약에 포함됐다는 뜻은 아닙니다.\n"
            "시간기록 CSV는 열 제목만 있으며, 실제 사람이 준비·수정·QA·납품에 "
            "사용한 시작/종료시각과 분 단위 소요를 직접 기록해야 합니다.\n"
            "자동 CI 소요시간은 6~8시간 수익성 검증에 포함하지 마세요.\n"
            "검증 항목은 합성 데이터 전용이며 실제 고객, 실제 사이트 권한, "
            "Windows 일반 사용자, 보안, 라이선스 및 환불 조건은 미승인입니다.\n",
            encoding="utf-8",
        )
        publish_directory(stage, out)
    return doc


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Synthetic 3-case quote-to-delivery rehearsal; no customer data")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        result = make(args.out)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        p.exit(2, "REHEARSAL_REJECTED: " + type(exc).__name__ + "\n")
    print(json.dumps({
        "classification": result["classification"],
        "three_case_count": result["three_case_count"],
        "cases": [c["case_id"] for c in result["three_cases"]],
        "overall_g0_g6_release": result["overall_g0_g6_release"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
