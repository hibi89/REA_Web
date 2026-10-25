# REA_Web dispatcher — SINGLE ACTIVE READY TASK (2026-10-25 KST)

Trigger: [REA_Web 깃헙 레포지토리 보고 작업이어가셈] or ㄱ means inspect actual GitHub and EXECUTE the next safe task immediately. No extra question, no background promise. Always read latest main HEAD, HANDOFF, STATUS, AGENTS, WORKER_START_HERE and this file before code edits.

## LAST DONE: REA-MVP-D3-01
- qa/cross-platform tested SHA e88c89f3ec12e61e63d2ca1255736fbf674c6e9e, later docs-only head 857a73e1f3e641f851fd4df1212872846528bdb9, [Draft PR #6](https://github.com/hibi89/REA_Web/pull/6) unmerged.
- [CI 40202313506](https://github.com/hibi89/REA_Web/actions/runs/40202313506) SUCCESS: Ubuntu 68/68 pytest + real Chromium for 3 independent local apps (cafe, inventory, trends), zero external calls, JS errors or script dialogs; Windows-latest 68/68 pytest + extracted ZIP launcher/CMD/HTTP PASS; 1 nonblocking TestClient warning each.
- Synthetic Actions artifact rea-d3-synthetic-linux-qa ID 12602316907 includes three screenshots + QA JSON + example ZIP. ZIP contains app.py, SQLite, local static assets, Windows guide/launcher and SHA-256 manifest; no vendor engines or original Fable source.
- **Windows false start:** run 40202205835 failed CMD launcher (py -3 interpreter choice). Fixed to PATH python; actual Windows success 40202313506. Do not repeat old launcher.
- Design comparison: docs/21_MVP_GAP_MATRIX.md; guide docs/22_D3_TEST_GUIDE.md on QA branch. Source imports and original D1/D2 feature branches unchanged; all PR #1–#6 Draft/unmerged.
- NOT_RUN customer/reference site, clean nondeveloper Windows PC, Windows Chromium, advanced security, license redistribution and production.

## ACTIVE READY: REA-MVP-D4-01 — close immediate customer-visible UX gaps
Preferred branch: create feature/mvp-summary-preview from actual latest tested qa/cross-platform **if no existing conflicting branch**, otherwise use and preserve its latest unique commits. No force. Do not modify pinned upstream engines/imports.

1. Verify latest GitHub branch heads and read docs/21_MVP_GAP_MATRIX.md + docs/02_ARCHITECTURE.md + docs/14_FINAL_DELIVERABLES.md + current rea/mvp.py, rea/templates/app.py, JS/HTML and tests. Use minimal changes.
2. Add **read-only dataset schema preview** from owner CSV headers/types as unapproved metadata, NOT semantic DB/API mapping, with explicit unknown/mixed and bounded types. Add simple **category counts** (total and per-category) endpoint and optionally a lightweight summary panel. No arbitrary formula/percentage, no write APIs.
3. Preserve all existing list/search/filter/detail, no overwrites, localhost only, optional Fable review gates and customer CSV-only generation. The owner-selected category counts are summaries of the supplied CSV, not reconstructed original site formulas. Avoid using synthetic engagement fields for business assumptions.
4. Add deterministic unit, negative and real Chromium tests for the new UI/API. Test all 3 datasets where feasible; run GitHub Actions on target SHA. Open Draft PR to integration/develop and record exact PASS/FAIL and unverified components.
5. After one bounded verified unit, update main STATUS/HANDOFF/NEXT_TASK and agent entrypoint, including SHA, CI run IDs and next business-critical pre-sale gates. If there is a blocker, record it and take next safe independent task, no questions already answered.

## After D4
Reconcile 300k offer (2 files/JSON advertised vs one CSV actual; no implicit scope shrink), full vendor and dependency redistribution license review, pre-sale security/recovery/clean Windows nondeveloper test, one authorized real reference/customer dataset only with explicit permission. Commercial sale/hosting remains BLOCKED until applicable gates PASS. Three-day sprint is ambitious target, not completion guarantee.
