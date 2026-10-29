# HANDOFF — REA_Web / current handoff (2026-10-30)

## Verified remote head and product status

- 기능 및 D27 CI 검증 기준 커밋은 `2dfbb90f514f94cb2f3bbe1a8ec4e4dc1a9376c6`이며, unavailable Python discovery guidance를 수정했습니다. 후속 문서 커밋은 해당 검증 결과를 반영합니다.
- Draft PR [#30](https://github.com/hibi89/REA_Web/pull/30) is **OPEN, UNMERGED**.
- Code commit D27 run [#40927550941](https://github.com/hibi89/REA_Web/actions/runs/40927550941) and D8 run [#40927551084](https://github.com/hibi89/REA_Web/actions/runs/40927551084) both completed **SUCCESS** on Linux and Windows. Exact-head D27 run [#40930084158](https://github.com/hibi89/REA_Web/actions/runs/40930084158) and D3 run [#40930083982](https://github.com/hibi89/REA_Web/actions/runs/40930083982) both completed SUCCESS on Linux and Windows.
- Local Windows focused tests: **12 passed**, plus CP949 inspect/wizard **2 passed**. Full regression: 407 passed, 22 skipped, 6 symlink-dependent tests deselected due host WinError 1314. Native synthetic ZIP smoke: actual Windows `cmd.exe`, loopback `/health`, four-row API **PASS**; same-folder stop/restart and copied-backup relaunch preserved four-row search/detail **PASS**. Recovery/customer-guidance tests: 23 passed, 2 symlink cases deselected. D3 run [#40930083982](https://github.com/hibi89/REA_Web/actions/runs/40930083982) completed SUCCESS on Windows native and Linux Chromium jobs. Local Chromium synthetic acceptance: 7/7 PASS, zero JS errors/external calls; the optional Fable/Astra case is BLOCKED locally because contracts are absent. Successful real `py.exe`/installed-runtime selection remains **NOT_RUN** on this workstation. Korean-named CSV/ZIP/extraction path and Korean search/title on actual Windows CMD also PASS with synthetic data.
- Human/customer acceptance remains **NOT_RUN**; source/dependency commercial redistribution clearance remains **NOT_GRANTED**. This is not a commercial release approval.

## Product boundaries

Supported: customer-authorized CSV or flat JSON, preview and explicit mapping approval, same-schema two-file ROW APPEND with both approvals, generated local read-only FastAPI/SQLite app with list/search/category filter/detail, and delivery ZIP. Different-schema SQL JOIN, scraping, hosting, accounts, payment, live sync and general CRUD are out of scope.

The source snapshot and validation evidence remain preserved locally. Continue with synthetic/local QA when independent; do not infer customer acceptance or rights from CI. Do not merge PR #30 without explicit review/approval.

---

## Historical handoff below (2026-10-25)

## Latest D2 checkpoint (2026-10-25 22:55 KST)
**REA-MVP-D2-01 DONE on feature only**. Feature SHA `fda96076de33ebf4f4b6118972a5033a3f703ba9`; Draft PR [#4](https://github.com/hibi89/REA_Web/pull/4), unmerged. Real GitHub Actions [CI run 40199741969](https://github.com/hibi89/REA_Web/actions/runs/40199741969) SUCCESS: **28/28 pytest**, pinned Astra validation and CLI approval-block check PASS on Ubuntu Python 3.11. PR CI run 40199766677 SUCCESS. `rea/adapter/fable_to_astra.py` adds read-only Fable schema v1.0 → review-only Astra candidate mapping, synthetic demo and tests; do **not** state functional UI, real backend, API ownership or chart lineage as observed. Windows, real customer data, cross-branch E2E, full vendor license audit, production service all NOT_RUN. No Vercel deployment for this unit (not applicable).

## Instructions for the next assistant
When owner writes **[REA_Web 깃헙 레포지토리 보고 작업이어가셈]**, inspect real GitHub and **perform the next READY development work immediately** without asking for context or another 'ㄱ'. Read `WORKER_START_HERE.md`, `STATUS.md`, `docs/17_NEXT_TASK.md`, `docs/SESSION_RESTART_PROTOCOL.md`; these are the canonical handoff. Future new chat will not contain our current code discussion, so this repository is the source of truth.

## Product and commercial intent
REA_Web is the **Fable 5.1 website technical/evidence analyzer + Astra Web Catcher functional-spec/independent web app engine**. Current customer-value-first MVP = take **customer-provided** clean CSV, generate usable standalone local app; reference URL optional. Avoid OHORA-like indefinite data collection / third-party API quota / unknown production DB complexity. First commercial price hypothesis 300,000 KRW fixed scope (2 screens, 3 simple features), not a 990k complex live DB job. Sale only after acceptance.

## Current technical status, with exact SHAs
- main documentation baseline before this handoff update: `71ed9a4656ef7642a32c335da9c6d664916cabee` (always refetch remote current SHA).
- Day1 generated local app: `feature/csv-local-mvp` @ `5515a7286d63211e32d2c577f93f77d61f37ce08`. Code `rea/mvp.py`, `rea/templates/app.py`, static HTML/CSS/JS, tests `tests/test_mvp.py`, actual Playwright browser `scripts/mvp_browser_smoke.py`. Draft PR #3, unmerged.
- CI run `40198326369`, job `121183903206`: **9 pytest PASS** + synthetic CSV app generation + compileall + real Chromium browser PASS; search, category, detail, reload; zero unexpected external request or JS error. No Windows/browser proof on Windows.
- Fable 88-source import: `import/fable51-bbe72c0` @ `7e6f273b359b207fad8f92016226e3058cbcb839`, pinned upstream `bbe72c0acd3a3e355062d6bd0d866af33e5274b0`, Draft PR #1.
- Astra P4 103-file bounded **partial** import (41 core astra_contracts modules): `import/astra-p4-b3166b6` @ `f044b66e799289a5a353fdb9cbfdb324e683ffa3`, pinned upstream `b3166b67604381a9d2afd41667b65f9a9b103b37`, Draft PR #2.
- Branches: integration/develop, feature/evidence-adapter (D2 next), feature/csv-local-mvp (D1), feature/orchestrator, qa/cross-platform, qa/vendor-fable, qa/vendor-astra; don't force-update feature work or mutate upstream imports.

## Single task to execute next
**REA-MVP-D2-02** `READY`, start automatically on exact trigger or `ㄱ`. Prefer `feature/orchestrator` after checking latest branch HEAD and the previous two feature branches. Use Fable report as **optional** analysis input to existing CSV→local app flow; leave website URL optional, require customer-provided CSV, retain `REVIEW_REQUIRED` and no automatic semantic mapping. Implement/test true synthetic demo, create Draft PR, and update main docs with exact proof. Only one unit per turn; next D3 three-example/browser/Windows/packaging/design-gap checks.

Do **not** repeat D2-01. Earlier section was historical. Source import branches remain pinned, partial Astra subset unchanged.

## Way of working
MVP-first target is 3 days (not a guarantee). Prioritize working result rather than huge theoretical scaffolding. Keep minimum non-deferable no overwrite/bounded CSV/SQL/DOM/localhost/authorization. Defer deeper security hardening until after functional proof, but not past customer delivery. Keep statuses PASS/NOT_RUN/BLOCKED accurate and always record commit SHA and work done in main STATUS/HANDOFF/NEXT_TASK.

No user actions are required for current D2 synthetic implementation; don't ask the owner for new data, tools, original ZIP, architecture confirmation or a different prompt. Only request explicit approval for production DB, external deployment or risky irreversible actions.

