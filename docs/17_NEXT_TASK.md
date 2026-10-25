# REA_Web dispatcher — SINGLE ACTIVE READY TASK (2026-10-25 KST)

Exact user trigger [REA_Web 깃헙 레포지토리 보고 작업이어가셈] or ㄱ authorizes immediate implementation of next bounded offline synthetic unit. Read current main and assigned branch HEAD, HANDOFF, STATUS, WORKER_START_HERE, AGENTS, source/tests. Do not ask for already known context or background execution.

## Last DONE — REA-MVP-D4-01
- Implemented in feature/mvp-summary-preview, tested source d8e26ed7d60ad86f64e35aefb3825655d6e19d25 and later documentation-only head e4e9c7954ba1369636bcc2107478a5d2dae2db7e; [Draft PR #7](https://github.com/hibi89/REA_Web/pull/7), unmerged.
- [CI 40203444938](https://github.com/hibi89/REA_Web/actions/runs/40203444938) SUCCESS Ubuntu 77 pytest, Windows-latest 77 pytest, true Chromium for 3 synthetic domains with schema/category summary & existing list/search/filter/detail/reload PASS. Windows extracted .cmd and localhost HTTP PASS. One warning per OS; no functional failed/skipped. No customer or live URL.
- Readonly schema field preview has review_status UNAPPROVED, no cell samples, no approved bindings. /api/summary counts only customer CSV rows. Original Fable review gate intact. Gap matrix docs/21_MVP_GAP_MATRIX.md updated on D4 feature.
- Original source/vendor import branches untouched, PRs #1–#7 remain draft.

## ACTIVE READY — REA-MVP-D5-01: JSON intake + documented 2-file product scope reconciliation
Target: new conflict-free feature branch derived from verified D4 (refetch actual head), do not force or edit upstream vendor/import refs.
1. Compare docs/07_KMONG_OFFER.md, docs/14_FINAL_DELIVERABLES.md, original architecture intake requirements and current rea/mvp.py / rea/orchestrator.py / rea/delivery.py. Confirm exact current one-CSV-only constraints.
2. Implement a **limited JSON array-of-objects intake** where explicit id/title/category keys are required; strict max bytes, rows, columns, string-only values or explicit safe conversion with clear rejection for ambiguous mixed/scalar/nested/sensitive formats. Keep existing CSV input exactly usable. No external fetches or automatic Fable field mapping.
3. Do NOT blindly merge two independent customer files. Document precisely which multi-file pattern is supported (if any) versus DRAFT advertised 2-file scope, label capability gap honestly. Reconcile contract by either safe, explicit supported two-file schema workflow in a separately tested unit or an owner-reviewed scope revision before sale. Never silently remove promised features.
4. Add tests for JSON valid/invalid, duplicate IDs, caps/encoding, original file no mutation, ZIP contents, approvals, real Chromium regression. Run GitHub Actions actual tests both OS, Draft PR to integration/develop, record SHA/PASS/FAIL/NOT_RUN.
5. Update main STATUS.md, HANDOFF.md, this dispatcher and README with exact evidence and next task (licence/provenance audit and final pre-sale security/recovery before customer order).

## After D5
Legal/license/dependency source rights audit, secure input/recovery tests, nondeveloper clean Windows real PC, authorized customer/reference-site consent and fixed 300k scope acceptance. No full original site clone, live database, public deploy or commercial launch until those gates actually pass.
