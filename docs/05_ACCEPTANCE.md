# 05 — Acceptance and definition of done

### Gate G0 import
Same upstream commit pinned, path count and content/hash manifest exported, no secrets or unauthorized data, original repositories unchanged; import snapshots isolated. Missing source files listed as explicit PARTIAL.

### Gate G1 evidence adapter
Preserves observed/inferred/unknown; never declares backend source/API ownership or precise formula inferred from URL. Fable x ASTRA schema v0.1 round-trip JSON Schema validation, redaction and unsupported field tests; conflicts return REVIEW_REQUIRED.

### Gate G2 owner data intake
CSV UTF-8 and reasonable Korean encodings by explicit choice; schema preview, inferred types marked unapproved, row/size caps, duplicate keys, invalid amount/date, CSV spreadsheet formula threat handled. No live customer DB or credential access. User approves mapping before code generation.

### Gate G3 generated app
Temporary isolated path only, independent source in user-deliverable folder, SQLite built from accepted CSV/JSON, list/search/filter/detail, healthy API, no mutation on source files; optional CRUD only when contract approved and independently tested.

### Gate G4 actual E2E
Run pytest on generated app; launch local server; Chromium browser type/search/filter/keyboard, compare expected rows to DB, reload/persistence, failed input and user isolation if auth is offered. Record command, head SHA, versions, PASS/FAIL/SKIP.

### Gate G5 3-case acceptance
3 different synthetic cases and 1 explicitly authorized non-sensitive real reference. Feature parity matrix: promised features must pass; unknown/unsupported unimplemented. Time log: manual prep, automated run, corrections, QA, customer delivery.

### Gate G6 product delivery
Windows setup/run, reliable export zip, launch/readme, user-safe errors, backup/restart, sanitized report, limitations and scope. 300k package excludes deployment, migrations and unrestricted support. Third-party code license review prior to redistribution.

A blocked gate means 'not complete'; upstream CI green alone cannot satisfy REA_Web gates.

## Current evidence status (2026-10-26 D10; non-certification)
- G0 upstream import pins and hash checking: **CHECKABLE/PASS for 88 Fable and 103 PARTIAL Astra selected blobs**, partial upstream source and legal rights still unverified.
- G1 strict observation/inference review: synthetic unit PASS, any authorized real website reference NOT RUN.
- G2 intake: synthetically verified UTF-8 CSV/flat JSON, explicit mapping approval and limited same-schema 2-file row append; Korean locale encoding beyond UTF-8, full customer rules and signed mapping permission PARTIAL.
- G3 local app source/SQLite/list/search/filter/detail/summary: synthetic PASS, customer custom interface parity NOT RUN.
- G4 Chromium 8 synthetic cases, Windows automated CMD HTTP and D1–D10 pytest: PASS ([CI 40210279358](https://github.com/hibi89/REA_Web/actions/runs/40210279358)), human usability/real customer NOT RUN.
- G5 3 independent synthetic domains exist, but authorized non-sensitive real reference and **three measured total labor cases** NOT RUN; gate BLOCKED.
- G6 extracted Windows scripted diagnostics/launcher, ZIP checksum PASS in CI; clean consumer Windows human, power-loss backup, full copyright/dependency redistribution/license/NOTICE and merchant support/correction terms NOT RUN; gate BLOCKED.
- **Do not mark overall G0–G6 release complete or approve commercial order from CI.**
