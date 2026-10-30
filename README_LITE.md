# REA WEB Lite — offline HTML catalog

This is the independent, no-server Lite option; it does not replace the existing Pro FastAPI/SQLite generator.

## Builder (seller only)

Run from the repository root with Python 3.11+:

```bash
python -m rea.lite_builder inspect --source examples/lite_cafe.csv
python -m rea.lite_builder build --source examples/lite_cafe.csv --out NEW_catalog.html --id-field item_code --title-field item_name --category-field group --source-sha256 INSPECTED_SHA256 --confirm APPROVE --theme cafe
```

Provide the exact SHA256 from inspect. Owner must authorize the source and field mapping. The output path must be new. No customer file, current Pro database, or existing HTML is overwritten.

## Customer use

Double-click delivered HTML in Chrome or Edge. Search/filter/sort/detail work without Python, network, or account. Choose a same-schema UTF-8 CSV to update in current tab; use **변경 내용 HTML로 저장** to download a new HTML with new embedded records, then open that new file next time.

There is no QR, sync, hosted service, update-in-place, authentication, encryption, or remote access. Embedded records are plaintext. Do not use secret or personal data without separate approval.

Limits: CSV <=10MiB, <=10,000 data rows, <=20 columns and <=2,000 characters per cell; unique mapped IDs, required fields. This is not commercial clearance.

## Verification

```bash
python -m pytest -q tests/test_rea_lite_builder.py
```

Previous standalone synthetic Node/Chromium tests were performed on the original Lite candidate before integration. Exact-source GitHub CI run 41116194878 has 2/2 SUCCESS: Linux and Windows Chromium actual file:// update/download/reopen (3 tests/OS), real Pro-parser unit tests (5/OS), Node tests (15+7/OS). Real nondeveloper Windows Chrome/Edge double-click and commercial approval remain NOT_RUN. Existing Pro full CI was already green at inherited code SHA; newly integrated Lite branch requires its own code-specific CI result.

## Automated synthetic seller delivery rehearsal (verified 2026-10-31)

```bash
python scripts/lite_delivery_rehearsal.py --out-dir NEW_DIR
```

Requires a brand-new output directory. It uses only synthetic data, actual `rea.mvp` parser and CLI, builds three separate themed HTMLs, verifies original input hashes/no-overwrite/offline embed, then creates `REA_WEB_Lite_Synthetic_Pilot.zip` and `rehearsal_report.json`. Windows+Ubuntu Actions [run 41117124085](https://github.com/hibi89/REA_Web/actions/runs/41117124085) 2/2 SUCCESS at code SHA `202e4dbab9153c4f3003170e8881576d75c63b0c`; CI artifacts include pilot samples. CLI benchmark times are **not** customer-service estimates. Human Windows Chrome/Edge double-click validation and legal/merchant approvals remain outstanding.

## Packaged ZIP end-to-end checks (2026-10-31)

Automated **actual delivery ZIP** member verification after the synthetic seller CLI creates a fresh `lite_delivery_output` directory:

```bash
python scripts/lite_delivery_rehearsal.py --out-dir lite_delivery_output
python -m pytest -q tests/test_lite_packaged_pilot.py
```

Windows system Edge additionally uses `REA_BROWSER_CHANNEL=msedge` in GitHub Actions; tests require installed Edge. [Verified Windows/Ubuntu GitHub CI run #41119834953](https://github.com/hibi89/REA_Web/actions/runs/41119834953) at code SHA `72f36ed25caf2d3a7b0ee08e53d0291f1bf5a212`: 2/2 SUCCESS. Manifest, ZIP content, real local `file://` and new-HTML persistence tested. This is automated and synthetic, not owner/customer acceptance or sale approval. Unapproved source-rights/data/terms review [docs/63](docs/63_LITE_PROVENANCE_PRIVACY_SALE_DRAFT_20261031.md) and Korean customer guide [docs/64](docs/64_LITE_CUSTOMER_GUIDE_DRAFT_20261031.md).
