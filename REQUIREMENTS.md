# REA_WEB — product requirements (owner-confirmed 2026-11-01)

## Core product, replacing the mistaken fixed-template interpretation
**Input A — a reference URL:** Fable 5.1 observes *public* site frontend appearance and accessible integration evidence; extract original-style design cues/layout/component composition and supported interaction **patterns**, not third-party private backend source, authentication, data, images, or protected UI assets.

**Input B — the owner's backend/logic ZIP:** Contains existing Python or Node API implementation, business logic and configuration the owner is authorized to use. Inspect without executing untrusted code; identify framework, static API declarations, modules, input schemas, runtime requirements, and readiness gaps. Do not assume a ZIP is complete or operational.

**Output:** Independently implemented frontend dashboard matching the high-level **design intent**, connected via documented/adapted interfaces to **the owner's existing backend logic**, not to the referenced website's private APIs. Generated source, verified local preview/HTTP/browser evidence, clear user-approved mappings, and an executable bundled source ZIP.

## Guardrails
- Never blindly clone copyrighted code, graphics or site branding, nor infer/claim private API schemas from public HTML headers.
- Original backend remains immutable; generated output and test sandboxes separate. No arbitrary uploaded code execution before authorized isolated verification.
- ZIP path traversal, symlinks, bombs, secrets, command injection, malicious files, SSRF and unsafe networks need defenses in each respective stage.
- API mapping and nontrivial inferred functional behaviors require explicit owner review; readonly source detection is never `APPROVED`.
- Upstream Fable/Astra, existing REA Pro CSV/JSON local app, REA Lite HTML demos are preserved as historical independent features; none is to be represented as the target final REA_WEB product.
- No external delivery/deployment/public sale or customer asset upload without owner authorization.

## Architecture choices and decision
- **A — extend existing REA_WEB**: lower cost and risk, uses existing Fable/Astra adapter, Pro FastAPI app generation, safe publish and tests. **Selected**.
- B — rewrite all components: better blank-slate uniformity but higher cost/time/compatibility risk. Not selected.
- Pipeline: reference Fable report → bounded sanitized design contract; backend ZIP → static endpoint contract → explicit mapping/review → generated original frontend → isolated runtime integration/browser tests → reproducible runnable ZIP.

## Current functional addendum (2026-11-01 23:34 KST)
- **S3 extended / CI PASS:** review-only bounded FastAPI AST route/request/response hints `rea.backend_schema.v0.1` matched to exact backend ZIP SHA. Explicit owner-selected JSON field names, KPI keys and one detail path variable now drive the generated UI; 99 PASS/2 SKIP on Windows and Linux real trusted FastAPI/Chromium CI. This is static schema and synthetic integration evidence, not arbitrary ZIP runtime validation, inferred owner approval or customer release.
- **S4 remains partial:** actual original owner ZIP runtime/OpenAPI/schema reconciliation, generalized composite source ZIP and Windows human acceptance remain NOT_DONE. No commercial/public deployment approved.

## S4 supplemental acceptance record (2026-11-01 23:58 KST)
- Synthetic trusted FastAPI OpenAPI supplied as bounded local JSON and reconciled with ZIP static route/schema artifacts at exact SHA; route/method/path/request/response field/type hints checked with fail-closed discrepancy reports. Functional SHA `538d3126aea0cf873da170bb1bf37ee8533848b9`. Windows+Linux Actions runtime #41318675062 each 43 PASS; frontend/browser #41318674988 each 99 PASS/2 SKIP. **This is declaration correspondence only**, without runtime origin attestation, representative payload/schema consistency, customer ZIP safe execution or owner approval.
- Next priority: isolated provenance validation, reviewed frontend gate, portable combined ZIP, owner Windows acceptance.

## Acceptance by stage (NOT all completed)
- **S1 DONE (2026-11-01):** source ZIP static FastAPI route declaration detection, malicious archive rejection, no code execution, cross-OS tests. `b140c034643b97584239f30691d4bb84c7f10ae0`; Windows+Linux Actions #41311814802 PASS. API signatures/response schemas/runtime not verified.
- **S2 SYNTHETIC VISUAL CAPTURE PASS (2026-11-01):** Fable origin/provenance review + bounded Chromium-computed layout/palette/component observations, origin-matched `rea.visual_reference.v0.1` and original CSS adaptation, Windows+Linux CI `4b3b658` 79 PASS/2 SKIP per OS. **Actual public URL capture/JS SPA fidelity/pixel similarity NOT VERIFIED**; Fable static JSON alone still contains no visual proof.
- **S3 SYNTHETIC BASELINE DONE (2026-11-01):** Exact declared FastAPI routes + explicit 3-GET owner fixture mapping → independent HTML/CSS/JS dashboard source, now including approved sanitized style hints from browser-observed reference. Arbitrary API response schemas, owner ZIP sandbox, and visual fidelity against real third-party sites NOT DONE.
- **S4 PARTIAL DONE (2026-11-01):** Trusted synthetic FastAPI backend real same-origin HTTP and generated frontend Chromium Windows/Linux CI (including failure-state UI) PASS on `f2d54b2`; SHA-verified **synthetic demo** ZIP generated. Arbitrary owner ZIP execution, combined user backend delivery packaging, physical Windows operator acceptance NOT DONE.
- **S5 HOLD:** rights/security/privacy/commercial approval and deployment where applicable.
