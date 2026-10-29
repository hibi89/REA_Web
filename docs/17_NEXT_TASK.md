# REA_Web — current delivery dispatcher (2026-10-30)

## Verified remote state

- Repository: `hibi89/REA_Web`; branch `feature/d27-windows-python-discovery`; exact D27 code/CI checkpoint `2dfbb90f514f94cb2f3bbe1a8ec4e4dc1a9376c6`. A following documentation-only commit records its results.
- PR [#30](https://github.com/hibi89/REA_Web/pull/30) remains OPEN, DRAFT, UNMERGED.
- D27 run [#40927550941](https://github.com/hibi89/REA_Web/actions/runs/40927550941) and D8 run [#40927551084](https://github.com/hibi89/REA_Web/actions/runs/40927551084) completed SUCCESS on Linux and Windows for the current code commit.
- Latest local Windows focused tests: 12 passed; D8 CP949 inspect/wizard: 2 passed. Actual native Windows ZIP launch, same-folder stop/restart, and copied-backup relaunch PASS; four SQLite rows/search/detail persist. Recovery/customer-guidance suite: 23 passed, 2 symlink tests deselected.
- Local Windows Chromium acceptance: 7/7 CSV/JSON/approved APPEND cases PASS, zero JS errors/external calls; Fable/Astra case BLOCKED because this source snapshot lacks pinned Astra contract modules.
- Workstation `py.exe` reports no registered runtime; the no-runtime error path is tested. Successful `py -3` runtime selection is NOT_RUN.
- Local regression: 407 passed, 22 skipped, 6 symlink tests deselected due WinError 1314. The unfiltered run is not clean on this host. Exact-head GitHub Windows/Linux CI is green.
- Human/customer acceptance NOT_RUN; commercial/source/dependency redistribution rights NOT_GRANTED; 299,000 KRW pricing and support/refund terms are not approved.

## Supported delivery scope

Customer-authorized UTF-8 CSV or flat JSON → preview → explicit field-mapping approval → generated local read-only FastAPI/SQLite app → list/search/category filter/detail → ZIP. Same-schema two-file ROW APPEND is supported only after both explicit approvals. Different-schema SQL JOIN, scraping/site cloning, CRUD, hosting, login/payment and live synchronization are not offered.

## Next independent actions

1. Continue the package recovery/privacy review and only rerun optional CI after the independent local work; code-specific D27 and D8 workflows have passed at commit `2dfbb90f514f94cb2f3bbe1a8ec4e4dc1a9376c6`. D3 run [#40928853301](https://github.com/hibi89/REA_Web/actions/runs/40928853301) has Linux SUCCESS and Windows QUEUED; continue independent work and recheck later.
2. Continue local synthetic failure/recovery checks and delivery receipts that do not require customer data.
3. When genuine evidence exists, complete nondeveloper Windows acceptance, successful `py -3` on a typical customer setup, source/data permission and redistribution review, privacy/security/backup review, measured service-time pilot and buyer scope/support/refund approval.

## Release gate

Not approved for sale or customer release. Do not represent synthetic CI or local smoke as human acceptance, commercial rights clearance or an authorized 299,000 KRW offer. Preserve existing source, customer data and PR history; no force push or unapproved merge.
