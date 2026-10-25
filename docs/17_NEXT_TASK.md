# REA_Web dispatcher — SINGLE ACTIVE READY TASK (2026-10-25 KST)

Trigger **[REA_Web 깃헙 레포지토리 보고 작업이어가셈]** or **ㄱ** means read real remote heads/main HANDOFF/STATUS/AGENTS and **execute next safe READY work in current turn**, no context re-asking or background promises.

## D5-01 DONE, verified
- **`feature/json-intake` SHA `b1ef76b5f3155ec23dc302af30876ecf9127ea5e`**, [Draft PR #8](https://github.com/hibi89/REA_Web/pull/8) to integration/develop; UNMERGED. Branch from tested D4; pinned imports unchanged.
- [GitHub Actions 40204413087](https://github.com/hibi89/REA_Web/actions/runs/40204413087) SUCCESS: Ubuntu + Windows-latest **111 pytest each**, 1 warning each; **four synthetic actual Chromium apps** (3 CSV plus JSON); Windows extracted CMD/localhost API PASS; CSV/JSON example ZIP generated and checksum verified; synthetic artifact **12603355940**.
- New one-file flat JSON array of string-valued objects accepted by `--json` (mvp/orchestrator/delivery) in addition to unchanged `--csv`. Strict same validation for unique id, required id/title/category, 10 MiB, 10k rows, 20 keys, 2000 chars/cell; reject nested/non-string/duplicate keys/symlink, with negative tests.
- Raw JSON source never copied to generated ZIP; CSV/JSON source_kind recorded, lexical/schema hints UNAPPROVED, Fable review separate REVIEW_REQUIRED.
- **IMPORTANT:** original 30만원 draft promises **up to TWO files**; actual combined intake **one file only**, with no safe approved automatic merge. D5 guide docs/24_JSON_INTAKE_SCOPE.md and feature docs/07_KMONG_OFFER.md explicitly mark scope discrepancy. Multi-file owner mapping or approved offer contract change is BLOCKED pending user business decision; do not silently change contract or claim full support.

## ACTIVE READY: REA-MVP-D6-01 — source provenance and license/dependency risk audit
Target a **new nonconflicting feature branch** based on D5 verified SHA after refetching current remote. NO force updates, vendor/import edits, releases or customer data.

1. Inspect GitHub `main` + `feature/json-intake` real heads and read `docs/05_ACCEPTANCE.md`, `docs/07_KMONG_OFFER.md`, `docs/14_FINAL_DELIVERABLES.md`, `docs/24_JSON_INTAKE_SCOPE.md`, `docs/21_MVP_GAP_MATRIX.md`.
2. Read exact immutable Fable and **partial** Astra snapshot manifests and LICENSE/NOTICE (where present), old upstream references, generated app `requirements.txt`, GitHub Actions pip install pins/bounds, and actual files entering `rea.delivery` package. Collect evidence with path+SHA and dependency identity/version; distinguish package source vs vendor source.
3. Generate concise evidence-grounded **dependency inventory / license+provenance review**: VERIFIED from sources, UNKNOWN, BLOCKED or NOT_ASSESSED for redistributability/attribution; don't invent a missing LICENSE or claim commercial compliance. Check packaged ZIP includes no original vendor engines or raw Fable input, no secrets. Offline synthetic safe script/check preferred.
4. Categorize release gates: 2-file contract unresolved, clean consumer Windows/manual setup, one authorized source and owner data rights, input security/recovery, licensing notices, 30만원 service support/feature promises. Separate blocked owner approval tasks from independent safe automated work.
5. Add test/CI for manifest/SBOM/offline license checklist if worthwhile, Draft PR to integration/develop, record exact SHA+CI evidence and NOT_RUN statuses, update main STATUS/HANDOFF/NEXT_TASK. DO NOT merge vendor snapshots, start live scrape, buy services, edit upstream repos, or approve commercial release.

## After D6
Finish high-risk security/recovery and clean Windows nondeveloper pilot, owner-approved multi-file feature/contract scope, source/data permissions, merchant terms. No general 1:1 source website clones or production/customer DB access. Three-day MVP-first timeline was a stretch target, not proof of commercial readiness.
