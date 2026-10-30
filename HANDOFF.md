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

# HANDOFF — REA_Web / current handoff (2026-10-30)

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
## Follow-up handoff state (2026-10-30)

- Feature branch exact HEAD: `64b28c986618c68472649474c6604c2b1fce7372`; branch compare shows 5 ahead / 0 behind `db6711e`. PR #30 remains OPEN/DRAFT/UNMERGED.
- Current CI evidence from connector: 27 returned workflows, all 27 SUCCESS. One expected workflow was not returned by the first-page-only API, so do not claim 28/28.
- Code at 64b bounds FastAPI, Starlette, and Uvicorn to supported lower/upper ranges. Local isolated customer guidance: 18 PASS, compileall PASS. Full local regression is incomplete due Windows sandbox filesystem `WinError 5`; targeted D27/D26 tests also encounter denied `os.link` at package publication.
- Cumulative patch is validated against `db6711e`; original ZIP snapshot stays untouched. Customer bundle and machine hashes live in `bundle_update_notes/`.
- Human/customer acceptance NOT_RUN; commercial redistribution rights NOT_GRANTED; seller listing/terms NOT_APPROVED. Do not promote CI or synthetic cases to those gates.
- A helper branch created via connector has an incomplete one-file tree and is not a usable source branch. The feature branch was not moved. Connector provides no safe branch delete operation; record it and do not build on it.

## Next independent work

1. Re-run the current complete D27/D1-D27 regression in an unrestricted, ordinary Windows environment so atomic rename/hard-link tests can run; mark this sandbox run incomplete.
2. Rebuild synthetic delivery ZIPs from exact 64b source, then execute extracted CMD, browser search/filter/detail and append flows; older `f6e34f6` receipts are not current-head proof.
3. Continue exact dependency vulnerability and license notice checks using source/release artifacts; legal source and vendor rights remain NOT_GRANTED until documented clearance.
4. Keep the human Windows acceptance protocol unfilled until an independent nondeveloper performs it.

## Verified remote head and product status

- Current feature branch HEAD: `578442b2bd22bb64a004e77bbd091a17930f614a`. Exact-head CI completed **28/28 SUCCESS**, including D27 Windows/Linux full regression and D6 supply-chain/security.
- D27 runs: PR [#40954859581](https://github.com/hibi89/REA_Web/actions/runs/40954859581), push [#40954852936](https://github.com/hibi89/REA_Web/actions/runs/40954852936). D6 run: [#40954859774](https://github.com/hibi89/REA_Web/actions/runs/40954859774).
- PR [#30](https://github.com/hibi89/REA_Web/pull/30) remains **OPEN, DRAFT, UNMERGED**. No force push or merge was performed.
- Generated runtime requirement includes Starlette `>=1.3.1,<2`; the customer preflight rejects lower versions and offers Korean recovery instructions for both `python` and `py -3`.
- Supported: customer-authorized CSV or flat JSON, preview/explicit mapping approval, same-schema two-file ROW APPEND with both approvals, local read-only FastAPI/SQLite app (list/search/category filter/detail), Windows ZIP. Different-schema JOIN, scraping, hosting, accounts, payments, sync, and general CRUD are excluded.
- Local: focused tests **13 PASS**, Python compile, dependency floor and `pip check` PASS; five synthetic ZIPs passed Windows preflight. Local interactive customer acceptance: **NOT_RUN**.
- Human acceptance **NOT_RUN**; source/dependency commercial redistribution rights **NOT_GRANTED**; customer-data/privacy operating agreement **NOT_APPROVED**. Sale is not approved. Current estimates: development **95%**, sale preparation **77%**.

## Next independent unit

Prepare a reproducible runtime dependency/license inventory from the actual generated-app dependency graph and the tested Windows environment. Record package versions, dependency edges, license metadata/source hashes, missing notices, and the limits of that evidence. Keep commercial clearance NOT_GRANTED until rights-holder/legal review. Then continue other independent package/privacy checks while any new docs-only CI runs.

The source snapshot and validation evidence remain preserved locally. Do not infer customer acceptance or rights from CI. Do not merge PR #30 without explicit approval.

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

