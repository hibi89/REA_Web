# REA_Web 원래 웹사이트 분석·재구축 P50 — 로컬 합성 종단 수용 (2026-11-12 KST)

## 확인한 정확한 기능과 CI
- 개발 저장소: `hibi89/REA_Web@feature/website-analysis-rebuild`; 정확한 CI 검증 SHA **`fb67616df6a5e7eb7ea14c1315a58dd689d2534d`**, 사용자 `hibi89` Author/Committer 확인.
- 신규 원본: `rea/website_rebuild.py` (기능 최초 SHA `a77b88030448b35014e4d9caea612c4fd3a71934`), `tests/test_website_rebuild_p50.py` (`94467969c76108fbe018bb7ee1e0a3ce5a2c5cff`), `.github/workflows/rea-website-p50.yml` (검증 SHA의 마지막 변경 `fb67616`).
- 검증: [GitHub Actions #43242189801](https://github.com/hibi89/REA_Web/actions/runs/43242189801) **Ubuntu24.04 31 PASS / 0 FAIL / 경고1**, **Windows2025 31 PASS / 0 FAIL / 경고1**, **2/2 Jobs SUCCESS**.
- 실행: `python -m pytest -q tests/test_website_rebuild_p50.py tests/test_orchestrator.py` (양 OS 동일, 별도 `PYTHONPATH=.vendor/astra/engines/astra_p4`); 구성 GitHub Actions 내 실제 frozen Fable SHA `7e6f273b...`, Astra P4 `f044b66e...`.
- 테스트 범위: 합성 HTML 원본+고정 SHA를 단일 `127.0.0.1` 루프백 서버에 게재, 실제 고정 Fable5.1 `scan.py` **정적 페이지 GET 정확 1회**, 실제 Astra P4 `ObservationBundle`과 `derive_spec`을 사용해 정적 구조로부터 inferred-only 명세 도출; 동작을 승인할 수 없는 `REVIEW_REQUIRED` 상태를 강제.
- Pro `rea.orchestrator.build` 호출은 오직 원본 SHA 고정·사용자 명시 승인된 합성 CSV 3행만 사용. FastAPI TestClient /health·GET 목록·검색/분류/상세, SQLite 레코드3개, 비서비스 review JSON 404, 원본 HTML·CSV 불변, 스캔 샘플 비밀 텍스트를 생성 앱에 복제하지 않음. 기존 Orchestrator regression 포함 총31.
- 보안/실패 경계: 승인값 누락, 위조 SHA, 매핑 중복, pinned Fable/Astra 누락, symlink/출력폴더 존재/부모 디렉터리 부재 시 FAIL-CLOSED·기존 파일 무변경. 원시 참고 사이트 HTML은 앱으로 복사하지 않음. 스캔 스크립트는 실제 pinned Fable이고 원격 공공 인터넷 사이트를 요청하지 않았음.
- 이전 CI 오류: 최초 workflow만 존재한 SHA `873d7e3`에서는 테스트 소스 누락으로 FAIL. 신규 테스트가 있는 `94467969`에서는 Ubuntu31 PASS, Windows **30 PASS/1 FAIL**; 원인 CI `PYTHONPATH`에서 Linux ':' 구분자를 Windows에 그대로 적용해 **기존 CLI subprocess Astra import 실패**. OS 공통 단일 경로로 최소 수정한 `fb67616`에서 **31 PASS 양 OS**, 소스 코드 그대로, 검증 성공.

## 정본 최종설계 대비 판정
- `docs/ORIGINAL_FINAL_DESIGN.md`의 **0→50 단계**인 기존 Pro 실제 FastAPI/SQLite, frozen Fable/Astra 기술 계약, 허가된 로컬 합성 관찰→명세 초안→별도 새 앱의 최소 1개 E2E를 충족한 것으로 평가: **최종상품 엔지니어링 완성률 50% 잠정**.
- 이것은 **제품 출시율/테스트 커버리지 50%가 아니다**. 원래 최종 목표의 사이트 자동 재구축 UI·구성요소/기능/반응형 비교, 실제 외부 URL/브라우저 행동 관찰, 실제 고객/운영 인수는 **미구현·미검증**. 생성 앱은 사이트 내용/디자인을 복제하지 않고 **별도 승인 CSV만으로** 만든 기본 카탈로그 앱이다.
- 원본 실사이트 정책/ToS/권리, 고객 Windows10/11 실기기, Fable record 인과 증거, 화면 디자인/동작 parity, 사이트 spec 인간 최종 승인 UI, 코드/제3자 라이선스·운영배포 등은 **P70 이후/고객 승인 전 HOLD**.
- **따라서 P50 엔지니어링 잠정 달성 / RELEASE HOLD / 판매 NO-GO / Production N/A**. 사용자 별도 P70 목표가 지정되기 전 [작업중] 새 표시를 자동 설정하지 않는다.

## 개발 절차·복구
- 현재 기능 브랜치의 부모 원본 `feature/d27-windows-python-discovery@97b6e5cab7b8ffb4e1ee7f5e593021f4dac2598d`; Pro/Fable/Astra import/Lite/DATA2WEB 원본 브랜치 변경 없음. 기존 소스 경로(Orchestrator+adapter+Pro)는 신규 모듈에서 import해서 재사용.
- 실패시 마지막 검증 SHA `fb67616` 로 복구 가능. 출력은 새 대상만 허용, 실패나 종료로 기존 고객 파일 삭제하지 않으며, 변경/중복 실행은 HOLD.
- 다음: 인가된 로컬 복수 fixture+실 Playwright Chromium/Edge 상호작용 증거/전후 state/URL+상태 비교를 Astra 후보·승인 상태에 연결하고, 실제 승인된 웹 UI 구조를 독립 앱 렌더링에 단계적으로 반영한 뒤 P70 검증. 실웹페이지는 사용자 명시적 권한·관찰 범위·브라우저 비용·PII 동의 없이는 자동 접속 금지.

## 확인 날짜
2026-11-12 KST, GitHub CI run #43242189801 최종 완료 시점 기준, 합성 데이터/호스티드 Windows와 Ubuntu 범위.
