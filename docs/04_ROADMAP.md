# 04 — Stage-gated execution roadmap (2026-10-25)

Durations are provisional engineering hours, not calendar promises. Product work is synchronous when a task is requested; no claim that agents run between chats.

| Stage | Scope | Est. hours | Gate |
| --- | --- | ---: | --- |
| P0 | Repo bootstrap, source manifests, safe branch imports, read-back hashes | 4–8 | all files provenance and branch HEADs |
| P1 | Fable result → Astra observation draft adapter, certainty/provenance guards | 8–14 | 15+ fixture/negative cases |
| P2 | CSV/JSON input validator, owner schema review, isolated sqlite | 8–14 | malicious/missing/duplicate data correctly rejected |
| P3 | generated minimal independent app: list/search/filter/detail and SQLite | 12–22 | generated file/tree + actual API/browser green |
| P4 | local orchestration: Analyze→Review→Generate→Test, saved reports | 10–18 | one-command synthetic end-to-end |
| P5 | cross-domain examples (catalog, trends, tasks), Windows run, recovery | 10–20 | 3 vertical slices, reproducible manual checklist |
| P6 | product UX, packaging, redaction, report, limited 300k offer pilot | 8–16 | reviewed local deliverable and 3 time/cost measurements |
| P7 | advanced owner API/DB, complex workflow, support & deployment (OPTIONAL) | scoped separately | new signed scope & risk test |

P0–P6 total rough **60–112 engineering hours**; this is not a 100% clone, complete no-code builder or enterprise integration. Import reuse assumptions may alter actual time. P7 explicitly not part of 300k fixed-price baseline.

## Dependency path
P0 → P1/P2 (independent) → P3 → P4 → P5 → P6. Refuse to skip P1 semantics or P2 input safety.

## Stop rules
If an identical approach fails twice: document cause and choose fallback. If a stage lacks a stable test result, do NOT claim it is done or start customer beta. If client data/URL rights or format are uncertain, analysis mode only. Report hours actually spent; avoid unbounded scope.

## First deliverable milestone
Version 0.1 is a genuine LOCAL synthetic CSV→app vertical slice, not a static mockup. Version 0.2 integrates evidenced Fable data to Astra draft. Version 1.0 is a tested, packaged **restricted** local application generator for supported data/behaviors.
