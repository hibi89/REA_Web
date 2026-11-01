# REA_WEB trusted synthetic combined project bundle — 2026-11-02

Purpose: ship a deterministic ZIP of an independently generated dashboard and a **self-authored trusted synthetic** FastAPI fixture. This is not an arbitrary customer backend ZIP runner or commercial release.

Module: `rea/adapter/project_bundle.py`. It checks the exact owner ZIP SHA256, source ZIP safety limits, approved frontend manifest/back-end SHA linkage, matched static-vs-supplied-OpenAPI route declarations and explicit developer synthetic fixture authorization. The generator never imports or executes ZIP source.

The backend profile intentionally permits `app.py`, optional `requirements.txt` and `README_KO.md` only. Unexpected files including `.env` are rejected rather than silently shipped. Output is no-overwrite and reproducible, including member SHA256SUMS and a truthful MANIFEST: `runtime_origin_attested=false` and `behavior_verified_by_bundle_generator=false`.

Command:
```
python -m rea.adapter.project_bundle --backend-zip trusted-synthetic.zip --frontend GENERATED_UI --runtime-review REVIEW.json --expected-sha256 EXACT_SOURCE_SHA --out NEW_BUNDLE.zip --developer-authorized-synthetic
```

Tests: `python -m pytest -q tests/test_project_bundle.py tests/test_project_bundle_browser.py`. The browser test explicitly executes only its self-authored FastAPI fixture after clean extraction and checks real loopback HTTP, JavaScript, API status, KPI, search and detail. Windows and Linux CI are separate and must be inspected for actual results; local browser runs can be blocked by environment policy.

Extracted package requires Python 3.11+, FastAPI and Uvicorn pre-installed; `START_WINDOWS.cmd` checks its source SHA and then explicitly launches the synthetic fixture bound to 127.0.0.1:8766. No auto-install, production deployment or access to external services. Real customer backend execution, provenance, auth, data/privacy and rights gates remain blocked.
