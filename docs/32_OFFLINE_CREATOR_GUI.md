# REA_Web D13 — 선택형 오프라인 제작 GUI

## 사용 방법
개발용 Python 3.11 이상, Tkinter GUI 사용 가능한 환경, 기존 FastAPI/Uvicorn 설치가 필요합니다.

    python -m rea.creator_gui

설치형 실행파일(.exe)이 아니며, 일반 Windows 소비자 기기에서 사람이 설치·사용한 검증은 아직 없습니다. Tkinter가 없는 환경이나 headless CI에서는 실행이 거부되고 기존 `python -m rea.guided inspect` / `python -m rea.guided pack` CLI 대체 명령을 표시합니다. 어떠한 네트워크 업로드도 수행하지 않습니다.

## 실제 GUI 구성
1. 권한을 보유한 **하나의 비민감 UTF-8 CSV 또는 평면 JSON**을 로컬에서 선택합니다. `rea.guided.preflight`로 SHA256, 컬럼명, 텍스트 기반 자료형 힌트, 빈 칸 수와 행 수만 확인합니다. 셀 원본값과 전체 경로는 원격으로 내보내지 않습니다. 자료형 힌트는 확정 매핑이 아닙니다.
2. id/title/category로 사용할 **서로 다른 원본 컬럼을 사용자가 직접** 선택합니다. 원본 컬럼의 이름이 id/title/category와 같아도 자동 승인/선택되지 않습니다.
3. 새 납품 .zip 경로와 앱 이름을 지정하고 **권한·비민감 자료 확인 체크박스 + 대소문자 정확한 APPROVE 입력**을 둘 다 완료해야 생성합니다.
4. 기존 `rea.guided.approved_selection` → `rea.delivery.create_delivery` → `rea.delivery.verify_delivery`를 사용합니다. 파일 SHA 변경, 중복 id, 잘못된 매핑, 기존 출력 파일 또는 심볼릭 링크 경로를 거부합니다. 정상 생성은 ZIP SHA/멤버 무결성을 검증하며 원본을 수정하지 않습니다. 생성 이후 승인은 재사용되지 않습니다.
5. ZIP 안 `app/data.sqlite`에는 고객 원본의 행이 들어 있습니다. 원본 CSV/JSON 파일 자체를 ZIP에 추가하지는 않지만 데이터가 민감하지 않다는 검증을 프로그램이 보장하지는 못합니다.

## 보안·상용 범위
- **한 파일의 명시적 컬럼 매핑 ZIP 생성만 GUI로 지원**합니다. 기존 CLI의 **동일 구조 두 파일 명시적 ROW APPEND** 기능은 GUI에 포함되지 않으며 JOIN은 어디에서도 지원하지 않습니다. 사이트 크롤링, 공개 배포, 생산 DB 액세스, API 키, 유료 API 호출, 인증/결제 기능 없음.
- Tkinter 선택은 간단한 오프라인 파일 선택과 0개 추가 서버 엔드포인트를 제공하므로, localhost 브라우저 wizard보다 데이터 취급·유지보수 표면이 작습니다. 대신 기본 Python/Tk 설치에 의존하며 현대식 웹 UI는 아닙니다.
- 자동화 GUI 없는 순수 컨트롤러 테스트와 headless fallback, 실제 CSV/JSON 합성 ZIP 생성, 기존 D1–D12 회귀, Linux Chromium 8+3, Windows native CMD/localhost를 CI에서 검증합니다. **실제 GUI 화면을 사람이 조작한 것과 clean Windows 비개발자 검증은 미실행**. CI가 통과해도 상용 G5/G6 및 법적 사용권/사람 작업시간 검증은 BLOCKED.
- 제품 가격 300,000원은 아직 가설이며 확정 상품이 아닙니다. 공용 GitHub 공개 소스나 CI는 제3자 재배포 허가가 아닙니다.

## 검증 범위
`python -m pytest -q tests` (D1–D13), `python -m rea.creator_gui` (GUI 환경), `python -m rea.guided inspect --csv samples/qa_guided.csv` (기존 명령). 진짜 브라우저/Windows 자동화 테스트 증거는 `.github/workflows/rea-d13.yml` 성공 로그와 실행 SHA로 판단합니다.

## 다음
상용 출시 전 가시적인 GUI 실사용 E2E (Windows clean user, 2가지 자료 유형), 설치/복구 과정, 상용 라이선스, 고객 승인 데이터, 3건 수동 작업시간, 지원/환불 조건이 필요합니다. 사용자가 실제 GUI 설치 화면을 확인하기 전 자동화 테스트를 화면 사용성 합격으로 발표하지 않습니다.
