# SITECRAFT AX P70 — independent three-site synthetic browser acceptance

## Contract and scope

Three **different owner-authored local synthetic HTML references** for search,
filter, and detail (catalog/inventory/directory), plus one separately supplied
owner-approved synthetic CSV. The strict JSON contract schema is
sitecraft.p70.synthetic.v1 with product=SITECRAFT AX,
mode=three_synthetic_local_browser_cases, sites=[exactly 3 entries], owner_csv,
owner_sha256, mapping {id,title,category}, permission=
YES_OWNER_AUTHORIZED_LOCAL_FIXTURE, approval=APPROVE_SYNTHETIC_ONLY,
external_network_allowed=false and commercial_release_allowed=false.

Each site entry has case (search/filter/detail), reference_html (local relative
name), reference_sha256, and approved_review_digest. Start with empty digest
strings, inspect all three cases via a real local Playwright Chromium browser,
read their Astra REVIEW_REQUIRED evidence and digest, and have the *synthetic
test harness* insert the reviewed digest. These strings are NOT authenticated
customer identity nor legal permission to reproduce third-party designs.

Run from a checkout with pinned Fable and Astra:
- python -m rea.sitecraft_p70 inspect --scope LOCAL/scope.json --astra-root .vendor/astra/engines/astra_p4
- python -m rea.sitecraft_p70 build --scope LOCAL/scope.json --fable-root .vendor/fable/engines/fable51 --astra-root .vendor/astra/engines/astra_p4 --out LOCAL/new_unique_package

All three inputs are SHA-pinned; the package has /search, /filter, /detail
independent Pro apps and a sitecraft_p70_report.json, each with browser
before/after evidence, Astra observed claims, and generated-browser state
comparison. Fable is the real static GET scanner; dynamic observations come
from separate Chromium, not from a purported Fable --record feature.
No reference source HTML, CSS, JS, imagery or guessed backend implementation is
copied. Any case failure aborts publication of the entire batch.

## Architecture selection

A) Manually reconstruct three apps: higher per-site cost, difficult reproducible
provenance and safe batching. B) Reuse original REA_Web P70 real browser
observer/Fable/Astra/Pro and isolate SITECRAFT scope, three-case evidence,
review-digest and atomic no-replace publishing: lower marginal cost, proven
contract test path and existing recovery primitives. Adopt B; no core rewrite.
Existing REA_Web, Fable/Astra pinned imports, DATA2WEB and deployment untouched.

## Acceptance and limitations

P70 synthetic engineering gate: 3 actual Chromium before/after DOM state
transitions, conservative Astra P4 observed source evidence, explicit synthetic
case review, independent Pro FastAPI/SQLite app generation, actual generated
Chromium comparison, negative permission/sha/review/duplicate/path gates, and
no-overwrite/partial-output rejection. Verify exact SHA in Ubuntu+Windows
Actions including P50 regressions.

User-approved **final blueprint official completion** remains UNASSESSED
pending full requirements to approved 100-point weights and acceptance.
P70 is only a bounded engineering milestone, not final-product 70% proof.
No real customer/site, genuine Fable headed Record, physical Windows10/11,
Chrome/Edge customer approval, third-party source rights, Production/Vercel,
or paid API validation. Commercial RELEASE HOLD and central [작업중] remain.
