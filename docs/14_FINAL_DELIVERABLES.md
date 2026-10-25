# 14 — Definition of final deliverable

## Customer-facing restricted v1.0
1. Web/local app with explicit three-mode wizard: analyze authorized URL (optional), review evidence/unknowns, select owner CSV/JSON and approve a data mapping, generate local app, run tests, export delivery.
2. Supported independent app functions: list, search, filter, detail and basic summary; optionally one CRUD action only with explicit approval and backup. Out-of-scope enterprise features remain unavailable.
3. Runs on clean Windows environment with reproducible setup, no need for production DB credentials or real-time external APIs.
4. Generated project: self-contained FastAPI+SQLite+HTML/JS source, tests, mapping report, README, known limitations, redacted results and manifest.
5. CLI plus lightweight GUI or equivalent guided workflow validated by at least one nondeveloper.
6. Three independent sample sites/data categories, precise function parity results, measured manual effort and error logs. One authorized website reference if scope allows.
7. Exact accepted features and 1-round correction policy clearly encoded in 300k basic service product.
8. Technical evidence: passing tests with separate source and integration proof, dependency/license check and safe input policy.
9. Standalone Fable and Astra upstream remain preserved with pinned SHAs and release traceability.

## Not final deliverables
Any arbitrary URL 1:1 copy, all code/API reconstruction, customer operational DB migration, auth/payment systems, commercial hosting, secret retrieval, automatic copyright clearance, unbounded data collection, instant universal no-code application building.

## Version boundaries
v0.1 = local CSV→app vertical slice. v0.2 = Fable→Astra observation adapter end-to-end. v0.9 = Windows/3-domain staging. v1.0 = supportable 300k package with tested limits.
