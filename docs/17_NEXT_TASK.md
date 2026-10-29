# REA_Web — current delivery dispatcher (2026-10-30)

## Verified remote state

- Repository: `hibi89/REA_Web`; branch `feature/d27-windows-python-discovery`; exact D27 code/CI checkpoint `6a6f07d0350368deacf413cab0be2a79eaca296f`. A following documentation-only commit records its results.
- PR [#30](https://github.com/hibi89/REA_Web/pull/30) remains OPEN, DRAFT, UNMERGED.
- Exact-head D27 runs [#40923311077](https://github.com/hibi89/REA_Web/actions/runs/40923311077) and [#40923323228](https://github.com/hibi89/REA_Web/actions/runs/40923323228) both completed SUCCESS: Linux D1–D27/Chromium and Windows D1–D27/native-package jobs.
- Latest local Windows focused tests: 12 passed. Actual native Windows synthetic ZIP test: generated ZIP, extraction, `cmd.exe` launcher, loopback health and four-row API all PASS.
- Workstation `py.exe` reports no registered runtime; the no-runtime error path is tested. Successful `py -3` runtime selection is NOT_RUN.
- Local full regression has known symlink-fixture permission failures; do not report the unfiltered local run clean. Exact-head GitHub Windows/Linux CI is green.
- Human/customer acceptance NOT_RUN; commercial/source/dependency redistribution rights NOT_GRANTED; 299,000 KRW pricing and support/refund terms are not approved.

## Supported delivery scope

Customer-authorized UTF-8 CSV or flat JSON → preview → explicit field-mapping approval → generated local read-only FastAPI/SQLite app → list/search/category filter/detail → ZIP. Same-schema two-file ROW APPEND is supported only after both explicit approvals. Different-schema SQL JOIN, scraping/site cloning, CRUD, hosting, login/payment and live synchronization are not offered.

## Next independent actions

1. Finish and record the synthetic Chromium acceptance across generated CSV/JSON and explicitly approved same-schema APPEND cases; verify search, filter, detail, reload, no unexpected network calls and no JS errors. Recheck CI after the work, not as a prerequisite.
2. Continue local synthetic failure/recovery checks and delivery receipts that do not require customer data.
3. When genuine evidence exists, complete nondeveloper Windows acceptance, successful `py -3` on a typical customer setup, source/data permission and redistribution review, privacy/security/backup review, measured service-time pilot and buyer scope/support/refund approval.

## Release gate

Not approved for sale or customer release. Do not represent synthetic CI or local smoke as human acceptance, commercial rights clearance or an authorized 299,000 KRW offer. Preserve existing source, customer data and PR history; no force push or unapproved merge.
