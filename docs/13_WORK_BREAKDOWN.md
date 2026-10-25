# 13 — Work packages and dependencies

| ID | Status | Branch | Deliverable | Acceptance |
| --- | --- | --- | --- | --- |
| REA-P0-01 | DONE | main | initial repo bootstrap documents | links/branch plan written |
| REA-P0-02 | IMPORTED_REVIEW_PENDING | import/fable51-bbe72c0 | Fable verified source snapshot | count + Git hash vs pinned commit |
| REA-P0-03 | PARTIAL_IMPORT_REVIEW_PENDING | import/astra-p4-b3166b6 | Astra p4 synthetic snapshot | manifest lists complete/partial |
| REA-P0-04 | READY_AFTER_VENDOR_QA | integration/develop | integration baseline and dependency isolation | isolated smoke in both engines |
| REA-P1-01 | BACKLOG | feature/evidence-adapter | Fable JSON→Astra observation draft | schema+15 negative/positive tests |
| REA-P1-02 | BACKLOG | feature/evidence-adapter | certainty/redaction/provenance QA | no inferred→observed inflation |
| REA-P2-01 | BACKLOG | feature/csv-local-mvp | CSV/JSON validation and schema preview | safe multilingual fixtures |
| REA-P2-02 | BACKLOG | feature/csv-local-mvp | fresh local SQLite data import | no mutation of source/real DB |
| REA-P3-01 | BACKLOG | feature/csv-local-mvp | generated local list/search/filter/detail app | browser/API success |
| REA-P4-01 | BACKLOG | feature/orchestrator | Analyse→Review→Generate→Test CLI | synthetic full E2E |
| REA-P5-01 | BACKLOG | qa/cross-platform | 3-domain and Windows regression | acceptance report |
| REA-P6-01 | BACKLOG | release/v0.1 | package+manual+commercial pilot | G0–G6 + 3 effort logs |

Source-import commits: Fable 7e6f273b359b207fad8f92016226e3058cbcb839 (88/88 ZIP-source entries); Astra f044b66e799289a5a353fdb9cbfdb324e683ffa3 (103 selected entries, not full repo). Draft PR #1 and #2 open to integration/develop, still unmerged.

READY statuses are source-import tasks, not product features. Mark DONE only after actual remote commit and source readback. The next exact task is docs/17_NEXT_TASK.md.
