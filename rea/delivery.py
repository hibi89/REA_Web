"""Deterministic local delivery ZIP for an offline generated REA app.

Packages generated app and launch instructions. Never includes Fable original
capture or upstream vendor engine. This is not a commercial release gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import stat
import zipfile

from rea.orchestrator import build
from rea.safe_publish import publish_archive

SCHEMA = "rea.delivery.v0.1"
FIXED_DATE = (2026, 1, 1, 0, 0, 0)
MAX_ARCHIVE_BYTES = 25 * 1024 * 1024
# Prefer a usable "python" command; fall back to installed "py -3".
# Never install Python or infer a user machine's executable path.
PYTHON_VERSION_PROBE = 'import sys;sys.exit(0 if sys.version_info[:2]>=(3,11) else 1)'
LAUNCH = "\r\n".join([
    "@echo off",
    "setlocal EnableExtensions DisableDelayedExpansion",
    "chcp 65001 >nul",
    'set "PYTHONIOENCODING=utf-8"',
    "rem Never expand REA_WEB_PORT in CMD; Python owns safe localhost argv.",
    'call python -c "' + PYTHON_VERSION_PROBE + '" >nul 2>nul',
    "if not errorlevel 1 goto launch_python",
    'call py -3 -c "' + PYTHON_VERSION_PROBE + '" >nul 2>nul',
    "if not errorlevel 1 goto launch_py",
    "goto missing_python",
    ":launch_python",
    'call python "%~dp0self_check.py" --launch',
    'set "_rea_launch_code=%ERRORLEVEL%"',
    "goto launch_result",
    ":launch_py",
    'call py -3 "%~dp0self_check.py" --launch',
    'set "_rea_launch_code=%ERRORLEVEL%"',
    "goto launch_result",
    ":missing_python",
    "echo [REA] MISSING_PYTHON: No usable Python 3.11+ found with 'python' or 'py -3'. Add it to PATH or repair its launcher. Nothing was installed.",
    'set "_rea_launch_code=10"',
    ":launch_result",
    'if "%_rea_launch_code%"=="0" goto launch_done',
    "echo [REA] Startup stopped. Follow the recovery steps shown above.",
    "pause",
    ":launch_done",
    "exit /b %_rea_launch_code%",
    "",
])
CHECK_LAUNCH = "\r\n".join([
    "@echo off",
    "setlocal EnableExtensions DisableDelayedExpansion",
    "chcp 65001 >nul",
    'set "PYTHONIOENCODING=utf-8"',
    "rem No-arg double-click shows diagnostic; --check exits without pause.",
    'if not "%~2"=="" goto invalid',
    'if "%~1"=="" goto check',
    'if /I "%~1"=="--check" goto check',
    "goto invalid",
    ":check",
    'call python -c "' + PYTHON_VERSION_PROBE + '" >nul 2>nul',
    "if not errorlevel 1 goto check_python",
    'call py -3 -c "' + PYTHON_VERSION_PROBE + '" >nul 2>nul',
    "if not errorlevel 1 goto check_py",
    "echo [REA] MISSING_PYTHON: No usable Python 3.11+ found with 'python' or 'py -3'. Add it to PATH or repair its launcher. Nothing was installed.",
    'set "_rea_check_code=10"',
    "goto finished",
    ":check_python",
    'call python "%~dp0self_check.py" --customer-check',
    'set "_rea_check_code=%ERRORLEVEL%"',
    "goto finished",
    ":check_py",
    'call py -3 "%~dp0self_check.py" --customer-check',
    'set "_rea_check_code=%ERRORLEVEL%"',
    "goto finished",
    ":invalid",
    "echo [REA] INVALID_ARGUMENT: Double-click or run check_windows.cmd --check.",
    "exit /b 2",
    ":finished",
    'if not "%_rea_check_code%"=="0" echo [REA] LOCAL_PREREQUISITES_NOT_VERIFIED. Do not launch the app.',
    'if "%~1"=="" (',
    "  echo [REA] Read the diagnostic above. This is NOT human or commercial acceptance.",
    "  pause",
    ")",
    "exit /b %_rea_check_code%",
    "",
])
WINDOWS_README = """# REA_Web 로컬 웹앱 Windows 시작 안내

**NOT commercially approved.** 아래 절차는 납품된 폴더 안의 앱을 본인 PC에서
실행하기 위한 안내입니다. 이 ZIP은 설치 프로그램이나 단독 EXE가 아닙니다.

## 1. 압축 해제와 사전 검사

1. ZIP 원본을 보관하고, 전체 ZIP을 쓰기 가능한 위치의 **새 빈 폴더**에 풉니다.
   예: `문서\\REA 앱`. ZIP 안 파일만 따로 옮기지 마세요.
