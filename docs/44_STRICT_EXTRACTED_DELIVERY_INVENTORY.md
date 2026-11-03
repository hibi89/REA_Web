# D25 — no unlisted files in extracted delivery ZIP (2026-10-27 KST)

## Evidence-based problem

The owner *outer* synthetic pilot ZIP D23/D24 has a strict file-tree check. However, each owner-authorized generated website in the **inner delivered ZIP** has its own shipped `self_check.py`. At D24 that local diagnostic checked listed files against `delivery_manifest.json` and SHA256, but did **not** enumerate the extracted directory to reject an added `.cmd`, `.exe`, unexpected Python file, hidden file or extra directory. A valid listed set **plus** an unlisted file could therefore still print `PASS_LOCAL_PREREQUISITES_NOT_COMMERCIAL_CLEARANCE`. This is a verification gap (not evidence of historical exploitation).

## Narrow correction

- `rea/customer_self_check.py` now includes `verify_exact_delivery_tree(root, members)`, a **standard-library only, read-only** traversal of the extracted customer delivery. It computes allowed file paths from the delivery manifest, requires the listed `delivery_manifest.json`, and derives permitted parent directories. Extra files/directories, hidden executables, symlinks, wrong file types and even empty extra folders all cause **FAIL_LOCAL_PREREQUISITES** before a read-only SQLite check and before the local app can launch. It does not read unknown file contents, start a listener, contact a server, change customer data or install packages.
- The existing D24 `launch_windows.cmd` invokes `self_check.py --launch`; any failed preflight still blocks Uvicorn. Validated ASCII port 1–65535 and fixed `127.0.0.1` binding remain.
- A successful server run commonly creates Python bytecode files in `app/__pycache__`. These files are **not** in the manifest, so the launcher now passes `PYTHONDONTWRITEBYTECODE=1` to its child Uvicorn process to keep subsequent preflights reproducible. Extract into a fresh empty folder; never run unknown files or manually modify a packaged website and expect it to be approved. Existing altered installations require re-extraction from a trusted original ZIP.
- `rea/delivery.py` Windows README explicitly explains clean new-folder extraction, unlisted-file refusal and preserved original content.

## Tests and completion criteria

`tests/test_d25_delivery_inventory.py` covers clean package repeat checks without mutating source, extra root `.cmd`/`.exe`/hidden and nested `app/` or `app/static/` files, empty unknown directories including cache, symlinks and symlinked expected folder refusal, confirmed non-launch for added files, real customer-side shipped selfcheck exit2 with no false successful integrity, and actual Windows native `cmd.exe` fail-closed. It also verifies the subprocess launch environment prevents Python bytecode writes.

`.github/workflows/rea-d25.yml` retains D24 complete Linux/Windows tests, Linux real Chromium **8+3**, actual GUI exercises, Windows real Tk→ZIP→fresh isolated venv localhost HTTP, native CMD positive and negative cases, pinned vendor Fable 88 and Astra P4 PARTIAL 103 SHA, and ten-file synthetic owner pilot selfcheck. D25 is complete ONLY when GitHub Actions at the exact tested feature SHA show both OS **COMPLETED SUCCESS**, per-OS pytest count and generated synthetic-only artifact.

## Explicit limits

This checks unexpected **filesystem entries**, not a malicious source that rewrites BOTH the manifest and original file hashes. SHA256 is not an author signature, human acceptance, software authenticity, legal rights grant or comprehensive penetration test. Users must not treat a check success as personal-data compliance, server deployment, customer authorization, or commercial readiness. G5/G6 (real user Windows session, 3 actually time-measured human jobs, rights/NOTICE, privacy/security/backup, agreed KRW300k scope/support/refunds) are **BLOCKED**. Draft PR/unmerged, no real customer file, vendor source changes, paid installs, cloud or Vercel.
