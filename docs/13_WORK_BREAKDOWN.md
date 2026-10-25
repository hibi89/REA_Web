# REA_Web — Work breakdown (live verified checkpoint 2026-10-25 KST)

| ID | Status | Branch | Deliverable / evidence |
| --- | --- | --- | --- |
| REA-P0-01 | DONE | main | Repo bootstrap & canonical docs |
| REA-P0-02 | IMPORTED_REVIEW_PENDING | import/fable51-bbe72c0 | 88 paths pinned; redistribution review pending |
| REA-P0-03 | PARTIAL_IMPORT_REVIEW_PENDING | import/astra-p4-b3166b6 | 103 selected paths, 41 contracts; NOT full vendor |
| REA-P0-04 | DEFERRED_BEFORE_SALE | integration/develop | Vendor license/dependency/provenance and merge review |
| REA-P1-01 | DONE_FEATURE | feature/evidence-adapter | Fable->Astra schema review adapter; 28 tests PASS |
| REA-P1-02 | DONE_FEATURE | feature/evidence-adapter | Strict inferred/observed and unapproved mapping guards |
| REA-P2-01 | PARTIAL_DONE_FEATURE | feature/csv-local-mvp | UTF-8 CSV cap/validator works; full owner JSON/mapping UX pending |
| REA-P2-02 | DONE_FEATURE | feature/csv-local-mvp | Fresh isolated read-only SQLite generator, no source overwrite |
| REA-P3-01 | DONE_FEATURE | feature/csv-local-mvp | List/search/filter/detail actual browser PASS |
| REA-P4-01 | DONE_FEATURE_MVP | feature/orchestrator | CSV-only + optional Fable review + independent app CLI, 55 pytest+browser PASS |
| REA-P5-01 | DONE_FEATURE_VERIFIED | qa/cross-platform | Three domains, Chromium PASS, Windows native CMD/API PASS, ZIP SHA256 artifact, design gap; CI 40202313506 68 pytest on Linux/Windows |
| REA-P5-02 | READY | feature/mvp-summary-preview | CSV schema preview / category count summary: no guessed formulas or Fable-to-DB bindings |
| REA-P6-01 | BACKLOG_BEFORE_SALE | release/v0.1 | Commercial scope, licenses, full security/recovery and clean Windows customer pilot |

**Verified combined feature SHA:** `46060b4665560922d0c9cf82b9e5c08971eb9427` ([CI 40200704855](https://github.com/hibi89/REA_Web/actions/runs/40200704855); PR #5 Draft, unmerged).
Separate D1 `5515a728...` / D2-01 `fda96076...`, both Draft/unmerged. Latest dispatch is `docs/17_NEXT_TASK.md`; historic implementation order has been superseded by MVP-first.

D3 actual QA proof: [CI 40202313506](https://github.com/hibi89/REA_Web/actions/runs/40202313506), verified test SHA e88c89f3ec12e61e63d2ca1255736fbf674c6e9e, draft PR #6, source unmerged. Artifacts include synthetic example ZIP and browser screenshots.
