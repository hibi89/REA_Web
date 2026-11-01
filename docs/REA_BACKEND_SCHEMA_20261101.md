# REA_WEB — review-only backend schema hints and owner field bindings

## Purpose

For the owner-confirmed product **reference URL/Fable evidence + the owner's backend ZIP → independently created dashboard wired to the owner's APIs**, this milestone adds a typed **review hint** extracted from a local FastAPI ZIP and extends explicit UI field mappings. It does **not** execute any owner ZIP or assert that observed decorators are live APIs.

## Source/API contract sequence

```powershell
python -m rea.adapter.backend_zip .\backend.zip --out .\backend-contract-new.json
python -m rea.adapter.backend_schema .\backend.zip --out .\backend-schema-new.json
python -m rea.adapter.frontend_bridge --fable .\fable.json --backend .\backend-contract-new.json --schema .\backend-schema-new.json --bindings .\owner-mapping.json
```

To create a frontend only **after actual owner approval of routes and mappings**, append `--owner-confirmed --out .\dashboard-new`. The output folder must not already exist. It serves only original frontend source, *not* an executable copy of owner backend source. Never pass real production ZIPs to any test runner without a separately approved sandbox.

The schema review artifact is `rea.backend_schema.v0.1`, `REVIEW_REQUIRED`, `execution_performed:false`, `generation_allowed:false`, tied to exact `backend_sha256` recorded by the separate ZIP inspector. It recognizes in-file Pydantic `BaseModel` declarations (bounded field names, simple allowlisted type grammar, **no default values retained**), static function parameters and path placeholders, and FastAPI `response_model` or Python return annotations where statically known. Imported models, dynamic declarations, inferred runtime responses/auth, and actual JSON payload schema remain **unknown**. Note that `query_or_dependency` is only a hint, not a classification. Use trusted runtime OpenAPI checks in a later isolated stage.

Both source inspections reuse ZIP limits (25 MiB total archive, 20 MiB expanded, 1,000 entries, unsafe links/paths, CRC, compression bomb rules). They neither extract ZIP entries nor import source. Schema artifact validation checks both review status and SHA plus route line/source identity before joining into frontend review. Nothing is autoapproved.

## Nonstandard response field mapping

The old `list`, `metrics`, `detail` response root selection remains backward compatible. Optional, explicitly confirmed `presentation` makes frontend rendering **independent of data column names**. For example:

```json
{
  "list": {"path":"/api/tasks","field":"results"},
  "metrics": {"path":"/api/insights","field":"summary"},
  "detail": {"path":"/api/tasks/{ticket_id}","field":"result","path_param":"ticket_id"},
  "presentation": {
    "item": {"id":"ticket","name":"task","category":"department","status":"phase"},
    "metrics": {"total":"all_count","completed":"success_count","pending":"queued_count"},
    "detail_fields": ["ticket","task","department","phase"]
  }
}
```

`list`/`metrics` must be parameter-free GET declarations, and detail exactly one explicitly named safe path parameter. HTML uses `textContent`, no `innerHTML` or eval. Response fields are **owner claims**, not inferred truths: browser HTTP E2E must still confirm each shape, and API authorization/host routing needs separate review. Do not connect to public reference site's APIs.

## Verification command

```powershell
python -m pytest -q tests/test_backend_schema.py tests/test_generic_presentation.py tests/test_generic_presentation_browser.py tests/test_backend_zip.py tests/test_frontend_bridge.py tests/test_frontend_bridge_browser.py tests/test_visual_reference.py
```

`test_generic_presentation_browser.py` runs a **trusted invented FastAPI server** and actual Chromium local HTTP using nonstandard response fields and detail parameter. It needs installed FastAPI, Uvicorn, Playwright, and Chromium. Linux/Windows GitHub CI runs this with the pre-existing browser integration suite. Owner's actual backend ZIP, public URL browser capture, runtime inference and combined source ZIP remain outside this test and **not approved**.

## Next stage

Reconcile static annotation hints against trusted, isolated runtime OpenAPI with strict endpoint/field validation; only then consider a combined reproducible backend+UI delivery ZIP and Windows user acceptance. No main merge, upstream modification, live deployment, personal customer data, or commercial release is authorized here.
