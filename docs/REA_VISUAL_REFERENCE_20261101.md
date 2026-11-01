# REA_WEB reference visual evidence — 2026-11-01

## Product boundary

This is an additional **reference design observation** unit, not a site clone or a dashboard release.
The original Fable 5.1 `result.json` generally contains technology/network evidence, **not** screenshot/layout/computed-style evidence. Never infer design pixels from that report.

The new `rea.adapter.visual_reference` captures *limited* runtime browser-computed CSS and structural hints from a public reference. Only the origin, viewport, five candidate color values, structural `sidebar/topbar/unknown` classification, bounded component counts, and boolean visibility markers are retained. No screenshots, text, page HTML, image assets, stylesheets, cookies, third-party URLs, site-specific scripts or user data are persisted. Results are `rea.visual_reference.v0.1`, `REVIEW_REQUIRED`. A SHA256 is for artifact integrity, **not authenticity or authorship**.

## Public reference URL capture (requires explicit network opt-in)

Python 3.11+, Playwright Chromium installed. Only owner-authorized public HTTPS URLs (no query, nonstandard port, IP literal or credentials), public-only pre-resolved DNS pinned for browser navigation; JavaScript/service workers OFF and cross-origin/non-GET requests aborted. No login. This is not a comprehensive anti-SSRF guarantee for hostile DNS/network topologies, and does not capture JavaScript-dependent SPAs reliably.

```powershell
python -m rea.adapter.visual_reference --url https://example.com/ --out .\visual-new.json --allow-network
```

Do not put private/intranet URLs, credentials, protected content or customer data into reference capture. Do not run from an untrusted network. A destination that already exists is not overwritten. Any remote request needs the user’s intentional opt-in.

## Join with inspected owner's backend ZIP contract

```powershell
python -m rea.adapter.frontend_bridge --fable .\fable-result.json --backend .\backend-contract.json --visual .\visual-new.json --bindings .\owner-bindings.json
# Only after owner confirms the exact backend routes and JSON-field mapping:
python -m rea.adapter.frontend_bridge --fable .\fable-result.json --backend .\backend-contract.json --visual .\visual-new.json --bindings .\owner-bindings.json --out .\new-dashboard --owner-confirmed
```

The independently authored dashboard keeps the existing read-only same-origin GET API code. The observed colors are reduced to validated CSS hex values, and layout is mapped only to generic sidebar/topbar arrangement. There is **no** reproduction of the target's component source, assets, logo or typography. Fable/visual origin mismatch, bad input, visual artifact tampering, unapproved API mapping, or existing output directory fail closed.

## Tests and verification scope

`python -m pytest -q tests/test_visual_reference.py tests/test_frontend_bridge.py tests/test_frontend_bridge_browser.py tests/test_backend_zip.py tests/test_adapter.py`

- Local Python 3.13 visual/bridge subset: 32 PASS / 1 SKIP (missing Chromium executable, not feature failure).
- GitHub Windows/Linux Python 3.11 CI will install Chromium for real tests; only report results after actual runs.
- Browser test uses an **intercepted synthetic URL** (no external network) to inspect computed CSS and the generated stylesheet in Chromium. The older synthetic FastAPI live-HTTP browser test remains in the same workflow.
- No public real-site capture, owner's actual backend ZIP execution, arbitrary API response-shape discovery, pixel-perfect copy, dynamic SPA/JS style observation, Windows physical operator run, sales approval or production deployment is claimed.