2. Windows 탐색기에서 **double-click check_windows.cmd**를 실행합니다.
   창에 검사 결과가 표시되고 키 입력을 기다립니다. 명령 프롬프트에서 자동화할
   때는 `check_windows.cmd --check`를 사용하면 같은 검사를 하고 바로 종료합니다.
   이 검사는 서버를 열거나 패키지를 설치하지 않습니다.
3. `PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE`이면 파일 무결성, SQLite
   읽기 가능 여부, Python 및 필수 패키지만 확인된 것입니다. 실제 고객 검수,
   개인정보 적합성 또는 상용 권리 승인은 뜻하지 않습니다.
4. 검사 실패 시 `launch_windows.cmd`를 실행하지 마세요. 안내된 조치 후 다시 검사하세요.

## 2. Python 및 패키지 확인

Python 3.11 이상이 필요합니다. 두 실행기는 같은 Python을 선택합니다. 먼저 PATH의
`python`이 3.11 이상인지 확인하고, 없거나 낮은 버전이면 Windows launcher "py -3"
를 확인합니다. 어느 쪽도 사용할 수 없으면 `MISSING_PYTHON` (exit 10)으로 끝나며
아무것도 설치하지 않습니다. Python 3.11 이상을 사용자 계정에 설치하고 새 CMD 창을 여세요.

패키지가 없다고 표시되면 먼저 명령 프롬프트에서 버전을 확인하세요.

```bat
python -c "import sys; print(sys.executable); print(sys.version)"
py -3 -c "import sys; print(sys.executable); print(sys.version)"
```

`python`이 3.11 이상이면 첫 번째 명령을, 그렇지 않고 `py -3`가 3.11 이상이면
두 번째 명령을 실행해 **검사기가 선택하는 같은 Python 환경**에 설치합니다.
따라서 위에서 버전을 확인한 동일한 Python 실행기를 사용해 패키지를 설치해야 합니다.

```bat
python -m pip install --user -r app\\requirements.txt
py -3 -m pip install --user -r app\\requirements.txt
```

이미 가상환경을 활성화했다면 그 상태를 유지하고 `--user`를 빼세요. 설치에는
인터넷이 필요할 수 있으며 사용자가 직접 결정해야 합니다. 사전검사는 pip를 실행하거나
네트워크에 접속하지 않습니다. 설치 후 `check_windows.cmd --check`를 다시 실행하세요.

## 3. 실행, 검색, 종료, 재실행

검사가 통과한 뒤 `launch_windows.cmd`를 더블클릭합니다. 브라우저에서
`http://127.0.0.1:8000/`을 엽니다. 앱은 현재 PC 안에서만 동작하며 외부 웹사이트로
공개되지 않습니다. 브라우저를 닫고 서버 창에서 `Ctrl+C`를 눌러 종료합니다.
다시 쓸 때 실행기를 시작하면 SQLite 데이터가 남아 있습니다. 앱은 읽기 전용이며
데이터 편집·백업 기능은 제공하지 않습니다.

백업이 필요하면 서버를 먼저 종료하고 압축 해제 폴더 전체를 **검사 폴더 밖의
비공개 위치**에 복사하세요. `app\\data.sqlite`에는 입력 데이터가 들어 있습니다.
검사 폴더 안에 백업 파일을 두면 추가 파일로 거부될 수 있습니다. 손상된 파일은
직접 덮어쓰지 말고, 보관한 원본 ZIP을 새 빈 폴더에 다시 풀어 복구하세요.

목록에서 검색, 카테고리 필터, 상세 보기를 사용할 수 있습니다. 보이는 내용은
납품된 데이터에 따라 달라집니다. 한글 CSV/JSON은 UTF-8 입력을 전제로 합니다.

## 4. 자주 발생하는 문제와 복구

