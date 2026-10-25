# 15 — Design and business decisions

2026-10-25:
- Name chosen by owner: REA_Web; repository hibi89/REA_Web.
- Integrate existing Fable 5.1 analysis + Astra Web Catcher independent generation; no throwaway rewrite.
- Preserve originals; source snapshots and integration development separate.
- First sale target: 300,000 KRW fixed scoped package. Live DB integrations are optional future quote only.
- Customer supplies clean data; developer does not collect it by default.
- Default stack: local Python FastAPI/SQLite/HTML JS, chosen to reuse validated components and ease ownership handoff. Re-evaluate after end-to-end demo rather than prematurely switching frameworks.
- Source behavior evidence != business rules. Human approval of field and formula semantics is mandatory.
- Owner privacy, redaction and authorization take precedence over aggressive extraction or unlimited scope.
- Stage completion requires evidence, not a percent inferred from number of commits.
