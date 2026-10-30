# REA WEB Lite — source provenance, rights and data-release decision draft
Prepared 2026-10-31 KST. **Internal review draft only; NOT a copyright/license grant, privacy policy or permission to sell.**

## 1. Exact component inventory (branch feature/lite-offline-html-integration)

| Component | Function and runtime | What inspection establishes | Unverified owner decision |
|---|---|---|---|
| `rea/lite_builder.py` | Seller Python3.11+ entrypoint | Imports actual local Pro `rea.mvp` parser; Python standard library only in this module; explicit input SHA, mapping and APPROVE; exclusive output create | Source authorship and redistribution rights for all source and derivatives |
| `rea/mvp.py` + `rea/safe_publish.py` | Seller parser dependency | Visible Python imports are standard library + local `rea.safe_publish`; no external dependency directly required by the inspected Lite pathway | Origin of existing Pro code and sublicensing authority |
| `rea/lite_assets/template.html` | HTML delivered to customer | Inline CSS and JS, system font stack, no `<script src>`, stylesheet CDN, font file, `@import` or external URLs observed in current template; CSP denies network connections | Ownership/provenance of all markup, CSS, JS and UI copy |
| `scripts/lite_delivery_rehearsal.py` | Seller CI synthetic only | Python standard library, synthetic generated files and SHA256 manifest, not shipped in customer HTML | Authorship and CI/license policy if later distributed |
| `tests/test_lite_file_browser.py`, `tests/test_lite_packaged_pilot.py` | Test-only | pytest/Playwright on GitHub-hosted Windows and Ubuntu runners | Test dependencies are not part of the customer HTML; check licenses if distributing test tools |
| `.github/workflows/lite-integration.yml` | Test-only | External GitHub Actions and test-time package installs are used for CI, **not** a customer runtime or shipped asset | CI dependency version/security review separately |

**Repository inventory result:** recursive Git tree inspected on 2026-10-31 (227 entries at head `d610146b19dbced1dcaf4eab9457a4ce4174d03a`) contained no root `LICENSE`, `NOTICE` or `COPYING` files. Absence of these files **does not prove code is unlicensed, fully original, or authorized for commercialization**. A public repo does not itself establish permission to redistribute someone else's source.

### Mandatory rights evidence before customer sale (G3)
1. Owner verifies who created the recovered standalone Lite candidate and integrated files; document whether AI-assisted, third-party, or adapted from another repository.
2. For any reused component or asset, record name, exact source URL/commit, license identifier/text, copyright attribution, required notices, modification permissions and redistribution constraints. No third-party claim unless verified.
3. Owner explicitly authorizes distribution of the **generated customer HTML**, and specifies whether seller generator/source stays private or is released.
4. Decide whether to introduce a repository license or delivery rights statement only **after** owner/legal review. This draft intentionally neither assigns copyright nor declares an SPDX license.

## 2. Customer-data boundary (G4 remains BLOCKED)

- Intended Lite input is a customer-owned or properly authorized **non-sensitive** CSV, ideally public catalog data, product descriptions or stock/product lookup IDs without customer identity, contact, payroll, health, payment or secret values. Where classification is ambiguous, do not process until authorized.
- Seller intake must record **source owner approval, lawful purpose, chosen schema and field mapping, owner-reviewed SHA256**, and permitted delivery recipients. Reinspect file immediately before build and refuse hash drift.
- Generated HTML contains **plaintext** source records. Customers who forward the HTML forward the data; no encryption, user accounts, central access revocation or multiuser permissions.
- The Lite page itself is self-contained and has no designed external fetch, analytics, cloud account or server; **this does not claim that the seller's intake/download workflow stores nothing**, or that the browser/device is secure.
- Establish an approved **actual** intake channel, temporary work folder, access restriction, retention duration, deletion instruction, incident contact, and deletion evidence process. No retention/deletion interval was approved here; **do not claim automatic deletion**.
- User/customer should verify samples before seller receives any real files, never upload real source CSV or generated HTML containing client data to the public GitHub repo, Actions artifacts, chat or shared files without explicit permission.
- Distinguish original customer CSV from delivery HTML, optional same-schema refresh CSV and seller working copies. Avoid collecting data that is not needed to create the app.

## 3. Draft seller operation controls (not yet approved)

`intake authorization → schema-only inspect/SHA256 → explicit 3-field mapping approval → verify file still matches SHA → generate new HTML (no overwrite) → local offline browser acceptance → review exported plaintext/no sensitive fields → deliver only via approved channel → confirm customer opens and can refresh/save-new → approved deletion/retention evidence`.

Evidence log should record job pseudonym, permission/reference, source SHA256 (not source bytes), mapping keys (not row values), approved theme/scope, generated HTML SHA256, machine test SHA+OS, customer acceptance state, final delivery confirmation, and retention/deletion state. **Do not log real client data or private contact details in GitHub.**

## 4. Commercial scope and terms requiring owner approval (G6)
- Lite **includes** one standalone read-only catalog with exactly one requested theme, local search/category/sort/detail, bounded same-schema CSV refresh, explicit save-as-new HTML.
- Lite **excludes** remote hosting, QR/LAN, authentication, multiuser sync, in-place file rewrite, live database/API, CSV editing within HTML, encryption, ongoing automatic data feed, and Pro server features.
- Seller must decide currency and price, number and definition of included revisions, support window and response time, after-sale updates, refunds/cancellations and consumer disclosures as applicable. These are **UNSET**. Do not advertise commitments invented by this document.
- Three automated synthetic CLI timing checks per OS do not measure actual human effort or time/cost. Complete three **human timed end-to-end** mock orders before pricing.

## Gate verdict
G3 SOURCE RIGHTS **NOT_CLEARED**. G4 DATA HANDLING/RETENTION **NOT_APPROVED**. G6 PRICE/TERMS **NOT_APPROVED**. Draft PR #31 **UNMERGED**. Customer launch **BLOCKED** until explicit owner decisions and independent Windows human acceptance.
