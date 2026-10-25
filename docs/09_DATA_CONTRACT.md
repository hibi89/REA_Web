# 09 — Interface contracts (DRAFT v0.1, not implemented)

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
