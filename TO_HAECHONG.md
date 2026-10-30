## REA_Web D27 continuation — 2026-10-30 KST (supersedes prior test snapshot)

- **Product code/test checkpoint:** `55cf80d162f1a725f075867104ced3f6821d1d1e` on `feature/d27-windows-python-discovery`; PR #30 stays OPEN/DRAFT/UNMERGED. Commit `1368a199` hardened exporter Windows device aliases and `eb8b3853` matched shipped offline customer checker, `55cf80d` added a six-case regression. Windows also reserves superscript COM¹/²/³ and LPT¹/²/³ (Microsoft official Naming Files, Paths, and Namespaces guide).
- **Focus tested:** Linux Python 3.13 `python -m pytest -q tests/test_sale_gate.py tests/test_delivery_zip_hardening.py` yielded **63 passed / 0 failed** in a deliberately isolated fixture workspace. The focused regression source file is verified identical to GitHub blob `4f5936b425c02a95d927b96cae0c8d1b52f0e321`; exact GitHub function checksums matched for `_safe`, `_members`, `verify_delivery`, and `_safe_member`. The helper modules used isolated source excerpts/stubs, **not the original full repository checkout**, native Windows or complete produced-ZIP E2E. The separate Linux environment has no `github.com` DNS for cloning.
- **CI observation:** On code checkpoint `55cf80d`, first 28 PR-triggered GitHub Actions runs were **QUEUED**, including D27 and D31. This is **not a failed job**, but there is **no latest-code Actions PASS evidence**. Old `c42c4c4` 29/29 SUCCESS cannot be transferred. A new documentation SHA after this update needs fresh head/CI lookup.
- **Production:** No Vercel project/URL applies; release target is offline local Windows ZIP, not hosted production. User-facing Windows native launch/browser/CRC/restart on exact code checkpoint **NOT_VERIFIED**.
- **Release gate unchanged:** Independent nondeveloper Windows acceptance NOT_RUN, actual source/dependency commercial redistribution rights NOT_GRANTED, privacy/customer-data handling NOT_APPROVED, seller terms NOT_APPROVED, measured human delivery rehearsal NOT_RUN. The six-field machine ledger alone is **not approval**. Prior engineering 95% and sale preparation 77% are *qualitative unrecalculated estimates*, not measured completion. **NOT APPROVED FOR SALE**.
- **Next task:** Check D27, D31 CI for this exact code HEAD after runners execute; inspect failing job logs, do minimum code correction; complete original-checkout Python 3.11 pytest plus synthetic Windows ZIP/extract/CMD/Chromium E2E when supported. Do not merge or force-push, and do not generate fake owner/rights sign-off.

---

## [LATEST] REA_Web release-hardening checkpoint — 2026-10-30 KST

