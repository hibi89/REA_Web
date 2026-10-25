# REA_Web — STATUS (2026-10-25 KST)

**PHASE: D5-01 VERIFIED on feature branch, D6-01 READY.** Product **NOT for sale, NOT production deployed**. Main remains documents/dispatch; feature code in unmerged Draft PR.

## Verified development by synthetic tests
| Unit | Exact source | Evidence |
| --- | --- | --- |
| D1 local CSV app | feature/csv-local-mvp 5515a7286d63211e32d2c577f93f77d61f37ce08 | 40198326369: 9 pytest & Chromium PASS |
| D2-01 Fable→Astra review | feature/evidence-adapter fda96076de33ebf4f4b6118972a5033a3f703ba9 | 40199741969: 28 pytest PASS |
| D2-02 optional Fable review + CSV app | feature/orchestrator 46060b4665560922d0c9cf82b9e5c08971eb9427 | 40200704855: 55 pytest & Chromium PASS |
| D3-01 3 synthetic domains/ZIP/native Windows | qa/cross-platform e88c89f3ec12e61e63d2ca1255736fbf674c6e9e | 40202313506: 68 pytest each OS & Chromium PASS |
| D4-01 CSV preview & category count | feature/mvp-summary-preview d8e26ed7d60ad86f64e35aefb3825655d6e19d25 | 40203444938: 77 pytest each OS & Chromium PASS |
| **D5-01 strict JSON intake** | **feature/json-intake b1ef76b5f3155ec23dc302af30876ecf9127ea5e**, [Draft PR #8](https://github.com/hibi89/REA_Web/pull/8) | [GitHub Actions 40204413087](https://github.com/hibi89/REA_Web/actions/runs/40204413087) **SUCCESS**: **111 pytest PASS Ubuntu + Windows-latest each**, 1 nonblocking warning each; **4 actual Chromium synthetic apps** (3 CSV + 1 JSON) PASS; Windows native CMD localhost/API PASS; two example ZIPs with SHA checksums PASS. |

D5 GitHub Actions synthetic artifact **rea-d5-synthetic-linux-qa**, ID **12603355940**, holds four browser screenshots, JSON report and CSV/JSON example ZIPs. Upstream vendor Fable and Astra imported sources unchanged; earlier source branches not modified. All Draft PRs #1–#8 unmerged.

## D5 actual scope and boundaries
- One **CSV OR JSON** file at a time. JSON must be a flat array of string-valued objects, mandatory id/title/category, consistent columns; duplicate ID/JSON keys, nested/scalar/numeric/bool/null, NaN, oversize and symlinks rejected. Both formats share strict row validation (10 MiB, 10k rows, 20 columns, 2000 chars/cell).
- Generated local FastAPI+SQLite readonly app includes listing/search/filter/detail, unapproved lexical schema preview and CSV/JSON-grounded category counts. Native Windows launcher/localhost API tested. Input source never overwritten nor copied into ZIP; optional prior Fable JSON technical findings remain unapproved and separate.
- **DRAFT commercial scope conflict unresolved:** docs/07_KMONG_OFFER.md promises **up to TWO files**, but D5 implements ONE file at a time. **No automatic cross-file joins/unions, no silently withdrawn promise.** Owner-approved mapping or explicitly approved contract change required before listing.
- Main is documentation/dispatcher, not a merged runnable release. No Vercel/production URL.

## NOT_RUN / release blockers
- Full vendor/third-party dependency redistribution license and provenance **NOT DONE**; Astra import is PARTIAL, Fable import separately pinned.
- Clean nondeveloper Windows PC install/Windows Chromium, authorized real customer+reference data rights/acceptance, detailed security/recovery, customer support and 30만원 scope/time study **NOT RUN**.
- No live DB, private backend extraction, arbitrary URL clone, public deployment, paid API, authentication or payment implementation.
- One nonblocking Starlette/TestClient warning and GitHub Actions Node deprecation warnings; no known D5 failing synthetic CI.

## NEXT READY: REA-MVP-D6-01
Read-only offline **vendor/dependency licensing + package provenance inventory and sale-readiness risk register**. Do not assert rights/clearance without source evidence; avoid vendor modifications. Cross-file promise stays BLOCKED pending explicit contractual choice, not automatically joined. See docs/17_NEXT_TASK.md. Next user ㄱ means execute D6-01 immediately with actual GitHub state.
