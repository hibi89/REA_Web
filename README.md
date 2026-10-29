# REA_Web — 고객 데이터 기반 로컬 웹앱 제작 도구

## 최신 원격 재확인 (2026-10-30; `50c82814821f89f0326cefcf04c2ee78e080d5c4`)

- 지정 브랜치 HEAD와 PR #30을 다시 확인했습니다. PR은 OPEN / DRAFT / UNMERGED 상태입니다.
- 이 정확한 HEAD의 GitHub Actions 첫 페이지에서 28개 모두 완료 SUCCESS, 진행 중/대기/실패 0건입니다. D27 `40969580989`, D3 `40969580958`, D31 `40969581132` 모두 SUCCESS입니다. 자동 검증 fixture는 합성 데이터이며 사람의 고객 검수로 간주하지 않습니다.
- 별도 격리 로컬 검사 기록은 고객 안내+D27 21 PASS, D6 14 PASS/1 SKIP, D9 경계·APPEND 15 PASS/2 DESELECTED, 새 ZIP 검증·CRC·깨끗한 압축 해제 후 실제 CMD 사전 검사 PASS입니다. 이 환경의 실서버 HTTP는 /health timeout/SQLite cleanup lock 때문에 BLOCKED/NOT_RUN이며 로컬 HTTP 성공으로 표현하지 않습니다.
- 개발 95% / 판매 준비 77%는 정성 추정치로 재측정하지 않았습니다. 상용 재배포 권리 NOT_GRANTED, 고객 데이터·개인정보/판매 조건 NOT_APPROVED, 비개발자 Windows 인수검수 NOT_RUN이므로 판매 승인 상태가 아닙니다.
- 아래에 남은 과거 시점 기록은 이 재확인보다 오래된 스냅샷입니다. 최신 상태를 주장할 때 이 메모와 정확한 원격 HEAD를 기준으로 삼으세요.




## 현재 검증 상태 (2026-10-30)

- 개발 브랜치의 제품 코드·D31 워크플로 검증 기준 `970bbde8c853f4ed1382c038091bb2ee48abea9f`에서 GitHub Actions 28/28이 성공했습니다. 이후 문서 전용 갱신은 제품 코드를 바꾸지 않았습니다. D27 Linux/Chromium 및 Windows/native-package 전체 자동 회귀와 D31 Ubuntu/Windows 생성 런타임 감사가 포함됩니다. 입력 자료는 합성 fixture입니다.
- 로컬 집중 검사: 안내/D27 21 passed, D6 14 passed/1 skipped, D9 15 passed/2 deselected. 깨끗한 합성 ZIP 추출과 Windows CMD 사전 검사는 통과했습니다. 이 환경의 실제 로컬 서버 HTTP 스모크는 응답 시간 초과로 BLOCKED/NOT_RUN이며 독립 고객 검수는 NOT_RUN입니다.
- 개발 95% / 판매 준비 77%는 정성적 추정치입니다. 재배포 권리 NOT_GRANTED, 고객 데이터/개인정보와 판매 조건 NOT_APPROVED이므로 판매 승인 상태가 아닙니다.


REA_Web은 고객이 권한을 가진 CSV 또는 flat JSON에서 별도의 읽기 전용 FastAPI + SQLite 웹앱을 만들고 ZIP으로 전달하는 도구입니다. 참고 사이트 분석은 선택 사항이며, 추정된 기능이나 API는 고객 데이터 매핑을 자동 승인하지 않습니다.

## 현재 지원하는 범위

- 고객 제공 CSV 1개 또는 flat JSON 1개 입력, 파일 검사와 스키마 미리보기
- 소유자 명시 승인 이후 필드 매핑
- 같은 구조의 두 파일은 양쪽 입력자 승인 이후 **ROW APPEND**만 지원합니다. 서로 다른 표의 SQL JOIN은 지원하지 않습니다.
- 생성 앱: 목록, 검색, 카테고리 필터, 상세 조회. 로컬 SQLite를 사용하고 기본적으로 읽기 전용입니다.
- 생성된 ZIP은 Windows 사전 검사, 무결성 검사, `127.0.0.1` 실행기를 포함합니다. 인터넷은 선택적 Python 패키지 설치 때만 필요할 수 있습니다.
- 프로젝트 제작 GUI 실행: `START_REA_CREATOR.cmd`. Windows 안내는 [docs/35_WINDOWS_CREATOR_LAUNCHER.md](docs/35_WINDOWS_CREATOR_LAUNCHER.md), 고객용 납품 안내는 생성 ZIP의 `README_WINDOWS.md`를 따르세요.

