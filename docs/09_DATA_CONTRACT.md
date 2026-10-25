# 09 — Interface contracts (DRAFT v0.1; D2-01 review-only adapter implemented)

Fable analysis output is untrusted data. REA adapter creates a reviewable observation draft. ASTRA cannot treat unverified site schema as customer-owned data. This schema is a proposal awaiting tests and versioning.

### Example adapter envelope
    {
      "schema_version": "rea.observation.v0.1",
      "source": {"engine":"fable51", "commit":"bbe72c0...", "authorized_scope":"public_page_only"},
      "observations": [
        {"id":"obs_001", "kind":"ui_control", "operation":"filter",
         "certainty":"observed", "evidence_ref":"redacted:step-001",
         "description":"Category selection changes the visible list"}
      ],
      "api_candidates": [
        {"method":"GET", "path_template":"/api/items",
         "certainty":"inferred", "response_shape_only":true}
      ],
      "unknowns":["actual_backend_code", "business_formula", "owner_db_mapping"],
      "approved_semantic_bindings": [],
      "generation_allowed": false
    }

### Required transformations
Fable static/runtime/record evidence can propose evidence links and structures. Additional observation provenance must be supplied for 'observed'; technology heuristic remains 'inferred'. Unknown stays unknown. Private origins, auth tokens and exact sensitive query values cannot be serialized.
Astra functional candidate IDs map to supported operation list; unknowns and mismatched aggregations trigger REVIEW_REQUIRED.
Client schema declaration only comes from an actual customer-owned sample and explicit human approval, never guessed from reference URL. Mapping approval is bound to checksum of customer schema and functional spec, not only field names.

### State gates
ANALYSIS_ONLY → SYNTHETIC_PREVIEW (safe fake data).
SYNTHETIC_PREVIEW → OWNER_APPROVED_GENERATION only after source rights, local output folder, schema/semantics and feature scope approved. No automatic transition to production deploy.

### Constraints
No code generation from unvalidated arbitrary prompt. No private service calls, write API or schema alterations in draft mode. Enforce predictable file outputs and no existing-folder overwrites.

## Implemented narrow bridge (2026-10-25)
D2-01 `fda96076de33ebf4f4b6118972a5033a3f703ba9` implements Fable 1.0 → optional Astra `ObservationBundle` / `FunctionalSpecDraft` via actual pinned Astra validators. See `docs/19_FABLE_ASTRA_ADAPTER.md` on the feature branch; pending Draft PR #4. Static/runtime findings only emit redacted counts, not fabricated UI observations. Record user-action markers emit **inferred** hypotheses with unresolved effects, never `observed`. If no eligible UI markers, the ASTRA bundle and spec are null. Only Astra-validated mode emits a spec; local preview marks validation NOT_RUN. All paths remain review gated; full target envelope/schema and mapping state machine are not implemented.

## D2-02 optional Fable review -> independent CSV app proof (2026-10-25)
Feature `feature/orchestrator` @ `46060b4665560922d0c9cf82b9e5c08971eb9427`; [CI 40200704855](https://github.com/hibi89/REA_Web/actions/runs/40200704855): 55 pytest and real Chromium PASS. `rea/orchestrator.py` requires owner CSV and accepts an optional **existing** redacted Fable result; outputs a local app sourced **only from CSV**, and a separate `review/fable_review.json` if reference provided. Astra validation is mandatory in Fable mode; no validation fallback or automatic observed UI assertions. Manifest states `generation_input=customer_supplied_csv_only`, `semantic_mapping_status=not_approved`. Reference review remains `REVIEW_REQUIRED`, not served by generated FastAPI; original Fable JSON not copied. This is an implemented narrow bridge, not the entire original design wizard/owner mapping-approval UX.
