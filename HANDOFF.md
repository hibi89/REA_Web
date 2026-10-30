## REA_Web checkpoint — strict ZIP manifest + customer checker — 2026-10-30 KST

- **Code checkpoint:** `7fb2e460bf4aa55abcfdb7d84c3ad33f94ab232a` on `feature/d27-windows-python-discovery`; PR #30 OPEN/DRAFT/UNMERGED. Changes are substantive executable code, not documentation-only.
- `rea/delivery.py`: ZIP `delivery_manifest.json` limited to 256 KiB; duplicate JSON object keys, NaN/Infinity, malformed UTF-8/JSON, invalid integer-size metadata including bool, and JSON nesting beyond 64 levels are rejected with bounded DeliveryError. Existing 100-member/25MiB total limits and SHA checks remain.
- `rea/provenance.py`: generated internal app/schema/mapping/append/review JSON also rejects nonfinite constants and nesting beyond 64 levels, in addition to prior type/duplicate-key checks. One shared `_json_depth_exceeds` in delivery is imported at runtime; no new dependency.
- Shipped standalone `rea/customer_self_check.py`: extracted delivery manifest now rejects duplicate keys, nonfinite constants and >64-level nesting; catches RecursionError for safe FAIL_LOCAL_PREREQUISITES rather than traceback. Existing bounded manifest/streaming integrity checks retained.
- Tests committed: `tests/test_delivery_manifest_strict.py` **17 pytest cases**, expanded `tests/test_provenance_malformed_metadata.py` by **8 cases**, expanded `tests/test_delivery_publication_guards.py` by **5 cases**. These three latest test updates are NOT run as a full, unmocked checkout.
- **Executed focused isolated Python 3.13:** 17/17 ZIP manifest tests + 13/13 generated JSON parser tests = **30 PASS** (functions independently verified against source checksums). Another isolated focused run covering prior sale/ZIP tests and extracted customer manifest = **75 PASS**. SHA/checksum equality matched 5 main ZIP functions, 3 provenance JSON parser functions, and 4 customer-parser/inspect functions. These are separate isolated test scopes and must NOT be described as full original-repo regression, native Windows E2E or consumer signoff.
- **Important reproduced failure and fix:** initial depth test saw **1 failure** because this Python runtime accepted 1,500 nested arrays. Replaced implicit parser RecursionError expectation with explicit 64-level cap and re-ran: 17/17 PASS. Do not claim the code was correct before this fix.
- **CI handling:** Initial exact-head GitHub Actions first-page 28 PR-triggered runs all QUEUED, with no conclusion. Skip CI waiting; inspect only after actual completions. No latest-code CI PASS claim.
- **Scope and gating:** customer-authorized CSV/flat JSON → approved mapping → local read-only FastAPI/SQLite + offline Windows ZIP, optional same-schema ROW APPEND only. No hosted Vercel URL or customer production deployment. Qualitative old development 95% / sale preparation 77% remain estimates, not remeasured. Independent Windows human acceptance, source/dependency redistribution rights, customer privacy/data handling, seller terms and timed manual delivery remain **NOT_RUN/NOT_GRANTED/NOT_APPROVED**. NOT APPROVED FOR SALE.
- **Next:** on genuine checkout run new strict JSON tests, existing full regression and generated ZIP Windows CMD+localhost+Chromium; fix actual failures. No merge, force push or artificial approval.

---

## 2026-10-30 — REA_Web semantic release gating checkpoint

- **Code checkpoint** `323013c2235884537389282045f7ed22437540b5`, feature branch `feature/d27-windows-python-discovery`, PR #30 OPEN/DRAFT/UNMERGED. Previous safety work retained.
- **Main change:** `rea/provenance.inspect_delivery` now refuses non-object, malformed UTF-8 and duplicate-key generated JSON documents (app manifest, schema preview, mapping receipt, two-file append receipt, optional Fable review) with bounded `AuditError`, and validates owner mapping fields before set/value operations. Rehashed ZIP contents no longer bypass semantic document-shape checks.
- **Publication integration:** `rea.delivery.create_delivery` now requires full `inspect_delivery(stage)` semantic allowlist/receipt audit AFTER ZIP integrity verification and BEFORE atomic publication, analogous to existing two-source ZIP handling. Stale approved source is rejected before creating destination parent. Existing source SHA is rechecked before publish; original owner files are not modified.
- **New/expanded regression:** `tests/test_provenance_malformed_metadata.py` contributes 15 parametrized synthetic ZIP cases covering malformed JSON, duplicate metadata keys, wrong input-kind type, mapping field types, two-source malformed receipt and clean-baseline acceptance; `tests/test_delivery_publication_guards.py` adds semantic-audit non-publication and valid semantic audit tests plus no destination parent on stale approval. Tests **committed, not executed on original checkout** in this session; no synthetic test PASS claimed for them.
- **File checkpoint:** `rea/provenance.py` Git blob a21a989ac6d9dc383978ec893c7f5da93246dc6b; `rea/delivery.py` Git blob 43722783b5d79f782fa6c8fdb41e57c6861f0885; `tests/test_provenance_malformed_metadata.py` Git blob e135f52ff7c31c1ec15b9485ed2aea7112b91a5f; `tests/test_delivery_publication_guards.py` Git blob 8e906f9bf7df06e3f339132f09880ad812480613. Test/commit identifiers point to source, not proof of execution.
- **CI policy:** Do not block on queued GitHub Actions; inspect D27 Windows/Linux/Chromium and D31 security after runners produce results. Do not infer latest-code PASS from old CI. Prior isolated tests do not establish full Windows E2E.
- **Scope:** customer-authorized CSV/flat JSON; explicit field mapping and consent; optional same-schema two-file ROW APPEND; local read-only FastAPI/SQLite Windows ZIP. No scraping, different-schema JOIN, auth/payments or hosting. No Vercel project/production deployment.
- **Commercial gates:** Independent nondeveloper Windows acceptance NOT_RUN; source redistribution and dependency/license notice clearance NOT_GRANTED; data/privacy handling and seller terms NOT_APPROVED; human-timed delivery rehearsal NOT_RUN. Historical qualitative 95% engineering / 77% seller prep not remeasured. **NOT APPROVED FOR SALE.**
- **Next priority:** Run exact-checkout synthetic ZIP proof for single CSV, JSON, approved mapping, same-schema append and corrupted metadata; execute Windows CMD+localhost+browser once a runner is available; only repair reproduced failures. No merge or force-push.

