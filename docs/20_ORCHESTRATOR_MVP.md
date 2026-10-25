# REA-MVP-D2-02 — optional Fable review and customer CSV app

**Purpose:** CSV is the sole source of generated app data and business behavior.
Fable's separate JSON technical evidence is optional and **never** upgrades
inferred functionality into observed facts or approved customer field mappings.

## Usage (offline; Python 3.11+)

CSV-only (no API key, website, Fable engine or Astra required):
```bash
python -m pip install "fastapi>=0.110,<1" "uvicorn>=0.27,<1"
python -m rea.orchestrator --csv samples/products.csv --out ./out/cafe
cd out/cafe && python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

With a previously obtained **authorized, redacted Fable 1.0** JSON result
(actual Astra contract validation is mandatory in this mode):
```bash
python -m pip install "pydantic>=2.6,<3"
PYTHONPATH=/path/to/pinned-astra/engines/astra_p4:. \
  python -m rea.orchestrator --csv samples/products.csv \
    --fable-result samples/fable_record_redacted.json --out ./out/cafe-reviewed
```
On Windows, use `--astra-root C:\\path\\to\\astra\\engines\\astra_p4`
instead of setting PYTHONPATH. The import must correspond to pinned snapshot
`f044b66e799289a5a353fdb9cbfdb324e683ffa3` (full vendor trees not merged).

**Outputs:** standalone `app.py`, `data.sqlite`, `static/`,
`requirements.txt`, `manifest.json`, `README.md`; optional
`review/fable_review.json` + review README. The raw Fable source is NOT
shipped or served. The review is a separate artifact and does not gate
the simple CSV demonstration; it's always `REVIEW_REQUIRED`.
No user-defined formula, scraping, non-local server, account login or real DB.

**Acceptance:** CI tests both modes, exact imported Astra models, no-overwrite,
CSV equality and true loopback Chromium browser interactions. Windows,
customer data, distribution licensing and product-level permissions not yet
verified. This isn't a full reverse-engineering clone or sale-ready release.

## Reused code provenance (exact pinned Git blob SHAs)
- CSV generator + FastAPI + template assets + 9 baseline tests:
  `feature/csv-local-mvp` @ `5515a7286d63211e32d2c577f93f77d61f37ce08`
- Evidence adapter + 28 tests:
  `feature/evidence-adapter` @ `fda96076de33ebf4f4b6118972a5033a3f703ba9`
- Astra model source: pinned, read-only import
  `f044b66e799289a5a353fdb9cbfdb324e683ffa3`.

Do not edit the source import branches. No deployment. Subsequent D3
checks compare the app with docs/02_ARCHITECTURE.md and docs/14_FINAL_DELIVERABLES.md.
