# REA_Web — STATUS (2026-10-25 KST)

**CURRENT PHASE:** D3-01 three-domain + Linux/Windows synthetic acceptance VERIFIED on QA feature branch; next D4 functional gap filling READY. Product NOT commercially or production ready. Main remains documentation and dispatch baseline (code still separate Draft PRs).

## Verified stage summary
| Unit | Branch / tested SHA | Actual evidence |
| --- | --- | --- |
| D1 local CSV web app | feature/csv-local-mvp / 5515a7286d63211e32d2c577f93f77d61f37ce08 | GitHub Actions 40198326369: 9 pytest PASS + Chromium PASS |
| D2-01 Fable-to-Astra review-only adapter | feature/evidence-adapter / fda96076de33ebf4f4b6118972a5033a3f703ba9 | Actions 40199741969: 28 pytest PASS + pinned Astra validators PASS |
| D2-02 combined CSV-only / optional Fable review | feature/orchestrator / 46060b4665560922d0c9cf82b9e5c08971eb9427 | Actions 40200704855: 55 pytest PASS + Chromium PASS |
| **D3-01 3 domains / ZIP / Windows** | qa/cross-platform / e88c89f3ec12e61e63d2ca1255736fbf674c6e9e (latest docs-only head 857a73e1f3e641f851fd4df1212872846528bdb9) | [Actions 40202313506](https://github.com/hibi89/REA_Web/actions/runs/40202313506) **SUCCESS**: Ubuntu 68 pytest PASS + 3 Chromium app scenarios; Windows-latest 68 pytest PASS + extracted Windows CMD→loopback API. 1 warning each, zero failed; synthetic artifact 12602316907. |

D3 test artifacts: screenshots for cafe/inventory/trends, qa_report.json and example reproducible REA_Web_Cafe_v0.9.zip, stored in [GitHub Actions artifacts](https://github.com/hibi89/REA_Web/actions/runs/40202313506) named rea-d3-synthetic-linux-qa. ZIP content checksums tested; source Fable JSON/vendor engines are not bundled. Optional Fable evidence always REVIEW_REQUIRED and is not served to the app. Three browser cases reported zero JS exceptions, script dialogs or unexpected external requests.

## Current deliverables
- Generator: customer CSV only → isolated local SQLite/read-only FastAPI+HTML/JS with list, search, filter, detail.
- Optional already-redacted Fable v1.0 JSON → validated Astra review-only draft stored separately; NO automatic owner DB mapping or business behavior extraction.
- Reproducible synthetic ZIP with SHA256 member manifest, Windows launcher, setup guide, checksum verifier.
- Original architecture gap matrix: [docs/21_MVP_GAP_MATRIX.md](https://github.com/hibi89/REA_Web/blob/qa/cross-platform/docs/21_MVP_GAP_MATRIX.md); test guide docs/22_D3_TEST_GUIDE.md on QA branch.
- Draft PRs #1–#6 OPEN and UNMERGED; no Vercel project or production deployment (NOT_APPLICABLE).

## Known remaining gaps / limits
- Interactive mapping approvals, JSON/two-file intake, optional summary, nondeveloper GUI and commercial scope reconciliation still MISSING/PARTIAL.
- Native Windows-latest launcher verified; clean end-user Windows install and Windows Chromium UI **NOT_RUN**.
- No genuine customer or authorized real-site reference tested; source rights/customer approval NOT_RUN.
- Third-party code/dependency/license distribution review, full security/recovery, pilot customer support and price acceptance NOT_DONE. No public hosting, account/payment, live DB or arbitrary source cloning.
- Initial Windows launcher returned code 0 too early when using py -3; corrected launcher to PATH python; Windows CI subsequently PASS. Do not repeat unsupported launcher assumption.
- Node action deprecation / Starlette TestClient warning nonblocking, not proof of customer safety.

## NEXT READY: REA-MVP-D4-01
Use feature branch for low-risk high-value **CSV schema preview and category count summary** without altering the existing list/filter/detail behavior; deterministic unit + browser test; compare impact to original design and fixed 300k offer. Avoid user/customer data, external network, vendor edits, production deployment. Detailed dispatch in docs/17_NEXT_TASK.md. Then final license/security/clean Windows/authorized customer acceptance BEFORE commercial release.

Every new chat: phrase [REA_Web 깃헙 레포지토리 보고 작업이어가셈] or ㄱ means execute next READY unit immediately after current GitHub head/docs check.
