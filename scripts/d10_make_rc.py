"""Make a test-only deterministic multi-option REA local delivery set.

All inputs are fixed synthetic repo samples; no customer files or network.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from rea.delivery import create_delivery
from rea.guided import preflight
from rea.provenance import inspect_delivery
from rea.safe_publish import publish_directory
from rea.two_source import preflight_pair, pack_pair

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_OPTIONS = ("01_single_csv.zip", "02_guided_json.zip", "03_two_source_append.zip")


def make(out: Path) -> dict:
    out = Path(out).absolute()
    if out.exists() or out.is_symlink():
        raise FileExistsError("RC folder must not already exist")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".rea-rc-staging-", dir=out.parent) as temp:
        stage = Path(temp) / "rc"
        stage.mkdir()
        csv = ROOT / "samples" / "qa_cafe.csv"
        guided = ROOT / "samples" / "qa_guided.json"
        first = ROOT / "samples" / "qa_guided.csv"
        second = ROOT / "samples" / "qa_pair_extra.json"
        create_delivery(csv, stage / REQUIRED_OPTIONS[0], "REA synthetic single CSV")
        create_delivery(
            guided, stage / REQUIRED_OPTIONS[1], "REA synthetic owner guided JSON",
            approved_mapping={"id": "item_code", "title": "label", "category": "region"},
            expected_source_sha256=preflight(guided)["source_sha256"],
        )
        preview = preflight_pair(first, second)
        pack_pair(
            first, second, stage / REQUIRED_OPTIONS[2], "REA synthetic two source append",
            {"id": "sku", "title": "display_name", "category": "group_name"},
            preview["sources"][0]["sha256"], preview["sources"][1]["sha256"],
            "APPROVE", "APPROVE", "APPEND",
        )
        entries = []
        for filename, expected_mode in zip(
            REQUIRED_OPTIONS,
            ("single_source", "owner_guided_one_source", "explicit_same_schema_row_append"),
        ):
            path = stage / filename
            report = inspect_delivery(path)
            if report["overall_commercial_clearance"] != "NOT_GRANTED":
                raise ValueError("Commercial clearance was incorrectly granted")
            if report["two_file_append_receipt_present"] != (expected_mode.endswith("row_append")):
                raise ValueError("Wrong two-source receipt in demo delivery")
            if report["owner_mapping_receipt_present"] != (expected_mode == "owner_guided_one_source"):
                raise ValueError("Wrong owner mapping receipt in demo delivery")
            entries.append({
                "filename": filename,
                "mode": expected_mode,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
                "integrity": report["delivery_integrity"],
                "contains_original_vendor_engine": False,
            })
        manifest = {
            "schema_version": "rea.rc.v0.1",
            "classification": "SYNTHETIC_LOCAL_TEST_ONLY_NOT_FOR_SALE",
            "source_kind": "SYNTHETIC_ONLY",
            "compliance": "NOT_CLEARED",
            "commercial_product_scope": "NOT_APPROVED",
            "packages": entries,
            "unverified": [
                "third_party_licenses_and_generated_source_rights",
                "clean_non_developer_windows_machine",
                "real_customer_reference_and_data_rights",
                "full_security_privacy_disaster_recovery",
                "business_contract_join_scope_and_support",
            ],
        }
        (stage / "rc_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8")
        (stage / "README_KO.md").write_text(
            "# REA_Web 합성 데이터 시험용 납품 후보 (판매 금지)\n\n"
            "01_single_csv.zip : 단일 CSV 예시\n"
            "02_guided_json.zip : 사용자가 직접 선택한 필드 매핑 JSON 예시\n"
            "03_two_source_append.zip : 동일 컬럼 구조 두 파일의 명시적 행 추가\n\n"
            "각 ZIP은 별도로 새 폴더에 압축 해제합니다. Windows에서는 "
            "check_windows.cmd를 먼저 실행하여 Python/라이브러리/파일을 확인한 뒤 "
            "launch_windows.cmd를 실행합니다. 인터넷 업로드와 자동 설치는 없습니다.\n\n"
            "상용 라이선스, 실제 고객 데이터 처리, 일반 Windows 사용자 설치 및 "
            "두 파일의 다른 스키마 조인은 승인되지 않았습니다.\n"
            "rc_manifest.json은 ZIP SHA256을 기록하지만 디지털 서명은 아닙니다.\n",
            encoding="utf-8",
        )
        publish_directory(stage, out)
    return manifest


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Synthetic test-only 3 delivery modes")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        report = make(args.out)
    except (OSError, ValueError) as exc:
        p.exit(2, f"RC_STAGING_FAILED: {exc}\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
