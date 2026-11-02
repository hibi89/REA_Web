## 최신 사용자 선택 상세조회 우선 적용 — 2026-11-03 KST
- 생성된 REA 대시보드의 상세 패널은 동시에 진행되는 여러 읽기 전용 GET의 실제 완료 순서와 관계없이 **가장 최근에 선택된 작업 ID**의 성공 또는 실패 결과만 표시한다. 먼저 선택한 작업의 늦은 응답은 상세 내용을 덮어쓰거나 기존 연결 정상 상태를 `API ERROR`로 바꾸지 않아야 한다.
- 단조 증가 `detailGeneration`을 요청 시작 시 부여하고, 성공 화면 반영 직전 및 예외 화면 반영 전 모두 최신 선택 여부를 확인한다. 기존 리스트/API `loadGeneration`, JSON 제한, 접근 정책·정적 생성·참조 디자인과 분리 보존한다.
- 검증은 실제 Chromium의 지연된 A 성공→B 최신 성공, 지연된 B HTTP404 실패→A 최신 성공 두 역순 응답 시나리오를 포함한다. 수정 전 1 FAIL 재현, 수정 후 실험/재구성 회귀 22/22 PASS. 소스 Git blob `352654d0c19365ceb12f1dd4b362bae354c0a349`, 테스트 Git blob `9086239d15ec5aec7bbb415ce666e27d9e39d598`. 정확한 GitHub Windows/Linux 및 실제 HTTP/배포는 미검증, RELEASE HOLD.

## Latest-request-wins dashboard reload under overlapping GETs — 2026-11-03 KST
- Generated REA same-origin dashboard must never let an obsolete earlier `load()` success or error overwrite the state belonging to a later reload. Use a local monotonically increasing generation token to guard both render/cache/KPI updates and API failure badge/retry changes after asynchronous API calls settle, preserving existing 1 MiB JSON stream bound, 10-second timeout, owner-defined GET bindings, escaping, original styling and retry.
- Verify in real Chromium with a deliberate stalled API response and a newer quick success, then with stalled success and newer quick HTTP503 failure. The deterministic browser test must await settlement of the stale request before final assertions, not rely on arbitrary sleeps.
- Reproduced prior behavior with 1 failing browser regression and corrected with source commit `e7ca41ebfeac370c2d1733709127760283dd5d50` / Git blob `57678b2cbebf18e4bf57b6b2f59a2c3fce8d89a6`. Current exact new test blob `4fb4681e3400370463d9d7f13d0980c8d54079ee`; reconstructed local Linux Chromium 21/21 PASS after fix. Cross-OS exact GitHub Actions and actual networked production remain unverified; RELEASE HOLD.

## Real Chromium view of packaged reference-styled synthetic frontend — 2026-11-03 KST
- A synthetic-only regression must assemble an approved reference-styled dashboard ZIP and inspect the actual archive's HTML, CSS, JS and visual manifest, then execute the packed CSS/JS in real Chromium with an explicit in-page, local, GET-only fake response provider. It must confirm KPIs, rows, text filtering, detail, computed reference navigation/accent CSS and zero JS runtime failures.
- The browser sandbox prohibits navigation in this environment. The test must distinguish **in-memory script evaluation** from actual origin/CSP/HTTP network operation. Checking that the output HTML contains a CSP directive is not proof of browser CSP enforcement; intentionally stripping CSP in the *test-only* DOM must not change the generated artifact.
- `tests/test_styled_bundle_offline_browser.py` blob `c2b6088a68959e7c12a3a83bf6e616c8c3ae3d87`, local reconstructed Linux Python3.13 suite 20/20 PASS; latest Windows/Linux exact-source CI and real FastAPI HTTP browser E2E UNVERIFIED. Explicit customer program and Docker execution remain gated; commercial RELEASE HOLD.

## Captured-reference CSS identity before synthetic ZIP distribution — 2026-11-03 KST
- REA frontend output manifest must carry only normalized and SHA256-validated `visual_contract` when a reference CSS palette/layout is used; neutral output records null.
- Synthetic ZIP assembler must independently validate visual evidence origin, SHA256 and `BROWSER_COMPUTED_STYLE_OBSERVED` provenance and require exact reproduction of generated visual CSS (not merely an editable manifest hash). It must continue rejecting altered generator JavaScript, HTML, and neutral CSS. Edited/missing visual evidence must be rejected before any ZIP output.
- Existing styled manifests generated before this evidence field may require regeneration from separately retained authorized observation, not silent acceptance of unverifiable CSS. No reference page HTML/scripts/media or customer private content should be stored as evidence.
- GitHub generator source blob `f71d0805b361c066a81544795f6143997c04c2cd`, bundle source blob `3cc4cb4081f07daf8c287531f40fda214b203362`, test blob `17d4854e67a8150a9150cbb4f7276dfe88c86a3b`. Reconstructed local Python3.13 subset **19/19 PASS**; exact GitHub full regressions, Windows/Linux 3.11 and production **UNVERIFIED**; release HOLD.

