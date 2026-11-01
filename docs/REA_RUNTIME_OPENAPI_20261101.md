# REA_WEB S4 — static ZIP route vs supplied runtime OpenAPI reconciliation

## Scope / evidence
- Source: `rea/adapter/runtime_contract.py` and `tests/test_runtime_contract.py`.
- Inputs: `rea.backend_contract.v0.1`, `rea.backend_schema.v0.1`, and a **separately obtained** OpenAPI 3.0 or 3.1 JSON. All must be trusted according to their own origin and owner authorization.
- **No backend ZIP execution, imports, extraction, network requests, or OpenAPI download** by this component. The caller must obtain runtime evidence inside a trusted, approved sandbox. Never auto-run arbitrary uploaded user ZIPs.
- Requires identical original ZIP SHA256 for both static input artifacts. Checks bounded declared route/method, router mount hint, path variables, Pydantic body field declarations, response model field declarations, primitive field types and required-field hints against OpenAPI structure. Differences produce `MISMATCH` and exit code 3; invalid or unsafe inputs exit 2.
- The report excludes OpenAPI `servers`, descriptions, examples, secret literals and actual response values. It is an **unattested comparison**: `runtime_origin_attested=false`, `generation_allowed=false`. Identical declarations do **not** prove runtime matches original ZIP, endpoint auth, business logic, JSON response payload, or API safety.

## Usage

```powershell
python -m rea.adapter.backend_zip owner-authorized.zip --out static-contract.json
python -m rea.adapter.backend_schema owner-authorized.zip --out static-schema.json
# First obtain openapi.json from an independently trusted, isolated local test instance.
python -m rea.adapter.runtime_contract --backend static-contract.json --schema static-schema.json --openapi openapi.json --out NEW-runtime-review.json
```

`NEW-runtime-review.json` must not exist; the command does not overwrite anything. No URLs accepted for `--openapi`; no unknown backend execution occurs.

## Test evidence and limits

`python -m pytest -q tests/test_runtime_contract.py` covers 15 synthetic cases including trusted FastAPI `TestClient` `/openapi.json`, matching declared paths, missing runtime operations/methods, path variables, missing and mistyped request/response fields, static ZIP SHA mismatch, unmounted router, secret-leak prevention, invalid input, CLI mismatch/no overwrite. The ZIP used by this test is hand-authored synthetic source, **not** automatically executed by the reconciliation component.

## Next

Approved sandbox runtime provenance with reproducible source SHA and safe extraction/allowlisted dependencies; then generation-time API review gating and deterministic, complete bundled backend+frontend deliverable. Real customer ZIP and Windows operator validation remain NOT_RUN; production/release HOLD.
