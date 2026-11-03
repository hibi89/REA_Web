# D9-01 — Two-source explicitly approved same-schema ROW APPEND

**Scope is narrow:** two distinct owner-authorized local CSV/flat JSON files,
which become one independent read-only SQLite app by **adding rows**. This is
not an arbitrary join, relation matching, lookup, record overwrite, AI semantic
mapping or a general-purpose two-file integration product.

## Local procedure
1. Preview both files (prints *column metadata* and SHA256, not record values):

    python -m rea.two_source inspect --first samples/qa_guided.csv --second samples/qa_pair_extra.json

2. Select exact three source fields for id/title/category, and confirm
   that these are the intended same-schema rows. Provide both source fingerprints
   as returned by inspect. For both sources, separately type APPROVE. To consent
   to row append specifically, type APPEND. For noninteractive execution:

    python -m rea.two_source build --first samples/qa_guided.csv --second samples/qa_pair_extra.json --id-field sku --title-field display_name --category-field group_name --first-sha256 FIRST_HEX --second-sha256 SECOND_HEX --approve-first APPROVE --approve-second APPROVE --confirm-append APPEND --out ./out/two-sources

   Use pack instead of build and a new .zip --out path for independent customer
   delivery. No auto-selection or default consent. Literal tokens do NOT
   authenticate owner identity or amount to a signed customer contract.

3. Generation rejects mismatched normalized columns, repeated IDs across both
   files, any malformed/nested/non-string source cell, missing required mapped
   values, duplicate aliases, symlinks, source changes, combined >10,000 rows,
   combined source bytes >10 MiB, or normalized output >10 MiB.
   Both sources must have the same explicit id/title/category source field
   mapping and matching normalized remaining column sets.

## Data and evidence boundaries
- Temporary normalized CSV is deleted; generated ZIP contains app/data.sqlite,
  app/manifest.json and app/append_report.json, NOT the two original sources.
- append_report.json keeps only both source SHA-256 digests, source types,
  row counts, selected field mappings, explicit local confirmation states,
  no row values, and mode SAME_SCHEMA_ROW_APPEND_NO_JOIN.
- D6 rea.provenance.inspect_delivery enforces the report/manifest pair and
  delivery checksum allowlist; missing, inconsistent approval receipts fail.
- The generated webapp remains readonly/local-only. The generic schema preview
  describes the derived CSV snapshot with review_status UNAPPROVED.
- No external URL, website capture, remote upload or vendor/source changes.
- The existing one-file CSV/JSON and single-file guided mapping CLIs remain
  unchanged. Fable/Astra inference never joins/approves customer data.

## Commercial exclusions / unverified checks
The proposed 300,000 KRW package describes up to two CSV/JSON files. D9 supports
ONLY explicitly approved **same-schema row append**, not two different
business tables linked by keys; the offer requires an explicit supported-scope
decision and owner approval before sale. Fable/Astra/generated source commercial
permissions, transitive dependency NOTICE/SBOM/license review, actual authorized
customer or website rights, general Windows nondeveloper user setup and browser,
data sensitivity screening, disaster backup/recovery, complete penetration tests
and paid-service/refund terms are still BLOCKED/NOT_RUN.

CI D9 runs full D1-D9 Python tests on Ubuntu+Windows, eight actual local
Chromium scenarios including the two-input append, Windows CMD/HTTP smoke,
pinned Fable 88/Astra PARTIAL 103 source blob verifications and safe ZIP audits.
Only mark PASS after checking the completed GitHub Actions jobs.
