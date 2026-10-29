# REA_Web — 고객 데이터 기반 로컬 웹앱 제작 도구

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
- D27 코드 CI: GitHub Actions [#40378905450](https://github.com/hibi89/REA_Web/actions/runs/40378905450) — Linux 412 PASS/4 SKIP, Windows 426 PASS. 상세 상태는 [STATUS.md](STATUS.md)를 봅니다.
- Draft PR [#30](https://github.com/hibi89/REA_Web/pull/30)은 아직 병합되지 않았습니다.
- 실제 비개발자 Windows 사용성, 고객 데이터/사이트 권한, 소스·의존성 재배포 라이선스, 개인정보·보안·백업, 계약·수정·환불·지원 범위는 확인되지 않았습니다. 따라서 이 프로젝트를 판매 승인 또는 고객 인수 완료로 설명하지 않습니다.

## 기능 제외

자동 크롤링·사이트 복제, 임의 API/실DB 연결, 서로 다른 스키마 자동 JOIN, 로그인·역할, 결제, 공개 호스팅, CRUD 데이터 수정, 실시간 동기화, 무제한 데이터 정리 및 수정은 제공하지 않습니다.

## 현재 확인된 상태 (2026-10-30)

- 기능 및 D27 CI 검증 기준 커밋: `6a6f07d0350368deacf413cab0be2a79eaca296f` on `feature/d27-windows-python-discovery`; 후속 커밋은 검증 결과를 반영하는 문서 갱신입니다.
- 새 커밋의 D27 GitHub Actions [#40923311077](https://github.com/hibi89/REA_Web/actions/runs/40923311077) 및 [#40923323228](https://github.com/hibi89/REA_Web/actions/runs/40923323228): Linux D1–D27/Chromium 및 Windows D1–D27/native package 모두 **SUCCESS**.
- 로컬 Windows 검증: D27·고객 안내 focused tests 12 PASS; 합성 납품 ZIP 생성·압축 해제·실제 `cmd.exe` 실행·`127.0.0.1` health 및 4행 API **PASS**.
- 고객의 실제 비개발자 검수는 **NOT_RUN**, 성공적인 실기기 `py -3` 런타임 선택은 **NOT_RUN**, 소스·의존성 상용 재배포 권리는 **NOT_GRANTED**입니다.
- 목표가 299,000원은 미승인 가정이며, 현 상태를 판매 승인/고객 인수 완료로 표현하지 않습니다. PR #30은 Draft/open/unmerged입니다.

기능 범위와 제외 항목은 위의 지원 범위를 따릅니다. 상세 기록은 [docs/47_LOCAL_COMMERCIALIZATION_FOLLOWUP.md](docs/47_LOCAL_COMMERCIALIZATION_FOLLOWUP.md)를 참고하세요.
