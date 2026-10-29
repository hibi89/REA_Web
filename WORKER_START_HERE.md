# REA_Web — CURRENT RESUME SNAPSHOT (2026-10-30)

## 최신 확인 상태 (2026-10-30; 정확한 HEAD)

- D27 제품 코드와 D31 감사 워크플로의 검증 기준은 `970bbde8c853f4ed1382c038091bb2ee48abea9f`입니다. 이후 `ebb1f22`는 상태 문서만 갱신했으며 제품 코드는 바뀌지 않았습니다. PR #30은 OPEN/DRAFT/UNMERGED입니다. 강제 푸시나 병합은 하지 않았습니다.
- 정확한 HEAD GitHub Actions 28/28 SUCCESS입니다. D27 전체 회귀 [#40967860714](https://github.com/hibi89/REA_Web/actions/runs/40967860714)의 Linux D1–D27/Chromium과 Windows D1–D27/native-package job이 모두 성공했습니다. D31 생성 런타임 보안 감사도 Ubuntu/Windows PASS입니다. 모두 합성 데이터 자동 검증이며 사람의 고객 검수는 아닙니다.
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

