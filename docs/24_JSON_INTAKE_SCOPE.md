# D5-01 — one-file strict JSON intake, scope reconciliation

## Implemented, without a live website
- Existing one CSV remains exactly supported via --csv.
- New --json supports one local UTF-8/UTF-8 BOM .json, root array of 1–10,000
  **flat objects whose values are all strings**. Required id/title/category
  must be present, nonblank, and id must be unique. All records must have the
  same column names (order may differ). Max input 10 MiB, max 20 columns and
  2,000 characters per normalized cell. No nested objects/arrays, null,
  numeric/bool auto-conversion, duplicate JSON keys, NaN or Infinity.
- CSV and JSON share _validate_records for key/length/duplicate/cell bounds.
- parse_input dispatches by extension; app data generated from that one file
  only. JSON raw source never included in ZIP. Source hash and filename go
  into manifest; sample cell values are not leaked into schema preview.
- New commands:
    python -m rea.orchestrator --json samples/qa_products.json --out ./out/json-demo
    python -m rea.delivery pack --json samples/qa_products.json --out ./out/json-demo.zip
    python -m rea.delivery verify --zip ./out/json-demo.zip
- CSV syntax is unchanged: --csv samples/qa_cafe.csv and CSV-only application
  generation. --csv and --json together intentionally fail.
- Fable JSON (if separately supplied with --fable-result) remains a
  review-only technical artifact, never a source of business fields/formulas.

## Commercial promise vs capability — explicitly NOT reconciled for two files

| Draft KRW 300k offer | Currently implemented | Decision / sale gate |
| --- | --- | --- |
| CSV or JSON | One standalone CSV OR one strict JSON | Tested at D5; this portion supported |
| Up to 2 files | **One input file only** | UNSUPPORTED. No implicit join, union, lookup or duplicate-ID merge; owner must approve a clear two-file contract and mapping before selling under that promise |
| 10k rows / 20 columns / 10MB combined | 10k/20/10 MiB limit on one input | Combined multi-file cap not meaningful until two-file workflow exists |
| 2 screens / up to 3 features | Existing local list/search/filter/detail and read-only category summary | Scope/feature count must be explicitly agreed, not silently changed |
| One authorized reference | Optional separate Fable review, no automatic original-site parity | Source/rights approval and real reference still NOT_RUN |
| Source ZIP and Windows guide | Synthetic ZIP/manifest, Windows native API smoke | Licenses, clean PC UX, actual customer acceptance NOT_DONE |

Two separate datasets may have incompatible meanings. Automatically combining
them would fabricate relationships and could violate user ownership/intent.
Do not market 'up to 2 files' as supported until a tested rule/owner-reviewed
mapping wizard or an expressly approved change to the commercial offer.

## CI acceptance / limitations
Workflow .github/workflows/rea-d5.yml runs Linux/Windows regression with
the pinned Astra contract import, Linux actual Chromium for cafe/inventory/
trends and JSON products, Windows extracted .cmd HTTP smoke, and generates
two synthetic ZIPs with checksum verification. Check real run logs before
claiming success. Full vendor redistribution rights, dependency licenses,
commercial security/recovery, end-user Windows PC and authorized customer/site
pilot all remain release blockers.