1. **Goal/confirmed scope:** KrW 299,000-class customer-owned CSV/flat-JSON → explicit mapping approval → readonly local FastAPI/SQLite → Windows ZIP, optional same-schema two-input ROW APPEND. No different-schema JOIN, hosting, payments or scraping.
2. **Work completed:** Windows path/device/casefold defenses in delivery ZIP and standalone extracted customer self-check; strict date gate; malformed non-object ZIP manifest now returns bounded validation errors instead of uncontrolled `AttributeError`. Code commit checkpoint **`40144c58fa84c1d5cc67ef239c43810e73f66eae`**. Do not change existing data or upstream imports.
3. **Tests:** Separate Linux Python 3.13 / no direct GitHub network; `python -m pytest -q tests/test_sale_gate.py tests/test_delivery_zip_hardening.py` returned **57 passed / 0 failed**. All three focused test/source sale-gate files matched exact Git blob SHA; ZIP-check tests used source-function excerpts matched to GitHub, isolated from unrelated application modules. These tests are **focused isolated verification, not entire original checkout, Windows or generated ZIP E2E**. The new eight malformed-manifest cases passed.
4. **State:** Engineering previously estimated 95% and sale preparation 77% (qualitative, carried; not remeasured). Latest code not yet approved for sale. This code checkpoint GitHub Actions query showed **first 28 PR workflows QUEUED**; full app CI current-head PASS not established.
5. **Failure/blocker:** Direct clone / remote network in local test container failed DNS (github.com could not be resolved); used connector-fetched exact source/test files plus isolated source excerpts instead. GitHub hosted CI queue pending; do not relabel queue as failure or success. No reason to repeat identical blocked network clones.
6. **Repository/branch:** `hibi89/REA_Web`, `feature/d27-windows-python-discovery`, code SHA `40144c58fa84c1d5cc67ef239c43810e73f66eae`, Draft PR #30 toward `integration/develop`; no merge, no force push. Main paths: `rea/delivery.py`, `rea/customer_self_check.py`, `scripts/rea_sale_gate.py`, `tests/test_delivery_zip_hardening.py`, `tests/test_sale_gate.py`.
7. **Deployment:** Windows local ZIP target; Vercel Production **NOT APPLICABLE**. Python 3.11+ and runtime dependencies may be installed by customer; ZIP is not standalone EXE. Exact build/test commands are in D27 workflow and Windows README.
8. **Original/backup/security:** No actual customer data used. Preserve customer-provided original ZIP and snapshots. Shipping SQLite is plaintext. Distribution/source/dependency licensing and customer privacy authorization are **NOT GRANTED**; never commit tokens or actual private ledgers.
9. **Next priority / completion gate:** On current exact branch SHA, inspect D27 Linux/Windows tests & browser and D31 dependency audit; if failing diagnose exact job logs. Run original checkout targeted+full pytest and Windows extracted synthetic ZIP if available. Six human/rights/seller gates remain: independent Windows operator, source redistribution rights, dependency notices, privacy/data handling, sale terms, measured human delivery. None is automatically approved by tests.
10. **Timestamp/evidence:** 2026-10-30 KST handoff; verified code checkpoint `40144c58fa84c1d5cc67ef239c43810e73f66eae`; document commit SHA must be re-read from live branch after this update. CI status is a sampled, time-sensitive observation, not a blanket latest pass. Final state **PARTIAL / SALE BLOCKED**, not 100%.

---

# TO_HAECHONG — REA_Web 개발 인수인계 / 2026-10-30

> **다음 해총 채팅에서 먼저 읽을 문서.** 이 문서는 완료 선언이 아니라 정확한 GitHub 상태와 다음 작업 우선순위를 전달한다. 본문 기록 시점의 브랜치 HEAD는 `2cffe5c6d56e95119f333a6881db62c084f204fd`이다. 재개할 때는 GitHub의 실제 HEAD와 PR/CI를 다시 조회하라.

## 0. 프로젝트와 운영 지시

