# D24 — Windows local launch: validated port, no command interpreter injection

## Concrete risk and bounded fix

Previously the generated delivery ZIP's `launch_windows.cmd` contained an unquoted `--port %REA_WEB_PORT%` expansion. When the environment variable includes Windows CMD metacharacters (such as `&`, `|` or `>`), that text should never be placed into a command interpreter as code. This is a code-level injection risk; it does **not** establish any historical exploitation.

**Chosen implementation:** the shipped `launch_windows.cmd` now invokes `python "%~dp0self_check.py" --launch` with no expansion of `REA_WEB_PORT` at all. The existing stdlib `self_check.py` runs its full delivery integrity/preflight first and refuses to start if the source files/dependencies have changed. It parses `REA_WEB_PORT` using a strict ASCII decimal grammar from `1` to `65535` without leading zeros. Default port is `8000`.

Upon successful preflight, Python runs Uvicorn through `subprocess.run([sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", str(port)], cwd=extracted_app)`, **without a shell**. The host is fixed to loopback. On invalid port or integrity failure, launcher exits nonzero and prints `REA_LOCAL_LAUNCH_BLOCKED`. No auto pip, winget, admin, registry, outgoing network or real customer data.

## Behavior and independent evidence

- `rea/delivery.py`: deterministic CRLF CMD template, Windows README explaining validated port and exact local-only behavior; rest of generated ZIP format unchanged.
- `rea/customer_self_check.py`: remains a read-only stdlib diagnostic when run without `--launch`; new explicit mode performs preflight then launches in a shell-free argument vector. Existing `check_windows.cmd` remains diagnostic-only. Does not claim legal/PII/redistribution clearance.
- `tests/test_d24_safe_loopback_launch.py`: allowed 1..65535, default and Windows metacharacter rejection, full generated ZIP and byte-level CMD template, tamper denial before spawning, actual Python argv host/port/cwd assertion, extracted `self_check.py` compatibility. On actual Windows CI: native `cmd.exe` with an injected `REA_WEB_PORT` must return nonzero and cannot create a sentinel file. Earlier Windows smoke also exercises the REAL generated launcher with a valid bound port and HTTP four rows; D18 separately tests Tk→two-source ZIP→fresh isolated venv localhost five rows.
- `.github/workflows/rea-d24.yml`: preserve full Linux/Windows pytest, Chromium 8+3 extracted apps, actual Linux Tk/Windows fresh venv and native CMD, pinned Fable 88/Astra P4 PARTIAL103 proof, ten-member synthetic owner kit. Specific Windows negative `cmd.exe` test is also a named CI step.

## Completion and release boundaries

Code alone is NOT a verified milestone. D24 passes only if an exact matching source SHA has completed SUCCESS on both OS including actual Windows CMD negative and positive, Linux Chromium 8+3 and synthetic extracted owner kit. This check is not a general penetration test, software authenticity signature, license approval or a real nondeveloper user acceptance. All PRs Draft/unmerged, no production or Vercel, no real customer data, G5/G6 rights/NOTICE/privacy/backup/3 human timed jobs/KRW 300k scope-support-refunds remain BLOCKED.
