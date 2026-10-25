# 07 — 300,000 KRW limited service proposal

**DRAFT ONLY — NOT FOR SALE. D9/D10 supports only explicitly approved same-schema TWO-file ROW APPEND, not arbitrary joins or unrelated business data. Original broad two-file promise requires owner-approved restrictions or more engineering.** Publish only after docs/05_ACCEPTANCE.md G0–G6 pass for the promised scope.

Offer name: "고객님이 제공한 엑셀/CSV로 맞춤형 로컬 웹앱을 제작해드립니다".
Fixed starter price hypothesis: KRW 300,000 (fees/taxes excluded). Target labor **6–8 hours** max, validate with three internal mock jobs; otherwise narrow scope or raise price.

### Included, mutually agreed before payment
- Customer-owned and clean CSV or JSON, up to 2 files, 10,000 data rows total, 20 columns per file, and 10 MB combined. No personal/sensitive data.
- One local web app, **up to 2 screens** and **up to 3 simple features** from list/search/category filter/detail/simple summary.
- Local SQLite seeded from supplied data; demo user documentation, source ZIP, Korean guide, single acceptance report.
- One batch of minor defect corrections against original acceptance checklist within seven days; not a new feature request.
- Up to one authorized reference site for interface inspiration, not code/asset copying. If no reference is necessary, Fable analysis is optional.

### Excluded / quote separately
- Data collection/scraping, unclear/damaged data restoration, unlimited data cleaning, live production DB migrations/integrations, payments, accounts/roles, private API access, web hosting, SEO, mobile store apps, sophisticated visual copying, ongoing updates, unlimited revisions.
- Client must provide a valid non-sensitive example and confirm ownership/approval; if not supplied, delivery scheduling does not start until scope is reconciled.

### Deliverable & acceptance
Agreement records input filenames/types, 3 features and 2 screens, output run environment, tested fixtures, screenshots/logs permitted for sharing, one correction round. Service does not include deployment or perpetual maintenance.

### Commercial safety
No binding delivery date or order acceptance before real 3-case internal rehearsal; refuse out-of-scope 990,000 KRW complex DB work rather than promising unlimited integration. Track actual hours and refund/cancellation terms consistent with platform policy.

## D5 implementation discrepancy / mandatory pre-sale resolution
- **Actually implemented:** one bounded standalone CSV **or** one flat JSON array of string-valued records, max 10 MiB, 10,000 records, 20 columns, local read-only webapp; [synthetic CI 40204413087](https://github.com/hibi89/REA_Web/actions/runs/40204413087) Linux+Windows 111 pytest each plus Chromium browser.
- **Not implemented:** proposed **up to TWO files**, automatic joins/union/lookups, semantics, customer authorization and field mapping. **Do not advertise multi-file support yet.** An explicitly owner-approved two-file field/relationship contract and tests, **or** an approved revision to this commercial draft, is required. Do not silently narrow the proposed inclusion.
- **Also pending:** actual end-user clean Windows, dependency/source licensing, security/recovery, customer/reference rights and agreed features/time/support. See D5 feature `docs/24_JSON_INTAKE_SCOPE.md`.

## 2026-10-26 D10 latest supported scope and exclusions (overrides historical D5 note)
- [CI 40210279358](https://github.com/hibi89/REA_Web/actions/runs/40210279358) 188 pytest each Linux/Windows + 8 Chromium synthetic apps + Windows CMD shows an actual test-only implementation: one CSV or string-only flat JSON, explicit owner-guided one-file id/title/category mapping, OR two local explicitly approved **same-schema ROW APPEND** sources (10 MiB combined/10k rows). No joins/relational mapping or unrestricted two-file ingestion.
- Delivered app has local readonly FastAPI/SQLite source, launcher, SHA/receipt checks and self_check Windows CMD. This does NOT satisfy clean human Windows onboarding, real customer rights, third-party source/licenses, exact dependency NOTICE/lock, full security/PII/backup, 2 screens/3 feature customer parity, single correction round/support/refund contract, or three manually timed 6–8h jobs. These remain explicit order blockers.
- The original D5 implementation history above is a historical milestone and no longer describes current D10 capabilities. Do not revise or publish this offer without owner signoff; do not infer approval from synthetic CI.

## 2026-10-26 D11 three synthetic quote checks (commercial hypothesis UNVALIDATED)
- [CI 40211563951](https://github.com/hibi89/REA_Web/actions/runs/40211563951): separate synthetic café, inventory and trends orders each 1 screen / 3 selected supported features, independent ZIP + extracted browser acceptance; G3/G4 synthetic subchecks pass. All are simulated fixtures, not actual buyers, site rights or signed approvals.
- **6–8 hours human labor target NOT VERIFIED.** Empty MANUAL_TIME_LOG_BLANK.csv created and requires three ACTUAL timed human trial jobs with prep, build, correction, QA, handoff minutes. CI run wall time does not count toward human service cost.
- Draft two-file promise still must be constrained to **approved same-schema ROW APPEND**, or separately scoped contract/integration. No broader joins, 2-screen custom customer parity, clean Windows nondeveloper, redistribution rights/NOTICE, customer privacy, correction guarantee/refund/support approved. Do NOT publish or accept binding sale without owner agreement.
