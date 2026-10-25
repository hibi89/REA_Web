# 17 — READY / next task (2026-10-25)

TASK ID: **REA-P0-04 / Pinned import QA and dependency isolation**.

1. Inspect source PR #1 and #2 and their exact HEADs; remain Draft/unmerged.
2. On branch **qa/vendor-fable** run: python tools/verify_vendor_manifests.py --vendor fable51; expect 88/88 exact Git blob SHA matches.
3. On branch **qa/vendor-astra** run: python tools/verify_vendor_manifests.py --vendor astra_p4; expect 103/103 exact Git blob SHA matches.
4. Check hosted GitHub Actions from each QA branch with actual run IDs; do not mark PASS based on workflow YAML existence.
5. Identify missing fixtures/tests in bounded Astra subset; supplement only safely after validating license/source and recording missing vs imported.
6. Isolate dependencies and run upstream-selected offline tests independently. Record real test exit codes, OS, SHA and SKIPs.
7. After P0 acceptance review, issue **REA-P1-01** on feature/evidence-adapter: Fable JSON→Astra evidence/functional draft schema with source-certainty preserved, >=15 synthetic + negative cases.
8. In parallel P2 CSV→local app under feature/csv-local-mvp; no live customer database, crawling or paid API.
9. Update STATUS.md, HANDOFF.md, docs/13_WORK_BREAKDOWN.md and this file on main after actual verified work.

**Important:** P0 snapshots exist but neither is merged to integration/develop. The 103-file Astra snapshot is PARTIAL, not a complete Astra checkout. The integrated REA_Web app and final product are NOT implemented. Do not promise order delivery.

User shorthand: 'ㄱ' = proceed with next safe READY work unit. If a step needs approval or customer data, mark BLOCKED and move to the next independent safe unit. Never overwrite source refs.
