# REA_Web Lite — owner-approved standalone offline HTML (2026-11-12 KST)

## Confirmed scope

Existing Pro is a local FastAPI + SQLite CSV/flat JSON builder with real `rea.mvp` parsing and owner-mapping. Lite is a separate customer-facing, **single HTML file requiring no Python or server**. The original 2026-10-31 Lite candidate was a **temporary uncommitted ZIP** unavailable in this session; this source is a newly implemented, independently tested Lite compatible with the documented Lite/Pro split, not a byte-for-byte copy of that ZIP. All source rights, original customer data, actual Windows customer acceptance and final sale remain unapproved.

## Design alternatives and decision

- A: wrap Pro FastAPI and SQLite as a customer installer. Pro source reuse is high but requires Python/dependencies, installation, localhost firewall decisions, a support burden and dependency-license audits. **Rejected for Lite**; existing Pro is left unchanged.
- B: reuse the **original Pro `rea.mvp` parser as a seller-side build-time dependency only**, then emit a self-contained, local-only HTML with inline CSS/JS and data for buyer browsing; in-browser File API imports an explicitly chosen updated CSV and downloads a new HTML on request. No hosting, API, EXE or external dependencies required for buyers; fewer operations and lower ongoing cost. **Selected.**

## Seller-side build contract

```powershell
# First inspect exact source columns and obtain SHA without printing data rows
python -m rea.guided inspect --csv "C:\Private\owner.csv"

# Only after checking permission, owner field names and SHA, build a new file
python -m rea.lite_builder --source "C:\Private\owner.csv" --out "C:\Private\catalog-NEW.html" --source-sha256 "<64-char SHA from inspect>" --id-field "식별자" --title-field "이름" --category-field "분류" --confirm APPROVE --theme cafe --name "시연 카탈로그"
```

Three allowed themes: `cafe`, `inventory`, `office`. Input `.csv` or Pro-compatible flat `.json` parsed via `rea.mvp.parse_input(require_semantics=False)`; owner must map exactly three **distinct existing columns** for id/title/category using `rea.mvp.map_owner_fields`. Never infer business semantics. Original source SHA256 is checked before/after parsing and again before and after a new `.html` write. An existing output is not replaced; no auto install or remote action.

Generated HTML embeds **plaintext data**. Only use owner-authorized, non-sensitive data. It performs client-side search/category/sort/item detail, 60-row pages, max 10,000 rows and 20 columns; supports explicit local CSV replacement of the **exact canonical header set or original approved source header set** (not arbitrary remapping), bounded UTF-8 decoding, CSV quoted cells, proper duplicate-ID checks and preserving previous rows on validation error. Changes persist **only** when the user clicks *새 HTML 저장*, then reopens downloaded file. No localStorage/IndexedDB/server/remote fetch. HTML source data is safely escaped for raw `script` text, DOM uses `textContent`, strict CSP `connect-src 'none'`; `script-src 'unsafe-inline'` is deliberately required for file-local self-contained JS and is not equivalent to a CSP hash/nonce.

The output receipt exposes only SHA/row counts, selected field names and HOLD status; no full source cell data. Customer must be advised that distributing HTML distributes contained record values in plaintext.

## Verified scope

- **Local Linux Python3.13.5:** `python -m unittest discover -s tests -p test_lite_builder.py -v`: **19 PASS / 0 FAIL / 0 SKIP**. Tests use a minimal local `rea.mvp` **contract double**, not the actual full Pro source; new `rea/lite_builder.py`, `rea/lite_assets/template.html`, `tests/test_lite_builder.py`, `tests/browser_lite_probe.py` Git Blob SHA exactly matches the local executed files.
- **Chromium synthetic DOM `page.set_content`** using generated HTML: real text DOM/search/category/sort/detail, invalid CSV retains prior data, canonical + source-owner headers update, local downloaded HTML reopening with revised data, 145 rows with 60/60/25 pages, imported `</script><img onerror>` rendered as inert text and safe after export/reopen, 0 page JS errors, 0 outgoing network requests. Browser launched Linux Chromium with Playwright; **real file:// Windows Chrome/Edge double-click not executed**.
- Historical Pro D27 full CI 28/28 SUCCESS belongs to prior SHA. This Lite change's **real Pro source import and full Pro regression** are part of the new scoped GitHub Actions; until new exact-SHA jobs conclude, mark them **UNVERIFIED**, even if Linux contract-double tests pass.
- No existing Pro `rea.mvp`, `rea/templates`, SQLite, FastAPI, user original input or Pro delivery artifacts changed in this feature; only new Lite files and scoped workflow/docs are added.

## Coverage scoring and release

Internal scope estimate for active Kmong REA_Web **75 → 85% provisional**: +4 Lite seller build with explicit source mapping/SHA and user-owned standalone HTML, +3 working in-browser replace/export/reopen, +2 category/search/sort/three-theme/60-row paging, +1 injection/symlink/non-overwrite/integrity regression. This is **engineering deliverable scope**, not a measured test pass rate or proof of customer release. Pending: new exact-SHA CI, Windows10/11 Chrome/Edge **physical file:// test**, nondeveloper 3-case delivery, source/license/privacy approval, Korean print/PDF as applicable, commercial terms and explicit owner sale approval. **RELEASE HOLD.**

## Next scope, not silently approved

If a Lite user needs larger sensitive data, authentication, remote sharing, edit persistence beyond explicit HTML export, or different schema, that is Pro/custom scope requiring a separate privacy/security review and owner approval, not a hidden Lite extension.
