# 08 — GitHub branches and review discipline

**main**: baseline documentation and only reviewed integration code. No force push, no direct unverified vendor merge.

**import/fable51-bbe72c0**: immutable copy of Fable 5.1 pinned bbe72c0..., under engines/fable51/ only. Upstream workflow YAML retained under nested vendor path, not repository .github/workflows.

**import/astra-p4-b3166b6**: immutable pinned P4 feature proof snapshot under engines/astra_p4/, synthetic-only; initial source may be a bounded subset and manifest MUST list imported/not-imported files.

**integration/develop**: tested merge target for import branches and new adapter, never assumed automatically safe. Separate code on feature branches.
**feature/evidence-adapter**: mapping contract Fable→Astra, no real DB.
**feature/csv-local-mvp**: sanitized CSV/JSON→local SQLite→minimal app, no network fetch.
**feature/orchestrator**: deterministic end-to-end CLI, scoped execution.
**qa/cross-platform**: runner/scripts for Linux + Windows browser acceptance.
**release/v0.1**: only when all v0.1 gates pass; tags on approved release SHA.

Sequence: main bootstrap → source snapshots → draft PRs to integration/develop → integration tests → reviewed main. Never create false commits marked DONE for plans alone.

Every PR must state origin SHA, changed paths, risks, exact test status, permissions, acceptance gates. Changing an immutable import branch requires a new import branch, never silent ref update. Source fixtures must contain NO customer data.
