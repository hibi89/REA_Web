# REA_WEB Fable reference + owner backend ZIP → original dashboard source (2026-11-01)

## Verified source and exact CI (2026-11-01 22:56 KST)
- Functional SHA `f2d54b231b8b40c0023d23df0ef3260c1b241e8a`. Windows/Ubuntu [#41313444046](https://github.com/hibi89/REA_Web/actions/runs/41313444046): each 62 passed, 2 skipped optional Astra checks, 1 expected duplicate-entry ZIP warning. Real Chromium→local synthetic FastAPI HTTP same-origin, KPI, filtering, detail, and forced 503 API-error status passed.
- Existing backend/Fable tests [#41313444122](https://github.com/hibi89/REA_Web/actions/runs/41313444122): Windows+Ubuntu 52 passed / 2 skipped each. No untrusted owner ZIP code was executed.
- The dashboard's indicator remains neutral until GET success and switches to ERROR on failed fetch; CSP unchanged (no `unsafe-eval`). Physical owner's Windows browser and arbitrary customer ZIP not verified.

## What this code actually does

`rea/adapter/frontend_bridge.py` joins (1) a Fable 5.1 `result.json` and (2) the **separately scanned** static FastAPI backend ZIP contract `rea.backend_contract.v0.1`. It preserves evidence boundaries: Fable static reports contain no verified original-site layout/palette, so the generated dashboard uses original REA styling, **not a copied website design**. Private reference URLs, query strings and secrets are removed from outputs. No reference website API is called and no untrusted ZIP is imported, extracted, run, deployed or modified.

The first supported frontend is an **explicitly bound, read-only jobs dashboard** with three GET roles (`list`, `metrics`, `detail`). Backend response shapes, authentication, and real runtime compatibility remain unverified until an isolated HTTP/browser test. A user-confirmed route and response field binding is required; static declarations alone never authorize a generated frontend.

## S2/S3 example

```powershell
python -m rea.adapter.backend_zip OWNER_BACKEND.zip --out backend-contract-NEW.json
python -m rea.adapter.frontend_bridge --fable fable-result.json --backend backend-contract-NEW.json --bindings owner-bindings.json
python -m rea.adapter.frontend_bridge --fable fable-result.json --backend backend-contract-NEW.json --bindings owner-bindings.json --out OUTPUT_NEW --owner-confirmed
```

The second command is **review-only**. The third command outputs a source directory on explicit `--owner-confirmed`; it does not start the backend. An example explicit mapping, valid only for the independently authored test FastAPI fixture:

```json
{
  "list": {"path":"/api/jobs", "field":"items"},
  "metrics": {"path":"/api/metrics", "field":"__root__"},
  "detail": {"path":"/api/jobs/{job_id}", "field":"__root__"}
}
```

The dashboard is served under `/dashboard/` **on the same origin as the owner's real `/api/*` paths**, so there is no automatic CORS relaxation. It uses CSP `connect-src 'self'`, no third-party scripts, DOM `textContent` instead of HTML interpolation, `no-store` reads, and no POST/side effects. Frontend generator uses existing `rea.safe_publish.publish_directory` to publish a fully staged output atomically without overwriting existing paths.

The frontend is **not** a self-contained backend ZIP or a Windows EXE. Real owner backend integration requires separate API shape/auth review and isolated execution approval. Do not use this synthetic mapping to run or approve arbitrary owner ZIPs.

## Tests and limitations

- Python unit tests: `python -m pytest -q tests/test_frontend_bridge.py`
- Real browser+same-origin HTTP integration on GitHub Windows/Linux: `python -m pytest -q tests/test_frontend_bridge_browser.py` (requires `fastapi`, `uvicorn`, `playwright`, installed Chromium). **Only the hardcoded synthetic FastAPI fixture in the test is executed.**
- Local browser in restricted environment: direct `127.0.0.1` browser navigation was blocked by administrator; the unit tests and an offline Chromium synthetic-reply preview passed. Do not conflate this with GitHub's separate real browser HTTP verification.
- Fable 5.1 runtime screenshot/layout extraction, arbitrary API response inference, arbitrary frameworks, security/rights reviews, backend+frontend runnable ZIP packaging, actual owner Windows acceptance, and production deployment **NOT DONE**.
