# 16 — Source import runbook

1. Bootstrap main docs once. Create import/fable51-bbe72c0 and import/astra-p4-b3166b6 from main.
2. Fable copy source from exact pinned SHA, corresponding to reviewer ZIP source/ 88 files under engines/fable51/. DO NOT copy examples/test_logs/manifests as live customer artifacts. Verify all paths against ZIP source listing and Git blob SHA. Vendor workflows nested, not active.
3. Astra copy pinned verified p4 core modules and required fixtures/scripts under engines/astra_p4/. Source baseline reference: feature/observation-contract-20261018 commit b3166b6. Keep unported app/main separate; if subset imported, clearly list it as PARTIAL. Document codex/p4 later Delta; never blend unverified changes.
4. Exclude cookies, tokens, PII, hidden environments, out/ and sqlite data; source manifests need exact per-path sha and upstream commit.
5. Because two engines may have same package names, avoid package-path shadowing: prefer separate subprocess invocations and JSON artifacts in P1. Do not patch upstream vendor modules directly.
6. Create integration/develop from main for new adapter. Open draft PRs from import branches with literal source paths and safety review. No importing changed source into main until integration tests succeed.
7. After each stage, confirm GitHub READ BACK by fetching a sentinel file and compare known upstream hash; update STATUS/HANDOFF/NEXT_TASK.