## Windows 제작 GUI 사전 조건

Python 3.11+, Tkinter, FastAPI, Uvicorn, Pydantic가 필요합니다. 실행기는 기존 로컬 환경을 검사하고 GUI를 엽니다. 자동 설치나 관리자 권한 상승은 하지 않습니다. 진단만 하려면 프로젝트 폴더에서 `START_REA_CREATOR.cmd --check`를 실행합니다.

## 상용 및 검수 상태

- 목표 상품가: **299,000원 (검토 중, 미승인)**
- 최신 제품 코드 검증 헤드 `b7eaaf405e686a93f8060ef3bbf5999a988a7bdd`: D27 [run](https://github.com/hibi89/REA_Web/actions/runs/40963047232) 및 D26 [run](https://github.com/hibi89/REA_Web/actions/runs/40963047281) Windows·Linux job PASS, 반환된 GitHub Actions 27개 모두 성공. 현재 브랜치 문서 헤드는 `2bdbee3e7ce1ae68eabc7b6a73b260368888d643`.
- Draft PR [#30](https://github.com/hibi89/REA_Web/pull/30)은 아직 병합되지 않았습니다.
- 실제 비개발자 Windows 사용성, 고객 데이터/사이트 권한, 소스·의존성 재배포 라이선스, 개인정보·보안·백업, 계약·수정·환불·지원 범위는 확인되지 않았습니다. 따라서 이 프로젝트를 판매 승인 또는 고객 인수 완료로 설명하지 않습니다.

## 기능 제외

자동 크롤링·사이트 복제, 임의 API/실DB 연결, 서로 다른 스키마 자동 JOIN, 로그인·역할, 결제, 공개 호스팅, CRUD 데이터 수정, 실시간 동기화, 무제한 데이터 정리 및 수정은 제공하지 않습니다.

## 최근 확인된 상태 (2026-10-30)

- 제품 코드 검증 기준 커밋: `b7eaaf405e686a93f8060ef3bbf5999a988a7bdd`. 이후 `e8e975c`는 이 상태를 기록한 `STATUS.md` 전용 커밋입니다.
- 기준 커밋에서 반환된 GitHub Actions 워크플로 27개가 모두 성공했습니다. D27/D26 Windows 및 Linux, D3 생성 앱 Chromium 납품 흐름, D9 동일 구조 2파일 ROW APPEND, Windows 추출 ZIP의 CMD/localhost HTTP 검증을 포함합니다. 상세 단계는 [STATUS.md](STATUS.md)와 D27 [run](https://github.com/hibi89/REA_Web/actions/runs/40963047232), D26 [run](https://github.com/hibi89/REA_Web/actions/runs/40963047281), D3 [run](https://github.com/hibi89/REA_Web/actions/runs/40963047275), D9 [run](https://github.com/hibi89/REA_Web/actions/runs/40963046981)를 참고하세요.
- 별도 로컬 점검: 고객 안내 18 PASS, D6 provenance 14 PASS / 1 SKIP, `compileall` 및 `pip check` PASS. 이 작업 환경의 전체 로컬 회귀·D7 symlink 사례·직접 CMD 실행은 sandbox 권한/프로세스 정리 문제로 NOT_COMPLETE이며 성공으로 보고하지 않습니다.
- 모든 자동 검증은 합성 데이터 기준입니다. 사람의 일반 고객 Windows 검수는 **NOT_RUN**입니다. 실제 고객 데이터 권리·동의와 개인정보/백업 검토는 **NOT_APPROVED**입니다.
- 목표 가격 299,000원은 검토용 제안이며 미승인입니다. 저장소 및 vendor 코드의 상용 재배포 권리는 **NOT_GRANTED**, 판매 약관과 지원·환불 조건도 **NOT_APPROVED**입니다. 이 프로젝트는 판매 승인 상태가 아닙니다. PR #30은 Draft/open/unmerged입니다.
- 지원 범위·제외 기능은 위 설명과 동일합니다. 서로 다른 테이블의 자동 JOIN, 로그인·결제, 공개 호스팅, CRUD, 실시간 동기화는 제공하지 않습니다.
