# REA-MVP-D3-01 — Three-domain and delivery acceptance guide

## Three independent synthetic scenarios

| File | Domain | Items | Category filter | Search |
| --- | --- | ---: | --- | --- |
| samples/qa_cafe.csv | Cafe | 4 | 음료: 2 | 카페라떼: 1 |
| samples/qa_inventory.csv | Inventory | 5 | 저장장치: 2 | NAS: 1 |
| samples/qa_trends.csv | Nail trend records | 5 | JP: 2 | 실버: 1 |

A sanitized synthetic Fable record is optional for the cafe test only.
The inventory fixture includes a literal script string as DATA. Trend
engagement is a sample customer CSV value, NOT an inferred business formula.

## Local commands

Python 3.11+, fastapi, uvicorn, pytest, httpx, pydantic, playwright required.
For optional Fable test, add pinned Astra contracts to PYTHONPATH.

    python -m pytest -q tests/test_mvp.py tests/test_adapter.py tests/test_orchestrator.py tests/test_d3.py
    python -m playwright install chromium
    python scripts/d3_browser_acceptance.py --report-dir ./out/d3-qa
    python -m rea.delivery pack --csv samples/qa_cafe.csv --out ./out/REA_Web_Cafe_v0.9.zip
    python -m rea.delivery verify --zip ./out/REA_Web_Cafe_v0.9.zip

GitHub Actions uploads SYNTHETIC screenshots (three PNG images), a browser
JSON report and the self-contained test ZIP after Linux CI. Keep all real
customers, tokens, API credentials and private Fable captures outside Git.

The ZIP contains FastAPI source, SQLite snapshot, HTML/CSS/JS, manifest,
README and a Windows CMD launcher. Source Fable JSON and vendor engines are
not bundled. SHA-256 checksums detect archive content changes, not site rights
or software-license compliance. Runtime binds to loopback address 127.0.0.1.

Native Windows CI extracts the ZIP, launches actual launch_windows.cmd and
fetches actual localhost health/items endpoints. This is not an actual
Windows Chromium run or a clean nondeveloper desktop installation.
Native Windows test results must come from completed Windows Actions job.

## Remaining requirements

See docs/21_MVP_GAP_MATRIX.md. Commercial and scope gates remain
NOT_DONE: customer rights, clean Windows manual install, commercial
provenance/license, security/recovery, acceptance and time estimates.
No public deployment, arbitrary URL clone or customer live DB.
