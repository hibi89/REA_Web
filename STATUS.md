# REA_Web STATUS — 2026-10-25 KST

**PHASE: D4-01 VERIFIED on feature branch; D5-01 READY. Product NOT commercially ready.**

## Working completed checkpoints
| Unit | Latest verified scope | Evidence |
| --- | --- | --- |
| D1 | Single CSV -> readonly local SQLite/FastAPI/HTML; list/search/filter/detail | feature/csv-local-mvp 5515a7286d63211e32d2c577f93f77d61f37ce08; CI 40198326369: 9 pytest, browser PASS |
| D2-01 | Fable inferred-only -> Astra review adapter | feature/evidence-adapter fda96076de33ebf4f4b6118972a5033a3f703ba9; CI 40199741969: 28 tests PASS |
| D2-02 | CSV-only/optional reviewed Fable report + independent app | feature/orchestrator 46060b4665560922d0c9cf82b9e5c08971eb9427; CI 40200704855: 55 tests + Chromium PASS |
| D3-01 | 3 independent synthetic app scenarios, ZIP SHA manifest, Windows native launcher | qa/cross-platform e88c89f3ec12e61e63d2ca1255736fbf674c6e9e; CI 40202313506: 68 pytest on Linux AND Windows, Chromium 3 cases PASS |
| **D4-01** | CSV column/lexical-type preview (UNAPPROVED), readonly /api/summary and category count UI | feature/mvp-summary-preview **d8e26ed7d60ad86f64e35aefb3825655d6e19d25**; [CI 40203444938](https://github.com/hibi89/REA_Web/actions/runs/40203444938) SUCCESS: **77 pytest PASS on each OS**, 3 real Chromium E2E PASS, Windows native CMD+API PASS. Docs-only feature head e4e9c7954ba1369636bcc2107478a5d2dae2db7e; Draft PR #7 unmerged |

## D4 confirmed behaviors
- Customer-supplied CSV remains sole source of the generated app. All previous list/search/category filter/detail behaviors retained.
- Generated unserved schema_preview.json and readonly /api/schema supply ordered column names, lexical types (integer, decimal, date, text, mixed, unknown), present/missing counts; **review_status=UNAPPROVED**, approved_semantic_bindings empty. No sample cell values in preview. This is not owner approval.
- Readonly /api/summary derives total and grouped category counts from local SQLite; UI displays up to 100 categories without HTML injection. No inferred site formula. Optional Fable report stays separate and REVIEW_REQUIRED.
- CI code SHA d8e26ed7d60ad86f64e35aefb3825655d6e19d25 has 77 pytest PASS with 1 nonblocking warning per OS; 3 actual Linux Chromium cases with schema/counts/search/filter/detail/reload, zero JS error/outbound call. Windows native extracted ZIP .cmd/localhost API PASS. Synthetic artifacts stored in same D4 Actions run.

## Branches and product limits
- PR #1–#7 remain Draft/unmerged. Main is documentation and handoff, not runnable integrated product or released code. Original Fable pinned import 7e6f273... and Astra PARTIAL f044b66... are unchanged.
- Windows native API CI verified; clean nondeveloper Windows machine + Windows real browser NOT_RUN. Real reference site/customer data/approval NOT_RUN.
- Full vendor/license distribution review, security/recovery, production hosting, paid integrations and commercial acceptance NOT_DONE. No 1:1 URL clone, no customer live DB, auth/payment or marketing site deployment.

## NEXT READY: REA-MVP-D5-01
Reconcile the current one-CSV input with the proposed KRW 300,000 scope listing optional JSON/two files. Deliver an explicit capability/scope contract and add a bounded JSON-array data import (id/title/category) sharing the existing parser and generator where safe, with independent tests. Avoid auto-joining two unrelated files or silently reducing the advertised scope; two-file semantics require explicit rules or scope revision. Then prioritise licensing/provenance and security before commercial launch. Follow docs/17_NEXT_TASK.md.

Restart trigger: [REA_Web 깃헙 레포지토리 보고 작업이어가셈] or ㄱ means execute next safe READY task in same turn, consult latest remote HEAD first. No future/background claim.
