# REA_Web — SESSION RESTART PROTOCOL / CANONICAL CONTEXT
Updated 2026-10-25 KST. Stable entrypoint for a fresh ChatGPT session.

## User instruction and interpretation
Exact trigger: **[REA_Web 깃헙 레포지토리 보고 작업이어가셈]**.
This is sufficient authority to load repository documents, inspect latest source and begin the next safe bounded development task without supplementary comments or clarifications. It is **not** authority to access production customer DBs, buy external services, publish a site, send customer data, or modify upstream repositories. The assistant must act now in the new turn, not promise background or future autonomous work.

## Project charter and buyer
- **REA_Web** = website analysis & independent application reconstruction automation: Fable 5.1 performs static/Chromium observations, technology and API-shape inference; Astra P4 supplies validated observations, functional specs, mapping/approval and synthetic independent webapp components.
- Realistic first product is **customer CSV -> local working web app**, with optional reference website observation later. This is not a universal website clone or private backend/source reverse engineering.
- A customer's clean CSV/JSON is supplied by them, not collected by the developer as a default service. Local read-only new SQLite, FastAPI, Korean-friendly screens, list/search/category filter/detail, optional simple summary. Original reference and customer's own data have independent provenance/rights.
- Business objective: initial fixed-scope **300,000 KRW** service. Draft scope: max 2 files, 10 MB and 10k rows total, max 20 columns per file, up to 2 screens / 3 basic functions, 1 minor correction batch. Actual first MVP currently supports single UTF-8 CSV and *four read-only behaviors*, so contract scope must reflect actual capability at release. No live DB, scraping, complex accounts, payments, ERP, public hosting, or unlimited corrections included. Product is NOT yet open for sales.

## Current development philosophy
**MVP -> compare against original design -> fill valuable gaps -> verify robustness/security before commercial release.**
- Timebox target = aggressive **3-day** sprint, not a factual completion claim and not a guarantee.
- Day1 deliver a real customer-like CSV→app vertical slice (DONE with evidence below).
- Day2 Fable→Astra evidence adapter; integration through explicit versioned JSON boundary, not combined monolithic Python env or full-source merge.
- Day3 3 synthetic scenarios, Chromium browser E2E, Windows run guide, packaging, compare to `docs/02_ARCHITECTURE.md` and `docs/14_FINAL_DELIVERABLES.md`, regressions, acceptance.
- Advanced pen testing/enterprise auth/production deployment deferred, but **minimum safety NEVER deferred**: sanitize inputs, safe local destination, no destructive writes, SQL queries parameterized, escape user text in DOM, read-only local backend default, consent/source-rights.

## Reliable state / code locations
- REA_Web main at start of this doc's authoring: `71ed9a4656ef7642a32c335da9c6d664916cabee` (historical; fetch current head on every new session).
- Day1 actual code `feature/csv-local-mvp` @ `5515a7286d63211e32d2c577f93f77d61f37ce08`:
  `rea/mvp.py` (CSV generator), `rea/templates/app.py` (FastAPI readonly SQLite), `rea/templates/static/` (HTML/CSS/JS), `samples/products.csv`, `tests/test_mvp.py`, `scripts/mvp_browser_smoke.py`, `.github/workflows/rea-mvp.yml`.
  CLI from that branch: `python -m rea.mvp --csv samples/products.csv --out ./out/demo --name "내 상품 관리"`. Then `cd out/demo` + `python -m uvicorn app:app --host 127.0.0.1 --port 8000`.
- Source import Fable: `import/fable51-bbe72c0` @ `7e6f273b359b207fad8f92016226e3058cbcb839`, 88/88 redacted review ZIP source files under `engines/fable51/` + 8 upstream Git SHA manifests. Pinned upstream `hibi89/fable5.1_web_catcher` @ `bbe72c0acd3a3e355062d6bd0d866af33e5274b0`. No need to ask for ZIP again to proceed with imported code.
- Source import Astra: `import/astra-p4-b3166b6` @ `f044b66e799289a5a353fdb9cbfdb324e683ffa3`, 103 selected files, 41 `astra_contracts` modules under `engines/astra_p4/`; **PARTIAL**, not complete upstream or later codex changes. Pinned upstream `hibi89/astra_web_catcher` feature source @ `b3166b67604381a9d2afd41667b65f9a9b103b37`.
- Other branches: `integration/develop` staging, `feature/evidence-adapter` Day2, `feature/orchestrator` Day3, `qa/cross-platform`; `qa/vendor-fable`, `qa/vendor-astra` for manifest integrity. Historical 940 pass/2 skip on upstream Astra; **not** REA_Web acceptance.
- PRs: `#1` source Fable 88, `#2` Astra P4 PARTIAL, `#3` Day1 CSV MVP, all Draft/unmerged. Source PRs are review-only; must not be silently merged. Avoid overwriting unique feature commits or forcing refs.

