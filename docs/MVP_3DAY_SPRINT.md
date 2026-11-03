# REA_Web / 3-day MVP spike

**Not the final Fable→Astra integrated product.** It is the first real vertical slice: customer CSV → SQLite → generated independent FastAPI app → interactive list/search/category filter/detail.

## Local run (Python 3.11+)
From repo root:
    python -m pip install fastapi uvicorn pytest httpx
    python -m rea.mvp --csv samples/products.csv --out ./out/demo --name "내 상품 관리"
    cd out/demo
    python -m uvicorn app:app --host 127.0.0.1 --port 8000

Open http://127.0.0.1:8000/. Do not bind to 0.0.0.0 or expose to internet: no authentication, readonly local MVP.
Tests (repo root): python -m pytest -q tests/test_mvp.py

## Function contract
Requires UTF-8 CSV with id,title,category headers; other columns appear as attributes. At most 10 MB, 10k records, 20 columns, no duplicate IDs. Output directory must not exist. SQL is parameterized, read-only API, static DOM uses textContent rather than injected HTML. The original CSV is never modified.

## Backlog for 3-day sprint
Day 1: working app generation from supplied CSV, actual API and local tests.
Day 2: wire Fable redacted analysis output → ASTRA supported functional draft, optional reference behavior comparison.
Day 3: 3 sample categories, browser E2E, Windows smoke, delivery ZIP, limitations and polish.

**Not included yet:** real URL import, Fable/Astra engine wiring, XLSX, JSON, CRUD, accounts, live DB/API, hosting, real-world security/penetration tests, user-provided website visual replication. Do not sell the finished package until verified.
