## 2026-10-31 04:42 KST — Latest Lite synthetic delivery checkpoint

On branch `feature/lite-offline-html-integration`, tested code SHA `202e4dbab9153c4f3003170e8881576d75c63b0c`: GitHub Actions Windows + Ubuntu **2/2 SUCCESS**, with three actual seller CLI synthetic output rehearsals, exact HTML byte-match cross-OS, ZIP+manifest SHA checked. Evidence `docs/61_LITE_CROSS_OS_DELIVERY_EVIDENCE_20261031.md`, artifacts Windows #13007070338 and Ubuntu #13004944630. Original Pro unchanged. Draft PR #31 UNMERGED. Independent human Windows Chrome/Edge, IP/licenses, plaintext privacy, real manual delivery times and seller pricing/refund/support remain BLOCKED/NOT_APPROVED. No Vercel. Handoff in HANDOFF.md.

## 2026-10-31 04:34 KST — LITE integration update on feature/lite-offline-html-integration

Lite independent code is now committed, and current code/test SHA `91c1d113f81f0b144ba217820e6f0ca4b2350166` passed Windows+Ubuntu real Pro parser and Chromium file:// CI 2/2. Draft PR #31 to Pro development branch, unmerged; customer Windows human NOT_RUN and commercial NOT_APPROVED. Follow branch-local HANDOFF.md/STATUS.md and docs/60_LITE_SALE_GATES_20261031.md. Existing Pro branch and PR #30 remain unchanged.

## 2026-10-31 KST — CURRENT DISPATCH OVERRIDE (READ FIRST)