- 저장소: `hibi89/REA_Web` — **`hibi89/web-rea-studio`와 혼동 금지**.
- 개발 브랜치: `feature/d27-windows-python-discovery`
- PR: [#30](https://github.com/hibi89/REA_Web/pull/30), `integration/develop` 대상으로 **OPEN / DRAFT / UNMERGED**.
- 최종 목표: 크몽에서 299,000원대 소규모 **고객 소유 CSV/flat JSON → 명시적 승인 → 읽기 전용 로컬 FastAPI/SQLite 웹앱 → Windows 납품 ZIP** 서비스 상품화.
- 선택 기능: **동일 구조 두 파일 각각 승인 후 ROW APPEND만**. 관계형 JOIN/실시간 수집/호스팅/로그인/결제/CRUD는 판매 범위에서 제외.
- 사용자 목표는 **가능한 기술 작업 100% 마감**. 그러나 검증하지 않은 법적 권리/인수 확인/계약 조건을 사실인 것처럼 100% 처리하지 않는다.
- 사용자에게 확인이 반드시 필요한 외부 조건을 제외하고 GitHub에서 자율적으로 기능·검증 작업을 이어라. 필수 차단 CI만 확인하고 단순 문서·반복 CI 대기를 개발 병목으로 만들지 말 것. 중간 설명보다 코드·테스트 결과 우선.
- 코드/테스트/제품 포장 변경은 기능 단위 커밋으로. **force-push, 기존 브랜치 초기화, PR 임의 병합, 고객 실제 자료 사용 금지**.

## 1. 이전 코덱스에서 받은 상태

- 코덱스가 GitHub 브랜치에 `c42c4c4` (`scripts/windows_native_smoke.py` 실패 로그·임시 폴더 보존)와 `ffbc7c8` (상태·핸드오프 문서)를 실제 커밋했다.
- 그때 `STATUS.md`/ `HANDOFF.md`는 **해당 코드 커밋** 기준 원격 GitHub Actions **29/29 SUCCESS**, D27 Windows **446 passed/1 warning**, Linux **431 passed/5 skipped/1 warning**을 기재했다. 합성 데이터 원격 CI 실증이지 일반 고객 인수검수는 아니다.
- 로컬 독립 Windows HTTP 점검은 이전 샌드박스의 `WinError 10013` 및 정리 권한 문제로 BLOCKED. 로컬 전체 테스트 INCOMPLETE. 완료한 것으로 둔갑시키지 말 것.
- 이전 문서의 개발 완성률 **95%**, 판매 준비 **77%**는 객관적 측정값이 아니라 계속 전달된 정성 추정치. 새 커밋으로 자동 상승/100% 처리하지 않는다.

## 2. 이번 해총이 실제 GitHub에 반영한 커밋

1. `5b1e50c` — `scripts/rea_sale_gate.py`: 6개 외부 출시 승인 증거 필드가 모두 기록돼야 'READY_FOR_SELLER_FINAL_REVIEW'를 반환하는 fail-closed **기록 검사 도구**. 법률 검증이나 고객 인증기가 아님. 초기 상태는 BLOCKED.
2. `cdffa84` — `tests/test_sale_gate.py`: 원장 비어 있음, 잘못된 날짜/증거, 잘못된 SHA, 중복 JSON 키, CLI 초기화/판정을 시험하는 새 테스트.
3. `7c9c955` — `docs/56_SALE_GATE_CLOSEOUT_20261030.md`: 외부 검증 6개 조건과 원장 실행 방법.
4. `0b76566` — `rea/delivery.py`: 배송 ZIP 검사에서 Windows 예약명(CON/PRN/AUX/NUL/COM*/LPT*), ':' ADS, 끝 공백/점, ZIP symlink 항목 차단 보강.
5. `2cffe5c` — `tests/test_delivery_zip_hardening.py`: Windows 특수 경로·악의적 심볼릭 링크 및 일반 파일 통과 회귀 케이스.

**코드와 테스트 파일이 GitHub 원격 브랜치에 실제 존재함을 확인했다.** 단, **이번에 추가한 테스트를 별도로 실행한 증거는 아직 없다.** 이전 채팅의 '로컬 6개 통과'라는 표현은 실행 로그가 없어 검증 완료로 계산하지 말 것. 특히 새 코드 커밋의 CI는 아래와 같이 대기 중이다.

## 3. 마지막 확인한 CI 상태와 재개 순서

- 확인 대상 HEAD: `2cffe5c6d56e95119f333a6881db62c084f204fd`.
- GitHub PR-trigger workflow 목록의 첫 페이지 **28개 전부 QUEUED / PASS 미확정** (점검 당시). 포함: D7, D25, D27, D31, D3. 일부 추가 workflow나 job은 목록에서 빠졌을 수 있다.
- 즉, 기존 `c42c4c4`의 29/29 성공을 **새 HEAD에 그대로 적용 금지**.
- 최우선 P0: **PR #30·브랜치 HEAD·Actions 완료 여부 재조회**. 실패/테스트 오류 있으면 원인과 실제 실패 항목만 수정. 각 패키징 함수/기존 고객 ZIP 불변성이 깨졌는지 확인.
- P1: `python -m pytest -q tests/test_sale_gate.py tests/test_delivery_zip_hardening.py` 실행 가능한 환경에서 실제 검증. 테스트가 미실행이면 NOT_RUN으로 보고. 필요하다면 `rea/delivery.py` 안전 검사와 `rea/customer_self_check.py` 검사의 정책 일치 여부도 비교.
- P2: `docs/56_SALE_GATE_CLOSEOUT_20261030.md` 근거로 판매 범위와 공급 코드/고지 대상의 실물 인벤토리, 실제 단순 고객 인수 시나리오 재점검. 권리 확인을 자동 생성하지 말 것.
- P3: CI 통과 뒤 작업이 실제로 필요할 때만 추가 보안·회복력 개선. 이미 구현된 CSV/JSON/APPEND/UI/ZIP을 중복 작성하지 않는다.
- P4: 기능 기술적 마감 여부, 미실시 수동 검증, 제품 판매 준비, 테스트 증거를 분리해 `STATUS.md` 또는 이 파일에 업데이트. 코드가 실제로 PASS할 때만 해당 항목을 완료 처리.

## 4. 기술적 범위 및 외부 승인 차단 항목

실증된 기존 기술: CSV/flat JSON 입력과 명시적 매핑 승인, 두 파일 ROW APPEND, SQLite 기반 읽기 전용 앱, 검색/필터/상세, ZIP CRC/해시, Windows CMD Python 3.11+ 찾기·실행/복구 안내, 합성 데이터 CI/Chromium/네이티브 실행.

**실제 판매 승인에 아직 필요한 6개 게이트:**

- **independent_windows_operator:** 비개발자가 실제 Windows에서 합성 ZIP으로 설치·실행·검색·종료/재시작·백업/복구·오류 상황을 확인하고 결과 기록. `docs/52_WINDOWS_CUSTOMER_ACCEPTANCE_PROTOCOL_NOT_RUN.md`
- **source_redistribution_rights:** 실제 고객 ZIP에 포함되는 REA/생성 코드 상용 재배포 권리 확인. `docs/25_SOURCE_LICENSE_AUDIT.md`
- **dependency_license_notices:** 실제 배포 의존성 및 LICENSE/NOTICE 의무 검토. 단순 metadata 수집은 승인이 아님. `docs/48_RUNTIME_DISTRIBUTION_REVIEW.md`
- **privacy_data_operations:** 고객 데이터 권리, 수령/보관/삭제 및 비암호화 SQLite가 ZIP에 들어감을 알리고 운영 결정. `docs/53_DATA_HANDLING_REVIEW_NOT_APPROVED.md`
- **seller_scope_terms:** 판매자 가격·수수료·납기·수정·지원·환불/취소 약관 명시 및 승인. `docs/07_KMONG_OFFER.md`, `docs/51_KMONG_SALE_GATE_20261030.md`
- **measured_delivery_rehearsal:** 사람의 실제 견적→생성→검수→납품 시간 측정; CI 시간으로 대체 불가. `docs/30_THREE_CASE_QUOTE_REHEARSAL.md`

외부 인간 판단/권리까지 자동화로 승인할 수 없다. `scripts/rea_sale_gate.py`는 **증거 기재 누락 검사일 뿐**, 기재된 증거의 진실성 또는 법적 효력 검증기가 아니다. 최종 판매 승인 판단은 별도.

## 5. 다음 채팅 시작 지시

> "해총, `hibi89/REA_Web`의 `feature/d27-windows-python-discovery`에서 `TO_HAECHONG.md`를 읽고 바로 이어가라. 현재 원격 HEAD/PR #30/CI부터 재검증하고, 이번에 추가한 ZIP 보안 검사와 릴리스 게이트 테스트를 실행/수정하라. CI 확인이 필수 병목이 아닐 때는 다음 독립 작업으로 진행. 실제 검수와 재배포 권리 없는 100% 판매 승인 선언 금지. 코드 구현/테스트/커밋·푸시를 우선하고 각 작업 종료 시 기능 완성률·판매 준비율은 근거를 구분하여 보고하라."

## 6. 인수인계 문서 링크

- PR: https://github.com/hibi89/REA_Web/pull/30
- 이번 릴리스 마감 가이드: https://github.com/hibi89/REA_Web/blob/feature/d27-windows-python-discovery/docs/56_SALE_GATE_CLOSEOUT_20261030.md
- 실제 브랜치: https://github.com/hibi89/REA_Web/tree/feature/d27-windows-python-discovery
- GitHub Actions: https://github.com/hibi89/REA_Web/actions
