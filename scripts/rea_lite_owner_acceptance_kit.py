"""Create a synthetic REA Lite owner acceptance kit; no customer data or sale approval.

An atomic, no-overwrite folder containing 3 offline HTMLs, valid/invalid CSV
fixtures, a checksum inventory and a human checklist with all fields blank.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import zipfile

from rea.lite_builder import build
from rea.mvp import source_sha256
from rea.safe_publish import publish_directory

_THEMES = ("cafe", "inventory", "office")
_BASE_CSV_BY_THEME = {
    "cafe": (
        "id,title,category,price\n"
        "S01,콜드브루,음료,4000\n"
        "S02,카페라떼,음료,4800\n"
        "S03,치즈케이크,디저트,6500\n"
    ),
    "inventory": (
        "id,title,category,price\n"
        "S01,USB-C 케이블,전자제품,12000\n"
        "S02,무선 마우스,전자제품,23000\n"
        "S03,노트북 거치대,사무용품,31000\n"
    ),
    "office": (
        "id,title,category,price\n"
        "S01,주간 업무보고,보고서,0\n"
        "S02,프로젝트 일정표,일정,0\n"
        "S03,팀 회의록,회의,0\n"
    ),
}
_VALID_CSV = (
    "id,title,category,price\n"
    "N01,NEW_CHECK_ITEM,Drink,100\n"
    "N02,SECOND_CHECK_ITEM,Office,200\n"
)
_DUPLICATE_CSV = (
    "id,title,category,price\n"
    "D01,Wrong,Drink,100\n"
    "D01,Duplicate,Drink,200\n"
)
_WRONG_HEADER_CSV = "id,title,category,amount\nN01,Wrong column,Drink,100\n"
_CHECKLIST = """REA_WEB Lite | Windows 사용자 검수표 (합성 데이터 전용)

이 패키지는 판매용이 아닙니다. 고객정보·개인정보·민감정보는 사용 금지입니다.
인터넷, Python 설치, 서버, 관리자 권한은 필요하지 않습니다.
원본 ZIP 및 기존 HTML 파일은 수정하지 마세요.

한 번만 수행하는 실제 검수 절차
1. ZIP을 새로운 폴더에 압축 해제합니다.
2. cafe.html을 더블클릭하여 Chrome 또는 Edge로 엽니다.
   항목 3개, '콜드브루' 검색, 상세 보기를 확인합니다.
3. duplicate_id.csv를 선택하고 'CSV 검증 후 적용'을 누릅니다.
   중복 ID가 거부되고 원래 항목 3개가 남아야 합니다.
4. wrong_columns.csv도 같은 방법으로 적용해 거부되는지 확인합니다.
5. valid_update.csv를 적용합니다.
   항목 2개와 NEW_CHECK_ITEM 표시를 확인합니다.
6. '갱신된 HTML 다운로드'를 누르고 내려받은 새 HTML을 다시 엽니다.
   항목 2개와 NEW_CHECK_ITEM이 유지되어야 합니다.
7. 필요한 경우 inventory.html 및 office.html 테마를 확인합니다.
8. 보안 정책으로 file:// 열기가 차단되면 BLOCKED로 기록합니다.
   관리자 권한이나 보안 정책 우회는 하지 않습니다.

직접 실행한 검수자만 아래 결과를 작성하세요.
검수 일시(KST): ____________________
Windows 버전: ______________________
브라우저 및 버전: ___________________
오프라인 HTML 열기: PASS / FAIL / BLOCKED / NOT_RUN
검색 및 상세 보기: PASS / FAIL / NOT_RUN
오류 CSV 거부 및 기존 데이터 보존: PASS / FAIL / NOT_RUN
정상 CSV 적용: PASS / FAIL / NOT_RUN
새 HTML 다운로드 후 다시 열기: PASS / FAIL / NOT_RUN
오류(개인정보/사용자 경로 제외): ___________________________
실제 사용자 소요시간(분): ________ 또는 NOT_MEASURED
최종 검수: PASS / FAIL / BLOCKED / NOT_RUN

미실시 항목을 자동 PASS로 처리하지 마세요. 본 검수와 상용 판매 승인은 별개입니다.
"""
_README = """REA_WEB Lite | Windows 오프라인 검수 패키지

CHECKLIST_KO.txt를 읽고 한 번만 실제 검수를 수행하세요.
- cafe.html / inventory.html / office.html: 서로 다른 업종별 합성 데이터와 색상의 오프라인 웹앱 3종
- duplicate_id.csv: 중복 ID 오류(반드시 거부)
- wrong_columns.csv: 열 구성 오류(반드시 거부)
- valid_update.csv: 정상 갱신 파일
- SHA256SUMS.txt: 이 파일을 제외한 9개 파일 무결성 해시
- MANIFEST.json: 자동 검증·실사용 및 판매 승인 상태

