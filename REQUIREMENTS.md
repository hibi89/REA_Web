# REA_WEB — confirmed product requirements (Lite / Pro)

## Lite (approved technical scope)

- Seller-side Python 3.11+ with real REA Pro parser; owner-approved local CSV, explicit map `id/title/category`, full source SHA256 and `APPROVE` required. No overwrite of owner CSV or a preexisting HTML file.
- Deliver one self-contained HTML in `cafe`, `inventory` or `office` theme. Customer opens it locally in a browser with no Python, server, cloud, login or internet.
- Search across fields, filter category, order by ID/title, view safe text-only details, 60 items/page. Customer may choose a same-schema UTF-8 CSV at any time; validation failures leave earlier records unchanged.
- CSV edits are ephemeral until the customer explicitly downloads a **new** HTML; never promise automatic persistence, current-file overwrite, sync or encrypted content.
- Maximum 10MiB UTF-8 CSV, 10,000 rows, 20 columns, 2,000 characters per cell. Mapped IDs must be unique and required values present. Embedded data is plaintext.
- No QR/LAN, cloud, EXE, authentication, customer CRM CRUD, live server, payment integration, third-party API or automatic file watching. Demo data synthetic.

## Pro (preserved historical scope)

- Customer-authorized UTF-8 CSV or flat JSON -> explicit field approval -> local SQLite/FastAPI read-only app and Windows ZIP, optional approved same-schema ROW APPEND. No arbitrary JOIN, URL cloning, external hosting or unapproved customer data.
- Current reference Pro code SHA `bbf2ec26923c0c6dc84a1263780f9e8e5b13fdf5` had 28/28 GitHub Actions PASS; no Pro source changed during Lite integration.

## Commercial gates: not approved

- Independent Windows nondeveloper hands-on, proprietary/third-party redistribution rights and notices, consent for customer data and delete/retention policy, three timed sample deliveries, price/refund/revision/support terms.
- Do not merge Lite Draft PR #31 into the inherited Pro branch or publish for sale absent owner's explicit release approval.