| 표시/증상 | 조치 |
| --- | --- |
| `MISSING_PYTHON` 또는 exit 10 | 사용 가능한 Python 3.11+를 `python` 또는 Windows launcher `py -3`에서 찾지 못했습니다. 설치되어 있다면 PATH 또는 launcher 구성을 확인한 뒤 새 CMD에서 다시 검사하세요. 미설치 상태라면 Python 3.11+를 설치하세요. 납품기가 자동 설치하지는 않습니다. |
| `MISSING_INSTALL_REQUIRED` 패키지 누락 | 위 Python 버전을 확인하고 같은 실행기에서 pip 명령을 실행한 뒤 다시 검사하세요. 설치가 싫거나 실패하면 ZIP을 보존하고 지원을 요청하세요. |
| `VERSION_OUT_OF_RANGE` | 필수 패키지가 지원 버전 범위를 벗어났습니다. CMD에서 `python` 실행기를 쓰면 `python -m pip install --user --upgrade -r app\\requirements.txt`, Windows launcher만 쓰면 `py -3 -m pip install --user --upgrade -r app\\requirements.txt`를 실행하고 다시 검사하세요. 오류가 계속되면 ZIP을 보존하고 지원을 요청하세요. |
| 무결성, 파일 개수, SQLite 검사 실패 | 원본 ZIP을 보존하세요. 실패한 폴더 파일을 고치거나 삭제하지 말고, 원본 ZIP 전체를 **다른 새 빈 폴더**에 다시 압축 해제해 검사하세요. 원본 ZIP도 손상됐다면 납품자에게 재전달을 요청하세요. |
| 압축 해제 위치/접근 거부 | 사용자 문서 폴더처럼 쓰기 권한이 있는 짧은 로컬 경로를 사용하세요. `Program Files`, 네트워크 드라이브, 동기화 중인 폴더는 피하세요. |
| `REA_LOCAL_PORT_UNAVAILABLE` 또는 포트 8000 사용 중 | 실행기는 서버 시작 전 포트 충돌을 검사하고 복구 방법을 표시합니다. 다른 앱을 종료하거나 CMD에서 `set REA_WEB_PORT=8765` 입력 후 `launch_windows.cmd`를 실행하고 `http://127.0.0.1:8765/`를 여세요. 허용 포트는 1~65535 숫자입니다. 오류 창은 키를 누를 때까지 유지됩니다. |
| 브라우저가 열리지 않음 | 주소를 직접 입력하세요. 서버 창이 실행 중이어야 합니다. 서버를 중지했다면 다시 실행하세요. |
| 한글이 깨지거나 CSV를 읽지 못함 | 원본을 보존하고 UTF-8로 다시 내보낸 복사본을 사용하세요. 확장자만 바꾸거나 원본을 덮어쓰지 마세요. 데이터 변환은 납품자와 범위를 먼저 정하세요. |

검사기는 추출 폴더 안의 추가 파일·숨김 파일·심볼릭 링크를 거부합니다. 매니페스트나
앱 파일을 직접 수정하지 마세요. SHA256 일치는 게시자 서명이나 저작권 허가가 아닙니다.
오류 문의에는 오류 코드와 Python 버전만 보내고, 실제 CSV, SQLite, 비밀번호 또는
개인정보를 공개 채널에 첨부하지 마세요.

기능 인수는 `ACCEPTANCE_CHECKLIST.md`를 사용해 실제로 확인한 뒤 기록하세요. 확인하지
않은 항목은 완료로 표시하지 마세요. 문제 재현에는 고객 행의 실제 값을 넣지 마세요.

## 5. 지원 범위와 제한

생성 흐름은 고객 제공 CSV 또는 flat JSON 배열을 받습니다. 같은 구조의 두 입력은
사용자가 각각 승인한 경우에만 **ROW APPEND**합니다. 서로 다른 테이블의 자동 JOIN,
임의 사이트 복제, 실시간 동기화, 로그인·결제, 호스팅·배포는 지원하지 않습니다.
제작 GUI는 프로젝트 제작 도구에 있으며 납품 ZIP은 결과 웹앱입니다.

납품 ZIP은 **암호화되지 않았으며**, `app\\data.sqlite`에 입력 행 전체가 포함됩니다. ZIP·앱 파일에 개인/민감정보, 비밀번호, 토큰 또는 제3자 비공개 자료를 넣지 마세요. 전달·보관 시 승인된 비공개 경로를 사용하세요. 자동 백업,
데이터 편집, 계정, 외부 공개 서버는 없습니다. 원본 데이터와 ZIP은 고객이 별도로
안전하게 보관해야 합니다. 실제 고객 검수, 소스 재배포 라이선스, 개인정보·보안 검토,
환불/지원 약관은 별도 확인이 필요하며 아직 상용 승인되지 않았습니다.
"""

DELIVERY_ACCEPTANCE = """# 납품 앱 검수 체크리스트

이 체크리스트는 납품된 결과를 고객이 직접 확인하기 위한 기록지입니다. 합성 테스트나
사전검사 통과가 고객의 실제 검수를 대신하지 않습니다. 확인하지 않은 항목은 비워 두세요.

## 실행 전

