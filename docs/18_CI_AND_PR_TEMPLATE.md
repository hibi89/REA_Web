# 18 — CI and PR contracts

## Suggested CI phases (not installed until code is integrated)
- source-manifest-check: per-path SHA and no sensitive paths; no external calls.
- evidence-adapter: pure pytest + JSON Schema fixtures, deterministic.
- csv-mvp: ephemeral DB and imported data validation/negative cases.
- app-e2e: loopback browser + three fixture sets + no unexpected external requests.
- Windows acceptance: command-line launch, test browser and packaging of offline product.

Set CI secrets empty, permissions contents:read, timeouts, no untrusted URL fetch in pull_request builds. Pull-request checks use synthetic test servers, not live customer or OWID sites.
Upstream GitHub workflows moved into engines/ paths are NOT top-level active workflows.

## Required PR fields
Task ID / source SHA / what changed / data permission / exact command and PASS FAIL SKIP / artifact hash / expected acceptance gates / manual review / rollback path / no-scope-creep notes. Draft until all required evidence exists.
