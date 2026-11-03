# REA_WEB — first-party FastAPI read-only paginated compatibility

Status: verified with project-owned rea/templates/app.py source and test-owned SQLite rows only; no customer source/runtime/rights proof. Commercial RELEASE HOLD.

## Observed first-party API semantics

- GET /api/items: total integer, items array; limit=1..100 (default 100), offset=0..100000. Previous adapter fetched only the first page, hiding additional rows.
- GET /api/summary: total_items and total_categories are actual numeric KPIs. The source does NOT supply completed/pending counts.
- GET /api/items/{item_id}: item detail fields id/title/category and attributes.
- GET / and GET /health also exist; they are non-API routes and must not poison the static API candidate review.

## Explicit owner bindings

Use the sample file samples/rea_firstparty_bindings.json for the original offline_compose CLI, or use samples/rea_firstparty_presentation.json with offline_wizard. These example mappings are valid only for that first-party response contract; do not automatically apply to another backend.

    python -m rea.adapter.offline_wizard --backend-zip OWNED_FIRSTPARTY.zip --fable fable.json --presentation samples/rea_firstparty_presentation.json --out NEW_FRONTEND --owner-authorized-source --paginated-list

The operator must personally choose /api/items as list, /api/summary as metrics, /api/items/{item_id} as detail, then enter list response field items, metrics response field __root__, pagination total field total, query parameters limit and offset, page_size 100, detail response field __root__, and type APPROVE after reading the mapping. CLI path numbers vary with exact ZIP and must never be assumed.

Only publish an independent five-file frontend after explicit approval. This does not run the ZIP, create backend DBs, infer hidden APIs, authorize login/session rights, inspect real customer data, or deploy a service.

## Actual native verification

- First-party feature SHA 6b82576662a4dbbdd89c7e5f4cff40c6af30bacf: GitHub Actions static ZIP 41639688394 Windows/Ubuntu 167 PASS/2 SKIP each; reviewed browser 41639688474 Windows/Ubuntu 149 PASS/2 SKIP each; existing clean ZIP/Chromium 41639688397 both 135 PASS. All jobs SUCCESS.
- Final wizard feature SHA d36afec39cb0d15d8dc6056dc307483c942cabda: static ZIP Actions 41640087374 Windows/Ubuntu each 167 PASS/2 SKIP; reviewed browser Actions 41640087406 Windows/Ubuntu each 153 PASS/2 SKIP; zero failures, all four jobs SUCCESS.
- tests/test_firstparty_adapter_browser.py uses EXACT repository-owned FastAPI source, a test-owned 130-row local SQLite database, headless Chromium, same-origin /dashboard GET, two pages (offset 0 and 100), search, detail and two authentic KPIs. The test app is explicitly launched from separately written first-party source; the static ZIP scanner never executes ZIP entries.
- tests/test_offline_wizard.py adds explicit --paginated-list CLI happy path and rejects invalid page_size, with no output on refusal.

## Remaining acceptance gate

1. Determine explicit legal scope/SHA of an owner-provided real backend ZIP, read-only GET paths and response semantics, authentication/same-origin/401/403 identity policy.
2. Run actual customer runtime or Docker/VM only after separate authorization and containment/egress/resource controls; do not send original sources, auth tokens or data to public CI.
3. Independently validate physical Windows operator run, original source/vendor rights, dependency redistribution notices, customer privacy/deletion, accepted product scope and commercial terms.

The page collector requires a stable integer total count at most 10000 and a finite number of id-distinct records; nonconforming responses fail rather than silently display fabricated data. Other custom backends require separately approved mappings.
