# REA_WEB — Offline explicit GET mapping wizard

The user-operated reviewed frontend mapping CLI requires no hand-written bindings.json file.
It is an optional presentation layer over the existing source-only offline_compose.

## Local usage (PowerShell)

    python -m rea.adapter.offline_wizard --backend-zip .\OWNED_BACKEND.zip --fable .\fable.json --out .\NEW_FRONTEND --owner-authorized-source

For an owner-authored nondefault display-field map, append:
    --presentation .\presentation.json

Only if the operator has lawful rights to inspect the exact ZIP, the tool lists mounted declared GET paths. The operator chooses list and metrics paths without parameters, one templated detail GET path, and types the exact JSON field for each role (or __root__ for root payload). These paths and fields are never treated as observed runtime response evidence. The wizard prints its mapping and output path and demands exact APPROVE. Nothing is published before approval.

The output contains exactly index.html, style.css, app.js, manifest.json and README_KO.md. The ZIP is statically parsed but never imported, executed, extracted or uploaded. The temporary bindings JSON is removed after composition. The preview SHA256 is checked again before generation. An existing output path is refused.

## Verified scope

Functional SHA 9171d78fb6c6d62aba263ea99e26ae38f5f71e62. GitHub native Windows2022 and Ubuntu22.04: frontend/Chromium suite run 41636103875 each 148 PASS/2 SKIP; static ZIP suite 41636104266 each 167 PASS/2 SKIP. No failures. No actual customer ZIP, authentication, same-origin live API response, real Windows nondeveloper pilot, or deployment was used. Commercial RELEASE HOLD.

The original CLI and the existing CSV/JSON Lite and Pro programs are unchanged. This tool is a terminal wizard, not a Windows graphical installer, legal authorization check or backend-runtime sandbox.