This section supersedes historical 2026-10-30 snapshots below. **Actual source/test SHA `bbf2ec26923c0c6dc84a1263780f9e8e5b13fdf5`: all 28/28 GitHub Actions concluded SUCCESS.** D27 Linux 645 pass/5 skip, Windows 656 pass/4 skip, Chromium 8 generated apps + 3 extracted ZIPs PASS. Current verified Windows synthetic pilot artifact [#12997912131](https://github.com/hibi89/REA_Web/actions/runs/41099504224/artifacts/12997912131) (ZIP SHA256 `a8d2076663e3dfb289e158c20653ad1e347208647e42962d30a58dcb464bec35`). Human Windows acceptance NOT_RUN, sale NOT_APPROVED, PR #30 Draft and unmerged, no public deployment. **Next 'ㄱ':** prioritize one independent Windows pilot or separately actionable license/privacy/seller gate; do not re-run 28 CI or generate docs-only commits without a new state change. Read `HANDOFF.md`, `STATUS.md`, `docs/17_NEXT_TASK.md` for latest detail. The product is not a general URL-to-site clone and does not support arbitrary JOIN or non-local hosting.

## REA_Web current handoff — 2026-10-30 KST, technical closeout sprint

**Verified GitHub code checkpoint:** `c52296bbf388547f118186e5e67298a7e002d0cb`, branch `feature/d27-windows-python-discovery`, Draft PR #30 OPEN/UNMERGED. Vercel production not applicable; offline Windows ZIP delivery product. No merge or force push.

**Two substantive code changes this sprint:**
1. `d042d99e750c6e1c777b8530bc12a8f71cdd0b17`: generated app `rea/templates/static/app.js` now launches primary list, overview, and optional categories fetch independently using `Promise.allSettled`. Failure of the optional categories endpoint no longer blocks all visible customer rows; overview failure shows explicit bounded error while preserving list functionality. `scripts/d3_browser_acceptance.py` adds a real Chromium network fault injection to the inventory case, checking list/summary survive category API failure and recover after reload. Earlier cafe aborted-list regression is retained.
2. `c52296bbf388547f118186e5e67298a7e002d0cb`: generated `rea/templates/app.py` now validates bounded (<=256KiB) `schema_preview.json` through a common metadata reader and returns safe HTTP 503 on missing, oversized, malformed or incompatible shape. `/health` now checks both metadata and read-only SQLite, so cannot falsely claim normal readiness when required schema is lost. `/api/schema` and `/api/summary` share the bounded reader. Healthy behavior and read-only SQLite semantics preserved; no customer source altered. `tests/test_generated_db_unavailable.py` adds two committed metadata failure tests. They have not been directly executed in the full original checkout.

**Executed tests with observed results:** Exact GitHub JS blob `010d1218ee2b564039dfc23105f0c5a60ce20648` compiled and executed in a synthetic JS DOM/fetch test harness: four cases PASS/0 FAIL (normal, category unavailable, summary unavailable, list unavailable). Exact GitHub Python app blob `ca185bd1e9df662e12423a76c572da103ff5b723` was reconstructed in a separate Python 3.13.5/FastAPI TestClient Linux sandbox and independently confirmed by Git blob SHA1 equality and Python AST parse. With a generator-compatible synthetic SQLite fixture, **31/31 HTTP assertions PASS** on healthy /health, literal wildcard search, list/summary/schema/category/detail, missing/malformed/oversized metadata (consistent 503), DB missing/table dropped (consistent 503), and no DB recreation/owner row change. Initial harness had a missing `assert_status` helper causing NameError before any assertions; helper was added and the full harness was rerun 31 PASS. These are exact runtime file tests but NOT the full original repository, original `rea.mvp.generate`, Windows CMD/Chromium or independent end-user validation.

**CI:** Latest prior documentation HEAD `fdc541e8` 28 Actions workflows/56 checks were QUEUED, no conclusions. New code-head D3/D27/D31 pending; no current-head CI PASS claim. Do not repeatedly poll. Run full original-checkout pytest, D3 Chromium and Windows generated ZIP native smoke when runners execute. Fix actual failures only; preserve functionality/data.

**Release state:** Historical engineering ~95% and seller readiness ~77% are qualitative old estimates, not remeasured. Independent nondeveloper Windows acceptance NOT_RUN, source/vendor and exact shipped-dependency redistribution rights NOT_GRANTED, data authorization/privacy handling NOT_APPROVED, seller price/terms NOT_APPROVED, human-timed delivery rehearsal NOT_RUN. Therefore **NOT APPROVED FOR SALE**. Completion remains PARTIAL/TECHNICAL-VERIFICATION-PENDING.

**Next steps:** (1) exact-head D27 Linux/Windows full regression and D3 browser, D31 security results after queue drains; (2) real Windows original generated ZIP -> new-folder restore -> command-line prerequisite check -> localhost /health/items/search/detail -> restart, plus manual screenshot/inspection; (3) independently authorize external licensing, data/privacy, seller terms and real Windows operator acceptance. No source license grant may be inferred from passing tests.

---

## Latest exact-head status (2026-10-30; branch HEAD c42c4c49f7e192af5921efe32b26d025a22ed60e)

- PR #30 remains OPEN / DRAFT / UNMERGED. Commit c42c4c4 changes only the Windows smoke QA helper; no merge or force update.
- Current exact-head GitHub Actions: **29/29 SUCCESS**. D27 Windows run 40984255021: **446 passed / 1 warning**, extracted ZIP/CMD/localhost checks passed; D27 Linux run 40984248440: **431 passed / 5 skipped / 1 warning** and Chromium passed. D3 Windows/Chromium run 40984254836 and D31 Ubuntu/Windows generated-runtime audit 40984254952 passed. All CI data/apps are synthetic, not customer acceptance or commercial clearance.
- Local Python 3.11.9: compileall and pip check PASS; focused D21/D25/D27/customer guidance **51 passed / 2 skipped**; non-ASGI suite **300 passed / 10 skipped / 1 deselected**. The latter excluded eight TestClient-heavy files and one D18 localhost test after sandbox stalls/denial.
- Local native Windows smoke prepared the ZIP in workspace QA temp but localhost /health was blocked by sandbox WinError 10013; process cleanup was denied. Full local suite remains INCOMPLETE; do not infer local HTTP success from remote CI.
- Offer scope remains CSV/flat JSON, owner-approved field mapping, optional same-schema two-file ROW APPEND, read-only local SQLite app and Windows ZIP. No JOIN between different schemas, crawling, hosted service, login/payment or CRUD.
- Human nondeveloper Windows acceptance NOT_RUN; source/vendor/dependency redistribution rights NOT_GRANTED; customer-data/privacy and seller terms NOT_APPROVED. Development 95% / sale preparation 77% are qualitative carried estimates. **NOT_APPROVED_FOR_SALE.**

## Exact-head continuation update (2026-10-30; `4ce86ec2472bd350b0009390f8ed49111d29b8ae`)

- GitHub branch `feature/d27-windows-python-discovery` and PR #30 were re-read at this SHA. PR is OPEN / DRAFT / UNMERGED; no merge or force push was performed.
- Current-head Actions query returned **28/28 completed SUCCESS**. D27 run `40976199908`: Windows **446 passed / 1 warning**, Linux **431 passed / 5 skipped / 1 warning**. D3 run `40976200008` passed Windows native and Chromium checks against three generated apps. D31 run `40976199915` passed Ubuntu and Windows generated-runtime audit. Fixtures and generated packages are synthetic.
- The exact-head local mirror matches **173/173 Git blobs**. Exact-136 synthetic CSV, flat-JSON, and approved same-schema two-file APPEND ZIPs pass CRC, clean extraction and Windows CMD prerequisite check. The runtime source was unchanged between 136e023 and 4ce86ec; the latter adds a recheck document only. Direct generated-handler checks cover health/list/search/category/detail/404 and SQLite quick_check; they are **not localhost HTTP or full browser tests**.
- Current sandbox localhost client connection remains **BLOCKED/NOT_RUN** (`WinError 10013`); local full pytest did not produce a final summary and is **INCOMPLETE**. GitHub Windows CI separately passed the extracted-package localhost checks. Do not conflate those scopes.
- Development **95%** / Kmong preparation **77%** are prior qualitative estimates, not recalculated. Independent nondeveloper Windows acceptance **NOT_RUN**; source/vendor/runtime redistribution rights **NOT_GRANTED**; real-customer data authorization/privacy and seller terms **NOT_APPROVED**. The product is **NOT_APPROVED_FOR_SALE**.
- Next independent engineering work: refresh the exact-head generated-runtime dependency/license evidence and continue synthetic privacy/backup checks. Keep external human and rightsholder gates open until evidence is supplied.

# REA_Web — CURRENT RESUME SNAPSHOT (2026-10-30)

## 최신 원격 재확인 (2026-10-30; `50c82814821f89f0326cefcf04c2ee78e080d5c4`)

- 지정 브랜치 HEAD와 PR #30을 다시 확인했습니다. PR은 OPEN / DRAFT / UNMERGED 상태입니다.
- 이 정확한 HEAD의 GitHub Actions 첫 페이지에서 28개 모두 완료 SUCCESS, 진행 중/대기/실패 0건입니다. D27 `40969580989`, D3 `40969580958`, D31 `40969581132` 모두 SUCCESS입니다. 자동 검증 fixture는 합성 데이터이며 사람의 고객 검수로 간주하지 않습니다.
- 별도 격리 로컬 검사 기록은 고객 안내+D27 21 PASS, D6 14 PASS/1 SKIP, D9 경계·APPEND 15 PASS/2 DESELECTED, 새 ZIP 검증·CRC·깨끗한 압축 해제 후 실제 CMD 사전 검사 PASS입니다. 이 환경의 실서버 HTTP는 /health timeout/SQLite cleanup lock 때문에 BLOCKED/NOT_RUN이며 로컬 HTTP 성공으로 표현하지 않습니다.
- 개발 95% / 판매 준비 77%는 정성 추정치로 재측정하지 않았습니다. 상용 재배포 권리 NOT_GRANTED, 고객 데이터·개인정보/판매 조건 NOT_APPROVED, 비개발자 Windows 인수검수 NOT_RUN이므로 판매 승인 상태가 아닙니다.
- 아래에 남은 과거 시점 기록은 이 재확인보다 오래된 스냅샷입니다. 최신 상태를 주장할 때 이 메모와 정확한 원격 HEAD를 기준으로 삼으세요.



## 최신 확인 상태 (2026-10-30; 검증 기준 commit `970bbde`)

- D27 제품 코드와 D31 감사 워크플로의 검증 기준은 `970bbde8c853f4ed1382c038091bb2ee48abea9f`입니다. 이후 `ebb1f22`는 상태 문서만 갱신했으며 제품 코드는 바뀌지 않았습니다. PR #30은 OPEN/DRAFT/UNMERGED입니다. 강제 푸시나 병합은 하지 않았습니다.
- 검증 기준 commit `970bbde8c853f4ed1382c038091bb2ee48abea9f`의 GitHub Actions 28/28 SUCCESS입니다. D27 전체 회귀 [#40967860714](https://github.com/hibi89/REA_Web/actions/runs/40967860714)의 Linux D1–D27/Chromium과 Windows D1–D27/native-package job이 모두 성공했습니다. D31 생성 런타임 보안 감사도 Ubuntu/Windows PASS입니다. 모두 합성 데이터 자동 검증이며 사람의 고객 검수는 아닙니다.
- 이번 로컬 집중 검사: 고객 안내 + D27 Python discovery **21 passed**; D6 provenance **14 passed, 1 skipped**; D9 boundaries/두 파일 APPEND **15 passed, 2 deselected**. 제외 항목은 실제 TestClient HTTP 대기와 symlink 권한 경계입니다.
- 실제 Windows ZIP을 합성 데이터로 생성하고 ZIP CRC 및 깨끗한 새 폴더 추출 후 `cmd.exe /d /c check_windows.cmd --check` **PASS**. 별도 로컬 더블클릭 HTTP 스모크는 /health 시간 초과와 SQLite 잠금 정리 문제로 **BLOCKED/NOT_RUN**이며 PASS로 처리하지 않았습니다. CI의 Windows localhost HTTP는 위 D27 run에서 PASS입니다.
- 개발률 **95%**, 판매 준비율 **77%**는 정성적 기존 추정치이며 다시 측정한 값이 아닙니다. 상용 재배포 권리 **NOT_GRANTED**, 고객 데이터 승인/개인정보 검토와 판매 조건 **NOT_APPROVED**, 비개발자 Windows 인수 검수 **NOT_RUN**. **판매 승인 아님**.
- D31 감사는 합성 앱이 생성한 broad requirements의 현재 호환 버전 및 전이 의존성을 검사합니다. 특정 고객 환경의 lockfile, 법률적 권리 또는 배포 승인 근거가 아닙니다.


## D27 product follow-up refresh (snapshot before this documentation update, 2026-10-30)

- The feature ref was re-read at `ab3eb2dd39ba334999fca95dcfaf65af4842c0c2`. Its 27 returned GitHub Actions runs later all completed successfully. D27 Windows+Linux run `40960995478`, D3 Windows-native+Linux-browser run `40960995506`, and D6 `40960995289`, D21 `40960995434`, D26 `40960995430` all passed.
- The isolated source copy was verified against all 171 Git blobs at that SHA. Three synthetic delivery ZIPs were generated from it; archive CRC and actual Windows `check_windows.cmd --check` passed 3/3. These are QA samples, explicitly not customer deliveries or sales authorization.
- Local Windows full pytest and focused regression did not complete: the full run stopped at 64% after showing a failure, and the focused run showed failures then stalled. Their failure causes are not adjudicated. The direct local CMD-launch/loopback smoke did not return health in time and cleanup encountered a locked SQLite file; local Chromium did not reach a case result. Do not claim local E2E success. Current-head GitHub Windows-native and Linux-browser jobs are the verified E2E evidence.
- The prior project estimates remain **88% development / 68% sale preparation**, carried forward from the detailed `6776582` validation report; they have not been recalculated for the newer commits. Human customer acceptance remains **NOT_RUN**, commercial redistribution rights **NOT_GRANTED**, customer-data authorization/privacy **NOT_APPROVED**, seller terms **NOT_APPROVED**. The product is not approved for sale.
- PR #30 remains open/draft/unmerged. This snapshot is the record immediately before the documentation follow-up commit; the latest branch tip should be read from GitHub.
## Current continuation note (2026-10-30; commit `2be8bb6`)

- Exact branch `feature/d27-windows-python-discovery` now points to `2be8bb6c6092ce771124977125502306f9dd2389`, a normal fast-forward child of `64b28c986618c68472649474c6604c2b1fce7372`. No force update or merge was used. This is six commits ahead of baseline `db6711e`.
- The connector showed nine workflows queued when queried immediately after `2be8bb6`; no success result for that commit is claimed here. The earlier 27/27 returned successes refer only to commit `64b28c9`.
- The direct dependency-boundary cases have now been committed. The isolated guidance tests were 18 PASS; compileall passed. Full local regression remains incomplete/blocked by sandbox filesystem denials; see the detailed validation receipt.
- Change patch and SHA-verified source/document bundle are in `bundle_update_notes`; these are GitHub review artifacts, not an independently runnable customer delivery ZIP.
- Helper branch `codex/REA_Web-bounds-regression` remains an accidental incomplete one-file tree. The connector exposes no branch deletion. Do not use it. The designated feature branch was safely advanced only after constructing/verifying a full base-tree-preserving commit.
- Human Windows acceptance: NOT_RUN; commercial redistribution rights: NOT_GRANTED; customer authorization/privacy: NOT_APPROVED; listing terms: NOT_APPROVED. **Not approved for sale/intake.**

The dated status snapshots below this note are historical and are superseded where they state an older branch head, test boundary status, or that the feature branch was not updated.
## Follow-up resume pointer (2026-10-30)

The designated feature branch currently resolves to `64b28c986618c68472649474c6604c2b1fce7372`. GitHub CI connector returned 27 successful completed runs, but omitted one expected workflow from its first-page response; do not claim 28/28. Local patched customer-guidance tests 18 PASS and compileall PASS. Full local regression is incomplete/blocked by sandbox WinError 5 during atomic file publication; D27/D26 focused tests reproduce that restriction.

Continue from `bundle_update_notes/REA_Web_kmong_db6711_to_64b28c9.patch` and `customer_bundle_changes/`. Patch applies to exact `db6711e` base. The original source ZIP snapshot has no `.git`; do not modify it as the only copy. Never use helper branch `codex/REA_Web-bounds-regression` (incomplete one-file tree). Target feature branch remains at 64b and was not changed in the rejected ref update.

Sale gates remain: independent human Windows acceptance NOT_RUN, commercial source/dependency redistribution NOT_GRANTED, real customer-data permission/privacy NOT_APPROVED, and seller terms/price NOT_APPROVED. Resume independent local work without waiting for CI; do not mark those gates complete from automation.

Latest feature branch HEAD: `578442b2bd22bb64a004e77bbd091a17930f614a`. Draft PR #30 is open and unmerged.

Exact-head GitHub Actions **28/28 SUCCESS**, including D27 Windows/Linux full regression, D6 supply-chain/security, extracted Windows CMD and localhost smoke, and Chromium synthetic scenarios. D27 runs: [PR #40954859581](https://github.com/hibi89/REA_Web/actions/runs/40954859581) and [push #40954852936](https://github.com/hibi89/REA_Web/actions/runs/40954852936); D6: [#40954859774](https://github.com/hibi89/REA_Web/actions/runs/40954859774).

The runtime security floor is Starlette `>=1.3.1,<2`. Customer preflight checks installed minimum versions; Korean recovery instructions cover both `python` and `py -3`. Local focused preflight/guidance tests: **13 PASS**; compile, local dependency floor check, pip check, five synthetic extracted ZIP checks and patch application: **PASS**. The ZIPs are synthetic and retain human-acceptance/commercial-rights disclaimers.

Customer-authorized CSV/flat JSON → explicit mapping approval → local SQLite webapp → ZIP is implemented and CI-verified. Same-schema two-file APPEND requires both approvals. Different-schema JOIN is unsupported.

**Not released for sale:** PR #30 remains draft; human/nondeveloper acceptance **NOT_RUN**; source and dependency redistribution rights **NOT_GRANTED**; real customer-data authorization/privacy review **NOT_APPROVED**. Current estimates: development **95%**, sale preparation **77%**. Do not treat CI as human or legal approval.

## Next safe task

Build a reproducible runtime dependency graph and license/NOTICE evidence for the generated app and tested environment. Report gaps and exact artifact/version limits; do not mark rights granted. Then continue independent local package/privacy checks. Preserve existing source and customer data; never force-push or merge the draft PR.

## Historical resume notes follow (2026-10-27)

# REA_Web — NEW CHAT ZERO-QUESTION RESUME ENTRYPOINT

## EXACT USER TRIGGER
**[REA_Web 깃헙 레포지토리 보고 작업이어가셈]**

The exact sentence above is a **standing instruction to immediately inspect this repository and EXECUTE the next READY engineering task**, not merely to summarize, ask what to do, or generate an unrelated plan. Do NOT require the owner to re-explain the project, attach a Fable ZIP again, specify a branch, or say 'ㄱ' separately. The trigger itself authorizes the next **bounded, safe, local/synthetic** task. No autonomous/background work occurs between user prompts.

## First tool actions every new session (mandatory)
1. Open the connected GitHub repository **hibi89/REA_Web**, fetch **current remote main HEAD**, and read in order:
   - `WORKER_START_HERE.md` (this file)
   - `STATUS.md`, `HANDOFF.md`, `docs/17_NEXT_TASK.md`
   - `docs/SESSION_RESTART_PROTOCOL.md`, `AGENTS.md`, `docs/MVP_3DAY_SPRINT_PLAN.md`
   - `docs/02_ARCHITECTURE.md`, `docs/08_BRANCH_POLICY.md`, `docs/14_FINAL_DELIVERABLES.md` as needed for assigned work.
2. Inspect the HEAD **and any actual changes since that HEAD** on the designated feature branch before writing. Read its README/tests and relevant source files; do not overwrite other work.
3. Verify current PR/CI status for claims you make. NEVER infer PASS from workflow YAML or past-turn logs.
4. Implement the **single latest READY task** on its designated branch, run available real checks, commit/push using GitHub, record results in `STATUS.md`, `HANDOFF.md`, and `docs/17_NEXT_TASK.md` (on main; merge/rebase only if conflict-safe). Include the commit SHA and NOT_RUN/blocked facts. If blocked, record concrete cause, switch to next independent safe item.
5. Respond only with actual completed changes, exact tests, verified URLs/SHAs, blockers, and next step. No questions already answered in these files.

## Current highest priority — ACTIVE at 2026-10-25 22:55 KST
**REA-MVP-D2-02: optional Fable report → CSV MVP orchestration**.
- **D2-01 is done**, not READY. Feature `feature/evidence-adapter` SHA `fda96076de33ebf4f4b6118972a5033a3f703ba9`, [Draft PR #4](https://github.com/hibi89/REA_Web/pull/4). CI [CI run 40199741969](https://github.com/hibi89/REA_Web/actions/runs/40199741969) passed **28 pytest with actual Astra contract checkout**; inferred-only review gate and CLI verified.
- **Next target branch: `feature/orchestrator`**. Inspect latest branch and `docs/17_NEXT_TASK.md`; read D1 `feature/csv-local-mvp` and D2 `feature/evidence-adapter` source; avoid overwriting unique branches.
- Implement real optional-report + **customer CSV** → independent local FastAPI/SQLite webapp flow, with CSV-only capability, no website scan required. Never automatically approve semantic mapping or Fable inferred UI behavior.
- Use synthetic data only; run tests/CI, create Draft PR, update main handoff docs. D3 adds three example domains, real browser, Windows and packaging.

## Last verified working result — do not lose
- Standalone CSV→SQLite→FastAPI+HTML/CSS/JS generator exists on `feature/csv-local-mvp` **`5515a7286d63211e32d2c577f93f77d61f37ce08`**; Draft **PR #3** to integration/develop (NOT merged).
- GitHub Actions `https://github.com/hibi89/REA_Web/actions/runs/40198326369`, job `121183903206`: **9 pytest PASSED** (1 warning); actual Chromium E2E PASS on **five synthetic Korean café rows**, filter to two, search to one, click detail, reload, zero JS errors and zero external-origin calls.
- It is a **CSV MVP only**, not yet integrated with Fable/Astra, no Windows, real customer DB/API or sale-ready verification.
- Fable pinned 88/88 source paths in `import/fable51-bbe72c0` @ `7e6f273b359b207fad8f92016226e3058cbcb839`. Astra P4 **103-file PARTIAL** snapshot (41 contract modules) in `import/astra-p4-b3166b6` @ `f044b66e799289a5a353fdb9cbfdb324e683ffa3`. Draft PRs **#1/#2** not merged.

## Non-negotiable intent and constraints
- Owner's chosen repository/product name: **REA_Web**. Keep Fable/Astra upstream independent, combine by adapter rather than blindly merging.
- **3-day MVP-first sprint**, code that creates real user-visible results first; compare to original architecture and fill gaps after. This is an **aggressive target**, NOT a guaranteed 3-day finish or background task.
- **30만원 (300,000 KRW)** narrow Kr몽 product hypothesis: customer provides clean CSV/JSON; up to 2 screens / 3 simple features / no default data collection. Do not offer unlimited production database integration.
- Do not postpone essential no-overwrite, bounds, SQL parameterization, output escaping, consent, localhost-only and no customer secrets. Advanced hardening/Windows/three examples may follow MVP core, but cannot be represented as already completed.
- If user sends **'ㄱ'** in any session, execute next safe READY task immediately. If the exact restart sentence is used, it **already means 'ㄱ'**.
- For full contract, architecture, branch policy, honest verification rules: `docs/SESSION_RESTART_PROTOCOL.md`.

**At any future session, latest actual GitHub HEADs and dispatch docs override this historical snapshot.**

