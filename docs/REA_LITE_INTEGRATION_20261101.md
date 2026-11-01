# REA_WEB Lite — Pro source integration (2026-11-01)

## Boundaries and source

- Work branch `feature/rea-lite-integrated-20261101`, derived from the existing Pro branch head `97b6e5cab7b8ffb4e1ee7f5e593021f4dac2598d`. Do not overwrite Pro or merge to main without release review.
- Original archived Lite candidate SHA256: `8078e56cceedb17f5cbaa40eb032c502fb309d0c475be2f7bfc48c06afb5edc8`. Original template reconstructed exactly from synthetic archived cafe HTML; Git blob `70387cfaf58af6c4fc633ab96e465c819bdec440`, identical to locally archived template. No purchased/customer data in repository.
- Uses Pro's original `parse_input`, `map_owner_fields`, `source_sha256` directly. Seller needs Python 3.11+ and checkout; **customer needs only HTML browser and no server or Python**.
- CSV or flat JSON input allowed to seller. Customer browser updates only by same-header UTF-8 CSV with mandatory unique ID/title/category. 10 MiB max, 10,000 rows, 20 fields, 2,000 chars per cell. No source overwrite, approvals required before generation.
- Three theme variants `cafe`, `inventory`, `office`; list/search/sort/category/details/pagination, local CSV update and new-HTML export. Records embedded as plaintext: do not use sensitive/private data until explicit processing policy. Do not upload HTML to websites.

## Synthetic owner workflow

Run from checked-out repo root:

```shell
python -m rea.lite_builder inspect --source samples/rea_lite_inventory_synthetic.csv
```

Inspect the SHA256 and schema. Choose a NEW output path (must not exist), and substitute the reported SHA below:

```shell
python -m rea.lite_builder build --source samples/rea_lite_inventory_synthetic.csv --out demo_inventory_NEW.html --id-field item_code --title-field item_name --category-field group --source-sha256 <INSPECTED_SHA256> --confirm APPROVE --theme inventory --name "Synthetic inventory"
```

Open the generated `demo_inventory_NEW.html` with Edge/Chrome. Change CSV only with exact original header names, then **download the new HTML**, close the old page, open the saved file, and confirm the updated item persists. A failed CSV must retain previous records. Files are not silently overwritten; avoid including secrets in either input or generated output.

## Evidence and test commands

```shell
python -m pytest -q tests/test_rea_lite_integration.py
node tests/test_rea_lite_csv.cjs
python -m pytest -q tests/test_rea_lite_browser.py
```

Browser tests require Playwright's Chromium. GitHub Actions `.github/workflows/rea-lite.yml` runs these against actual Pro code with Python3.11/Node22 on Windows and Linux. [Automated job #41302599725](https://github.com/hibi89/REA_Web/actions/runs/41302599725) was successful on `f0e088e`: real generated file:// navigation, unsafe CSV denial, CSV update, Blob download, file:// reopened data and no external network request. This is **not human Windows acceptance**.

## Release gates (all required)

- Windows 10/11 actual user Edge/Chrome double-click and review, file:// CSV upload + exported HTML persistence, Console/Network check and support UX.
- Owner's exact original source rights, vendor and wheel LICENSE/NOTICE obligations, no misleading IP claims.
- Approved customer privacy/data retention policy for plaintext embedded HTML, terms, refund/support boundaries, pricing and 3 measured end-to-end delivery rehearsals.
- Explicit owner GO before any seller listing, public ZIP, user data, merge to release branch or distribution.

Current status: **TECHNICAL INTEGRATION VERIFIED / COMMERCIAL RELEASE HOLD**. Pro original scope and known tested behavior preserved; hosted production N/A.
