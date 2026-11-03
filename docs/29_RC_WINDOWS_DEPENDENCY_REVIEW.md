# D10-01 — Synthetic release-candidate staging and Windows self-check

**Scope: TEST-ONLY staging, NOT a production release or commercial licensing clearance.**
All inputs are committed synthetic fixtures and no real customer data is
accessed, uploaded or processed. Generated data.sqlite still contains fixture
rows and must never be treated as PII-free with arbitrary customer input.

## Three supported and verified delivery modes
Run locally with Python 3.11 and installed FastAPI, Uvicorn and dev/test tools:

    python -m scripts.d10_make_rc --out ./rea-d10-synthetic-rc

This creates a **new, non-overwriting folder** with three separately generated
ZIPs, `rc_manifest.json` listing ZIP SHA-256 checksums and a Korean guide.

- 01_single_csv.zip: exact-schema customer-supplied CSV input → readonly app.
- 02_guided_json.zip: local field-approved flat JSON → readonly app.
- 03_two_source_append.zip: two local same-schema files, separate APPROVE tokens
  and explicit APPEND of rows → readonly app. **No relational joins**.

Each ZIP is validated by original D3 SHA-256 package verification and D6
exact-member allowlist, carries only local app/source and non-web-served owner
approval receipts where relevant. Fable/Astra vendor engine sources and
original raw CSV/JSON files are not packaged. Both the generator and sample
build scripts remain available in GitHub but not customer ZIPs.

## Windows onboarding self-check
Each ZIP now includes self_check.py and check_windows.cmd in its root.
Windows users can extract ZIP to a **new** folder and run check_windows.cmd
without administrator access. This calls the system Python and uses only Python
standard library to check Python >=3.11, package SHA-256 against the delivery
manifest, sqlite read-only opening and row count (no cell values), and reported
FastAPI/Uvicorn installed version presence. It does NOT install packages,
start a server, make a network request, inspect sensitive cell contents, or
approve licenses/rights. A nonzero exit code or FAIL means stop and check the
friendly README_WINDOWS.md steps before launch. If Python isn't installed or
isn't on PATH, CMD naturally fails with actionable guidance in the README;
the Python program cannot detect itself missing.

After PASS, users can run launch_windows.cmd (localhost 127.0.0.1 only).
Python packages may require an optional user-controlled pip install with
Internet access; neither the ZIP nor self-check bundles Python/wheels.
Existing Windows CI runner smoke verifies extracted ZIP→native CMD→localhost
HTTP separately. **A clean nondeveloper Windows-machine acceptance is NOT RUN.**

## Observed runtime metadata and license audit distinction
REA `rea.observed_deps` enumerates installed CI Python distributions reachable
from FastAPI/Uvicorn, versions, reported license metadata/classifiers and
candidate LICENSE/NOTICE **file names only**. It does not read full terms,
authenticate license grants, produce a locked transitive wheel file, perform
vulnerability/CVE scans, or prove customer reproducibility. Exact package
versions are **CI observations** and may change because shipped
app/requirements.txt uses ranges, not a version/hash lock.
A clean environment should be pinned after commercial rights and support
strategy is reviewed. The raw observation JSON is a synthetic CI artifact,
not an approved legal SBOM.

## Remaining blockers for 300,000 KRW offer / v1.0
- Two-input offer is ONLY partially covered by same-schema append. Arbitrary
  joins/different customer business schemas and reference-site design work
  need explicit narrower written service scope or separate implementation.
- Generated template distribution rights, Fable/Astra original source rights,
  PyPI direct/transitive license grants and actual notices NOT CLEARED.
- Local Windows self-check is automated; **real nondeveloper fresh-PC/manual**
  UI/install/update/repair/recovery experience NOT RUN.
- No authorized real client/reference or personal-data review, full
  penetration/privacy/threat audit, disaster/power-loss recovery, support/refund
  terms and measured three mock job 6-8h cost verification.
- No Vercel or other public production site, no credentials, paid calls, live
  customer DB access, scraping or automatic legal approval.

## Verification gates (must record exact Actions results)
D1–D10 pytest on Ubuntu and Windows; eight headless Chromium synthetic apps;
Windows native ZIP CMD HTTP + new diagnostic CMD; Fable 88/Astra partial 103
exact pinned Git blob checks; three example package audits and observed package
metadata. A green CI run is **test-only evidence**, not commercial readiness.
