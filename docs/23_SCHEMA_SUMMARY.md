# D4-01 — CSV field preview and category summary

Generated local webapp now includes a read-only category count panel and
expandable CSV column preview. The values are supplied only by customer CSV.

## Evidence contract
- /api/summary counts items grouped by original CSV category; no inferred formula.
- /api/schema returns field header names, lexical type hints (integer,
  decimal, date, text, mixed, unknown), and nonempty/empty counts only.
  No cell samples, raw Fable capture, original website credentials or URLs.
- All lexical types remain UNAPPROVED. approved_semantic_bindings is empty.
- Optional Fable record review stays separate and is never used for automatic
  data mapping. Report files are not served as web endpoints.
- DOM uses textContent, category count display caps 100 groups.

## Local smoke
Python 3.11+, FastAPI and Uvicorn:
    python -m rea.orchestrator --csv samples/qa_cafe.csv --out ./out/cafe
    cd out/cafe
    python -m uvicorn app:app --host 127.0.0.1 --port 8000

Workflow tests D1-D4 regressions on Linux and Windows, with actual Chromium
checks for 3 synthetic scenarios on Linux and CMD/localhost smoke on Windows.
Do not report PASS without checking completed GitHub Actions results.

Missing before sale: JSON/two-file promised intake, approved mapping wizard,
commercial redistribution licenses, clean customer Windows setup, full
security/recovery and authorized real-customer/site acceptance.
