# REA_WEB — Confirmed Lite/Pro Requirements (2026-10-31 KST)

## Product split (approved direction)
- **Pro:** Existing Python 3.11+ CSV/flat JSON -> explicit source/field approval -> local FastAPI/SQLite read-only app + delivery ZIP. Preserve original product source and tests.
- **Lite:** Seller uses the **same real** `rea.mvp` parser/validation/mapping. Customer receives **single offline HTML**, no server, Python, SaaS account, cloud, LAN QR, 0.0.0.0, installer or remote API.
- Three color themes: cafe/inventory/office. Data stored inside HTML only, not encrypted. No sensitive customer data.

## Lite acceptance
1. Seller accepts only verified regular UTF-8 CSV or flat JSON, <=10 MiB, <=10,000 rows, <=20 fields and unique nonempty `id,title,category` (or exact owner-confirmed mapping). Explicit `APPROVE` and optional source SHA pin required.
2. HTML: search any field, category filter, sort, detail, responsive 60-row pages.
3. Browser File API: explicit same-schema UTF-8 CSV choose/validate/apply; malformed content must not replace the current catalog.
4. Persistence only via explicit updated-HTML download; original delivered HTML is never silently modified. Reopen should retain changes.
5. No data network access or raw HTML rendering of uploaded values. Do not enable permissions or upload customer inputs without approval.
6. Real Windows Chrome/Edge double-click `file://` trial + export/reopen, human acceptance and legal/commercial gates are required before paid sale.

## Architecture comparison / decision
- Existing **Pro-only** distribution: richer API/filtering and export but Windows Python/package installation and support overhead.
- **Lite single HTML + optional Pro**: simpler customer setup, no continuous infrastructure/API cost, lower support burden; less suitable for sensitive/large datasets and custom server logic. This is the approved default.
- No feature scope expansion (hosting, client login, AI API, remote upload, QR or LAN binding) without further owner approval.

## No-go gates
- License and source redistribution rights and notices; data/privacy/retention/termination terms; support/revisions/refund/price; measured real jobs; Windows real end-user acceptance.
- This repository is currently public; any change of visibility or access requires owner approval.