모두 합성 데이터입니다. 고객정보·민감정보 입력 및 전송을 금지합니다.
원본 HTML은 갱신 후에도 변경되지 않습니다.
새 버전 보관은 '갱신된 HTML 다운로드'를 통해 진행하세요.
내장 데이터는 Base64로 인코딩된 평문이며 암호화되어 있지 않습니다.
판매·저작권·개인정보 처리 승인 없이 유료 납품하지 마세요.
"""
_FILES = frozenset({
    "cafe.html", "inventory.html", "office.html",
    "valid_update.csv", "duplicate_id.csv", "wrong_columns.csv",
    "README_FIRST.txt", "CHECKLIST_KO.txt", "MANIFEST.json", "SHA256SUMS.txt",
})
_RE_DATA = re.compile(rb'<script id="rea-data" type="application/octet-stream">([^<]+)</script>')


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def verify_kit(folder: Path) -> dict:
    """Check fixed inventory, checksums and actual embedded synthetic records."""
    folder = Path(folder)
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError("Kit must be a regular directory")
    names = {p.name for p in folder.iterdir()}
    if names != _FILES or any(not p.is_file() or p.is_symlink() for p in folder.iterdir()):
        raise ValueError("Unexpected or missing kit files")
    expected = {}
    for line in (folder / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        if not match or match[2] in expected:
            raise ValueError("Invalid checksum inventory")
        expected[match[2]] = match[1]
    if set(expected) != names - {"SHA256SUMS.txt"}:
        raise ValueError("Checksum inventory incomplete")
    for name, sha in expected.items():
        if _sha((folder / name).read_bytes()) != sha:
            raise ValueError(f"Integrity mismatch: {name}")
    manifest = json.loads((folder / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest != {
        "schema": "rea.lite.owner.acceptance.synthetic.v1",
        "synthetic_only": True,
        "human_windows_acceptance": "NOT_RUN",
        "commercial_release": "NOT_APPROVED",
        "themes": list(_THEMES),
        "embedded_rows_per_html": 3,
    }:
        raise ValueError("Manifest/approval flags invalid")
    for theme in _THEMES:
        html = (folder / f"{theme}.html").read_bytes()
        m = _RE_DATA.search(html)
        if not m or b"connect-src 'none'" not in html:
            raise ValueError(f"Missing embedded data/offline CSP in {theme}")
        data = json.loads(base64.b64decode(m[1], validate=True))
        if data.get("theme") != theme or len(data.get("records", [])) != 3:
            raise ValueError(f"Invalid synthetic data in {theme}")
        first = data["records"][0]
        expected_first = {"cafe": "콜드브루", "inventory": "USB-C 케이블", "office": "주간 업무보고"}
        if first["id"] != "S01" or first["title"] != expected_first[theme]:
            raise ValueError(f"Unexpected theme-specific synthetic fixture in {theme}")
        if len({row["title"] for row in data["records"]}) != 3:
            raise ValueError(f"Duplicate synthetic titles in {theme}")
    return {"status": "SYNTHETIC_OWNER_KIT_VERIFIED",
            "files": len(_FILES), "html_themes": len(_THEMES),
            "human_windows_acceptance": "NOT_RUN", "commercial_release": "NOT_APPROVED"}


def build_kit(destination: Path) -> dict:
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Kit destination exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".rea-lite-owner-kit-", dir=destination.parent))
    try:
        src = stage / "source.csv"
        for theme in _THEMES:
            src.write_text(_BASE_CSV_BY_THEME[theme], encoding="utf-8", newline="")
            digest = source_sha256(src)
            build(src, stage / f"{theme}.html", name=f"REA Lite Synthetic {theme}",
                  theme=theme, approval="APPROVE", expected_source_sha256=digest)
        src.rename(stage / "base.csv.tmp")
        (stage / "base.csv.tmp").unlink()
        for filename, data in (
            ("valid_update.csv", _VALID_CSV),
            ("duplicate_id.csv", _DUPLICATE_CSV),
            ("wrong_columns.csv", _WRONG_HEADER_CSV),
            ("README_FIRST.txt", _README),
            ("CHECKLIST_KO.txt", _CHECKLIST),
        ):
            (stage / filename).write_text(data, encoding=("utf-8-sig" if filename in {"README_FIRST.txt", "CHECKLIST_KO.txt"} else "utf-8"), newline="\n")
        manifest = {
            "schema": "rea.lite.owner.acceptance.synthetic.v1",
            "synthetic_only": True,
            "human_windows_acceptance": "NOT_RUN",
            "commercial_release": "NOT_APPROVED",
            "themes": list(_THEMES),
            "embedded_rows_per_html": 3,
        }
        (stage / "MANIFEST.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        hashes = [f"{_sha((stage / name).read_bytes())}  {name}" for name in sorted(_FILES - {"SHA256SUMS.txt"})]
        (stage / "SHA256SUMS.txt").write_text("\n".join(hashes) + "\n", encoding="utf-8")
        verification = verify_kit(stage)
        publish_directory(stage, destination)
        return verification
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def archive_kit(folder: Path, zip_path: Path) -> None:
    """Create a fresh ZIP, refuse overwrite, read back every member."""
    verify_kit(folder)
    zip_path = Path(zip_path).absolute()
    if zip_path.exists() or zip_path.is_symlink():
        raise FileExistsError(f"ZIP destination exists: {zip_path}")
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "x", compression=zipfile.ZIP_DEFLATED) as z:
        for name in sorted(_FILES):
            z.write(folder / name, arcname=name)
    with zipfile.ZipFile(zip_path) as z:
        if set(z.namelist()) != _FILES or z.testzip() is not None:
            raise ValueError("ZIP inventory or CRC failed")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build synthetic-only Windows owner acceptance kit")
    ap.add_argument("--out", type=Path, required=True, help="NEW output folder")
    ap.add_argument("--zip", dest="zip_path", type=Path, help="NEW ZIP path")
    args = ap.parse_args(argv)
    if args.zip_path and (args.zip_path.exists() or args.zip_path.is_symlink()):
        ap.error("ZIP already exists")
    result = build_kit(args.out)
    if args.zip_path:
        archive_kit(args.out, args.zip_path)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
