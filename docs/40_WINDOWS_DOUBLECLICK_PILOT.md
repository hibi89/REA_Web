# REA_Web D21 — Windows double-click offline pilot checker

## Choice
A: Include a native Windows CHECK_PILOT_WINDOWS.cmd as ninth SHA-pinned member of synthetic-only owner kit. Requires existing Python 3.11+; never pip-installs, contacts network, starts a generated app, elevates privileges, modifies customer files, or contacts cloud. B: EXE/MSI/winget installers deferred pending redistribution/signing/security decisions.

## Manual operator instructions
1. Extract the synthetic-only GitHub Actions kit ZIP into a NEW folder. SHA256 integrity is not publisher authentication or copyright permission.
2. Double-click CHECK_PILOT_WINDOWS.cmd. Its window holds the result. Automated or Command Prompt usage: CHECK_PILOT_WINDOWS.cmd --check (without pause).
3. The launcher checks existing py -3.11 and then existing python version. Missing both prints MISSING_PYTHON (exit 10), missing local checker prints MISSING_CHECKER (exit 11), invalid arguments print INVALID_ARGUMENT (exit 2). No installation or downloads.
4. Read OFFLINE_KIT_INTEGRITY_PASS for nine exact members, five public synthetic rows, same-schema APPEND receipt. Failures show KIT_NOT_VERIFIED and preserve the underlying code. Do not open the app after a failed check.
5. See README_WINDOWS.txt to separately launch the local read-only demo at 127.0.0.1. This step is never performed by the wrapper.

## Code and tests
- scripts/d21_check_pilot_windows.cmd: uses cmd.exe, per-process UTF-8, local script beside launcher (Windows batch directory expansion), Python version check, no-argument pause versus noninteractive --check, and no env/registry changes.
- scripts/d19_owner_pilot.py: exact CMD source inside 9-member manifest, fixed SHA and deterministic no-overwrite ZIP; original synthetic CSV/JSON fixture allowlist unchanged.
- scripts/d20_offline_kit_check.py: includes CMD in file integrity allowlist.
- tests/test_d21_windows_pilot_cmd.py: Linux source tests and Windows native cmd.exe tests for successful --check, double-click, nonzero on missing Python / missing checker / bad args / tamper, spaces and metacharacter paths, original unchanged.
- .github/workflows/rea-d21.yml: all existing Linux and Windows pytest, 8+3 real Chromium and Windows GUI ZIP HTTP plus specific native CMD tests; synthetic-only artifact.

## Boundaries
Do not mark D21 verified until exact code SHA both OS CI succeeded. Human nondeveloper Windows user acceptance and elapsed time NOT_RUN; clients/third-party redistribution, NOTICE, 3 real timed orders, security/privacy/backup, 300k KRW scope/refunds/support BLOCKED. PR Draft, unmerged, no production/Vercel.