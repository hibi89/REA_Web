# D12 — Offline runtime dependency and legal-file evidence (developer CI only)

## Target and boundaries
The generated REA customer ZIP contains its own app and app/requirements.txt with two declared ranges (fastapi>=0.110,<1 and uvicorn>=0.27,<1), not downloaded third-party wheels or a lockfile. D12 adds rea.dependency_evidence to inspect the currently installed Python environment OUTSIDE customer ZIPs; the existing D10 customer self-check and D11 customer-like ZIPs are unchanged.

D12 is NOT an SPDX verification, copyright authorization, vulnerability scan, legal clearance, supply-chain attestation or wheel-archive hash lock. Public GitHub source does not confer vendor redistribution rights. Fable and Astra are not packaged in customer ZIPs. A License-Expression or LICENSE SHA indicates only a declaration/observed bytes; actual commercial rights and obligations remain UNKNOWN/NOT_GRANTED.

## What is measured
- FastAPI/Uvicorn direct roots and transitive requirements reachable in this Python/platform environment by importlib.metadata. Each edge records declared specifier, version satisfaction/mismatch, missing install, optional extra skip or platform marker skip; parse and extra-expansion ambiguity are explicit.
- Installed version (name==version) is a DEVELOPER-ONLY candidate constraints suggestion, not fully reproducible resolution. No upstream wheel was downloaded/hashed and platform-specific markers, wheel selection, requested extras and dependency solvability need an independent lock procedure.
- Installed METADATA SHA256 when readable, declaration fields License-Expression, legacy License, listed License-File names and SHA256 of found LICENSE/LICENCE/NOTICE/COPYING files (maximum 1MB/file, 100 entries/distribution). No legal text or absolute machine file path is copied to report. Missing, unsafe, unreadable and ambiguous evidence is documented rather than silently passed.
- Program uses no network and opens requested output file exclusively (no overwrite). Artifacts produced under CI temp path, not app/ZIP source. All vendor imports stay pinned/unmodified.

## Developer-only execution
Python 3.11 with installed direct/runtime dependencies and packaging from test/developer environment:

    python -m rea.dependency_evidence --out ./new-d12-developer-evidence.json

To reproduce in a clean environment, install required dependencies in an isolated DEVELOPER environment before running the strictly offline auditor. Network activity of CI dependency setup must not be confused with auditor network calls.

## Evidence and gates
Workflow .github/workflows/rea-d12.yml runs D1-D12 pytest on Ubuntu and Windows, pinned Fable 88 and partial Astra 103 Git blob proof both OS, 8 existing Chromium synthetic webapps and 3 additional extracted-customer-ZIP Chromium checks on Linux, Windows native CMD/localhost HTTP, and D12 metadata audit on both OS. Uploads developer-only JSON evidence, never customer data or package legal text. Exact counts and SHAs come from actual CI, not this document.

**G5 BLOCKED:** no signed customer, authorized non-sensitive reference, or manually measured labor for three actual jobs.
**G6 BLOCKED:** human clean Windows, license attribution/redistribution grants, PII/privacy, backup/power-failure, security review, support/correction/refund approval.
**Commercial release: BLOCKED.** Owner has not authorized commercial sale/merge/deployment. The 300,000 KRW scope supports only explicitly approved same-schema 2-file ROW APPEND, not unlike-table joins.

## Next
After CI validates D12, move to D13 safe synthetic/owner-onboarding refinement or rights/Windows/human acceptance planning. No invented customer/time/legal evidence; do not change vendor source or existing ZIPs.
