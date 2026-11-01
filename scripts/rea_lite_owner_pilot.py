"""Build a deterministic, entirely fictional REA Lite three-theme owner pilot ZIP.

No customer data; never publish this artifact for sale. No overwrite.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import zipfile

from rea.lite_builder import build, inspect, THEMES
from rea.mvp import parse_input

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"
MAPPING = {"id": "item_code", "title": "item_name", "category": "group"}
SYNTHETIC_FILES = {
    "cafe": "rea_lite_cafe_synthetic.csv",
    "inventory": "rea_lite_inventory_synthetic.csv",
    "office": "rea_lite_office_synthetic.csv",
}
UPDATE_FILES = {
    "cafe": "rea_lite_cafe_update.csv",
    "inventory": "rea_lite_inventory_update.csv",
    "office": "rea_lite_office_update.csv",
}
README = """REA_WEB Lite 합성자료 전용 Windows 오프라인 검수 ZIP

※ 판매·납품·실고객 자료용이 아닙니다. 자료는 전부 가상 데이터입니다.
※ 고객 PC에 Python/서버/계정/API 연결이 필요하지 않습니다.

1. 압축 해제 후 해당 테마의 cafe.html, inventory.html, office.html을
   Windows Edge 또는 Chrome으로 더블클릭해 열어보세요.
2. 검색·카테고리·항목 상세를 확인하세요.
3. CSV 파일 변경에서 updates/cafe_update.csv 등 이름이 대응하는
   합성 CSV를 선택하고 갱신 성공을 확인하세요.
4. '변경 내용 HTML로 저장'을 눌러 새 HTML을 다운로드하세요.
5. 다운로드된 새 HTML을 다시 열어 변경된 항목이 남았는지 확인하세요.
6. 기존 HTML/CSV 원본은 덮어쓰지 않습니다.
7. Console/Network 오류와 렌더링·한글·Windows 사용성을 별도로 확인하세요.

HTML 안에 데이터가 평문으로 포함됩니다. 개인/민감 정보 입력과
공개 서버 업로드는 하지 마세요.
SHA256SUMS.json과 MANIFEST.json은 패키지 내부 검수용입니다.
정식 판매 전 실기기 검수/라이선스·원본 권리/지원·환불·개인정보
처리방침과 사용자 명시 승인이 필요합니다.
"""


def _digest(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def create(out: Path) -> dict:
    out = Path(out)
    if out.suffix.lower() != ".zip" or out.exists() or out.is_symlink():
        raise ValueError("Use a new .zip path; never overwrite an existing bundle")
    out.parent.mkdir(parents=True, exist_ok=True)
    entries = {"README_FIRST_KO.txt": README.encode("utf-8")}
    source_sha = {}
    with tempfile.TemporaryDirectory(prefix="rea-lite-pilot-", dir=out.parent) as tmp:
        tmpdir = Path(tmp)
        for theme in THEMES:
            src = SAMPLES / SYNTHETIC_FILES[theme]
            update = SAMPLES / UPDATE_FILES[theme]
            info = inspect(src)
            source_sha[theme] = info["sha256"]
            columns, _rows = parse_input(src)
            update_columns, _update_rows = parse_input(update)
            if columns != update_columns:
                raise ValueError(f"Update sample schema mismatch: {theme}")
            dest = tmpdir / f"{theme}.html"
            receipt = build(
                src, dest, mapping=MAPPING, approved_sha=info["sha256"],
                confirmation="APPROVE", title=f"합성 {theme} 카탈로그", theme=theme,
            )
            if receipt["status"] != "CREATED_UNAPPROVED_FOR_SALE":
                raise ValueError("Unexpected application sale status")
            entries[f"{theme}.html"] = dest.read_bytes()
            entries[f"updates/{theme}_update.csv"] = update.read_bytes()
        manifest = {
            "schema": "rea-lite.owner-synthetic-pilot.v1",
            "status": "PILOT_ONLY_NOT_APPROVED_FOR_SALE",
            "contains_real_customer_data": False,
            "requires_browser": True,
            "requires_customer_python": False,
            "themes": list(THEMES),
            "source_sha256": source_sha,
            "files": {key: _digest(value) for key, value in sorted(entries.items())},
        }
        entries["MANIFEST.json"] = (
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        ).encode("utf-8")
        entries["SHA256SUMS.json"] = (
            json.dumps({key: _digest(value) for key, value in sorted(entries.items())},
                       ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        ).encode("utf-8")
        staged = tmpdir / "rea-lite-owner.zip"
        with zipfile.ZipFile(staged, "w", compression=zipfile.ZIP_DEFLATED,
                             allowZip64=False) as archive:
            for name, blob in sorted(entries.items()):
                item = zipfile.ZipInfo(name, date_time=(2026, 11, 1, 0, 0, 0))
                item.compress_type = zipfile.ZIP_DEFLATED
                item.create_system = 3
                item.external_attr = 0o100644 << 16
                archive.writestr(item, blob)
        try:
            os.link(staged, out)  # exclusive creation: never replace an existing ZIP
        except FileExistsError as exc:
            raise ValueError("Output appeared concurrently; overwrite refused") from exc
    return {"status": "PILOT_ONLY_NOT_APPROVED_FOR_SALE",
            "sha256": _digest(out.read_bytes()), "bytes": out.stat().st_size,
            "files": len(entries), "path": str(out)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(create(args.out), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"REA_LITE_PILOT_BLOCKED: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
