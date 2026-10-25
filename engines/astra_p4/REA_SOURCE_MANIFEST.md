# Astra P4 pinned source subset — provenance

Upstream: hibi89/astra_web_catcher @ b3166b67604381a9d2afd41667b65f9a9b103b37 (feature/observation-contract-20261018).

**103 source/test/docs/fixture files** copied verbatim from exact pinned upstream commit in nine commits (12+12+12+11+12+12+12+12+8). File paths and original Git blob SHA stored in provenance/BATCH_01.json through BATCH_09.json.

This is a **BOUNDED PARTIAL SNAPSHOT**, not the complete Astra repository or the later codex-p4 branch. It includes all 41 astra_contracts modules, the 2 demo backend Python files with static HTML/JS/CSS and migration, selected key tests, synthetic fixtures, scripts and proof docs, but omits numerous other tests/fixtures/docs and six upstream P4 GitHub Actions. Some tests in this subset may depend on omitted fixtures. Do not claim that entire upstream suite has been reproduced from this tree.

Upstream historical evidence: 940 PASS / 2 SKIP on exact earlier P4 commit and synthetic Chromium E2E; not a REA_Web test. Later codex-p4-20261019 has unresolved Windows whole-suite failures; never silently replace this pinned snapshot. No real owner DB/production access, deployment or general URL-to-app generator here.

Next step: reproduce selected tests with complete fixture dependencies in isolated venv, compute remote imported Git blob hashes, and implement independently versioned Fable→Astra adapter. No main merge until evidence checks and approval.
