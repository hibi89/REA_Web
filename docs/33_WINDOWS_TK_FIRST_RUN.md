# D14 — REA_Web Windows 첫 실행 및 실제 Tk GUI 검수

## 용도와 확정된 제한
현재 제품은 **로컬 Python 3.11 + Tkinter 제작 GUI(옵션)** 및 **고객 데이터로 생성한 로컬 읽기 전용 웹앱**입니다. 고객용 단일 설치파일(`.exe`)은 제공하지 않습니다. GUI는 한 개의 UTF-8 CSV 또는 평면 문자열 JSON만 선택·명시적 매핑 후 ZIP을 만듭니다. 원본 파일은 변경하지 않지만 **ZIP 안 SQLite DB에는 원본의 실제 데이터 행이 들어 있습니다.** 민감한 개인·회사·비밀 데이터는 사용하지 마십시오.

GUI가 두 파일의 관계를 알아서 조합하거나 기존 웹사이트를 복제하지 않습니다. 별도 CLI에는 승인된 동일 구조 2파일의 ROW APPEND만 있으며 JOIN은 없습니다. 실제 고객·라이선스·상용 납품 승인은 아직 불가합니다.

## Windows 10/11 초보 사용자 안내 (개발자용 합성 테스트 우선)

1. 신뢰하는 Python 배포처에서 Python 3.11 이상을 설치합니다. 사용 중인 Windows PC에서는 실행 전에 기존 설치와 권한을 확인하십시오. REA_Web은 자동 설치나 관리자 권한 요청을 수행하지 않습니다.
2. PowerShell 또는 명령 프롬프트에서 `py -3.11 --version`으로 해당 Python이 있는지 확인합니다. Windows Python launcher가 없다면 `python --version`을 확인합니다. 오류가 나면 Python 설치/실행 PATH 또는 다른 Python 버전 선택을 점검합니다.
3. `py -3.11 -m tkinter` 실행 시 작은 Tk 테스트 창이 열리고 종료할 수 있어야 GUI 사용이 가능합니다. 실패하면 선택형 GUI가 아닌 기존 CLI를 사용할 수 있습니다. 이 명령이 성공해도 **REA_Web 생성 GUI를 실제 사용자가 끝까지 검수한 것은 아닙니다**.
4. 저장소 코드가 있는 폴더에서 사용자의 기존 환경과 분리하고 싶다면 `py -3.11 -m venv .venv`, `.\.venv\Scripts\python.exe -m pip install "fastapi>=0.110,<1" "uvicorn>=0.27,<1" "pydantic>=2.6,<3" "httpx>=0.27,<1" "packaging>=23,<27"`을 실행할 수 있습니다. 이 **pip 설치는 사용자가 실행하면 인터넷을 사용**하며, 패키지 공급처 및 라이선스는 별도 확인 대상입니다. 검증되지 않은 설치/재배포 허용을 의미하지 않습니다.
5. 해당 Python 인터프리터로 `.\.venv\Scripts\python.exe -m rea.creator_gui`을 실행합니다. 창이 열리면 **파일 선택 → 컬럼 검사 → 서로 다른 id/title/category 컬럼을 직접 선택 → 새 ZIP 경로 지정 → 사용 권한 확인 → 정확히 APPROVE 입력 → ZIP 생성** 순서입니다. 아무 컬럼도 자동 승인하지 않습니다.
6. 생성된 ZIP을 안전한 새 폴더에 압축해제하고 `check_windows.cmd`로 무결성/로컬 선행조건을 확인합니다. 오류가 없다면 `launch_windows.cmd`로 `127.0.0.1`에서만 실행합니다. 필요한 패키지가 없으면 사용자 승인을 받아 설치해야 하며, 스크립트가 인터넷이나 관리자 권한으로 자동 설치하지 않습니다.

## 자주 발생하는 오류

| 상황 | 의미 | 조치 |
| --- | --- | --- |
| `No module named tkinter` 또는 디스플레이 생성 오류 | 선택형 GUI에 Tk가 없거나 화면 세션이 불가 | Python/Tk 설치 확인, 또는 `python -m rea.guided` CLI 사용 |
| `Owner must explicitly type APPROVE` | 명시적 승인 없음 | 권한/민감정보를 확인한 뒤 정확히 대문자 APPROVE 입력 |
| `Source SHA changed` | 검토 후 원본 파일이 변경됨 | 원본을 다시 검사하고 매핑/승인을 처음부터 반복 |
| `Output already exists` | 기존 대상 보호 | 새 ZIP 파일명/경로를 선택, 기존 파일 덮어쓰지 않음 |
| `Missing Python dependency` | 납품된 앱 실행 환경에 필요한 패키지 미설치 | 설치 출처·권한 확인 후 사용자 통제 하에 설치, 재검사 |
| 웹앱 접속 불가 | 실행 실패 또는 로컬 포트 사용 중 | 콘솔 오류 확인, `127.0.0.1` 바인딩·포트 충돌 점검, 임의로 인터넷에 공개 금지 |

## D14 GUI 자동화의 정확한 검증 범위
- Linux CI: Xvfb 가상 화면에서 **실제 Tk 창/콤보박스/체크박스/Entry/버튼 이벤트**를 동작시킵니다. 파일 대화상자는 **커밋된 합성 fixture 경로만 반환하도록 스텁**을 사용합니다. 승인 전 생성 거절, 승인 후 해시 검증한 ZIP, 재승인 없이 재시도 거절을 검증합니다. Pillow가 지원하면 합성 GUI PNG와 JSON 상태 기록을 보존합니다.
- Windows CI: Tk 실제 desktop 창 생성 가능 시 합성 위젯 흐름을 추가 실행하고, 화면 접근이 불가능하면 **GUI_NOT_AVAILABLE_NOT_RUN**으로 증거를 기록합니다. 모듈 import만으로 화면 검증 성공이라고 보고하지 않습니다.
- 이 테스트는 실제 Windows 소비자 설치, 사용성, 시력/접근성, 한글 폰트, 관리자 정책, 재부팅/복구, 고객 승인 데이터, 제3자 사용권과 별개입니다. **G5/G6 및 상용 판매는 BLOCKED**입니다.

CI 실행은 `.github/workflows/rea-d14.yml`, 합성 위젯 스크립트는 `scripts/d14_tk_visual_smoke.py`, Windows 조건부 스크립트는 `scripts/d14_windows_gui_probe.py`를 참조하십시오. 코드와 문서가 있는 현재 상태는 아직 Draft PR이며, 테스트 로그 결과 없이 완료로 간주하지 않습니다.
