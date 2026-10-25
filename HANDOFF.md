# REA_Web HANDOFF — 2026-10-25 KST

## Goal and product scope
REA_Web builds a restricted independent readonly local FastAPI/SQLite/HTML+JS app from customer-owned data. Fable 5.1 supplies optional separately validated technical observations; Astra P4 contracts keep inferred evidence unapproved. No universal website cloning, private backend retrieval or automatic data mapping. Starter 300,000 KRW scope remains a draft, not an offer. Development policy is MVP -> compare original design -> fill gaps -> final robust security/licenses/recovery before sale. 3-day timeline stretch goal only.

## Completed work and rationale
- D1 single UTF-8 CSV -> SQLite + list/search/category filter/detail.
- D2-01 Fable v1.0 -> Astra evidence/spec review-only adapter (never assumed observed behavior).
- D2-02 optional Fable report + CSV-only app generator separated by explicit source boundaries. Fable source never used to create app data.
- D3-01 three independent synthetic cases, reproducible ZIP+SHA256 manifest, tested Windows CMD launcher, Linux Chromium snapshots, initial architecture gap matrix.
- **D4-01** schema preview and category counts: generated schema_preview.json (only CSV headers, lexical-type hints, missing/present counts; no raw sample values), /api/schema and /api/summary readonly endpoints, local UI summary and expandable preview. Unapproved source meaning, no automatic owner data binding. Source code based on verified QA feature head, no Fable/Astra vendor source modifications.

## Real test evidence
Functional D4 code commit: d8e26ed7d60ad86f64e35aefb3825655d6e19d25; feature docs-only latest head: e4e9c7954ba1369636bcc2107478a5d2dae2db7e. Actions [run 40203444938](https://github.com/hibi89/REA_Web/actions/runs/40203444938) SUCCESS Ubuntu Python 3.11 **77 pytest PASS** and real Chromium cafe/inventory/trends UI PASS; Windows-latest Python 3.11 **77 pytest PASS** and extracted ZIP Windows .cmd -> loopback HTTP PASS. One nonblocking TestClient warning per OS. No JS errors/outbound requests/dialogs in synthetic Chromium.
Earlier CI: D1 40198326369 (9), D2-01 40199741969 (28), D2-02 40200704855 (55), D3-01 40202313506 (68 each on Linux/Windows).
Test command with pinned Astra on PYTHONPATH: python -m pytest -q tests/test_mvp.py tests/test_adapter.py tests/test_orchestrator.py tests/test_d3.py tests/test_d4.py. Browser: python scripts/d3_browser_acceptance.py --report-dir /tmp/rea-d4-test. Delivery: python -m rea.delivery pack --csv samples/qa_cafe.csv --out /tmp/demo.zip; verify with python -m rea.delivery verify --zip /tmp/demo.zip.

## Status and issue history
D4 actual CI green; no open functional issue from this task. D3 first Windows launcher at 40202205835 failed because py -3 exited too early; switched to installed PATH python and verified PASS at 40202313506. Never restore old launcher. Known warnings from FastAPI/Starlette TestClient and GitHub checkout node deprecation nonblocking. Do not mistake synthetic tests for real customer authorization.
Completed D1–D4 on feature branches, all Draft/unmerged. D5-01 READY; commercial release blocked by unsupported JSON/two-file draft offer, third-party distribution licenses, clean Windows end-user pilot, data rights, full security and support/acceptance.

## Repository and exact refs
Repo hibi89/REA_Web public; main documentation BEFORE this update 401b6ad58ce65fb3c56ab2f9f669ea4eccd7e977 (always refetch); active D4 feature/mvp-summary-preview e4e9c7954ba1369636bcc2107478a5d2dae2db7e [Draft PR #7](https://github.com/hibi89/REA_Web/pull/7) based on qa/cross-platform 857a73e1f3e641f851fd4df1212872846528bdb9. Other PR #1–#6 Draft/unmerged.
Files edited in D4: rea/mvp.py, rea/templates/app.py, rea/templates/static/index.html, app.js, style.css, scripts/d3_browser_acceptance.py, tests/test_d4.py, docs/23_SCHEMA_SUMMARY.md, docs/21_MVP_GAP_MATRIX.md and .github/workflows/rea-d4.yml.
Immutable imported vendors: Fable 7e6f273b359b207fad8f92016226e3058cbcb839 (88 sources), Astra PARTIAL f044b66e799289a5a353fdb9cbfdb324e683ffa3 (103 selected files). Original upstream repositories must not change. GitHub feature branch and CI artifacts are backups/restore points; no real customer or secrets in Git.

## Run/deployment/access
No Vercel configured and no production URL. Local-only: python -m rea.orchestrator --csv samples/qa_cafe.csv --out ./out/demo; cd out/demo; python -m pip install -r requirements.txt; python -m uvicorn app:app --host 127.0.0.1 --port 8000. Optional sanitized Fable JSON review requires pinned Astra contract modules; never merge or distribute source blindly. No live APIs, paid accounts or owner credentials.

## Next priority
REA-MVP-D5-01: reconcile the fixed-price advertised 'up to 2 CSV/JSON' intake with actual one-CSV implementation. Prefer bounded JSON array-of-objects input converted by the same strict fields/rows validator and no raw data in metadata, while leaving ambiguous two-file joining blocked until explicit owner mapping/scope. Tests (positive/negative/browser) and CI with exact SHAs, Draft PR, update main STATUS/HANDOFF/NEXT_TASK. Then licence/dependency audit and pre-sale security, clean Windows/manual acceptance, actual customer rights before publishing. No extra owner question for offline synthetic unit.

## Verification boundary
Updated 2026-10-25 KST based on D4 tested commit d8e26ed7d60ad86f64e35aefb3825655d6e19d25 and CI 40203444938. Windows Chromium/manual clean device, actual customer/web reference rights, distribution licenses, real data handling and production hosting are NOT_RUN/NOT_DONE. This handoff is maintained synchronously; no autonomous work between user turns.
