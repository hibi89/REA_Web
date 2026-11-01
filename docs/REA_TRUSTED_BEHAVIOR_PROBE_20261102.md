# REA_WEB — trusted synthetic bundle response evidence (2026-11-02 KST)

## Purpose and exact boundary
The product target is independently generated frontend from a reference URL's *authorized public design cues* and the owner's own backend source ZIP. This development unit checks a **previously approved SELF-AUTHORED SYNTHETIC** combined ZIP after extraction and separate operator-started localhost backend runtime. It does **NOT** execute imported/source ZIP code, start the server, sandbox arbitrary uploaded code, audit credentials/authorization, or prove the listening process originated from the inspected ZIP.

Module: `rea/adapter/behavior_probe.py` (`rea.behavior_probe.v0.1`). Dependencies: Python 3.11+ stdlib only (probe side). The trusted fixture runtime itself needs preinstalled FastAPI/Uvicorn. No remote URL, outside-network call, write endpoint, cookies or token supplied by the probe.

### Supported workflow (test fixture only)
1. Build the trusted fixture with the prior `project_bundle` API and record the resulting bundle SHA256 from an independent trustworthy location.
2. Extract the exact ZIP into a fresh directory. Start the synthetic fixture intentionally with `python runtime_entry.py --run-trusted-synthetic --port 8766`. **Never substitute real customer/unreviewed ZIP code into this runner.**
3. From the REA_WEB source checkout, run:
   ```bash
   python -m rea.adapter.behavior_probe --bundle-zip /path/bundle.zip --extracted /path/extracted --expected-bundle-sha256 <64-char-known-sha256> --port 8766 --out /path/NEW-behavior-review.json --developer-authorized-synthetic
   ```
4. Exit code `0` = `PASS_REVIEW_REQUIRED`, `3` = sampled HTTP/body mismatch and report produced, `2` = rejected evidence/unsafe source/no-overwrite. A successful probe is **not** deploy/sale approval.

### Integrity checks (before ANY request)
- One independently supplied exact ZIP SHA256 required. Source path is no-follow/regular with 25 MiB cap; allowed inventory is only the specific synthetic bundle's known names (12–14). Reject duplicate/case-fold names, links, unexpected files, or mismatched ZIP CRC.
- Extracted file inventory must exactly equal zipped files. No injected `.py`, cached `.pyc`, symlink, omitted file or altered byte is accepted. `MANIFEST.json`, `SHA256SUMS.json`, original source hash and frontend/backend source linkage are checked against ZIP contents. Hashes establish **integrity of inspected bytes**, not that this code is trustworthy.
- Updated trusted synthetic `runtime_entry.py` sets `sys.dont_write_bytecode = True` to keep the extracted tree stable after running. This is not a general sandbox or program isolation.

### Actual localhost HTTP observations
The probe issues only `GET` to literal `127.0.0.1:<nonprivileged port>` based on owner-confirmed `dashboard/manifest.json` binding paths:
- list: HTTP 200, JSON (<=256 KiB), non-empty bounded list, mapped ID/name/category/status types, 1–200 records.
- metrics: HTTP 200, numeric nonnegative mapped total/completed/pending with basic consistency bounds.
- detail: HTTP 200, mapped first-item ID and details consistent.
- missing detail: HTTP 404. No redirects or credential/header forwarding and no POST/PATCH/DELETE.

Output only includes schema/status, known ZIP/source hashes, four HTTP status codes, item count, and redacted error-code categories. **No raw body, name, individual ID, auth token, private query or secret** in report. If a live server does not match these narrow assumptions the probe returns FAIL, not a universal API incompatibility conclusion.

### Evidence limitations
- `runtime_process_identity_attested: false` ALWAYS. A different process may bind the same localhost port. A file hash and successful GET are not a running-process attestation.
- Actual customer source execution requires an authenticated owner-approved VM/container isolation strategy, no sensitive data and controlled network/filesystem, then runtime-to-source provenance; **not done here**.
- No real reference URL design fidelity, Windows physical GUI acceptance, customer authorization or public release approval.

### Tests
`python -m pytest -q tests/test_behavior_probe.py tests/test_project_bundle.py`

Tests include real trusted synthetic subprocess GET, malformed/non-JSON/oversized/redirect responses, missing fields, bad KPI types, false 404, unknown local process, source modification, symlink, unexpected archive content, no-approval and destination no-overwrite. CI integrates these with the existing clean ZIP/Chromium test on Windows and Ubuntu.