---

## REA_Web production-path hardening — 2026-10-30 KST

- Feature branch: feature/d27-windows-python-discovery; PR #30 remains draft and unmerged. Code/test checkpoint **cc894dfd459f1dea55c05c6963bb8f4558a71d67**.
- Actual work, not CI waiting: (1) `rea.delivery.create_delivery` now SHA-pins the customer-owned CSV/flat JSON source before building and rechecks it after archive verification but BEFORE atomic ZIP publication; source mutation must leave no new ZIP. An explicit preflight source SHA mismatch also aborts before build. (2) Shipped stdlib-only `rea.customer_self_check` now caps manifest bytes to 256 KiB, inventory to 100 members and total described file bytes to 25 MiB, validates per-member size and SHA-256 format, and hashes extracted files in 64-KiB chunks instead of unbounded `Path.read_bytes()`.
- New `tests/test_delivery_publication_guards.py`: 8 test functions / 13 pytest cases covering clean extracted SQLite, chunked checksum, oversized manifest, six malformed metadata variants, changed source before publish, stale approved source before build and no overwrite of existing private ZIP. These tests are COMMITTED; the entire original-repository new test module is **NOT_RUN** here. Do not claim 13/13 passing.
- Independent isolated Python 3.13 smoke on exact-matching checker source excerpts: synthetic ZIP verification PASS; extracted manifest SHA PASS; read-only SQLite row count 4 PASS; unknown extracted file rejected PASS; oversized manifest rejected PASS; 101 inventory rejected PASS; 70KB chunked SHA PASS. `inspect` and `_member_sha256_bounded` excerpts independently matched connected GitHub on normalized function Adler32: 42be1972 and e584c915. This is focused isolated code/excerpt verification, NOT actual product ZIP/Windows customer E2E or native app launch.
- GitHub blob IDs: checker c9eb3bf24ba9be8313a926a0879aa2a96132e2e2, exporter 4b281f19c560abfc5aad339ca8f2ce0df2f9af83, test f3751b64eb090c1ca3f398b278adb1b7a6c69ab8. Previous bounded source fingerprint (mvp/guided/two_source) and Windows collision hardening remain.
- CI rule: pending/queued workflows are NON-BLOCKING; do not wait/poll repeatedly. At later natural checkpoint, use exact HEAD D27 Windows/Linux/full pytest, D3 browser and D31 audit outcomes; investigate only actual job failures.
- Status: offline Windows ZIP, Vercel N/A. Historical development ~95%, sales prep ~77% qualitative estimates unchanged (not recalibrated); **sale NOT APPROVED**. Six real-world gates (independent Windows operator, source redistribution rights, shipped dependency notices, privacy/handling authorization, seller terms, human-timed delivery rehearsal) require external real evidence; no fake signatures or approval.
- Next: original full checkout/exact-head test module and Windows CMD + generated ZIP/Chromium E2E, ideally when external CI runners execute. Keep feature branch open; no merge/force push.

---

## REA_Web core intake progress — 2026-10-30 KST

- **Product code checkpoint** `0c6f20927009ec19e2bafa95bc9252b4cc115e06` (last test commit); branch `feature/d27-windows-python-discovery`, PR #30 Draft/unmerged. This tranche works on the ACTUAL CSV/flat-JSON build, GUI/guided approvals and approved same-schema two-file ROW APPEND, rather than blocking on GitHub CI queue.
- `rea/mvp.py`: new `source_sha256` enforces regular .csv/.json, rejects symlinks and >10MiB inputs *before opening*, uses 64KiB SHA256 streaming and fstat regular-file validation; generator replaces three unbounded `source.read_bytes()` fingerprints with bounded SHA and a pinned manifest digest, rejects changed source before publication.
- `rea/guided.py`: preview checks the source fingerprint before and after parsing; rejects changing file before an approval can be tied to stale rows. Existing explicit APPROVE flow is retained.
- `rea/two_source.py`: approval, prepare, compose and final ZIP publication source hashes now all share `source_sha256`; avoids full in-memory source reads for paired ROW APPEND. Existing per-file approval, APPEND and total 10MiB/10k-row gates remain.
- New `tests/test_source_fingerprint.py` has **9 committed test functions**: exact SHA, no read_bytes in generator, overlimit before open, symlink, source-mutated preview, changed source during generation, two-file streaming, combined oversize, stale approved pair. New full-repo test results are **NOT_RUN** (GitHub Actions still queued; repository clone in isolated runtime blocked by DNS).
- Independent Linux Python 3.13 isolated reproduction of the new exact `source_sha256` implementation: **10 targeted checks PASS** (valid CSV/JSON, empty source, 10MiB edge, oversize, symlink, suffix, absent path, directory, read_bytes guard). This is **function-only validation**, not full repo integration or Windows E2E.
- GitHub blob verification after commit: `rea/mvp.py` `48ff9197fe738cfc4b4e72f496180d3294b10167`, `rea/guided.py` `e6f2a82364426c88286a05d9761867cc8d842764`, `rea/two_source.py` `34dacd6d2f317db603f884f0d0c8d57d88e93c5c`, `tests/test_source_fingerprint.py` `cb0ddc2c1c0cd2d1972db30ea5dd4952a9273964`.
- **CI policy:** DO NOT wait for queued workflows or create unnecessary CI-only commits. After runners execute, inspect exact-code D27 Windows+Linux full pytest, D3 Chromium and D31 vulnerability audit. Prior CI evidence predates these code changes. No claimed current-code suite PASS.
- **Release boundaries:** offline Windows ZIP, no Vercel production. Qualitative prior development ~95%, sales readiness ~77% are unchanged estimates, NOT verified progress percentages. Sales remain **BLOCKED** pending real independent Windows operator, commercial source/dependency redistribution rights, privacy/retention, terms and timed delivery evidence. No merge or force-push.

