# REA_Web D18 — first fresh Windows Tk ZIP to actual localhost HTTP

## Purpose and scope

Extend D17's `SYSTEM_SITE_PACKAGES_FALSE` Windows developer CI with the **same fresh interpreter** through local Tk APPEND approval, SHA-verified synthetic ZIP, temporary extraction, Uvicorn startup and HTTP contract. This closes the first-run integration gap without creating a publicly hosted app or changing the customer's launcher.

## Implementation

- Source branch: `feature/fresh-windows-http-e2e`, based on D17 verified `92355fec1152be0379a398b496f4e382ca57c55d`.
- `scripts/d15_pair_tk_smoke.py`: default remains unchanged; only optional `--retain-synthetic-zip-for-d18` copies the fixture-only, verified archive to a **new** scratch output path. No ordinary user GUI behavior changes.
- `scripts/d18_windows_fresh_http.py`: native Windows-only developer CI, stages allowlisted local modules and two committed synthetic source fixtures; verifies missing packages (exit 11) in a clean `.venv`, installs requirements to this isolated **CI venv only**, validates READY (exit 0), runs actual two-input Tk widget approvals with that Python, then runs the HTTP probe with that SAME Python. No install added to shipped CMD.
- `scripts/d18_http_probe.py`: verifies ZIP and APPEND source SHA receipts with both pinned public fixtures, confirms **no inferred JOIN** and no commercial clearance, extracts an allowlisted ZIP to scratch, starts `sys.executable -m uvicorn app:app --host 127.0.0.1` on a transient local port and asserts 200 health, five expected IDs, Unicode query from second file, category filter, second-file detail, HTTP 404 for unknown detail, read-only summary and unapproved semantic schema. Uses bounded readiness/HTTP timeouts and `finally` teardown, including native Windows process-tree kill fallback.
- `tests/test_d18_fresh_http.py`: negative tests for one-file ZIP, tampered ZIP, approval mismatch, existing evidence no-overwrite, Windows-only refusal; independently runs real HTTP contract using controller-only synthetic fixture on CI OSes. These unit cases do **not** count as actual Tk GUI acceptance.
- `.github/workflows/rea-d18.yml`: full Ubuntu/Windows pytest, Linux Chromium eight baseline + three actual extracted ZIPs, real Tk Linux and Windows synthetic UI, pinned Fable 88/Astra partial 103 source SHA, Windows native CMD/HTTP and additional SAME-venv D18 run; artifact is path-free status metadata only, **not** generated ZIP or real cell values.

## Design decision

A. **Selected:** synthetic-only fresh-venv HTTP end-to-end, strictly 127.0.0.1 and temporary package. Better integration evidence and no new commercial product behavior.
B. **Not selected:** accept ZIP checksum as sufficient without starting the app. Cheaper but cannot detect missing runtime modules, server/import failures or broken actual API.

## Proof policy

Only the exact commit whose **actual workflow jobs** complete SUCCESS can be marked verified. Prior D17 proof: Actions 40218363629, Linux and Windows 290 pytest each (zero skip), 11 genuine Linux Chromium generated-app checks, native Windows CMD/localhost and actual 2-file Tk widget exercise.

**D18 actual CI proof:** PENDING at initial document creation; record final tested SHA, run ID, pass/fail counts and exceptions in `STATUS.md` / `HANDOFF.md` only after confirming jobs.

## Out-of-scope and release blockers

No customer files/consent, private web crawling, arbitrary site cloning, database joins, public hosting, source/vendor redistribution, auto-install, payment or signed/commercial clearance. Actual nondeveloper Windows onboarding, real client/reference permission, three human-timed jobs, legal NOTICE/rights, security/PII/backup and 300k KRW fixed scope/support/refunds remain **G5/G6 BLOCKED**. No production URL or Vercel deployment.
