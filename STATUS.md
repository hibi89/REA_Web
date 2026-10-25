# REA_Web STATUS — 2026-10-26 KST

**D9-01 VERIFIED in isolated feature branch; D10-01 READY.** Not for commercial sale, not production deployed; main is documentation/dispatch and PRs #1–#12 remain Draft/unmerged.

## Evidence-backed milestones
| Unit | Working scope | Verified CI |
| --- | --- | --- |
| D1 | CSV -> readonly local app | 40198326369, 9 pytest + Chromium |
| D2-01 | Fable/Astra inferred-only review adapter | 40199741969, 28 pytest |
| D2-02 | Independent CSV app + optional review | 40200704855, 55 pytest + Chromium |
| D3 | ZIP, 3 synthetic domains, Windows | 40202313506, 68 pytest each OS |
| D4 | UNAPPROVED field preview and category counts | 40203444938, 77 pytest each OS |
| D5 | One strict JSON OR CSV | 40204413087, 111 pytest each OS |
| D6 | Vendor 88/103 hashes, ZIP allowlist/audit | 40205614846, 125 pytest each OS |
| D7 | Atomic no-overwrite ZIP/dir and recovery | 40206549211, 141 pytest each OS |
| D8 | Explicit single-input owner field approval | 40207742776, 164 pytest each OS |
| **D9** | **Two explicitly approved same-schema source files row APPEND only** | **[Actions 40209013017](https://github.com/hibi89/REA_Web/actions/runs/40209013017) SUCCESS: Ubuntu 181 pytest PASS and Windows 181 pytest PASS, real Chromium 8 synthetic apps, Windows .cmd/HTTP PASS, pinned Fable 88 + PARTIAL Astra 103 SHA PASS on both OS**. |

D9 feature branch `feature/owner-approved-append`, tested SHA `addb5067a3422cd7ecad6836bcf6620d2f03db1e`, [Draft PR #12](https://github.com/hibi89/REA_Web/pull/12) unmerged. One nonblocking TestClient warning per OS. Evidence artifact `rea-d9-synthetic-approved-append` ID **12604208149** includes screenshots, browser JSON and sample ZIP/provenance reports.

## D9 feature contract
- `python -m rea.two_source inspect` privately prints two source schema headers, counts and SHA-256, with no cell samples.
- `build` or `pack` requires exact source field mapping and separate literal APPROVE for each source plus final APPEND confirmation. CSV+JSON or other supported combinations only when explicitly mapped **same column set**, distinct IDs, combined source bytes at most 10 MiB and combined rows at most 10,000.
- Data row **append** only; no unknown foreign key joins, dedup/overwrite, live DB, original source rewriting, guesses from Fable, implicit approvals or public uploads.
- Generated app/ZIP includes unserved `append_report.json` with each source SHA, type, row counts and local approval status; D6 ZIP auditor checks consistency, allowing no unrecorded mixed-source package. Original data is held in generated data.sqlite; never claim deliverable is PII-free.
- D1–D8 CLI and browser functions remain intact; 8 synthetic Chromium cases including new 2-file customer-approved append passed.

## Outstanding commercial gates
- **Draft 300,000 KRW up-to-two-file claim is ONLY partially covered**: same-schema row append supported but cross-table joins and different business schemas unsupported. Marketing/spec change or clearly approved supported-scope contract is required before accepting an order.
- Fable/Astra/generated app redistribution rights and exact FastAPI/Uvicorn plus transitive package lock/licenses/NOTICE/SBOM not cleared.
- Customer-facing guided GUI, clean nondeveloper Windows setup + browser, authorized real customer/reference acceptance, privacy review, full security/backups/power-loss, correction/refund and 6–8h labor trial NOT RUN.
- Production hosting, personal data, paid service or external site scan NOT USED/DEPLOYED.

## NEXT READY D10-01
Create a **single isolated release-candidate staging branch** from verified D9 source (not merge to integration/develop), build reproducible test-only ZIP and end-user Windows onboarding self-check, inspect exact dependency metadata/license/NOTICE as available, validate no package provenance regression; mark unmet license and human acceptance gates BLOCKED. CI and Draft PR, then update main handoff. See docs/17_NEXT_TASK.md.