---

## LATEST REA_Web continuation — 2026-10-30 KST

1. Goal: customer-authorized CSV/flat JSON → explicit mapping approval → read-only local FastAPI/SQLite Windows ZIP. Optional approved same-schema ROW APPEND. No JOIN, hosting, login, payments, scraping or live sync. Hypothetical 299,000 KRW offer, not approved for sale.
2. Code: rea/delivery.py now rejects case-insensitive parent-file/nested-file collisions such as app/Foo and app/foo/child.txt using _member_paths_conflict. Standalone rea/customer_self_check.py rejects the same conflict in an extracted manifest. Regression tests in tests/test_delivery_zip_hardening.py. Prior Windows device names, ADS, symlinks, non-object manifest and release-date validation preserved.
3. Evidence: Code checkpoint e0fb1d89c69ca0143168ef6e04d7b10ffcbe4288. In an isolated Linux Python 3.13 workspace, python -m pytest -q tests/test_sale_gate.py tests/test_delivery_zip_hardening.py: 69 PASS, 0 FAIL. Regression file matched GitHub blob b776228ca47a6290bce23e293784789ab766a2c3; core validator and customer-check function excerpts checked against GitHub. A hand-built synthetic ZIP was verified, extracted, with manifest SHA and 4-row read-only SQLite checks PASS and an unlisted-file refusal PASS. NOT the original full repository checkout, product-generated ZIP, Windows E2E or browser test. The isolated environment reported FAIL_LOCAL_PREREQUISITES, not an application launch.
4. CI: PR #30 OPEN/DRAFT/UNMERGED; code checkpoint's first-page 28 Actions workflows all QUEUED, including D27 and D31. No current-code whole-suite PASS. Engineering 95% and sale preparation 77% remain old qualitative unrecalculated estimates. No 100% completion claim.
5. Issue/pivot: ZIP verifier previously ACCEPTED a file/directory prefix alias on case-sensitive Linux, despite Windows extraction conflict. Fixed and regression-covered. Direct git clone failed GitHub DNS; fetched exact source/test through connected GitHub instead. Queued jobs have no failure logs, so do not claim job failure.
6. Repository: hibi89/REA_Web, branch feature/d27-windows-python-discovery, code SHA e0fb1d89c69ca0143168ef6e04d7b10ffcbe4288, PR https://github.com/hibi89/REA_Web/pull/30 targeting integration/develop. No PR merge/force push; preserve upstream pinned source branches.
7. Deployment: offline Windows ZIP, not Vercel; Production URL/project N/A. Requires Python 3.11+ and compatible requirements. Exact-source native Windows CMD/localhost/Chromium/restart still NOT_VERIFIED.
8. Security/original: no real customer material or secrets used; preserve originals, Git commits provide rollback. Shipped SQLite is plaintext. Redistribution rights, dependency notices and real customer privacy approval NOT_GRANTED.
9. Next: after CI runs, inspect exact code SHA D27 Windows/Linux/Chromium and D31 audit; fix only confirmed problems. Run original-checkout full pytest and actual generated synthetic ZIP + extracted Windows CMD/browser E2E. Human Windows acceptance, source rights, dependency notices, data handling, seller terms, measured human delivery remain six separate gates requiring actual evidence.
10. Updated 2026-10-30 KST. Confirmation scope: 69 isolated source/test cases, 4 synthetic archive/checker checks, GitHub branch and first-page queued CI. Documentation head after this update must be re-read. Classification PARTIAL / SALE BLOCKED.

---

## REA_Web D27 continuation — 2026-10-30 KST (supersedes prior test snapshot)

- **Product code/test checkpoint:** `55cf80d162f1a725f075867104ced3f6821d1d1e` on `feature/d27-windows-python-discovery`; PR #30 stays OPEN/DRAFT/UNMERGED. Commit `1368a199` hardened exporter Windows device aliases and `eb8b3853` matched shipped offline customer checker, `55cf80d` added a six-case regression. Windows also reserves superscript COM¹/²/³ and LPT¹/²/³ (Microsoft official Naming Files, Paths, and Namespaces guide).
- **Focus tested:** Linux Python 3.13 `python -m pytest -q tests/test_sale_gate.py tests/test_delivery_zip_hardening.py` yielded **63 passed / 0 failed** in a deliberately isolated fixture workspace. The focused regression source file is verified identical to GitHub blob `4f5936b425c02a95d927b96cae0c8d1b52f0e321`; exact GitHub function checksums matched for `_safe`, `_members`, `verify_delivery`, and `_safe_member`. The helper modules used isolated source excerpts/stubs, **not the original full repository checkout**, native Windows or complete produced-ZIP E2E. The separate Linux environment has no `github.com` DNS for cloning.
- **CI observation:** On code checkpoint `55cf80d`, first 28 PR-triggered GitHub Actions runs were **QUEUED**, including D27 and D31. This is **not a failed job**, but there is **no latest-code Actions PASS evidence**. Old `c42c4c4` 29/29 SUCCESS cannot be transferred. A new documentation SHA after this update needs fresh head/CI lookup.
- **Production:** No Vercel project/URL applies; release target is offline local Windows ZIP, not hosted production. User-facing Windows native launch/browser/CRC/restart on exact code checkpoint **NOT_VERIFIED**.
- **Release gate unchanged:** Independent nondeveloper Windows acceptance NOT_RUN, actual source/dependency commercial redistribution rights NOT_GRANTED, privacy/customer-data handling NOT_APPROVED, seller terms NOT_APPROVED, measured human delivery rehearsal NOT_RUN. The six-field machine ledger alone is **not approval**. Prior engineering 95% and sale preparation 77% are *qualitative unrecalculated estimates*, not measured completion. **NOT APPROVED FOR SALE**.
- **Next task:** Check D27, D31 CI for this exact code HEAD after runners execute; inspect failing job logs, do minimum code correction; complete original-checkout Python 3.11 pytest plus synthetic Windows ZIP/extract/CMD/Chromium E2E when supported. Do not merge or force-push, and do not generate fake owner/rights sign-off.

