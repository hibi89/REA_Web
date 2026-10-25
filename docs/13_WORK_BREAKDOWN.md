# REA_Web — Work breakdown (live verified checkpoint 2026-10-25 KST)

| ID | Status | Branch | Deliverable / evidence |
| --- | --- | --- | --- |
| REA-P0-01 | DONE | main | Repo bootstrap & canonical docs |
| REA-P0-02 | IMPORTED_REVIEW_PENDING | import/fable51-bbe72c0 | 88 paths pinned; redistribution review pending |
| REA-P0-03 | PARTIAL_IMPORT_REVIEW_PENDING | import/astra-p4-b3166b6 | 103 selected paths, 41 contracts; NOT full vendor |
| REA-P0-04 | BLOCKED_RIGHTS_CLEARANCE | integration/develop | D6 pinned provenance hashes PASS but absent conventional LICENSE/NOTICE at upstream refs; distribution rights/dependency lock NOTICE review NOT DONE |
| REA-P1-01 | DONE_FEATURE | feature/evidence-adapter | Fable->Astra schema review adapter; 28 tests PASS |
| REA-P1-02 | DONE_FEATURE | feature/evidence-adapter | Strict inferred/observed and unapproved mapping guards |
| REA-P2-01 | PARTIAL_DONE_FEATURE | feature/csv-local-mvp | UTF-8 CSV cap/validator works; full owner JSON/mapping UX pending |
| REA-P2-02 | DONE_FEATURE | feature/csv-local-mvp | Fresh isolated read-only SQLite generator, no source overwrite |
| REA-P3-01 | DONE_FEATURE | feature/csv-local-mvp | List/search/filter/detail actual browser PASS |
| REA-P4-01 | DONE_FEATURE_MVP | feature/orchestrator | CSV-only + optional Fable review + independent app CLI, 55 pytest+browser PASS |
| REA-P5-01 | DONE_FEATURE_VERIFIED | qa/cross-platform | Three domains, Chromium PASS, Windows native CMD/API PASS, ZIP SHA256 artifact, design gap; CI 40202313506 68 pytest on Linux/Windows |
| REA-P5-02 | DONE_FEATURE_VERIFIED | feature/mvp-summary-preview | CSV lexical schema preview UNAPPROVED, category count UI; CI 40203444938 77 tests each OS and Chromium PASS |
| REA-P5-03 | DONE_FEATURE_VERIFIED | feature/json-intake | One bounded JSON intake plus CSV, shared validator; CI 40204413087 111 pytest on each OS and 4 Chromium synthetic cases PASS; 2-file scope NOT SUPPORTED | 
| REA-P5-04 | BLOCKED_OWNER_SCOPE | none | Two-file join/mapping rules or expressly approved commercial offer revision |
| REA-P6-00 | DONE_AUDIT_NOT_LICENSED | feature/license-provenance | D6 SHA b97443657e46a8f701e12b83bf87f5a0339b224c; 125 pytest each OS, pinned 88+103 Git blobs both OS, ZIP allowlist SHA256/negative tests, CI 40205614846 | 
| REA-P6-02 | DONE_SYNTHETIC_VERIFIED | feature/security-recovery | Atomic no-replace directory + complete ZIP publication, fail injection, readonly SQLite, [CI 40206549211](https://github.com/hibi89/REA_Web/actions/runs/40206549211) 141 tests each OS, 5 Chromium synthetic cases |
| REA-P6-03 | DONE_SYNTHETIC_VERIFIED | feature/guided-intake | Owner field inspect/wizard/build/pack, explicit approval, ZIP receipt; CI 40207742776 164 tests each OS, 7 Chromium |
| REA-P6-04 | READY | new D9 feature branch | Strict explicit same-schema two-input APPEND prototype, no implicit relation/joins and no commercial scope approval |
| REA-P6-01 | BACKLOG_BEFORE_SALE | release/v0.1 | Commercial scope, licenses, full security/recovery and clean Windows customer pilot |

**Verified combined feature SHA:** `46060b4665560922d0c9cf82b9e5c08971eb9427` ([CI 40200704855](https://github.com/hibi89/REA_Web/actions/runs/40200704855); PR #5 Draft, unmerged).
Separate D1 `5515a728...` / D2-01 `fda96076...`, both Draft/unmerged. Latest dispatch is `docs/17_NEXT_TASK.md`; historic implementation order has been superseded by MVP-first.

D3 actual QA proof: [CI 40202313506](https://github.com/hibi89/REA_Web/actions/runs/40202313506), verified test SHA e88c89f3ec12e61e63d2ca1255736fbf674c6e9e, draft PR #6, source unmerged. Artifacts include synthetic example ZIP and browser screenshots.
