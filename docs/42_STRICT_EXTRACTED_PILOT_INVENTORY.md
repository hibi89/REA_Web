# D23 — strict extracted synthetic pilot folder inventory (2026-10-27 KST)

## Finding

The previous D22 integrity script verified the SHA256 of all **ten listed files**, but it did not enumerate the extracted directory to refuse **additional** files or directories. A kit containing all valid source files *plus an unexpected executable* could still print `OFFLINE_KIT_INTEGRITY_PASS`. File hashes do not validate unexpected files and are not signatures/rights grants.

## Narrow fix

- `scripts/d20_offline_kit_check.py` now calls `verify_exact_extracted_inventory()` **before** trusting the manifest. The only permitted root files are the ten member names without a slash; permitted subfolders are exactly `sources` and `demo` with their manifest-defined fixed immediate file names. Additional files, hidden entries, extra directories, unknown executables, symlinks, or expected paths whose types changed are rejected.
- This preflight is fully stdlib, read-only, no network or install, no app launch, and no access outside the extraction root. New helper has no bytes of customer content in output. The existing manifest SHA/source fixity, human logs blank, 3+2 APPEND and `NOT_GRANTED` requirements remain unchanged.
- The launcher `CHECK_PILOT_WINDOWS.cmd` still invokes the same checker; it propagates failure. A real person should **never run unknown extra files** and should re-extract the trusted synthetic ZIP into a new clean folder after failure. Windows README describes this constraint. Human log copies remain outside the original folder.

## Tests

`tests/test_d23_extra_extracted_entry.py` checks genuine extracted clean kit remains valid and unmodified; extra root `.exe`, `.cmd`, `.hidden`, `desktop.ini`, extra fixture/ZIP, unknown folders (including empty), foreign symlinks, missing known file, subprocess CLI refuses unknown file without PASS, copies of logs stored OUTSIDE kit do not affect validation.

`.github/workflows/rea-d23.yml` runs the **unchanged** full Linux+Windows D1–D23 pytest suite plus Linux actual Tk and Chromium 8+3, Windows native CMD, fresh isolated Tk→ZIP→localhost HTTP, pinned Fable 88/Astra PARTIAL 103 original Git blobs, extracted checker and **synthetic-only** kit artifact. Only mark D23 VERIFIED after both real OS jobs complete success at exact feature SHA and artifact is inspected.

## Boundaries

This catches accidental/malicious **unexpected directory entries**, not a determined adversary that replaces Python executable, Python stdlib, OS, GitHub source, or all hashes/manifest with new values. SHA256 is **not a code signature** and this is **not a penetration audit**. This change does not claim a real nondeveloper Windows session, legal/data usage consent, privacy clearance, human labor cost or buyer acceptance. No customer data, Vercel/production, paid dependencies or vendor source editing. D23 Draft/UNMERGED, G5/G6 blocked.