---

## [LATEST] REA_Web release-hardening checkpoint — 2026-10-30 KST

1. **Goal/confirmed scope:** KrW 299,000-class customer-owned CSV/flat-JSON → explicit mapping approval → readonly local FastAPI/SQLite → Windows ZIP, optional same-schema two-input ROW APPEND. No different-schema JOIN, hosting, payments or scraping.
2. **Work completed:** Windows path/device/casefold defenses in delivery ZIP and standalone extracted customer self-check; strict date gate; malformed non-object ZIP manifest now returns bounded validation errors instead of uncontrolled `AttributeError`. Code commit checkpoint **`40144c58fa84c1d5cc67ef239c43810e73f66eae`**. Do not change existing data or upstream imports.
3. **Tests:** Separate Linux Python 3.13 / no direct GitHub network; `python -m pytest -q tests/test_sale_gate.py tests/test_delivery_zip_hardening.py` returned **57 passed / 0 failed**. All three focused test/source sale-gate files matched exact Git blob SHA; ZIP-check tests used source-function excerpts matched to GitHub, isolated from unrelated application modules. These tests are **focused isolated verification, not entire original checkout, Windows or generated ZIP E2E**. The new eight malformed-manifest cases passed.
4. **State:** Engineering previously estimated 95% and sale preparation 77% (qualitative, carried; not remeasured). Latest code not yet approved for sale. This code checkpoint GitHub Actions query showed **first 28 PR workflows QUEUED**; full app CI current-head PASS not established.
5. **Failure/blocker:** Direct clone / remote network in local test container failed DNS (github.com could not be resolved); used connector-fetched exact source/test files plus isolated source excerpts instead. GitHub hosted CI queue pending; do not relabel queue as failure or success. No reason to repeat identical blocked network clones.
6. **Repository/branch:** `hibi89/REA_Web`, `feature/d27-windows-python-discovery`, code SHA `40144c58fa84c1d5cc67ef239c43810e73f66eae`, Draft PR #30 toward `integration/develop`; no merge, no force push. Main paths: `rea/delivery.py`, `rea/customer_self_check.py`, `scripts/rea_sale_gate.py`, `tests/test_delivery_zip_hardening.py`, `tests/test_sale_gate.py`.
7. **Deployment:** Windows local ZIP target; Vercel Production **NOT APPLICABLE**. Python 3.11+ and runtime dependencies may be installed by customer; ZIP is not standalone EXE. Exact build/test commands are in D27 workflow and Windows README.
8. **Original/backup/security:** No actual customer data used. Preserve customer-provided original ZIP and snapshots. Shipping SQLite is plaintext. Distribution/source/dependency licensing and customer privacy authorization are **NOT GRANTED**; never commit tokens or actual private ledgers.
9. **Next priority / completion gate:** On current exact branch SHA, inspect D27 Linux/Windows tests & browser and D31 dependency audit; if failing diagnose exact job logs. Run original checkout targeted+full pytest and Windows extracted synthetic ZIP if available. Six human/rights/seller gates remain: independent Windows operator, source redistribution rights, dependency notices, privacy/data handling, sale terms, measured human delivery. None is automatically approved by tests.
10. **Timestamp/evidence:** 2026-10-30 KST handoff; verified code checkpoint `40144c58fa84c1d5cc67ef239c43810e73f66eae`; document commit SHA must be re-read from live branch after this update. CI status is a sampled, time-sensitive observation, not a blanket latest pass. Final state **PARTIAL / SALE BLOCKED**, not 100%.

---

## 2026-10-30 KST — isolated exact-code regression checkpoint (no sale authorization)