- [ ] 전달받은 원본 ZIP을 보관했습니다.
- [ ] ZIP 전체를 새 빈 폴더에 압축 해제했습니다.
- [ ] `check_windows.cmd` 결과가 `PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE`입니다.
- [ ] 합의한 입력 파일명·행 수·화면·기능을 별도 작업 합의서와 대조했습니다.

## 기능 확인

- [ ] `launch_windows.cmd` 실행 후 `http://127.0.0.1:8000/` 페이지가 열립니다.
- [ ] 화면의 전체 행 수가 합의한 샘플/입력과 맞습니다.
- [ ] 실제 데이터에서 확인 가능한 단어로 검색 결과를 확인했습니다.
- [ ] 카테고리 필터를 선택하고 결과를 확인했습니다.
- [ ] 항목을 열어 상세 내용을 확인했습니다.
- [ ] 서버를 종료(Ctrl+C)하고 다시 실행한 뒤 데이터가 유지되는지 확인했습니다.
- [ ] 두 파일 계약인 경우, 동일 스키마 ROW APPEND 결과 행 수를 확인했습니다. 서로 다른 스키마 JOIN은 지원하지 않습니다.

## 기록

- 확인 날짜/시간: ____________________
- 확인자: ____________________
- 미통과 항목과 기대/실제 결과: ____________________________________________
- 재현 순서(개인정보·실제 행 내용 제외): ____________________________________
- 수정 요청 일괄 전달일: ____________________

