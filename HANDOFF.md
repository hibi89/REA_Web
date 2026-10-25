# REA_Web — HANDOFF (2026-10-25 KST)

## 1. Goal, buyer, confirmed requirements and technology
REA_Web integrates Fable 5.1 technical observations, Astra P4 evidence review and an **independent local app generated only from customer-provided CSV**. Python 3.11, SQLite, FastAPI, HTML/CSS/JS; localhost readonly by default. Commercial 300,000 KRW starter is a hypothesis, not an active offering. Plan: MVP first -> compare retained design -> high-value additions -> final security/licensing/reliability before sale. 3-day ambition, no guaranteed timing or background execution.

## 2. Completed work and engineering decisions
D1 generated webapp list/search/filter/detail, D2-01 Fable/Astra inferred-only review, D2-02 combined optional Fable review + CSV app, **D3-01** 3 independent domains (cafe, inventory, trends) with real Chromium smoke, deterministic delivery ZIP/manifest and Windows CMD launcher. All vendor imports remained pinned; original D1/D2 feature sources preserved. Fable clues NEVER become approved DB mapping or observed UI behavior. ZIP contains app only, no vendor engines or raw Fable capture.

## 3. Exact tests and proof
**Tested D3 functional SHA:** e88c89f3ec12e61e63d2ca1255736fbf674c6e9e; final QA documentation head 857a73e1f3e641f851fd4df1212872846528bdb9 (later docs-only commits, no functional code changes). [Actions 40202313506](https://github.com/hibi89/REA_Web/actions/runs/40202313506) SUCCESS: Ubuntu Python 3.11 **68 pytest PASS**, 1 warning, **3 actual Chromium E2E PASS** on local generated apps, search/filter/detail/reload, XSS text remains text, zero outbound calls/JS errors/dialogs. Windows-latest Python 3.11 **68 pytest PASS**, 1 warning; ZIP extract -> genuine launch_windows.cmd -> HTTP health/items (4 rows) PASS. Packaging deterministic/checksum/negative tests also PASS. GitHub Actions artifact rea-d3-synthetic-linux-qa ID 12602316907 includes 3 PNG screens, qa_report.json and sample ZIP.
Commands: python -m pytest -q tests/test_mvp.py tests/test_adapter.py tests/test_orchestrator.py tests/test_d3.py ; python scripts/d3_browser_acceptance.py --report-dir ./out/qa ; python -m rea.delivery pack --csv samples/qa_cafe.csv --out ./out/sample.zip ; python -m rea.delivery verify --zip ./out/sample.zip. Optional Fable mode requires pinned Astra on PYTHONPATH.
Separate D1 40198326369 (9 PASS), D2-01 40199741969 (28 PASS), D2-02 40200704855 (55 PASS).
**NOT_RUN:** clean customer Windows hardware/manual onboarding; Windows real Chromium UI; customer or authorized real reference acceptance; production deployment and penetration/licensing review.

## 4. Completed/active/waiting/blocked checkpoint
D1, D2-01, D2-02, D3-01 DONE on feature branches; D4-01 READY. Main/docs dispatch only. No current technical blocker for synthetic D4. Commercial delivery BLOCKED by full licenses, mapping consent, customer/site rights, clean Windows pilot, support/limited price contract and full security.

## 5. Error cause, attempts, forbidden repeats, alternatives
Initial D3 Windows native launcher test at Actions 40202205835 FAILED while Python 68 tests and Linux Chromium passed. Command launcher used py -3 and process exited code 0 without running expected server. Changed ZIP launcher to use Python interpreter already on PATH; retry at 40202313506 PASS on Windows. Do not repeat py -3 launcher without explicit interpreter matching. Warning from TestClient and Node action deprecations remains nonblocking. No force push, no fake test PASS, no merging unreviewed vendor packages.

## 6. Repository, branches, SHAs, paths
GitHub hibi89/REA_Web (public); main documentation prior to this update 2e7babbd8782472d0c7a04f27573bc74c7fc31c0 (refetch remote), QA branch qa/cross-platform current docs head 857a73e1f3e641f851fd4df1212872846528bdb9; tested source commit e88c89f3ec12e61e63d2ca1255736fbf674c6e9e, [Draft PR #6](https://github.com/hibi89/REA_Web/pull/6) to integration/develop, unmerged. Prior Day1 5515a728..., D2-01 fda96076..., D2-02 46060b46.... New code: rea/delivery.py, tests/test_d3.py, scripts/d3_browser_acceptance.py, scripts/windows_native_smoke.py, samples/qa_*.csv, .github/workflows/rea-d3.yml. Design gap docs/21_MVP_GAP_MATRIX.md; guide docs/22_D3_TEST_GUIDE.md.

## 7. Production/Vercel URL, run command, environments
No Vercel setup or Production URL; current product local-only. Generated app: python -m uvicorn app:app --host 127.0.0.1 --port 8000 from extracted app folder; requirements in app/requirements.txt. ZIP contains launch_windows.cmd, run using python interpreter on PATH after python -m pip install -r app/requirements.txt. CI verified Linux Chromium and Windows native HTTP only, not internet hosting. No paid API, customer secret or permission changes.

## 8. Original/backup/access/never edit
Immutable Fable pinned import branch import/fable51-bbe72c0 at 7e6f273b..., upstream hibi89/fable5.1_web_catcher bbe72c0...; Astra PARTIAL import import/astra-p4-b3166b6 at f044b66..., upstream hibi89/astra_web_catcher b3166b6.... Preserve source repos and previous feature branch SHAs as recovery points. No real customer data in public Git; only synthetic fixtures and redacted Fable example. Credentials, .env, customer ZIPs and secrets must never be uploaded. Actual production rights require owner approval.

## 9. Next priority, procedure, acceptance, approval
**REA-MVP-D4-01 READY:** implement CSV schema/field preview and read-only category summary counts as highest-value low-risk gap, retaining existing CSV-only path and report gate, with unit/API/real browser tests, Draft PR and exact CI logs. Validate against retained target design; do not add arbitrary Fable-based formulas. Next pre-sale final sequence: input contract vs 2-file/JSON offer scope; third-party/dependency licenses; security/recovery; clean Windows nondeveloper; customer rights/acceptance and approved publishing. External data, production deployment, paid calls, security/rights changes or irreversible merges require owner approval.

## 10. KST update time, evidence scope and documentation baseline
Updated 2026-10-25 KST after verifying actual D3 run https://github.com/hibi89/REA_Web/actions/runs/40202313506, SHA e88c89f3ec12e61e63d2ca1255736fbf674c6e9e, QA documentation head 857a73e1f3e641f851fd4df1212872846528bdb9. This HANDOFF file is being committed after main 2e7babbd...; the resulting main commit SHA is canonical. Verified synthetic Linux/Windows Actions only; no claims for real customer/site, clean Windows consumer, sale readiness or production.
