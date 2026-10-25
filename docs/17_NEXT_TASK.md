# REA_Web — SINGLE ACTIVE READY (2026-10-26 KST)

Trigger ㄱ or [REA_Web 깃헙 레포지토리 보고 작업이어가셈] means refetch GitHub main/feature heads, read STATUS/HANDOFF/AGENTS and implement the next safe bounded task NOW, no further context questions or background work.

## D9-01 DONE, measured verification
- Feature `feature/owner-approved-append` functional source `addb5067a3422cd7ecad6836bcf6620d2f03db1e`, [Draft PR #12](https://github.com/hibi89/REA_Web/pull/12), UNMERGED. 
- [Actions 40209013017](https://github.com/hibi89/REA_Web/actions/runs/40209013017) SUCCESS: Ubuntu **181 pytest PASS** + Windows-latest **181 pytest PASS** (one nonblocking warning each), 8 actual Linux Chromium independent synthetic apps (including two-file approved append), native Windows CMD/localhost HTTP PASS, pinned Fable 88 and Astra PARTIAL 103 SHA proofs BOTH OS PASS. Evidence artifact `rea-d9-synthetic-approved-append` ID **12604208149**.
- New rea/two_source.py inspect/build/pack supports two distinct authorized local CSV/flat JSON inputs **only for same normalized field schema and row APPEND**. Literal APPROVE each file + APPEND overall, SHA pinned each source, no duplicate IDs or cross-source join, combined <=10 MiB <=10k rows, original untouched. Private normalized temp CSV deleted; delivered app/ZIP contains unserved append_report.json and source hash/consent metadata cross-checked by D6 ZIP allowlist audit. No sensitive original rows in receipt; generated data.sqlite DOES contain owner rows.
- Initial D9 CI first failure was expected error wording mismatch, second Windows hardlink test linked C: and D: drives; these were test fixtures, not product exceptions, fixed in final SHA. Latest complete CI green. Original D1–D8 CLI features retained.
- Draft 300k up-to-two-file offer now **partially supported** (approved SAME-SCHEMA APPEND only). Unsupported: joins/foreign-key linking/heterogeneous schema, unauthenticated owner data rights, source commercial rights. Do not advertise arbitrary two-file integration.

## NEXT READY D10-01 — isolated release-candidate staging and Windows onboarding check
1. Refetch actual latest main, D9, pinned Fable/Astra refs and docs/05_ACCEPTANCE.md, docs/07_KMONG_OFFER.md, docs/14_FINAL_DELIVERABLES.md and docs/28_TWO_FILE_APPEND.md. New nonconflicting feature branch from D9 tested SHA. No merge or force push.
2. Produce **one coherent synthetic demonstration delivery** with exact clearly supported options: standalone one CSV/JSON, guided single-file approved mapping, or strictly approved same-schema two-source APPEND only. Packaging must retain D6 provenance checker, owner no-overwrite, local binding, user docs and no vendor source or sensitive real data.
3. Provide a beginner-safe reproducible Windows setup/self-diagnostic process usable with ordinary CMD/PowerShell without asking for admin privileges if possible. Must not claim actual nondeveloper clean-PC acceptance (NOT_RUN).
4. Inventory exact resolved runtime dependency versions/licenses/notice **as observed in CI**, differentiate declared ranges, transitive dependencies and missing license/attribution clearance; do not mistake CI install for a licensed bundled runtime.
5. Meaningful Linux+Windows tests, actual Chromium regressions (8 cases), native Windows launcher and pinned Fable 88/Astra PARTIAL 103 source hashes; Draft PR, exact SHA/CI/NOT_RUN evidence, update main STATUS/HANDOFF/NEXT_TASK.
6. Explicit blockers remain: commercial up-to-two-file broader interpretation and owner scope acceptance, copyright/licensing, clean actual nondeveloper Windows and customer/reference site authorization, privacy/power loss/production security and support/refunds. No live scrape, public deploy, customer file upload, paid subscriptions or source branch merges.

After D10, owner-reviewed v1.0 feature contract and three measured mock jobs; license/NOTICE audit and clean Windows human trial; real non-sensitive authorized customer reference; only then business offer/purchase.