- Source/test code checkpoint: `1a49bffaccf0136056c0b7500ac895f76772ea79` (latest code before documentation updates). Feature PR #30 remains open/draft/unmerged.
- On a separate Linux/Python 3.13 environment without network access, tested `python -m pytest -q tests/test_sale_gate.py tests/test_delivery_zip_hardening.py`: **49 passed / 0 failed**. The GitHub `scripts/rea_sale_gate.py`, `tests/test_sale_gate.py`, `tests/test_delivery_zip_hardening.py` were reproduced with their exact Git blob SHA; for the ZIP tests, only verbatim source function excerpts `_safe`, `_members`, `verify_delivery` and `_safe_member` (each line-normalized checksum matched GitHub) were used, with other application code isolated/stubbed. Therefore this is a **focused code-region verification**, **NOT an original-checkout or generated-ZIP/full-app E2E pass**.
- On the last exact-head query before this documentation update, PR #30 HEAD `fd77d4dc5834f47f65730cc862138f458331c531` had the first page of **28 PR workflow runs all QUEUED**. CI success, native Windows customer launch, production/deployment and whole project suite are **UNVERIFIED** for the latest code; old c42c4c4 29/29 passes do not apply to the new code.
- No extra application code changes were made after the hardened test checkpoint. Previously added ZIP path/device name/casefold protections and the standalone self-check alignment are committed. Sale evidence gates (independent nondeveloper Windows check, source redistribution permission, actual dependency notice/legal inspection, data/privacy handling, seller contract terms, human-timed delivery) remain **NOT_APPROVED/NOT_RUN**.
- Prior qualitative engineering estimate **95%** and sale preparation estimate **77%** remain *unchanged*; they are estimates, not audited percentages. **NOT APPROVED FOR SALE**. No Vercel deployment is applicable to the current offline Windows ZIP scope.
- Next work: obtain exact-head completed D27 Windows/Linux/Chromium and D31 dependency results, troubleshoot any failing jobs, repeat the original-checkout targeted tests and generate/verify/extract a synthetic Windows ZIP. Do not claim 100% or accept orders before independent gates have evidence.

## REA_Web hardening continuation (2026-10-30 KST; product/test code checkpoint `1a49bffaccf0136056c0b7500ac895f76772ea79`)

