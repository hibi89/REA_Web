## S4 Docker and ZIP bounded preflight — 2026-11-02 KST
- Functional SHA `00b86b0442eb07795bd0f33e645471e7c3d59331` requires ZIP declared per-member size cap, types and names be validated **before** CRC inflation; exact archive SHA, clean extraction SHA and approved frontend mapping remain. Docker synthetic runner now requires local Linux daemon OS/arch (amd64/arm64), locally present `image@sha256` RepoDigests and matching local image Linux architecture before any run. Test evidence [Windows+Ubuntu #41329152957](https://github.com/hibi89/REA_Web/actions/runs/41329152957): **94 PASS each**.
- Docker CLI compatibility tests are simulated, not real sandbox or image signature/provenance. No unreviewed image pulls, Docker daemon modifications or arbitrary owner ZIP. Customer data, reference-site private assets and commercial rollout remain HOLD.

## Docker synthetic non-root staging addendum — 2026-11-02 KST
- `8901f6acc1aed611bc045d46c5872fe81d4d4483` changes Docker bind source to an ephemeral synthetic-only mount tree from exact independently hashed ZIP bytes, with final post-stage checksum/manifest/frontend binding verification. Original extracted directory permissions are preserved; staged temp directory is made 0755/0644 for container UID65534 and always removed. [Windows+Ubuntu CI #41328474922](https://github.com/hibi89/REA_Web/actions/runs/41328474922) **87 PASS each**.
- This staging **intentionally allows other local host users to read synthetic files temporarily** and does not satisfy private code protection for customer ZIPs. No customer execution, actual Docker engine security validation, signed image acceptance, real reference fidelity or commercial GO.

## S4 Docker security addendum — 2026-11-02 KST
- Current Docker-specific source `e496f0e7b8d65d0b499bcface6e89f62b70d6cf3`: explicit builtin seccomp, nonroot+read-only+network-none+cap/resource/time/cleanup Docker command, strict receipt allowlist and independent source archive digest; synthetic embedded in-container script directly tested on trusted Windows/Linux hosts against real localhost FastAPI. Windows and Linux CI 83 PASS each [run #41327525151](https://github.com/hibi89/REA_Web/actions/runs/41327525151).
- This does **not** attest any actual Docker daemon containment, kernel enforcement, approved/signature-verified image origin or arbitrary customer ZIP safety. Actual Docker image is unapproved/missing; owner ZIP automatic execution and release HOLD. Only explicit separately authorized customer work in an independently verified protected sandbox could extend scope.

## S4 synthetic process challenge verification (2026-11-02 KST)
- Functional SHA `2f98be1da225f7309410ea2b81e1b69f71961457`: exact trusted synthetic ZIP source and extracted inventory checked, then managed localhost FastAPI child confirms a per-launch challenge, child PID, and embedded backend source SHA before read-only API payload probing. Local 50 PASS; Windows/Linux [GitHub Actions #41325578504](https://github.com/hibi89/REA_Web/actions/runs/41325578504) 51 PASS each, and prior frontend/ZIP regression CI both SUCCESS. Child stopped after probe. Only a **trusted-host synthetic process challenge**, not kernel process isolation, general customer ZIP sandbox, actual external design quality or commercial release authorization.
- Next: actual container/VM isolation and signed runtime/source provenance with privileges, egress, timeout/pids/memory bounds and owner-approved scope before any customer ZIP can be executed. See `docs/REA_SUPERVISED_SYNTHETIC_RUNTIME_20261102.md`.

## S4 additional acceptance — read-only trusted fixture behavior probe (2026-11-02 KST)
- On source SHA `a42d742033b42e464ba71419186ee4d0acc2ee5e`, bound source ZIP SHA256 and exact clean extracted package file bytes to approved local GET list/metrics/detail/error behavior. Safe fail-closed checks for response type, shape, size, status, redirects, mapped fields and integrity, with no user data in report. [GitHub Actions #41324157939](https://github.com/hibi89/REA_Web/actions/runs/41324157939) Windows+Linux 36 PASS each including Chromium/real trusted synthetic FastAPI HTTP.
- Only SELF-AUTHORED SYNTHETIC profile permitted. File identity verified but runtime process provenance explicitly NOT attested. Full arbitrary owner ZIP isolation, real public site fidelity, authentic customer workflows and commercial GO remain NOT DONE/HOLD.

## S4 synthetic combined ZIP acceptance (2026-11-02 KST)
- Reproducible, explicit-developer-authorized **self-authored synthetic FastAPI** source + independently generated frontend ZIP `rea.project_bundle.v0.1` now exists on functional SHA `b6f82d41a6a2200641d8fca7ea3c4e3a2c83600a` and is verified after clean extraction with real localhost HTTP + Windows/Linux Chromium **15 PASS each** [Actions #41321384964](https://github.com/hibi89/REA_Web/actions/runs/41321384964). Output contains SHA256SUMS, manifest and local-only launcher; owner ZIP and frontend review provenance are SHA checked, no unapproved file copying or code execution at build time.
- Scope remains **trusted synthetic profile only**, not an arbitrary customer backend runtime adapter. External public URL fidelity, real customer ZIP provenance, credentials/auth, native owner Windows acceptance and commercial approval remain NOT_DONE/HOLD.

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
