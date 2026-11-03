# REA_WEB — Customer backend integration readiness gate
Status: STATIC-ONLY PREPARATION. REAL CUSTOMER ZIP / AUTH / DOCKER / PRODUCTION NOT APPROVED. COMMERCIAL RELEASE HOLD.
Baseline: tested synthetic code SHA 5a047372c30f0eb81c3de36f42ad28abe34a0b52, Windows+Linux Chromium/FastAPI CSP suite each 135 PASS, not customer verification.

## Design comparison
A. Mount and import real customer backend ZIP directly into generated dashboard runtime: fewer manual steps but unknown code execution, auth, side effects, rights and dependency risks. Rejected at this stage.
B. Review bounded ZIP and API declarations statically, require explicit owner-approved read-only bindings, and validate runtime only later in separately approved sandbox. Reuses existing backend_zip.py, backend_schema.py, runtime_contract.py and frontend_bridge.py; deterministic/no API cost, lower security exposure. Selected.

## Required evidence before any real integration
| Category | Evidence to obtain | Gate |
|---|---|---|
| Source rights | Ownership, lawful use/distribution, file SHA-256, immutable backup and safe allowed file inventory | No unknown customer archive is examined or executed without permission |
| Route inventory | Static FastAPI methods, paths, mount resolution, unresolved declarations, version and dependencies | Static AST is only a hint, not actual response proof |
| List | Owner-chosen same-origin GET path, array field, stable ID, displayed title/category/status, malformed/empty list handling | No inferred field mappings |
| Metrics | Approved GET path, exact total/completed/pending field names and numeric semantics | Compare to real response only after runtime approval |
| Detail | Approved GET path with encoded ID parameter, response shape and 404/403/5xx handling | Preserve inspector-only failure and no data leaks |
| Auth | Same-origin session/identity model, 401/403 behavior, token/cookie policy, data access scope and CSP | Never embed secrets in frontend JS or store customer tokens in Git |
| Data and licensing | PII minimization, no copied reference site HTML/scripts/media, API data ownership and redistribution rights | Unknown rights or secrets stop release |
| Isolation/Windows | Specific trusted image digest/source/license, egress deny, CPU/RAM/PID limits, no host mounts, timeouts, logs, rollback, Windows ACL/AV | Execution, Docker and physical Windows checks need separate approval |

## Synthetic fixture (not a customer contract)
Self-authored tests use GET /api/jobs returning an items array of id/name/category/status; GET /api/metrics returning total/completed/pending; GET /api/jobs/{job_id} returning matching object or HTTP 404. tests_static_fixture.py explicitly maps list.field=items and metrics/detail.field=__root__. These are examples only.

## Stage gates
1. STATIC READY: Explicit owner rights and source SHA; bounded read-only inspection and confirmed GET role mappings. No arbitrary ZIP code runs. Not yet satisfied for customer data.
2. SANDBOX READY: Separate user consent to process/run the exact customer source; dependency/image/egress/resource policies, no secrets, isolated runtime and exact auth/JSON evidence. NOT_RUN.
3. WINDOWS / PRODUCT ACCEPTANCE: Physical Windows validation (browser, path, ACL, AV), independent design licensing, rollback, schema/authorization errors and deployment checks. NOT_RUN.
4. COMMERCIAL RELEASE: Owner acceptance after security and policy review. Current RELEASE HOLD.

NEXT READY: Continue synthetic fixtures and static preparations only. The optional Astra module skipped in CI is not verified; no blind merge of unrelated Astra source. Do not request unnecessary user work now.
