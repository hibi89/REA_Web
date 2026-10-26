# D27 — generated Windows app Python discovery parity (2026-10-27 KST)

## Demonstrated code-level operator defect

The OUTER pilot kit `CHECK_PILOT_WINDOWS.cmd` tries the Windows `py` launcher and the `python` command. The **generated INNER delivery** (on D26) only used the literal `python` command for both `check_windows.cmd` and `launch_windows.cmd`. Some legitimate Windows Python installations provide `py -3` but have no `python` executable in PATH (or leave PATH pointing to an older Python). With such an environment, the generated app reports command-not-found without trying the installed Python. That is an observable packaging/diagnostic incompatibility, **not** evidence of a completed real operator trial.

## Bounded correction

In `rea/delivery.py`, both generated `.cmd` templates first silently check whether `python -c "import sys; sys.exit(...)"` is Python >=3.11, then use that very interpreter. If not available/current, they test the Windows Python launcher `py -3` for Python >=3.11 and invoke the SAME shipped `self_check.py` with `py -3`. If neither is usable, both explicitly emit `[REA] MISSING_PYTHON`, return code **10**, and **never install or run an app**.

- Human `check_windows.cmd` double-click still waits for keypress even when missing Python; automated `--check` never pauses. Python preflight, integrity and dependency errors preserve the checker return code.
- `launch_windows.cmd` still invokes **only** validated `self_check.py --launch`; port validation and Uvicorn `127.0.0.1` shell-free argument vector are unchanged; no CMD expansion of `REA_WEB_PORT`.
- Only interpreter version probes hide their output. Actual checker results and failures are displayed. Selection is deterministic; there is **no implicit downgrade or change of interpreter after a failed package check**.
- Windows README now explains interpreter order and that optional user-approved dependency installation (never automatic) must target the same interpreter, i.e. `python -m pip` or `py -3 -m pip`.

## Test and proof contract

`tests/test_d27_python_discovery.py` covers shipped batch bytes and no network/installer commands and, on **real native Windows cmd.exe**, a test PATH that deliberately lacks `python.exe` but provides a local test-only `py.cmd` shim to the CI-installed Python executable; positive `--check`, human readable no-arg pause, `--launch` hostile port blocked without app startup, out-of-date `python.cmd` fallback to working `py`, and both missing interpreters exit10. A separate actual host PATH test confirms prior Python behavior remains. No customer files or network used by these tests.

`.github/workflows/rea-d27.yml` keeps all D1–D27 Linux/Windows pytest and prior actual Linux Tk/Chromium 8+3, Windows native CMD plus real Tk→APPEND ZIP→fresh isolated venv localhost HTTP, original pinned Fable88/Astra P4 PARTIAL103 proofs and outer 10-member synthetic owner kit checker. **D27 may be marked verified only with exact source SHA and BOTH Linux/Windows completed SUCCESS including real native Windows interpreter-selection tests and artifact.**

## Boundaries

This does NOT prove real nondeveloper Windows acceptance. A publisher identity/rights check, installed package security, arbitrary system configurations and business licenses remain unverified. Actual human Windows session/time logs, 3 genuinely measured client service jobs, approved customer/reference rights and Fable/Astra/dependency redistribution NOTICE, privacy/security/backup, written KRW300k SAME-SCHEMA ROW APPEND-only scope/support/refunds are G5/G6 **BLOCKED**. No PR merges, real customer data, production or Vercel.

## CI follow-up (2026-10-27 KST)

Initial run #40376830500 revealed a test assertion mismatch (checker stores exit code10 in `_rea_check_code` for visible no-arg pause; test assumed direct `exit /b 10`) and a genuine Windows test harness issue: `py.cmd` test-only launcher wrapper takes control away from its calling `.cmd` unless invoked through CMD `call`. Updated both generated entrypoints to use `call py -3` for version probe and dispatch; this also supports a Windows environment where `py` itself is a script-wrapper, while real `py.exe` remains supported. Original `python` primary path remains unchanged. These are **source corrections, not verified successes** until a fresh exact SHA Linux and native Windows workflow completes. The test now verifies the checker's actual status-variable propagation and app launcher's direct exit10. Earlier failed run cannot be reused for acceptance.
