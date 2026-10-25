# REA_Web STATUS — 2026-10-26 KST

**D12-01 VERIFIED in Draft PR #15; D13-01 NEXT READY (guided offline creator UI).** main holds documentation/dispatcher; all PR #1–#14 remain Draft/unmerged. No production hosting or commercial release.

## Exact evidence milestone
| Unit | Synthetic working unit | Verified tests |
| --- | --- | --- |
| D1 | CSV independent local webapp | 40198326369, 9 tests + Chromium |
| D2-01/02 | Isolated Fable technical observation -> Astra REVIEW_REQUIRED and app orchestration | 40199741969 28; 40200704855 55 |
| D3 | Windows ZIP / 3 browser scenarios | 40202313506, 68 pytest per OS |
| D4 | Unapproved lexical schema and category summary | 40203444938, 77 per OS |
| D5 | Strict single flat JSON/CSV | 40204413087, 111 per OS |
| D6 | Vendor 88/103 pinned blobs and ZIP allowlist | 40205614846, 125 per OS |
| D7 | Atomic no-overwrite, readonly SQL and recovery | 40206549211, 141 per OS |
| D8 | Guided owner field mapping and SHA/APPROVE | 40207742776, 164 per OS |
| D9 | Explicit SAME-SCHEMA two-file ROW APPEND, NOT joins | 40209013017, 181 per OS |
| D10 | Three synthetic RC ZIPs, Windows offline self-check and observed dependencies | 40210279358, 188 per OS |
| **D11-01** | **Three independent synthetic quotes -> ZIP -> extracted self-check -> browser -> G0–G6 scorecard + EMPTY manual labor log** | **[Actions 40211563951](https://github.com/hibi89/REA_Web/actions/runs/40211563951) SUCCESS: 201 pytest PASS on Ubuntu and 201 pytest PASS on Windows-latest (one nonblocking warning each); existing eight real Chromium synthetic apps PLUS three additional Chromium runs using EXTRACTED customer ZIPs; Windows actual ZIP CMD/localhost HTTP PASS; 88 Fable and PARTIAL 103 Astra pinned blobs PASS on BOTH OS.** |

D11 isolated feature branch feature/three-case-rehearsal SHA a49f05e969fd49e44b2c8beed2779447d6d56d3e, [Draft PR #14](https://github.com/hibi89/REA_Web/pull/14), UNMERGED. CI synthetic artifact rea-d11-synthetic-acceptance ID **12606062263** includes three generated app ZIPs, acceptance_scorecard.json, MANUAL_TIME_LOG_BLANK.csv, customer-facing test docs, three screenshots and combined browser acceptance ledger. First D11 CI failed packaging app rows lookup; second Windows source-only test imported absent Playwright; both fixed and final source hash a49f05e969fd49e44b2c8beed2779447d6d56d3e CI green.

## D11 actual simulated order scope
- **Cafe** 4 synthetic rows, 1 screen; contract list/search/category_filter.
- **Inventory** 5 synthetic rows, 1 screen; contract list/search/detail.
- **Trends** 5 synthetic rows, 1 screen; contract list/category_filter/simple_summary.
- Each fixed KRW 300,000 is a **nonbinding price hypothesis** only; each selected feature is a 3-feature contract, although generated UI may also show existing uncontracted functionality.
- Each has actual generated deterministic ZIP, D6 provenance audit, extracted standalone self-check, browser screenshot and only requested-feature verification against extracted ZIP app. No external site requests/JS errors/dialogs.
- Machine-readable G0–G6 ledger allows **PASS_SYNTHETIC_SUBCHECK** for generated app/browser only. G5 (authorized real client/reference + measured manual effort) and G6 (consumer Windows, license/NOTICE, backup, support) remain **BLOCKED**. Main release overall BLOCKED.
- Manual labor CSV has ONLY header row: no human prep/build/correction/QA/delivery time supplied, no proof of 6–8 hour target. Details [D11 guide](https://github.com/hibi89/REA_Web/blob/feature/three-case-rehearsal/docs/30_THREE_CASE_QUOTE_REHEARSAL.md).

## Release blockers that CI cannot clear
- Initial 300,000 KRW package's up-to-2-files promise supports only explicitly approved same-schema row APPEND, not unlike-table relational joins. No binding scope approval or signed client agreement.
- Copyright source/redistribution grants for Fable, Astra, generated templates, runtime exact dependency locks and complete SPDX/NOTICE/transitive license compliance not verified.
- NO actual authorized client/reference site, human clean Windows, GUI onboarding, real personal-data/PII/backup/power-loss/penetration security, buyer acceptance or correction/refund/support signoff.
- Three manually measured jobs and the suggested 6–8 hour service economics remain NOT_RUN.
- PR branches are not merged or published; no Vercel/live customer API, customer ZIP or real site accessed.

## NEXT READY: D12-01
An isolated, synthetic-only **reproducible CI dependency resolution + NOTICE/license evidence triage** unit: record exact direct/transitive versions, hashes and metadata/notice contents where legally permitted; produce a deterministic *developer-only* constraints/SBOM evidence without automatically modifying customer ZIP or asserting compliance. Test Linux+Windows full regression and actual Chromium. Keep ownership, signed customer license rights, clean Windows human and real buyer blocked. docs/17_NEXT_TASK.md is authoritative.

## D12-01 VERIFIED — offline exact dependency and legal-file SHA evidence (2026-10-26 01:45 KST)
- Feature `feature/dependency-notice-evidence` SHA `e18e07f714199a734699e1baca24d857c873fa60`, [Draft PR #15](https://github.com/hibi89/REA_Web/pull/15) **UNMERGED**. [GitHub Actions #40213031424](https://github.com/hibi89/REA_Web/actions/runs/40213031424) **SUCCESS** Ubuntu Python 3.11 **217 pytest PASS + 1 nonblocking warning**, Windows-latest Python 3.11 **217 pytest PASS + 1 nonblocking warning**. Existing 8 Chromium synthetic apps + 3 Chromium tests of extracted delivery ZIPs PASS (Linux), native Windows extracted ZIP CMD/localhost HTTP PASS, Fable 88/Astra PARTIAL 103 pinned source hashes PASS both OS.
- Added 16 D12 tests over D11's 201. Earlier Windows failed 1/216 due to POSIX `/LICENSE` not recognized as absolute under Windows; fixed with independent PurePosixPath/PureWindowsPath validation, added backslash traversal tests. Final 217/217 both OS PASS, not a bypassed test.
- `rea/dependency_evidence.py`: no-network read-only installed versions/PEP508 marker/conditional/missing/specifier evidence; hash of installed metadata and observed LICENSE/LICENCE/NOTICE/COPYING bytes where safe, never legal contents. Developer-only candidate constraints; **NO wheel archive hash lock, NO actual compliance approval/CVE scan**. 14 installed distributions observed both OS, extras expansion explicitly unresolved. Linux artifact **12606655901**, Windows artifact **12606481398**. CI reports outside actual delivery ZIP; no customer data, vendor source changes, payment or hosting.
- G5 and G6 still BLOCKED: actual approved client/reference, 3 measured human jobs, nondeveloper clean Windows, redistribution/license grants and attribution, privacy/recovery/security, actual 300k two-file scope signoff, correction/refund/support. Commercial readiness BLOCKED, Production **not applicable**.
- **NEXT D13-01:** restore high-value original-vs-MVP gap: optional local guided creator GUI for choosing owner CSV/JSON, reviewing consent/mapping and explicitly approving export; preserve CLI, avoid real files and remote upload. Compare stdlib Tkinter wrapper with localhost browser wizard, prefer optional Tkinter if tested; no autopermission. See docs/17_NEXT_TASK.md.
