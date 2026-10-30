# Synthetic backup/restore and runtime inventory evidence — 2026-10-30

## Baseline

- Repository: `hibi89/REA_Web`
- Branch: `feature/d27-windows-python-discovery`
- Source baseline: `97f1ea7d3ce551494ac44e93d1f90bcd27cdc400`
- Evidence uses the repository's synthetic `samples/qa_cafe.csv`; no customer data was opened.

## Manual backup and recovery rehearsal

- Rebuilt a synthetic CSV delivery ZIP using the current local source; archive CRC passed and it extracted to a fresh isolated path.
- Read the generated `README_WINDOWS.md` and confirmed it directs the user to stop the server, copy the complete extracted delivery folder to a private location, and restore from the original ZIP into a new empty folder if files are damaged.
- Ran the actual Windows `cmd.exe /d /c check_windows.cmd --check` against both the extracted delivery and the restored copy. Both returned the expected local-prerequisite pass marker.
- Created a copy of the complete extracted folder as the manual backup, then copied that backup into a separate restore folder. SHA-256 inventories matched across the original extraction, backup and restored folder (15 files).
- SQLite `PRAGMA quick_check` returned `ok`; the generated database contained 4 synthetic rows before and after copying.
- The synthetic input CSV SHA-256 remained unchanged. The archive contains no raw `.csv` source member. Derived `manifest.json` and `schema_preview.json` contain metadata; the scan found none of the distinctive sample titles/descriptions in those metadata files. The SQLite database intentionally contains the generated rows, and the ZIP is unencrypted.
- Receipt: `backup_restore_recheck_20261030.json` in the local evidence bundle.

This verifies the documented manual copy/restore procedure and package preflight. It does not verify HTTP relaunch after restore, an independent customer's Windows environment, or a human acceptance session. The app has no automatic backup feature.

## Runtime dependency metadata observation

A read-only walk of the active dependency markers in the developer's Windows Python 3.11.9 environment found 14 distributions and 19 active dependency edges; no missing distributions, direct-range violations, or requirement parse errors were observed. `pip check` passed, and an installed license/notice metadata file was present for each observed distribution.

This is not an exact customer lockfile, signed SBOM, wheel-hash verification, vulnerability audit, legal review, or license grant. Source and dependency commercial redistribution rights remain **NOT_GRANTED**. Inventory JSON: `observed_runtime_dependency_graph_windows_20261030_97f1ea7.json` in the local evidence bundle.

## Current release gates

- Human customer Windows acceptance: **NOT_RUN**.
- Customer data authorization/privacy operations review: **NOT_APPROVED**.
- Source/vendor/dependency redistribution rights: **NOT_GRANTED**.
- Seller terms and commercial listing approval: **NOT_APPROVED**.
- Local native localhost smoke remains blocked by sandbox `WinError 10013`; no localhost PASS is claimed.
- Automated synthetic checks do not close any of these gates. The product remains **NOT_APPROVED_FOR_SALE**.

