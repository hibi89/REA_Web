# 2026-10-30 local Windows snapshot recheck

## Scope and source identity

- Tested a separate working copy made from `E:\REA_Web_Kmong\REA_Web-feature-d27-windows-python-discovery`; the provided source folder was left unchanged.
- The supplied folder is a ZIP snapshot with no `.git`. The recorded GitHub branch head at the time of this check was `f6e34f604cc2769f06927af8b9cd5ac6aad998f4`.
- The snapshot differs from that remote tree in 17 tracked files and lacks three remote files. This report is explicitly **not** an exact-head full regression.
- To remove two stale D8 CP949 failures, the isolated copy's `rea/guided.py` and `tests/test_d8_guided.py` were replaced with the byte-identical current-head copies already verified in the separate QA workspace. SHA-256 matched between the two copies for each file. No customer data was used.

## Results

| Check | Result | Notes |
| --- | --- | --- |
| Full local Windows suite, unfiltered | **FAIL: 396 passed, 22 skipped, 8 failed** | Six failures could not create symlinks (Windows `WinError 1314`); two came from stale D8 files in the snapshot and disappeared after syncing the current-head files. |
| Full suite after current-head D8 sync and explicit symlink deselection | **398 passed, 22 skipped, 6 deselected** in 98.73 seconds | The six exclusions are precisely tests requiring Windows symlink privilege, unavailable on this test host. |
| D27 Python discovery tests | **3 passed** | Executed on native Windows, including CMD launcher selection cases. |
| Chromium synthetic app flow | **7 passed** | Inventory, JSON, formula escaping, owner-mapped CSV/JSON, approved same-schema two-file ROW APPEND, and trends. Search/filter/detail/reload passed; JS errors, dialogs, and unexpected network requests were zero. |
| Optional Fable+Astra browser case | **BLOCKED** | Local snapshot lacks `astra_contracts`; current-head GitHub D27/D3 CI evidence is separately recorded in the commercialization evidence bundle. |

The default D3 browser script expects the optional Astra checkout for its Fable fixture. The local run therefore executed the seven independent CSV/JSON/mapping/append cases and omitted only that optional fixture. The Chromium script's own JSON metadata is conservative and labels the process environment as CI; this report identifies the actual run as local Windows and does not use that field to claim CMD coverage.

## Evidence and limits

- Full regression command: `python -m pytest -q -p no:cacheprovider` with six explicit `--deselect` selectors for the Windows symlink-privilege cases.
- D27 command: `python -m pytest -q -p no:cacheprovider tests\test_d27_python_discovery.py`.
- Chromium command: imported `scripts.d3_browser_acceptance`, excluded only the case marked `fable=True`, then called its actual `main()` with a fresh report directory.
- The Chromium run is synthetic only. The local workspace is not a complete checkout at the remote branch head; exact-head CI, current-head sample ZIP checks, and human acceptance are separate evidence.
- Customer Windows acceptance remains **NOT_RUN**. Commercial/source/dependency redistribution clearance remains **NOT_GRANTED**. This report does not authorize publishing the service.
