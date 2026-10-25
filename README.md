# REA_Web — 웹서비스 분석·재구축 자동화 엔진

> 2026-10-26 · **MVP 기능 브랜치 D12까지 CI 검증** (Linux·Windows 각 217 tests, 11 Chromium 합성 사례) · main 문서 기준점, PR 전부 미병합, 상용 검증 미완성

**새 채팅 즉시 재개:** `[REA_Web 깃헙 레포지토리 보고 작업이어가셈]` — 질문 없이 최신 GitHub 문서·코드 확인 후 다음 READY 개발 작업을 수행한다. **최우선 안내:** [WORKER_START_HERE.md](WORKER_START_HERE.md) · [세션 복원 프로토콜](docs/SESSION_RESTART_PROTOCOL.md).

## 제품 목표
고객이 권한을 가진 참고 웹사이트의 관찰 정보를 Fable 5.1로 분석하고, Astra의 증거·명세·매핑 모듈을 사용해 **고객 제공 CSV/JSON으로 동작하는 별도의 웹앱**을 생성·검증한다. 외부 소스 복제, 숨겨진 서버 로직 추출 또는 무허가 데이터 수집 제품이 아니다.

## 지금 실제로 동작하는 것 (Day1)
- `feature/csv-local-mvp` @ `5515a7286d63211e32d2c577f93f77d61f37ce08`: UTF-8 CSV → 새 SQLite → 독립 로컬 FastAPI 웹앱 (목록·검색·카테고리 필터·상세).
- 실제 GitHub Actions [40198326369](https://github.com/hibi89/REA_Web/actions/runs/40198326369): 9 pytest PASS, Chromium 루프백 E2E PASS (5개 목록, 필터 2, 검색 1, 상세, 새로고침), JS·외부 요청 오류 0건. Windows와 실제 고객 데이터는 미검증.
- [Draft PR #3](https://github.com/hibi89/REA_Web/pull/3) · 미병합. **main은 현재 통합 앱 실행 브랜치가 아니라 프로젝트 명세/인수인계 기준점**이다.

## 코드 및 브랜치
- Fable 5.1 고정 소스 88개: `import/fable51-bbe72c0`, [Draft PR #1](https://github.com/hibi89/REA_Web/pull/1).
- Astra P4 선택 소스 103개(41개 계약 모듈; PARTIAL): `import/astra-p4-b3166b6`, [Draft PR #2](https://github.com/hibi89/REA_Web/pull/2).
- 작업 타깃: `feature/evidence-adapter` (D2-01), `feature/csv-local-mvp` (D1), `feature/orchestrator` (D2-02), `integration/develop`, `qa/cross-platform` (D3 QA PASS).
- 원본 Fable/Astra 소스 저장소는 변경하지 않는다.

## Day2 구현·검증 완료 (feature 브랜치)
- `feature/evidence-adapter` `fda96076de33ebf4f4b6118972a5033a3f703ba9`, [Draft PR #4](https://github.com/hibi89/REA_Web/pull/4).
- 합성 샘플 Fable 결과 → 검토 전용 Astra 증거·명세 제안, 추정/관찰 구분, 승인·생성 차단. GitHub Actions [CI run 40199741969](https://github.com/hibi89/REA_Web/actions/runs/40199741969): Ubuntu Python 3.11, **28 테스트 통과**, 고정 Astra 계약 모델 검증 및 CLI 통과.
- Day1/Day2 서로 다른 브랜치에서 테스트되었으며 **전체 REA_Web 통합 완료가 아님**.

## Day2 통합 MVP 실제 완료 (feature 브랜치)
- `feature/orchestrator` @ `46060b4665560922d0c9cf82b9e5c08971eb9427`, [Draft PR #5](https://github.com/hibi89/REA_Web/pull/5).
- 고객 CSV 단독 → FastAPI/SQLite 웹앱 생성, Fable 1.0 JSON은 선택적으로 Astra 검증용 비공개 로컬 보고서만 추가 (앱 자동 매핑/승인 없음).
- [GitHub Actions 40200704855](https://github.com/hibi89/REA_Web/actions/runs/40200704855): **55 테스트 통과 / 경고 1**, 두 CLI 모드·실제 Chromium 필터/검색/상세/새로고침 통과. 별도 PR CI도 성공. 미병합·미배포.
- 실행: `python -m rea.orchestrator --csv samples/products.csv --out ./out/demo` (미리 설치된 FastAPI/Uvicorn 필요), 참고 분석 추가 시 `--fable-result ...` + 고정 Astra 계약 필수. 자세한 내용: [D2 통합 가이드](https://github.com/hibi89/REA_Web/blob/feature/orchestrator/docs/20_ORCHESTRATOR_MVP.md).

## D3 검증 완료 (QA 브랜치)
- qa/cross-platform: 기능 검증 SHA `e88c89f3ec12e61e63d2ca1255736fbf674c6e9e`; 문서 보완 최신 SHA `857a73e1f3e641f851fd4df1212872846528bdb9`; [Draft PR #6](https://github.com/hibi89/REA_Web/pull/6), 미병합.
- [GitHub Actions 40202313506](https://github.com/hibi89/REA_Web/actions/runs/40202313506) Ubuntu 68 pytest + 카페·재고·트렌드 3개 Chromium 실동작 PASS, Windows 68 pytest + ZIP 압축해제/.cmd/127.0.0.1 API PASS. 예시 납품 ZIP·화면 3장·JSON 결과는 해당 Actions Artifacts에서 다운로드 가능. 실제 고객/윈도우 사용자 PC/실사이트는 미검증.
- [최초 설계 대비 차이표](https://github.com/hibi89/REA_Web/blob/qa/cross-platform/docs/21_MVP_GAP_MATRIX.md); [D3 사용·검수 가이드](https://github.com/hibi89/REA_Web/blob/qa/cross-platform/docs/22_D3_TEST_GUIDE.md).

## 다음 작업 (지금 시작 가능)
**D13-01 READY:** 선택형 오프라인 GUI로 고객 파일 선택·매핑 승인·앱 생성의 사용성 격차를 메운다. D12는 완료; CLI·원본 보존, 유료 서비스 및 상용 권리 승인 차단 유지. 정확한 다음 작업은 [docs/17_NEXT_TASK.md](docs/17_NEXT_TASK.md). 전체 소스는 Draft PR 상태, 상용화/배포 전.

## 사업/범위
초기 크몽 가격 가설 300,000원. 소규모 고객 제공 CSV 중심, 2개 화면·3개 단순 기능 이내 정액 납품을 목표로 한다. 데이터 수집 대행·운영 DB 접근·복잡한 인증·결제·무제한 수정 제외. 아직 판매 개시/납품 준비가 완료된 상태가 아니다.

**설계도:** [아키텍처](docs/02_ARCHITECTURE.md) · [3일 계획](docs/MVP_3DAY_SPRINT_PLAN.md) · [최종 산출물](docs/14_FINAL_DELIVERABLES.md) · [인수검사](docs/05_ACCEPTANCE.md) · [30만원 범위](docs/07_KMONG_OFFER.md) · [최신 작업지시](docs/17_NEXT_TASK.md).

## D4-01: 컬럼·자료형 미리보기 + 카테고리별 집계 검증 완료
- feature/mvp-summary-preview: d8e26ed7d60ad86f64e35aefb3825655d6e19d25 (코드 테스트), e4e9c7954ba1369636bcc2107478a5d2dae2db7e (최신 문서), [Draft PR #7](https://github.com/hibi89/REA_Web/pull/7) 미병합.
- [CI 40203444938](https://github.com/hibi89/REA_Web/actions/runs/40203444938) Linux/Windows 각각 77 테스트 PASS, 3업종 실제 Chromium 검증 PASS, Windows 런처/로컬 API PASS. D4 테스트와 설명서: docs/23_SCHEMA_SUMMARY.md (해당 기능 브랜치).
- 카테고리별 데이터 건수는 CSV 기반 단순 집계이고 컬럼 자료형은 승인되지 않은 추정. 고객 데이터/실사이트를 검증한 것은 아님.

## D5 — 1개 JSON 입력 추가 및 상품 범위 차이 공개 (2026-10-25)
- **구현:** `feature/json-intake` `b1ef76b5f3155ec23dc302af30876ecf9127ea5e`, [Draft PR #8](https://github.com/hibi89/REA_Web/pull/8) (미병합). 기존 `--csv` 유지, `--json` 1개 지원. 예시 `python -m rea.orchestrator --json samples/qa_products.json --out ./out/json-demo`.
- **검증:** [GitHub CI 40204413087](https://github.com/hibi89/REA_Web/actions/runs/40204413087): Linux/Windows **각각 111 테스트 PASS**, 실제 Chromium CSV 3개+JSON 1개, Windows CMD/HTTP PASS. JSON 납품 ZIP/체크섬 PASS.
- **중요:** 30만원 상품 초안의 **최대 2개 파일** 입력은 **아직 미구현**. 단일 CSV 또는 JSON만 지원하며 서로 다른 데이터 파일을 승인 없이 결합하지 않습니다. [D5 범위·제약](https://github.com/hibi89/REA_Web/blob/feature/json-intake/docs/24_JSON_INTAKE_SCOPE.md). 현재 판매/배포 불가, 상용 재배포 라이선스·보안·실고객·Windows 사용성 검증 필요.
- 다음 READY: D6 라이선스/의존성/원본 추적성 점검(미승인 항목은 BLOCKED 명시). 인수인계 `HANDOFF.md`·`docs/17_NEXT_TASK.md` 참조.

## D6-01 — 원본 추적·납품 패키지 감사 (2026-10-26)
- 기능 브랜치 `feature/license-provenance` SHA b97443657e46a8f701e12b83bf87f5a0339b224c, [Draft PR #9](https://github.com/hibi89/REA_Web/pull/9), 미병합.
- [실제 CI 40205614846](https://github.com/hibi89/REA_Web/actions/runs/40205614846) Linux/Windows 각각 **125개 pytest PASS**, Fable 원본 **88개**·Astra P4 부분 원본 **103개** Git Blob SHA 무결성 PASS, Chromium 4개 합성 웹앱/Windows 로컬 런처 PASS.
- 납품 ZIP SHA256·허용파일 목록 감사, 원본 엔진/.env 재삽입 거부. [라이선스·의존성·상용 위험 보고서](https://github.com/hibi89/REA_Web/blob/feature/license-provenance/docs/25_SOURCE_LICENSE_AUDIT.md).
- **라이선스/원본 재배포 권한은 아직 미승인**. 직접 의존성 두 개의 정확한 설치 버전·전이 의존성 미확인, 고객 데이터가 SQLite에 포함됨. **2파일 약속 미구현**, Windows 일반 사용자/실고객/보안 전체 검증 전까지 판매 불가.
- 다음 작업 D7 합성환경 보안·복구 실패주입 검사. 최신 인수인계는 main STATUS.md/HANDOFF.md/docs/17_NEXT_TASK.md.

## D7 verified (2026-10-26)
- `feature/security-recovery` tested SHA `8e7baa8eb14340eae2e7b46f1cf7b9272799c715`, docs SHA `f85b40836ffb1a9343193a8a2fc224249749958d`, [Draft PR #10](https://github.com/hibi89/REA_Web/pull/10) unmerged.
- [GitHub Actions 40206549211](https://github.com/hibi89/REA_Web/actions/runs/40206549211) **141 pytest each on Linux and Windows**, 5 actual Chromium synthetic samples, native Windows .cmd HTTP and 88/103 source blob checks PASS.
- Fixed race-owner directory clobber, partial ZIP exposure, readonly DB; [failure-injection scope and limits](https://github.com/hibi89/REA_Web/blob/feature/security-recovery/docs/26_SECURITY_RECOVERY.md). Unsupported OS and filesystem fail closed, not a full pentest or permission to sell.
- Next D8: guided single CSV/JSON owner field review and explicit approval. Original 2-file offer NOT implemented; legal/source rights, full dependency audit, real customer data and clean Windows human acceptance BLOCKED.

## D8-01 입력 안내·명시적 매핑 승인 (2026-10-26)
- `feature/guided-intake` SHA `a6c35688a5d4cbda93274bc0cd21d1aa825fb255`, [Draft PR #11](https://github.com/hibi89/REA_Web/pull/11), 미병합.
- [CI 40207742776](https://github.com/hibi89/REA_Web/actions/runs/40207742776) Linux/Windows 각각 **164개 테스트 PASS**, Chromium 실제 7개 합성 웹앱, Windows CMD/HTTP·Fable 88/Astra 103 원본 해시 PASS.
- 고객 파일 셀 원본값을 화면에 노출하지 않는 로컬 입력 정보 확인, id/title/category 컬럼 직접 선택, `APPROVE` 입력, 변경 감지 SHA 확인, 생성물 내 매핑 승인 기록과 ZIP 감사. [실행 가이드](https://github.com/hibi89/REA_Web/blob/feature/guided-intake/docs/27_GUIDED_OWNER_INTAKE.md).
- 아직 GUI, 서명된 고객 동의, 두 파일 결합, 상용 라이선스, 실제 고객/일반 Windows 설치 검수는 미완료. 다음 D9: 별도 승인된 동형 두 파일만 안전하게 합치는 실험, 임의 관계 추론/조인 금지.

## D9-01 — 명시적 승인된 동형 2파일 행 추가 (2026-10-26)
- 기능 브랜치 `feature/owner-approved-append` SHA `addb5067a3422cd7ecad6836bcf6620d2f03db1e`, [Draft PR #12](https://github.com/hibi89/REA_Web/pull/12) 미병합.
- [CI 40209013017](https://github.com/hibi89/REA_Web/actions/runs/40209013017) Linux/Windows 각각 **181 테스트 PASS**, 실제 Chromium 8개 합성 앱, Windows CMD/HTTP, Fable 88/Astra 103 원본 SHA PASS.
- 고객이 별도 승인한 동일한 컬럼 구조의 CSV/JSON 두 개만 APPEND(행 추가). 두 원본 SHA·개별 APPROVE·최종 APPEND 필수. 중복 ID, 구조 불일치, 합산 10MB/1만 행 초과 거부, 원본 보존, `append_report.json` 납품감사 포함. [D9 사용 설명](https://github.com/hibi89/REA_Web/blob/feature/owner-approved-append/docs/28_TWO_FILE_APPEND.md).
- **다른 사업 테이블 간 조인/관계 추론 지원 안 함.** 기존 30만원 제안의 보편적인 두 파일 처리 약속은 별도 범위 명시 승인 전까지 판매 불가. 라이선스·실고객·Windows 인간 검수·보안/개인정보 미완료. 다음 D10 검증용 릴리스 후보와 Windows 설치 확인.

## D10-01 — 납품 후보·Windows 설치 진단 (2026-10-26)
- `feature/rc-selfcheck` SHA `1c0b708a3e5d979ad152e89848ef07f800d367c4`, [Draft PR #13](https://github.com/hibi89/REA_Web/pull/13), 미병합.
- [실제 CI 40210279358](https://github.com/hibi89/REA_Web/actions/runs/40210279358): Linux/Windows **각각 188개 테스트 PASS**, Chromium 8개 합성 앱, Windows CMD 로컬 실행, Fable 88/Astra 103 Git 해시 PASS.
- `python -m scripts.d10_make_rc --out NEW_FOLDER` → 단일 CSV / 고객 승인 JSON / 동일 구조 2파일 APPEND 3가지 **합성 데이터 전용 ZIP**과 SHA256 목록. ZIP 내부 `check_windows.cmd`는 Python·라이브러리·SQLite·파일 무결성만 검사, 자동 설치/인터넷 연결 없음. [D10 가이드](https://github.com/hibi89/REA_Web/blob/feature/rc-selfcheck/docs/29_RC_WINDOWS_DEPENDENCY_REVIEW.md).
- CI에서 의존성 14개 메타데이터를 확인했으나 상용 라이선스·정확한 배포 버전 고정은 미완료. **진짜 사용자 Windows 수동 설치, 고객/참조사이트 권한, 개인정보·보안·복구, 고객용 GUI, 30만 원 상품 범위는 미승인**. 다음 D11 합성 고객 3건 견적→납품 예행연습과 미검증 사항 기록.

## D11-01 — 합성 고객 3건 견적→납품 예행연습 (2026-10-26)
- feature/three-case-rehearsal SHA a49f05e969fd49e44b2c8beed2779447d6d56d3e; [Draft PR #14](https://github.com/hibi89/REA_Web/pull/14) 미병합.
- [CI 40211563951](https://github.com/hibi89/REA_Web/actions/runs/40211563951) Linux/Windows **각각 201개 pytest PASS**, 기존 Chromium 8개 + 완성된 납품 ZIP을 풀어 실행한 Chromium 3개, Windows 로컬 CMD, Fable 88/Astra 103 원본 Git 해시 PASS.
- 3개 합성 가상 고객: 카페 목록/검색/필터(4행), 재고 목록/검색/상세(5행), 네일 트렌드 목록/필터/요약(5행). 각 1화면, 계약기능 3개. ZIP·검수표·Chromium 스크린샷·수동시간 **빈 템플릿** 생성. [D11 설명](https://github.com/hibi89/REA_Web/blob/feature/three-case-rehearsal/docs/30_THREE_CASE_QUOTE_REHEARSAL.md).
- **상용 출시 불가:** 30만 원 가격은 미검증 가설. 실제 고객·참조사이트 허가, 일반 Windows 사용자 수동검수, 제3자 상용 라이선스, 개인정보·복구·완전 보안, 3건의 사람 작업시간·환불/지원 계약 미완료. 다음 D12는 정확한 Python 의존성·라이선스·NOTICE 근거를 조사하되 상용 승인으로 간주하지 않음.

## D12-01 — Linux/Windows 의존성·라이선스 증거 감사 완료 (2026-10-26)
- `feature/dependency-notice-evidence` @ `e18e07f714199a734699e1baca24d857c873fa60`, [Draft PR #15](https://github.com/hibi89/REA_Web/pull/15), 미병합.
- [실제 CI #40213031424](https://github.com/hibi89/REA_Web/actions/runs/40213031424) Ubuntu/Windows 각 **217 pytest PASS**, 경고 1건(비차단)씩. 실제 Chromium 합성 앱 8+3 Linux, Windows native ZIP CMD/localhost, Fable 88/Astra PARTIAL 103 소스 SHA 모두 통과.
- 14개 패키지의 관측 버전·조건부 의존성·기설치 라이선스/NOTICE 파일 SHA 증거(개발 CI 전용). Python wheel 아카이브 해시 완전 lock 아님, 법적 사용권·재배포 권한 판단 아님. 원본·고객 납품 ZIP 무수정. [D12 상세](https://github.com/hibi89/REA_Web/blob/feature/dependency-notice-evidence/docs/31_RUNTIME_DEPENDENCY_EVIDENCE.md).
- 다음 D13: 고객용 실행/제작 UX 격차(선택형 로컬 GUI). 30만 원 상품 판매·퍼블릭 배포·고객 실제 납품·완전한 라이선스/보안 검증은 승인되지 않음.
