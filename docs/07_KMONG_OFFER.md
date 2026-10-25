# 07 — 300,000 KRW limited service proposal

**Draft only, NOT offered as currently implemented. D5 functionality does NOT fulfill the promised two-file input.** Publish only after docs/05_ACCEPTANCE.md G0–G6 pass for the promised scope.

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
