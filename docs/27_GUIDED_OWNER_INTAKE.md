# D8-01 Guided owner input and explicit field approval

## Workflow (one private local file only)

**Inspect**, without printing record values:

    python -m rea.guided inspect --csv samples/qa_guided.csv

Shows source column names, counts, lexical type hints and input SHA-256.

**Interactive wizard**, prompts for id/title/category *source* column names,
shows the chosen mapping and requires the literal word APPROVE:

    python -m rea.guided wizard --csv samples/qa_guided.csv --out ./out/demo

**Noninteractive after a human's explicit review** (digest copied from inspect):

    python -m rea.guided build --json samples/qa_guided.json --id-field item_code --title-field label --category-field region --source-sha256 HEX64 --confirm APPROVE --out ./out/demo

Replace build with pack to deliver an audited standalone ZIP. Exact existing
CSV/JSON fast-path CLIs continue unchanged for already matching schemas.

## Controls and evidence

- No mappings selected automatically and no Fable technical hints used for
  mapping. All three source columns must exist and be DISTINCT. Values must
  pass duplicate id, required nonblank, size/row/field limits and type checks.
- Preflight prints no cell values and supplies SHA256. Build verifies source
  SHA before generation and rejects changed source. Source never uploaded.
- Generated app manifest and non-web-served mapping_report.json record exact
  approved source columns, original file SHA, single-local-build approval
  state, and prohibition of Fable-inferred mapping.
- D6 package audit checks matching map report, source digest, receipt states
  and allowed ZIP members. Lexical type preview remains UNAPPROVED; a CLI
  confirmation is NOT a signed or externally authenticated owner consent.
- Only one owner-provided nonsensitive UTF-8 CSV or flat string-valued JSON,
  10 MiB, 10,000 rows, 20 fields, 2,000 chars/cell. No implicit 2-file join,
  arbitrary URL, real-site capture, live DB, paid APIs, public hosting or
  production credentials.

## Verify real CI

D8 workflow runs D1-D8 tests on Ubuntu and Windows, seven local real Chromium
synthetic scenarios (including two custom-map datasets), native Windows
CMD/localhost HTTP, 88 Fable and partial 103 Astra immutable Git blob checks,
package hash/allowlist and negative approval tests. Do not claim CI success
until the run actually finishes.

## Remaining before selling
Draft 300,000 KRW offer promises up to TWO files, which is NOT implemented.
Owner-approved combined-data mapping or approved scope revision required.
This is a CLI, not a three-mode consumer GUI; clean nondeveloper Windows
human test, real authorized customer/reference test, full dependency license
and notices, commercial rights, privacy review, backup/power loss, complete
pentest, support/refund contract are NOT RUN / BLOCKED. Test success is not a
commercial license grant or production security certification.