## Verified execution proof
- GitHub Actions run https://github.com/hibi89/REA_Web/actions/runs/40198326369, source SHA `5515a7286d63211e32d2c577f93f77d61f37ce08`, job `121183903206`, Ubuntu Python 3.11; 9 pytest PASS, 1 warning, CLI created 5-row sample app and compileall PASS.
- **Real Chromium loopback browser** opened generated app and confirmed 5 cards, category filter 2 results, search 1, detail title/price, reload to 5, no JS exception or external request. No Windows real browser/production site/customer dataset tested. Not Fable→Astra integrated. Actions summary must not be extrapolated to final product.
- Before Day1 Chromium, initial run 40197993285 had 9 pytest PASS + CLI generated app/compileall. Use latest run for current proof.

## Latest done checkpoint and next READY D4-01
D3-01 **DONE** on qa/cross-platform: functional tested SHA `e88c89f3ec12e61e63d2ca1255736fbf674c6e9e` (latest doc-only QA head `857a73e1f3e641f851fd4df1212872846528bdb9`), [CI 40202313506](https://github.com/hibi89/REA_Web/actions/runs/40202313506) SUCCESS. Ubuntu Python 3.11 68 pytest + three true Chromium browser domains; Windows-latest Python 3.11 68 pytest + extracted CMD launcher and real localhost HTTP PASS. Deterministic synthetic ZIP and SHA manifest; screenshot/JSON/ZIP artifact ID 12602316907. The earliest Windows CMD failure used mismatched py -3 interpreter; corrected to PATH python. This is not a clean user PC or Windows browser verification and vendor license rights not approved.

**REA-MVP-D4-01 READY:** source QA feature branch is unmerged. Create a new nonconflicting feature branch from verified qa/cross-platform, minimal schema/header preview and readonly category count summary grounded only in supplied CSV. Retain Fable as unapproved review and no arbitrary original website formula. Run actual tests, browser if possible, Draft PR and update main HANDOFF/STATUS/NEXT_TASK. Then license/security/clean Windows/owner rights/offer acceptance before sale. See docs/17_NEXT_TASK.md.

## Handoff and workflow after each bounded unit
1. Read latest remote main + docs + target branch HEAD and changes; source of truth is git, not chat narrative.
2. Work only on assigned feature. Small MVP-first increments; two failed identical approaches ⇒ change method, document blocker.
3. Run real tests where possible, never invent tests, verify GitHub Actions statuses instead of claiming from workflow definitions.
4. Preserve original upstream and immutable import branches; no customer credentials, non-consensual scraping, unapproved DB schema changes or public deploy.
5. Update on main: `STATUS.md`, `HANDOFF.md`, `docs/17_NEXT_TASK.md` with task ID, exact test evidence, commit SHA, what remains; update feature branch docs as helpful.
6. In final response report actual commit/PR, test counts and NEXT TASK. User's next 'ㄱ' or exact trigger starts the next job.

## Deliverables target
Restricted independent local FastAPI+SQLite+HTML/JS source, CSV schema and mapping report, sample fixture, automated acceptance tests, Windows launch instructions, export manifest and ZIP, limitations. See `docs/14_FINAL_DELIVERABLES.md` and `docs/07_KMONG_OFFER.md`. No unsupported "arbitrary URL 1:1 copy" claims.

## 2026-10-25 D4 update — current dispatch overrides historical D3 reference
D4-01 verified on feature/mvp-summary-preview code SHA d8e26ed7d60ad86f64e35aefb3825655d6e19d25, docs head e4e9c7954ba1369636bcc2107478a5d2dae2db7e, Draft PR #7, [CI 40203444938](https://github.com/hibi89/REA_Web/actions/runs/40203444938) Linux+Windows each 77/77 tests plus three real Chromium synthetic cases and native Windows CMD/HTTP PASS. Next READY is **D5-01 limited JSON intake and 2-file offer scope reconciliation**; see docs/17_NEXT_TASK.md, this overrides previous D4-ready historical paragraphs. No customer/site rights or license and security approval implied.
