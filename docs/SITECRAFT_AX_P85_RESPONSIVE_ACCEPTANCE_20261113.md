# SITECRAFT AX P85 — isolated three-site responsive Chromium and security acceptance

## Stage, design and scope

This new product-specific adapter `rea/sitecraft_p85.py` reuses the original
`rea.website_p85` and the P70 local-scope SHA/permission parser. It accepts
only three separately pinned, owner-authored **synthetic local HTML** references
with fixed roles search/catalog, filter/inventory, detail/directory and one
separately pinned owner CSV. It does not touch original REA_Web, Fable/Astra,
or DATA2WEB implementations.

The JSON scope fields match SITECRAFT P70 but set
`schema=sitecraft.p85.synthetic.v1`,
`mode=three_synthetic_local_responsive_cases`.
Each `sites[]` entry supplies `case`, `reference_html`,
`reference_sha256`, `approved_review_digest`. Before inspection the
synthetic digest field is empty. After real Chromium observation, a human
must inspect the receipt and explicitly select the synthetic test digest.
Neither the JSON token nor this demo tests actual customer identity or rights.

CLI (pinned Fable and Astra checkout installed):
- `python -m rea.sitecraft_p85 inspect --scope LOCAL/scope.json --astra-root .vendor/astra/engines/astra_p4`
- `python -m rea.sitecraft_p85 build --scope LOCAL/scope.json --astra-root .vendor/astra/engines/astra_p4 --fable-root .vendor/fable/engines/fable51 --out LOCAL/new_unique_package`

## Required acceptance

- Each of 3 different local synthetic HTML sites is observed at desktop
  **1280×720** and mobile **390×844** by real Playwright Chromium.
- In each viewport execute search → category filter → detail selection,
  recording actual DOM before/after and 4 PNG screenshots. All 3 websites
  total **18 observed state transitions**, **24 reference screenshots**.
- Astra P4 contracts produce 6 observed action claims, 8 screenshot references
  and conservative review-required candidate specs per site. Each reviewed
  digest binds exact reference hash, screenshots, DOM states, responsive metrics.
- Original frozen Fable 5.1 performs STATIC GET scan; independent REA Pro
  FastAPI/SQLite apps are built from owner CSV, not reference HTML/JS/CSS.
  For each new app actual Chromium repeats both viewport sequences:
  **24 generated PNGs**, **24 Pillow RGB comparison reports** across all 3.
- Pixel matching is NOT claimed. Every RGB result says
  `VISUAL_DIFFERENCE_REQUIRES_HUMAN_REVIEW`; site behavior remains
  unapproved for third-party reproduction.
- Fail-closed on permission, unexpected schema, local path traversal, source
  hash drift, stale/forged review receipt, URL marker or third-party iframe,
  existing destination, and intermediate case failure. Only complete
  three-app bundles atomically publish to a new folder.
- Synthetic XSS data passes through generated APIs as text and is not placed
  into the raw HTML template; static JS uses `textContent`, not `innerHTML`.
  This is bounded XSS regression, **not** a complete security audit.

## Release and completion interpretation

P85 **engineering synthetic acceptance** is verified only after exact-code SHA
Github Actions on Ubuntu and Windows pass the new tests and old P50/P70/P85
regressions. This stage number is **not** an official 85 percent of user final
blueprint. The overall official completion is `UNASSESSED` unless the
user-approved 100-point per-requirement evidence matrix is complete.
Do not remove central SITECRAFT `[작업중]` or `RELEASE HOLD`.
No real client site, legal license, Fable --record dynamic feature,
physical Windows10/11 with Edge/Chrome client, deployed Vercel/Production,
actual customer signature, accessibility full audit, or image pixel-parity
was validated by this synthetic harness. Preserve original branches and data.

Design alternatives: (A) build another headless observer manually: more duplicate
maintenance and uncertain screenshots; (B) reuse exact upstream reviewed P85
observer and Pro builder with isolated multi-site SHA/digest and atomic publish:
lower cost, repeatable QA and no original source changes. Implement B.
