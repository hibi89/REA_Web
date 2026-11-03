# REA-MVP-D7-01 — security/recovery failure-injection report

Scope: offline synthetic samples and local FastAPI/SQLite/ZIP only.
**NOT** a production penetration test or assurance of commercial safety.
Exact PASS counts and CI SHA must be recorded after the workflow succeeds.

## Findings, remediations and verification

| Risk | Finding / change | Actual D7 validation |
| --- | --- | --- |
| Owner folder overwritten during race | Linux generic directory rename may replace an existing empty directory. New rea/safe_publish.py uses Linux renameat2(RENAME_NOREPLACE); Windows directory rename rejects existing destination. Unsupported OS fails closed. | Inject race with owner empty/nonempty directory; destination preserved, stage cleaned |
| Partial ZIP exposed or left behind | Old publish copied bytes into destination file while file was visible. New flow verifies complete staged ZIP then uses same-filesystem os.link atomically, never replacing existing archive. Filesystem without hard links fails closed. | Inject owner archive race, simulated unsupported hardlink, failed ZIP verification, ensure absent/unchanged output and cleanup |
| Output symlink redirect | Generator uses literal absolute output leaf instead of resolving symlink; checks existing and broken symlink. | Broken redirect and owner destination cases |
| Generated SQLite writable connection | Generated app URI constructed via Path.as_uri with mode=ro, explicitly sets PRAGMA query_only=ON. | INSERT blocked, POST/PUT/DELETE APIs reject writes |
| JSON category origin mislabeled CSV | API summary previously hardcoded CSV snapshot even for JSON sources. | Reads source_kind from locally generated unapproved schema preview, tested JSON |
| Malformed data and SQL queries | Existing bounded CSV/JSON parsing and SQL bound parameters retained; wildcard LIKE properly escaped. | Negative format/ID/size tests, injection-like/wildcard search |
| HTML / CSV spreadsheet formulas | CSV formula-looking values are kept as text, rendered with textContent in HTML; no spreadsheet export feature exists. | Added synthetic formula dataset to actual Chromium: no JavaScript dialogs/external requests |
| Zip contents | D3 checksum, D6 exact file allowlist and review unapproved status maintained. | Corrupt ZIP and unexpected vendor/secret file injection tests |
| Fable report / metadata | Optional review-only Fable report remains separate, not web served, no semantic autoapproval. | Existing review contract tests and HTTP 404 metadata tests |

## Platform boundaries and recovery

- Linux: renameat2 on local filesystem; Windows: regular directory rename
  rejects existing target. macOS and unsupported operating systems fail closed
  for directory publication until safe atomic no-replace is independently added.
- ZIP publication uses hard links between files located under the same
  destination parent filesystem; on a drive/share without hard links it fails
  without writing a partial delivery. NTFS/ext4 GitHub runner evidence is not
  evidence about arbitrary network, removable or encrypted drives.
- Staging exceptions should remove private temporary directories and preserve
  source and existing destination. Abrupt power loss/fsync and backup recovery
  after hardware failures remain NOT_RUN. SQLite backup/restore procedure also
  remains NOT_RUN.
- The user can override localhost restriction by launching Uvicorn manually
  with an unsafe --host; this product only supports loopback.
- data.sqlite **contains input rows**, therefore no claim of redaction or
  secret-free deliverable. Do not use real customer data in public CI.
- CSV formula cells are NOT safe to write straight back into a spreadsheet.
  If exporting XLSX/CSV is added later, apply output-specific formula escaping.

## Release blocker ledger

- Owner product draft: up to 2 data files. Currently 1 CSV OR 1 JSON only.
  No approved multi-file join, mapping or scope revision. BLOCKED.
- Fable and Astra source hashes are verified, but source commercial licensing
  and generated-code/customer distribution terms not cleared. BLOCKED.
- Runtime dependency exact version locks, transitive notices, vulnerability
  audit and full SBOM not complete. NOT_ASSESSED.
- Clean nondeveloper Windows setup/browser and authorized real customer/site
  reference acceptance not performed. NOT_RUN.
- Full production security, adversarial multiuser, filesystem actor, recovery
  tests and merchant support/refund policy not done. NOT_RELEASE_READY.

Evidence workflow: .github/workflows/rea-d7.yml, source tests/test_d7_recovery.py,
browser scripts/d3_browser_acceptance.py (five synthetic cases), safe publisher
rea/safe_publish.py. New GitHub Draft PR targets integration/develop and must not
be merged automatically.
