# REA_Web D16 — Windows 제작 GUI 실행 바로가기

## 목적과 안전 범위
저장소 폴더의 `START_REA_CREATOR.cmd`를 실행하면 **기존 Python/Tk 제작 GUI**를 로컬에서 실행합니다. GUI는 1파일 및 승인된 동일 구조 2파일 ROW APPEND만 지원합니다. Windows 설치 프로그램이나 단일 실행파일(EXE)이 아닙니다.

**자동 설치, 관리자 권한 상승, pip/winget 실행, URL 접속, PATH·레지스트리 수정, 시스템 변경을 하지 않습니다.** 사용자 승인 없이 패키지나 Python을 다운로드하지 않습니다. 작성된 ZIP에는 로컬 SQLite와 원본 데이터 행이 들어 있으므로 비민감·권한 있는 데이터만 사용하세요.

## 사용하기
1. 이 기능 브랜치의 REA_Web 저장소를 **전체 폴더로** 준비합니다. CMD 파일 하나만 복사하면 Python 모듈을 찾지 못합니다.
2. Python 3.11 이상과 Tk, FastAPI, Uvicorn, Pydantic가 로컬에 준비되어 있어야 합니다. 이미 존재하는 `.venv\Scripts\python.exe`가 있으면 **그 환경을 우선** 사용합니다. 그렇지 않으면 `py -3.11`을 우선 시도하고, 없으면 사용자의 `python` 명령을 사용합니다.
3. `START_REA_CREATOR.cmd`를 더블클릭합니다. 실패 시 오류를 확인할 수 있도록 창을 닫지 않고 일시 정지합니다. 정상 실행 시 기존 1파일 GUI가 열리며, 별도의 2파일 APPEND 버튼으로 두 번째 창을 열 수 있습니다.
4. 환경만 점검하려면 명령 프롬프트에서 저장소 폴더로 이동 후 `START_REA_CREATOR.cmd --check`를 실행합니다. `--check`는 **GUI를 실행하지 않습니다**. 실행 위치가 다른 경우에도 CMD가 스스로 저장소 루트 폴더로 이동합니다.
5. 정확한 입력, 권한 확인 및 APPROVE / APPROVE + APPROVE + APPEND가 별도로 필요합니다. 이 CMD는 사용자 동의를 자동으로 표시하거나 생성 경로를 덮어쓰지 않습니다.

## 환경 진단 반환 코드

| 코드 | 진단 상태 | 사용자가 할 일 |
| --- | --- | --- |
| 0 | READY | 로컬 Python 3.11+, 필수 모듈, Tk 화면 생성이 현재 환경에서 확인됨. 실제 사용자 인수 검증은 아님 |
| 2 | INVALID_ARGUMENT | 인자 없이 실행하거나 --check만 사용 |
| 10 | NO_PYTHON / UNSUPPORTED_PYTHON | Python 3.11 이상이 설치·선택되었는지 확인 |
| 11 | MISSING_MODULES | 필요한 fastapi, uvicorn, pydantic가 선택된 Python 환경에 있는지 확인. 자동 설치하지 않음 |
| 12 | TK_UNAVAILABLE | Python Tkinter와 Windows 대화형 화면 세션을 확인. 아니면 기존 CLI 사용 |
| 13 | LOCAL_DIAGNOSTIC_ERROR / GUI_LAUNCH_FAILED | 로컬 상태를 점검, 에러 코드 공유. 설치·배포 성공으로 간주하지 않음 |

`--check` 성공은 **실제로 제작 GUI 사용을 끝마쳤거나** 사용자의 기존 PC에서 납품할 준비가 됐다는 증거가 아닙니다. Python 환경이 바뀌면 다시 검사해야 합니다.

## 기술 선택
선택 A: **작은 로컬 CMD + Python 읽기 전용 사전 진단**. 유지보수와 외부 설치·법적 표면이 작고 기존 소스에 결합하기 쉽습니다.

선택 B: Python/Tk 의존성을 묶은 EXE. 타사 구성요소 재배포 라이선스, 코드 서명, 백신 오탐, 자동 업데이트, 사용자 PC 검증 등이 추가로 필요해 보류합니다.

## 개발자 검증
`python -m pytest -q tests` 전체 회귀, `python -m rea.creator_preflight --check`, 실제 Windows `python scripts/d16_windows_creator_smoke.py`에서 CMD --check, 알 수 없는 인자, 격리된 PATH 내 Python 부재 거부를 확인합니다. CI는 기존 1·2파일 Tk 합성 동작, Linux Chromium 11개 사례, Windows 압축해제 후 localhost HTTP, 고정 Fable/Astra 소스 해시를 유지해야 합니다.

**상용 G5/G6는 여전히 BLOCKED**: 합법적 제3자 재배포 권한/NOTICE, 실고객 승인, 사용자용 클린 Windows 설치·사용성, 개인정보·백업·보안, 세 건의 수작업 소요시간과 고정가 30만원 계약·지원·환불 약관이 검증되지 않았습니다.