## Generated frontend source identity at synthetic project ZIP boundary — 2026-11-03 KST
- `rea/adapter/project_bundle.py` MUST reject a frontend whose `app.js` differs byte-for-byte from the same REA generator `JS` constant with canonically validated confirmed bindings, even when `manifest.json` is edited to claim approval. MUST reject changed `index.html`; without a captured visual reference, MUST also reject changed neutral `style.css`. Preserve observed-reference style generation and separate design provenance review.
- This guards the **generator-to-bundle stage**, not a signed attestation, arbitrary customer ZIP execution, nor modification of output after extraction; the latter retains independent manual SHA checks. Functional commit `b22388a3`, four regression definitions `48bf5bd8`, isolated implementation-contract harness 5/5 PASS; full package/browser cross-OS CI **NOT VERIFIED**.

## Actual Chromium local offline replay acceptance — 2026-11-03 KST
- A deterministic synthetic `fetch` browser test must import the **actual generated frontend JS** constant, execute it in real Chromium, and verify KPI/list, search/detail, HTTP-error retry, 1MiB header and streaming refusal, HTML MIME refusal, malformed JSON, 10-second timeout and read-only GET+AbortSignal. It must clearly declare mocked HTTP: do not equate `page.set_content` or `fetch` interception with networked FastAPI/E2E/production tests.
- `tests/test_frontend_bridge_offline_browser.py` source Git blob `95023596948609a225ba37c0ea01fc4d49ab3d9c` locally Python3.13/Chromium **1 PASS, 9 functional groups**, zero page JS errors, original frontend JS byte-length/hash parity verified. Separate real Chromium localhost navigation is administrator-blocked; corresponding cross-OS CI latest SHA is not verified. No change to authorization gates, Docker/customer ZIP execution or Pro/Lite.

## Dashboard read-only GET resilience — 2026-11-03 KST
- All generated dashboard API JSON GETs must reject non-JSON MIME, abort after 10 seconds, enforce a **1 MiB limit while streaming** (not after whole-response buffering) and refuse oversized Content-Length before body reads.
- A visible `API 다시 연결` retry must be available after API errors without full reload. On success, stale error text/failed badge must be cleared and KPIs/list restored. Owner-approved API paths, same-origin CSP, GET-only behavior and backend provenance controls remain unchanged.
- Functional SHA `d5b432277a0961d6c6d3e645230b9d748afb787e`, E2E test-definition SHA `b365e0e8ef35480fd8958ff8aaca708636237248`; local Node guard 6 PASS and extracted GitHub generated JS mock-DOM 5 PASS, but updated Chromium/Windows/Linux CI **NOT VERIFIED**. No production/sale or owner ZIP authorization.

## Bounded browser GET responses + same-page retry — 2026-11-03 KST
- Independently generated same-origin REA dashboard must require a JSON MIME response, cap each JSON payload at **1 MiB while reading** (including Content-Length preflight), and abort stalled fetches after **10 seconds**. HTTP/API errors, malformed JSON and oversized content must fail into an explicit UI error.
- Display a user-operated in-page retry after an error. A successful retry must clear the error, hide the retry control, remove failed connection styling, and restore the live KPIs/list. No auto-POST, cross-origin API, source ZIP execution, customer upload or implicit owner approval.
- Source functional SHA `d5b432277a0961d6c6d3e645230b9d748afb787e`, Chromium regression definition SHA `b365e0e8ef35480fd8958ff8aaca708636237248`. Local 6 Node fetch-guard synthetic cases PASS + 5 exact-GitHub-JS mock DOM integration states PASS; full FastAPI/Chromium CI at exact new SHA **NOT VERIFIED**. Existing Pro/Lite untouched; commercial RELEASE HOLD.