- Source branch: `feature/d27-windows-python-discovery`; PR [#30](https://github.com/hibi89/REA_Web/pull/30) remains DRAFT/OPEN/UNMERGED at last check. No upstream merge/force-push.
- New verified remote GitHub commits: `79dd289` delivery ZIP rejects additional Windows-illegal filename chars/devices and casefold collisions; `558d2f3` ZIP regression cases; `8810a3d` exported standalone extracted-folder self-check aligns with path policy; `953f816` comparison tests; `1f4cf6c` strict sign-off date grammar; `1a49bff` date regression.
- The modified source and tests were fetched back from the GitHub feature branch and inspected. **New targeted pytest NOT_RUN in this chat**: this environment cannot fetch/clone the repository to execute the exact source. The GitHub Actions first-page 28 workflows for earlier `953f816` were QUEUED at last query; current product/test checkpoint has no confirmed PASS. Do not transfer earlier c42c4c CI status to new commits.
- Security scope is bounded Windows ZIP paths and manual sign-off metadata format; Windows operator test, redistribution license rights, privacy/data operations, seller terms and measured human delivery still require genuine outside evidence.
- Carry existing qualitative estimates **engineering 95% / sale preparation 77%**, not recalculated. Commercial disposition: **NOT APPROVED FOR SALE**.
- Next: check current exact-head Actions and investigate any failures; run `python -m pytest -q tests/test_sale_gate.py tests/test_delivery_zip_hardening.py` in a real repository checkout, then perform synthetic delivery and extracted-Windows regression before asserting completion. Independent nondeveloper acceptance and commercial rights remain NOT_RUN/NOT_GRANTED.

---

## Latest exact-head status (2026-10-30; branch HEAD c42c4c49f7e192af5921efe32b26d025a22ed60e)

- PR #30 remains OPEN / DRAFT / UNMERGED. Commit c42c4c4 changes only the Windows smoke QA helper; no merge or force update.
- Current exact-head GitHub Actions: **29/29 SUCCESS**. D27 Windows run 40984255021: **446 passed / 1 warning**, extracted ZIP/CMD/localhost checks passed; D27 Linux run 40984248440: **431 passed / 5 skipped / 1 warning** and Chromium passed. D3 Windows/Chromium run 40984254836 and D31 Ubuntu/Windows generated-runtime audit 40984254952 passed. All CI data/apps are synthetic, not customer acceptance or commercial clearance.
- Local Python 3.11.9: compileall and pip check PASS; focused D21/D25/D27/customer guidance **51 passed / 2 skipped**; non-ASGI suite **300 passed / 10 skipped / 1 deselected**. The latter excluded eight TestClient-heavy files and one D18 localhost test after sandbox stalls/denial.
- Local native Windows smoke prepared the ZIP in workspace QA temp but localhost /health was blocked by sandbox WinError 10013; process cleanup was denied. Full local suite remains INCOMPLETE; do not infer local HTTP success from remote CI.
- Offer scope remains CSV/flat JSON, owner-approved field mapping, optional same-schema two-file ROW APPEND, read-only local SQLite app and Windows ZIP. No JOIN between different schemas, crawling, hosted service, login/payment or CRUD.
- Human nondeveloper Windows acceptance NOT_RUN; source/vendor/dependency redistribution rights NOT_GRANTED; customer-data/privacy and seller terms NOT_APPROVED. Development 95% / sale preparation 77% are qualitative carried estimates. **NOT_APPROVED_FOR_SALE.**

## Exact-head continuation update (2026-10-30; `4ce86ec2472bd350b0009390f8ed49111d29b8ae`)

- GitHub branch `feature/d27-windows-python-discovery` and PR #30 were re-read at this SHA. PR is OPEN / DRAFT / UNMERGED; no merge or force push was performed.
- Current-head Actions query returned **28/28 completed SUCCESS**. D27 run `40976199908`: Windows **446 passed / 1 warning**, Linux **431 passed / 5 skipped / 1 warning**. D3 run `40976200008` passed Windows native and Chromium checks against three generated apps. D31 run `40976199915` passed Ubuntu and Windows generated-runtime audit. Fixtures and generated packages are synthetic.
- The exact-head local mirror matches **173/173 Git blobs**. Exact-136 synthetic CSV, flat-JSON, and approved same-schema two-file APPEND ZIPs pass CRC, clean extraction and Windows CMD prerequisite check. The runtime source was unchanged between 136e023 and 4ce86ec; the latter adds a recheck document only. Direct generated-handler checks cover health/list/search/category/detail/404 and SQLite quick_check; they are **not localhost HTTP or full browser tests**.
- Current sandbox localhost client connection remains **BLOCKED/NOT_RUN** (`WinError 10013`); local full pytest did not produce a final summary and is **INCOMPLETE**. GitHub Windows CI separately passed the extracted-package localhost checks. Do not conflate those scopes.
- Development **95%** / Kmong preparation **77%** are prior qualitative estimates, not recalculated. Independent nondeveloper Windows acceptance **NOT_RUN**; source/vendor/runtime redistribution rights **NOT_GRANTED**; real-customer data authorization/privacy and seller terms **NOT_APPROVED**. The product is **NOT_APPROVED_FOR_SALE**.
- Next independent engineering work: refresh the exact-head generated-runtime dependency/license evidence and continue synthetic privacy/backup checks. Keep external human and rightsholder gates open until evidence is supplied.

# HANDOFF — REA_Web / current handoff (2026-10-30)

## 최신 원격 재확인 (2026-10-30; `50c82814821f89f0326cefcf04c2ee78e080d5c4`)

- 지정 브랜치 HEAD와 PR #30을 다시 확인했습니다. PR은 OPEN / DRAFT / UNMERGED 상태입니다.
- 이 정확한 HEAD의 GitHub Actions 첫 페이지에서 28개 모두 완료 SUCCESS, 진행 중/대기/실패 0건입니다. D27 `40969580989`, D3 `40969580958`, D31 `40969581132` 모두 SUCCESS입니다. 자동 검증 fixture는 합성 데이터이며 사람의 고객 검수로 간주하지 않습니다.
- 별도 격리 로컬 검사 기록은 고객 안내+D27 21 PASS, D6 14 PASS/1 SKIP, D9 경계·APPEND 15 PASS/2 DESELECTED, 새 ZIP 검증·CRC·깨끗한 압축 해제 후 실제 CMD 사전 검사 PASS입니다. 이 환경의 실서버 HTTP는 /health timeout/SQLite cleanup lock 때문에 BLOCKED/NOT_RUN이며 로컬 HTTP 성공으로 표현하지 않습니다.
- 개발 95% / 판매 준비 77%는 정성 추정치로 재측정하지 않았습니다. 상용 재배포 권리 NOT_GRANTED, 고객 데이터·개인정보/판매 조건 NOT_APPROVED, 비개발자 Windows 인수검수 NOT_RUN이므로 판매 승인 상태가 아닙니다.
- 아래에 남은 과거 시점 기록은 이 재확인보다 오래된 스냅샷입니다. 최신 상태를 주장할 때 이 메모와 정확한 원격 HEAD를 기준으로 삼으세요.



## 최신 확인 상태 (2026-10-30; 검증 기준 commit `970bbde`)

- D27 제품 코드와 D31 감사 워크플로의 검증 기준은 `970bbde8c853f4ed1382c038091bb2ee48abea9f`입니다. 이후 `ebb1f22`는 상태 문서만 갱신했으며 제품 코드는 바뀌지 않았습니다. PR #30은 OPEN/DRAFT/UNMERGED입니다. 강제 푸시나 병합은 하지 않았습니다.
- 검증 기준 commit `970bbde8c853f4ed1382c038091bb2ee48abea9f`의 GitHub Actions 28/28 SUCCESS입니다. D27 전체 회귀 [#40967860714](https://github.com/hibi89/REA_Web/actions/runs/40967860714)의 Linux D1–D27/Chromium과 Windows D1–D27/native-package job이 모두 성공했습니다. D31 생성 런타임 보안 감사도 Ubuntu/Windows PASS입니다. 모두 합성 데이터 자동 검증이며 사람의 고객 검수는 아닙니다.
- 이번 로컬 집중 검사: 고객 안내 + D27 Python discovery **21 passed**; D6 provenance **14 passed, 1 skipped**; D9 boundaries/두 파일 APPEND **15 passed, 2 deselected**. 제외 항목은 실제 TestClient HTTP 대기와 symlink 권한 경계입니다.
- 실제 Windows ZIP을 합성 데이터로 생성하고 ZIP CRC 및 깨끗한 새 폴더 추출 후 `cmd.exe /d /c check_windows.cmd --check` **PASS**. 별도 로컬 더블클릭 HTTP 스모크는 /health 시간 초과와 SQLite 잠금 정리 문제로 **BLOCKED/NOT_RUN**이며 PASS로 처리하지 않았습니다. CI의 Windows localhost HTTP는 위 D27 run에서 PASS입니다.
- 개발률 **95%**, 판매 준비율 **77%**는 정성적 기존 추정치이며 다시 측정한 값이 아닙니다. 상용 재배포 권리 **NOT_GRANTED**, 고객 데이터 승인/개인정보 검토와 판매 조건 **NOT_APPROVED**, 비개발자 Windows 인수 검수 **NOT_RUN**. **판매 승인 아님**.
- D31 감사는 합성 앱이 생성한 broad requirements의 현재 호환 버전 및 전이 의존성을 검사합니다. 특정 고객 환경의 lockfile, 법률적 권리 또는 배포 승인 근거가 아닙니다.


## D27 product follow-up refresh (snapshot before this documentation update, 2026-10-30)

- The feature ref was re-read at `ab3eb2dd39ba334999fca95dcfaf65af4842c0c2`. Its 27 returned GitHub Actions runs later all completed successfully. D27 Windows+Linux run `40960995478`, D3 Windows-native+Linux-browser run `40960995506`, and D6 `40960995289`, D21 `40960995434`, D26 `40960995430` all passed.
- The isolated source copy was verified against all 171 Git blobs at that SHA. Three synthetic delivery ZIPs were generated from it; archive CRC and actual Windows `check_windows.cmd --check` passed 3/3. These are QA samples, explicitly not customer deliveries or sales authorization.
- Local Windows full pytest and focused regression did not complete: the full run stopped at 64% after showing a failure, and the focused run showed failures then stalled. Their failure causes are not adjudicated. The direct local CMD-launch/loopback smoke did not return health in time and cleanup encountered a locked SQLite file; local Chromium did not reach a case result. Do not claim local E2E success. Current-head GitHub Windows-native and Linux-browser jobs are the verified E2E evidence.
- The prior project estimates remain **88% development / 68% sale preparation**, carried forward from the detailed `6776582` validation report; they have not been recalculated for the newer commits. Human customer acceptance remains **NOT_RUN**, commercial redistribution rights **NOT_GRANTED**, customer-data authorization/privacy **NOT_APPROVED**, seller terms **NOT_APPROVED**. The product is not approved for sale.
- PR #30 remains open/draft/unmerged. This snapshot is the record immediately before the documentation follow-up commit; the latest branch tip should be read from GitHub.
## Current continuation note (2026-10-30; commit `2be8bb6`)

- Exact branch `feature/d27-windows-python-discovery` now points to `2be8bb6c6092ce771124977125502306f9dd2389`, a normal fast-forward child of `64b28c986618c68472649474c6604c2b1fce7372`. No force update or merge was used. This is six commits ahead of baseline `db6711e`.
- The connector showed nine workflows queued when queried immediately after `2be8bb6`; no success result for that commit is claimed here. The earlier 27/27 returned successes refer only to commit `64b28c9`.
- The direct dependency-boundary cases have now been committed. The isolated guidance tests were 18 PASS; compileall passed. Full local regression remains incomplete/blocked by sandbox filesystem denials; see the detailed validation receipt.
- Change patch and SHA-verified source/document bundle are in `bundle_update_notes`; these are GitHub review artifacts, not an independently runnable customer delivery ZIP.
- Helper branch `codex/REA_Web-bounds-regression` remains an accidental incomplete one-file tree. The connector exposes no branch deletion. Do not use it. The designated feature branch was safely advanced only after constructing/verifying a full base-tree-preserving commit.
- Human Windows acceptance: NOT_RUN; commercial redistribution rights: NOT_GRANTED; customer authorization/privacy: NOT_APPROVED; listing terms: NOT_APPROVED. **Not approved for sale/intake.**

The dated status snapshots below this note are historical and are superseded where they state an older branch head, test boundary status, or that the feature branch was not updated.
## Follow-up handoff state (2026-10-30)

- Feature branch exact HEAD: `64b28c986618c68472649474c6604c2b1fce7372`; branch compare shows 5 ahead / 0 behind `db6711e`. PR #30 remains OPEN/DRAFT/UNMERGED.
- Current CI evidence from connector: 27 returned workflows, all 27 SUCCESS. One expected workflow was not returned by the first-page-only API, so do not claim 28/28.
- Code at 64b bounds FastAPI, Starlette, and Uvicorn to supported lower/upper ranges. Local isolated customer guidance: 18 PASS, compileall PASS. Full local regression is incomplete due Windows sandbox filesystem `WinError 5`; targeted D27/D26 tests also encounter denied `os.link` at package publication.
- Cumulative patch is validated against `db6711e`; original ZIP snapshot stays untouched. Customer bundle and machine hashes live in `bundle_update_notes/`.
- Human/customer acceptance NOT_RUN; commercial redistribution rights NOT_GRANTED; seller listing/terms NOT_APPROVED. Do not promote CI or synthetic cases to those gates.
- A helper branch created via connector has an incomplete one-file tree and is not a usable source branch. The feature branch was not moved. Connector provides no safe branch delete operation; record it and do not build on it.

## Next independent work

1. Re-run the current complete D27/D1-D27 regression in an unrestricted, ordinary Windows environment so atomic rename/hard-link tests can run; mark this sandbox run incomplete.
2. Rebuild synthetic delivery ZIPs from exact 64b source, then execute extracted CMD, browser search/filter/detail and append flows; older `f6e34f6` receipts are not current-head proof.
3. Continue exact dependency vulnerability and license notice checks using source/release artifacts; legal source and vendor rights remain NOT_GRANTED until documented clearance.
4. Keep the human Windows acceptance protocol unfilled until an independent nondeveloper performs it.

## Verified remote head and product status

- Current feature branch HEAD: `578442b2bd22bb64a004e77bbd091a17930f614a`. Exact-head CI completed **28/28 SUCCESS**, including D27 Windows/Linux full regression and D6 supply-chain/security.
- D27 runs: PR [#40954859581](https://github.com/hibi89/REA_Web/actions/runs/40954859581), push [#40954852936](https://github.com/hibi89/REA_Web/actions/runs/40954852936). D6 run: [#40954859774](https://github.com/hibi89/REA_Web/actions/runs/40954859774).
- PR [#30](https://github.com/hibi89/REA_Web/pull/30) remains **OPEN, DRAFT, UNMERGED**. No force push or merge was performed.
- Generated runtime requirement includes Starlette `>=1.3.1,<2`; the customer preflight rejects lower versions and offers Korean recovery instructions for both `python` and `py -3`.
- Supported: customer-authorized CSV or flat JSON, preview/explicit mapping approval, same-schema two-file ROW APPEND with both approvals, local read-only FastAPI/SQLite app (list/search/category filter/detail), Windows ZIP. Different-schema JOIN, scraping, hosting, accounts, payments, sync, and general CRUD are excluded.
- Local: focused tests **13 PASS**, Python compile, dependency floor and `pip check` PASS; five synthetic ZIPs passed Windows preflight. Local interactive customer acceptance: **NOT_RUN**.
- Human acceptance **NOT_RUN**; source/dependency commercial redistribution rights **NOT_GRANTED**; customer-data/privacy operating agreement **NOT_APPROVED**. Sale is not approved. Current estimates: development **95%**, sale preparation **77%**.

## Next independent unit

Prepare a reproducible runtime dependency/license inventory from the actual generated-app dependency graph and the tested Windows environment. Record package versions, dependency edges, license metadata/source hashes, missing notices, and the limits of that evidence. Keep commercial clearance NOT_GRANTED until rights-holder/legal review. Then continue other independent package/privacy checks while any new docs-only CI runs.

The source snapshot and validation evidence remain preserved locally. Do not infer customer acceptance or rights from CI. Do not merge PR #30 without explicit approval.

---

## Historical handoff below (2026-10-25)

## Latest D2 checkpoint (2026-10-25 22:55 KST)
**REA-MVP-D2-01 DONE on feature only**. Feature SHA `fda96076de33ebf4f4b6118972a5033a3f703ba9`; Draft PR [#4](https://github.com/hibi89/REA_Web/pull/4), unmerged. Real GitHub Actions [CI run 40199741969](https://github.com/hibi89/REA_Web/actions/runs/40199741969) SUCCESS: **28/28 pytest**, pinned Astra validation and CLI approval-block check PASS on Ubuntu Python 3.11. PR CI run 40199766677 SUCCESS. `rea/adapter/fable_to_astra.py` adds read-only Fable schema v1.0 → review-only Astra candidate mapping, synthetic demo and tests; do **not** state functional UI, real backend, API ownership or chart lineage as observed. Windows, real customer data, cross-branch E2E, full vendor license audit, production service all NOT_RUN. No Vercel deployment for this unit (not applicable).

## Instructions for the next assistant
When owner writes **[REA_Web 깃헙 레포지토리 보고 작업이어가셈]**, inspect real GitHub and **perform the next READY development work immediately** without asking for context or another 'ㄱ'. Read `WORKER_START_HERE.md`, `STATUS.md`, `docs/17_NEXT_TASK.md`, `docs/SESSION_RESTART_PROTOCOL.md`; these are the canonical handoff. Future new chat will not contain our current code discussion, so this repository is the source of truth.

## Product and commercial intent
REA_Web is the **Fable 5.1 website technical/evidence analyzer + Astra Web Catcher functional-spec/independent web app engine**. Current customer-value-first MVP = take **customer-provided** clean CSV, generate usable standalone local app; reference URL optional. Avoid OHORA-like indefinite data collection / third-party API quota / unknown production DB complexity. First commercial price hypothesis 300,000 KRW fixed scope (2 screens, 3 simple features), not a 990k complex live DB job. Sale only after acceptance.

## Current technical status, with exact SHAs
- main documentation baseline before this handoff update: `71ed9a4656ef7642a32c335da9c6d664916cabee` (always refetch remote current SHA).
- Day1 generated local app: `feature/csv-local-mvp` @ `5515a7286d63211e32d2c577f93f77d61f37ce08`. Code `rea/mvp.py`, `rea/templates/app.py`, static HTML/CSS/JS, tests `tests/test_mvp.py`, actual Playwright browser `scripts/mvp_browser_smoke.py`. Draft PR #3, unmerged.
- CI run `40198326369`, job `121183903206`: **9 pytest PASS** + synthetic CSV app generation + compileall + real Chromium browser PASS; search, category, detail, reload; zero unexpected external request or JS error. No Windows/browser proof on Windows.
- Fable 88-source import: `import/fable51-bbe72c0` @ `7e6f273b359b207fad8f92016226e3058cbcb839`, pinned upstream `bbe72c0acd3a3e355062d6bd0d866af33e5274b0`, Draft PR #1.
- Astra P4 103-file bounded **partial** import (41 core astra_contracts modules): `import/astra-p4-b3166b6` @ `f044b66e799289a5a353fdb9cbfdb324e683ffa3`, pinned upstream `b3166b67604381a9d2afd41667b65f9a9b103b37`, Draft PR #2.
- Branches: integration/develop, feature/evidence-adapter (D2 next), feature/csv-local-mvp (D1), feature/orchestrator, qa/cross-platform, qa/vendor-fable, qa/vendor-astra; don't force-update feature work or mutate upstream imports.

## Single task to execute next
**REA-MVP-D2-02** `READY`, start automatically on exact trigger or `ㄱ`. Prefer `feature/orchestrator` after checking latest branch HEAD and the previous two feature branches. Use Fable report as **optional** analysis input to existing CSV→local app flow; leave website URL optional, require customer-provided CSV, retain `REVIEW_REQUIRED` and no automatic semantic mapping. Implement/test true synthetic demo, create Draft PR, and update main docs with exact proof. Only one unit per turn; next D3 three-example/browser/Windows/packaging/design-gap checks.

Do **not** repeat D2-01. Earlier section was historical. Source import branches remain pinned, partial Astra subset unchanged.

## Way of working
MVP-first target is 3 days (not a guarantee). Prioritize working result rather than huge theoretical scaffolding. Keep minimum non-deferable no overwrite/bounded CSV/SQL/DOM/localhost/authorization. Defer deeper security hardening until after functional proof, but not past customer delivery. Keep statuses PASS/NOT_RUN/BLOCKED accurate and always record commit SHA and work done in main STATUS/HANDOFF/NEXT_TASK.

No user actions are required for current D2 synthetic implementation; don't ask the owner for new data, tools, original ZIP, architecture confirmation or a different prompt. Only request explicit approval for production DB, external deployment or risky irreversible actions.