문제를 공유할 때 실제 CSV, SQLite, 비밀번호 또는 개인정보를 첨부하지 마세요. 합의된
범위 밖 기능 요청은 별도 견적 대상입니다. 이 목록은 저작권·라이선스 승인, 개인정보
적합성, 보안 인증, 공개 배포, 무제한 유지보수를 의미하지 않습니다.
"""


class DeliveryError(ValueError):
    pass


def _zipinfo(name: str) -> zipfile.ZipInfo:
    item = zipfile.ZipInfo(name, FIXED_DATE)
    item.compress_type = zipfile.ZIP_DEFLATED
    item.external_attr = 0o100644 << 16
    item.create_system = 3
    return item


def _safe(name: str) -> bool:
    parts = name.split("/")
    # Windows rejects/resolves device paths, alternate streams and trailing dots.
    reserved = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} | {
        f"COM{i}" for i in range(1, 10)
    } | {f"LPT{i}" for i in range(1, 10)} | {
        f"{prefix}{digit}" for prefix in ("COM", "LPT") for digit in ("¹", "²", "³")
    }
    return bool(name and len(name) <= 260 and not name.startswith("/")
                and "\\" not in name and ":" not in name
                and not any(ch in '<>"|?*' or ord(ch) < 32 for ch in name)
                and all(p not in ("", ".", "..") and not p.startswith(".")
                        and not p.endswith((" ", "."))
                        and p.split(".", 1)[0].upper() not in reserved
                        and p != "__pycache__" for p in parts))


def _member_paths_conflict(names) -> bool:
    """Reject Windows case-insensitive aliases and file-as-directory conflicts."""
    folded = [name.casefold() for name in names]
    existing = set(folded)
    if len(existing) != len(folded):
        return True
    for name in folded:
        segments = name.split("/")
        if any("/".join(segments[:index]) in existing
               for index in range(1, len(segments))):
            return True
    return False


def _members(project: Path) -> dict[str, bytes]:
    members: dict[str, bytes] = {}
    for path in project.rglob("*"):
        if path.is_symlink():
            raise DeliveryError("Symlink in delivery output prohibited")
        if not path.is_file():
            continue
        rel = "app/" + path.relative_to(project).as_posix()
        if not _safe(rel):
            raise DeliveryError("Unsafe ZIP member")
        if path.stat().st_size > MAX_ARCHIVE_BYTES:
            raise DeliveryError("A generated file exceeds size limit")
        members[rel] = path.read_bytes()
    members["README_WINDOWS.md"] = WINDOWS_README.encode("utf-8")
    members["ACCEPTANCE_CHECKLIST.md"] = DELIVERY_ACCEPTANCE.encode("utf-8")
    members["launch_windows.cmd"] = LAUNCH.encode("ascii")
    members["check_windows.cmd"] = CHECK_LAUNCH.encode("ascii")
    members["self_check.py"] = (Path(__file__).resolve().parent / "customer_self_check.py").read_bytes()
    # Windows treats paths case-insensitively: refuse clashing generated files.
    if _member_paths_conflict(members):
        raise DeliveryError("Case-insensitive ZIP member collision")
    if sum(len(x) for x in members.values()) > MAX_ARCHIVE_BYTES:
        raise DeliveryError("Delivery exceeds 25 MiB")
    required = ("app/app.py", "app/data.sqlite", "app/requirements.txt",
                "app/manifest.json", "app/static/index.html",
                "app/static/app.js", "app/static/style.css")
    if any(x not in members for x in required):
        raise DeliveryError("Incomplete generated app")
    return members


def _manifest(members: dict[str, bytes]) -> dict:
    return {
        "schema_version": SCHEMA, "product": "REA_Web local synthetic MVP v0.9",
        "status": "REVIEW_ONLY_NOT_COMMERCIALLY_APPROVED",
        "runtime_binding": "127.0.0.1",
        "windows_native_validated_by_exporter": False,
        "raw_fable_capture_bundled": False,
        "vendor_engines_bundled": False,
        "files": [
            {"path": name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
            for name, data in sorted(members.items())
        ],
    }


def verify_delivery(archive: Path) -> dict:
    """Validate ZIP members and SHA256 (does not execute them)."""
    with zipfile.ZipFile(archive, "r") as zf:
        info = zf.infolist()
        names = [item.filename for item in info]
        if (len(names) > 100 or len(names) != len(set(names))
                or _member_paths_conflict(names)
                or any(not _safe(n) for n in names)
                or any(stat.S_ISLNK(item.external_attr >> 16) for item in info)):
            raise DeliveryError("Unsafe, symlink, or duplicate ZIP member")
        if "delivery_manifest.json" not in names:
            raise DeliveryError("Missing manifest")
        if sum(item.file_size for item in info) > MAX_ARCHIVE_BYTES:
            raise DeliveryError("ZIP contents too large")
        doc = json.loads(zf.read("delivery_manifest.json").decode("utf-8"))
        if not isinstance(doc, dict):
            raise DeliveryError("Invalid manifest object")
        if doc.get("schema_version") != SCHEMA:
            raise DeliveryError("Unsupported manifest")
        rows = doc.get("files")
        if not isinstance(rows, list) or len(rows) != len(names) - 1:
            raise DeliveryError("Manifest file count mismatch")
        expected = {}
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("path"), str) or row["path"] in expected:
                raise DeliveryError("Invalid manifest entry")
            expected[row["path"]] = row
        if set(expected) != set(names) - {"delivery_manifest.json"}:
            raise DeliveryError("Manifest member mismatch")
        for name, row in expected.items():
            data = zf.read(name)
            if len(data) != row.get("bytes") or hashlib.sha256(data).hexdigest() != row.get("sha256"):
                raise DeliveryError("Checksum mismatch: " + name)
        return doc


def create_delivery(csv_file: Path, output_zip: Path, name: str = "REA local app",
                    *, fable_result: Path | None = None,
                    astra_root: Path | None = None,
                    approved_mapping: dict[str, str] | None = None,
                    expected_source_sha256: str | None = None) -> dict:
    csv_file, output_zip = Path(csv_file), Path(output_zip).absolute()
    if output_zip.exists() or output_zip.is_symlink():
        raise FileExistsError("Output archive already exists: " + str(output_zip))
    if output_zip.suffix.lower() != ".zip":
        raise DeliveryError("Output must end with .zip")
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".rea-export-", dir=output_zip.parent) as temp:
        work = Path(temp)
        project = work / "app"
        build(csv_file, project, name, fable_result=fable_result, astra_root=astra_root,
              approved_mapping=approved_mapping,
              expected_source_sha256=expected_source_sha256)
        members = _members(project)
        manifest = _manifest(members)
        members["delivery_manifest.json"] = (
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        ).encode("utf-8")
        stage = work / "ready.zip"
        with zipfile.ZipFile(stage, "x", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9, allowZip64=False) as zf:
            for filename, data in sorted(members.items()):
                zf.writestr(_zipinfo(filename), data, compress_type=zipfile.ZIP_DEFLATED,
                            compresslevel=9)
        verify_delivery(stage)
        publish_archive(stage, output_zip)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create/verify offline REA delivery ZIP")
    sub = parser.add_subparsers(dest="command", required=True)
    pack = sub.add_parser("pack")
    source = pack.add_mutually_exclusive_group(required=True)
    source.add_argument("--csv", type=Path)
    source.add_argument("--json", type=Path)
    pack.add_argument("--out", required=True, type=Path)
    pack.add_argument("--name", default="REA local app")
    pack.add_argument("--fable-result", type=Path)
    pack.add_argument("--astra-root", type=Path)
    check = sub.add_parser("verify")
    check.add_argument("--zip", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = (create_delivery(args.csv or args.json, args.out, args.name,
                    fable_result=args.fable_result, astra_root=args.astra_root)
                  if args.command == "pack" else verify_delivery(args.zip))
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