## Strict image evidence JSON parsing — 2026-11-03 KST
- The offline Docker image evidence verifier MUST reject duplicate JSON object keys at all nesting levels and nonstandard numeric tokens `NaN`, `Infinity`, `-Infinity` in manifest, artifact descriptors, wheel lock, and SPDX content, even if all independent SHA-256 values match. File integrity is not equivalent to unambiguous JSON semantics.
- Preserve existing strict caps, signature/image nonauthorization, read-only behavior, no-overwrite and Pro/Lite separation. No format-breaking canonicalization or external runtime introduced.
- Functional source `5caa6687`, tests exact locally checked blob `93c6f86891d799d4b928a880afc5faf67abe37b7`, functional branch checkpoint `983a79d358cf60ac44ec8d47eb847feefd645ea1`. Local Linux Python3.13 **25/25 PASS** (18 baseline + 7 new), remote Windows/Linux exact-commit CI **NOT VERIFIED**. Real image/container/customer ZIP and commercial release remain HOLD.

## Image evidence fail-closed parsing addendum — 2026-11-02 KST
- `rea/adapter/docker_image_evidence.py`: image reference path segments must be canonical, maximum 256 characters, allow only digest-pinned references; disallow `..`, hidden path segments and empty components. Wheel list <=512 and SPDX inventory <=4096; reject all duplicate normalized SPDX package identities. Deeply nested invalid JSON must fail as typed `UnsafeEvidence`, not crash the scanner. No change to `rea.docker_image_evidence.v0.1` review-only nonauthorization semantics.
- Linux Python3.13 exact mirrored source/test **18/18 local pytest PASS**, 0 FAIL, 0 SKIP. Source `ff1d1c07`, test `7a3d2c59`, blob hash parity with GitHub confirmed. Windows/Ubuntu new CI not verified; actual Docker engine, image signing, licenses and client ZIP remain HOLD.

## Docker image evidence local review-only gate — 2026-11-02 KST
- Source `rea/adapter/docker_image_evidence.py` with offline contract `rea.docker_image_evidence.v0.1` cross-checks independently SHA-bound manifest and six local file artifacts, rejects path escapes/symlinks/duplicates/oversize, requires pinned hash-backed FastAPI/Uvicorn wheels and matching SPDX package name/version inventory. CLI never overwrites an output and must not execute Docker/registry or customer ZIP.
- A structurally complete evidence set must ALWAYS return `EVIDENCE_INVENTORY_REVIEW_REQUIRED` with signature cryptographic verification, full closure, license rights, independently reviewed CVEs, actual engine isolation and all runtime/release approval booleans FALSE. Self-asserted receipts/licenses/SBOM are not independent verification. Actual image signature/SBOM, license and Docker daemon/container validation require separate approval.
- Local synthetic Python3.13 `10 PASS / 0 FAIL`, source/test file Git Blob SHA equal to GitHub. Windows/Linux exact-SHA CI not verified. Retain RELEASE HOLD, 74%/26%.

## Docker CLI preflight/cleanup output cap and approval gate — 2026-11-02 KST
- Source/test branch commits `8936cd4e5083ca7f5dda47b289ef066a960d6815` / `62f6752dc1effa3984d9235161d0fced5f38ebee`: output from **every** Docker CLI process (not only `run`) must be live-bounded: 4KiB/stream for local read-only image/server inspection and cleanup, 8KiB/stream for `run`. On cleanup overflow, never claim verified removal. Added negative tests; exact new CI status is **UNVERIFIED**.
- Image provenance/approval remains an **external cryptographic and license decision**, not satisfied by matching local RepoDigests. Require immutable derived digest, signed/verifiable builder identity, pinned hashed dependency lock, SBOM/license and actual real-engine synthetic isolation evidence before owner approval. See `docs/REA_DOCKER_IMAGE_REVIEW_20261102.md`. No pull/build/run, permission changes or customer ZIP execution; RELEASE HOLD.

## Docker subprocess output flood protection addendum — 2026-11-02 KST
- `6dd99240cd9273715242b7cba8a8ebd380ba0559`: Docker **run** CLI stdout and stderr must each be bounded to 8KiB **during execution**, not only checked after subprocess exit. A stream flood must kill CLI and refuse, then force-remove named container, verify daemon absence and delete synthetic mount. Timeout must not create host fallback. [Cross-OS CI #41330437617](https://github.com/hibi89/REA_Web/actions/runs/41330437617): Windows and Ubuntu **100 PASS each**, with real trusted synthetic child process output/timeout and Docker mock cleanups.
- This does not attest real container enforcement, signed image, owner code or external site integration. `docker version`/`image inspect` still use <=7s CLI timeout and post-run size validation; runtime is HOLD until actual approved Docker/VM verification.

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
