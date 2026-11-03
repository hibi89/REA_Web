# D26 — readable Windows generated-app prerequisite diagnostics

## Evidence-backed operator issue

The D25 synthetic Windows guide explicitly says **double-click `check_windows.cmd`**, but the generated INNER app ZIP used the batch file `@echo off; setlocal; python "%~dp0self_check.py"; exit /b %errorlevel%`. On a typical File Explorer double-click, the transient Command Prompt terminates as soon as Python exits, leaving a nondeveloper with no opportunity to read either PASS or missing Python/dependencies/SHA failure details. The OUTER pilot kit's `CHECK_PILOT_WINDOWS.cmd` had already implemented visible double-click diagnostics; the generated app did not. This mismatch does **not** establish that a real human tested it.

## Narrow operator fix

- `rea/delivery.py` `CHECK_LAUNCH` in every NEW generated ZIP has a manual no-argument path that runs the existing local Python read-only `self_check.py`, captures its exit code, displays an explicit failure warning when nonzero, and **pauses until a keypress** to let a person read status. The `--check` mode performs the **same** diagnostic and exits without a pause for CI or scripts.
- Reject unknown or multiple arguments with exit code 2, do not run any web server from the check, never auto-install, elevate, update registry or access remote URLs. Preserve the underlying checker exit code 0/2 (and other runtime failures), the local-first boundaries, and the existing generated `launch_windows.cmd` D24 safe port/loopback behavior.
- The ZIP's `README_WINDOWS.md` distinguishes **File Explorer double-click** from **already-open Command Prompt `check_windows.cmd --check`**. Existing D10 Windows CI diagnostic invocation updated to `--check` to avoid a user-only pause in automation.

## Tests

`tests/test_d26_customer_check_doubleclick.py` checks a fresh synthetic generated ZIP's exact CRLF batch payload, expected guidance, static no network/install/app-start, existing standalone read-only checker and on **native Windows** actual `cmd.exe` using a folder with spaces and `&`:
- script-mode `--check` returns 0 and **does not pause**
- double-click-like no-arg invocation with one newline on stdin visibly pauses then forwards 0
- invalid arguments refuse with 2 and never show a success
- tampered app file fails 2 on both modes, visible pause only in manual mode
- manual/human acceptance remains `NOT_RUN`; no process or original generated data changed.

`.github/workflows/rea-d26.yml` retains full D1–D26 pytest on Linux/Windows, real Linux Tk widgets and Chromium 8 synthetic apps + 3 extracted delivery ZIP browser flows, Windows native CMD and Tk GUI→ZIP→fresh isolated venv→127.0.0.1 HTTP 5 rows, pinned Fable88/Astra P4 PARTIAL103 source hashes and owner outer synthetic 10-member checker. **Do not mark D26 verified until exact current source SHA both jobs COMPLETED SUCCESS** with actual Windows native pause proof and synthetic artifact.

## Boundaries

A synthetic native Windows `cmd.exe` invocation with simulated user input is NOT real nondeveloper usability acceptance. Human pilot, real logs/time, customer/reference rights, commercial license redistribution/NOTICE, privacy/security/backup, and KRW 300k SAME-SCHEMA APPEND-only scope/support/refunds all remain G5/G6 BLOCKED. All feature PRs Draft/unmerged; no production or Vercel.
