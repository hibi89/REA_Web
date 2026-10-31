# REA_WEB Lite — Offline HTML (work branch)

Pro remains untouched. Customers receive **one portable HTML file**; no server, Internet, administrator, SaaS, EXE or LAN QR. The file contains the catalog records in **plaintext (base64-encoded, not encrypted)**. Use only non-sensitive/authorized data.

## Seller build (Python 3.11+ and the real Pro repository)

```bash
python -m rea.lite_builder --source samples/products.csv --out demo-new.html --name 'My Catalog' --theme cafe --approval APPROVE
```

Before approval, preview the schema with Pro's existing `rea.mvp.parse_input` / `preview_schema` and pin `--source-sha256` obtained by `rea.mvp.source_sha256`. For noncanonical headers supply `--mapping-file owner_mapping.json` with exact keys `id,title,category` mapped to the confirmed source fields. All 3 values must refer to distinct existing fields. No automatic inferred mapping. The output path must not exist.

## Customer use

Open the delivered HTML in Chrome or Edge **without a server**. Filter/search/sort and inspect details. Choose a UTF-8 CSV with exactly the same ordered columns, click **CSV 검증 후 적용**, then **갱신된 HTML 다운로드**. Reopen the downloaded file to confirm persistence. The original HTML is not overwritten. Malformed CSV refuses changes; the old in-memory catalog remains.

Limits: source max 10MiB, max 10,000 records, 20 fields, 2,000 characters per cell, unique nonblank id. UI shows 60 per page. Browser CSV schema must exactly match, including column order. Browser data is kept in memory until explicit HTML download; it is not auto-saved.

## Tests and status

```bash
python -m pytest -q tests/test_rea_lite_builder.py
python -m pytest -q tests/test_lite_file_browser.py
```

File-based Chromium test uses a real local `file://` navigation. On machines with a nonstandard Chromium path set `REA_CHROME_PATH`. This still does **not** certify a customer's Windows Chrome/Edge. Public GitHub branch is a development source, not a commercial release or permission to process customer data. Commercial redistribution, licenses/notices, pricing, service terms and hands-on Windows pilot remain approval gates.
