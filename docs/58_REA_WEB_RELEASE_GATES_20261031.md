# REA_WEB commercial release gate — verified technical artifact, 2026-10-31 KST

**Decision:** narrow local REA_WEB MVP passed automated *synthetic* E2E. **NOT_APPROVED_FOR_SALE.** This audit records evidence and reduces unknowns, not authorization, commercial legal advice, or user Windows acceptance.

## 1. Source and test boundary

- Canonical product source tested: `hibi89/REA_Web@feature/d27-windows-python-discovery`, commit `dc277de57d6d8686b47ff08a49168caf10335ecf`. Subsequent docs-only commits have no runtime changes.
- 28/28 workflows at code SHA COMPLETED SUCCESS. [D27 run 41096230436](https://github.com/hibi89/REA_Web/actions/runs/41096230436): Linux **633 pytest passed, 5 skipped, 0 failed**, real Chromium eight generated synthetic apps + three extracted synthetic customer-style ZIP apps passed; Windows **644 passed, 4 skipped, 0 failed**, native CMD/Tk/ZIP/fresh-venv/localhost-HTTP covered. D7 recovery [41096230400](https://github.com/hibi89/REA_Web/actions/runs/41096230400), D11 [41096230860](https://github.com/hibi89/REA_Web/actions/runs/41096230860), D18 [41096230515](https://github.com/hibi89/REA_Web/actions/runs/41096230515), D31 [41096230631](https://github.com/hibi89/REA_Web/actions/runs/41096230631) both OS SUCCESS.
- The scope is owner-approved local CSV/flat JSON → preview/explicit field mapping → SQLite/FastAPI read-only app → Windows ZIP. Same-schema two-file ROW APPEND only. **Never claim auto website cloning, unlike-schema JOIN, public SaaS, auth/payment or unrestricted features.**
- PR [#30](https://github.com/hibi89/REA_Web/pull/30) OPEN/DRAFT/UNMERGED. Main/product deployment unchanged; Vercel Production N/A.

## 2. Actual artifact bytes independently inspected by 해총

- GitHub [Actions artifact #12996213068](https://github.com/hibi89/REA_Web/actions/runs/41096230436/artifacts/12996213068) (artifact wrapper `rea-d19-owner-pilot.zip`) downloaded and inspected by Python `zipfile` and `hashlib`, **without executing downloaded CMD/Python code**.
- Inner **original pilot ZIP** exact `35,051` bytes, SHA-256 **`ff6228e4bf3d9b12bd51ee9c5bdc63e9f854fc3109b32bb005ff31cc40480cc0`**. Contains 10 original members (manifest excluded from nine hash rows). Every manifest-recorded file size and SHA256 matched.
- Nested `demo/approved_pair.zip`: `25,568` bytes, SHA-256 **`d5c6c48eae8c8029a0d6fbe5db7106229bfde89dd4c100b1ac2c80a382e56e3f`**, containing 16 original members. Every listed member size/SHA256 matched. `app/data.sqlite` passed read-only `PRAGMA integrity_check` and `SELECT COUNT(*) FROM items` **5 synthetic rows**.
- Outer manifest explicitly says `real_human_acceptance=NOT_RUN`, `commercial_clearance=NOT_GRANTED`, `customer_data=NOT_USED`; human/time CSVs contain blank header only. **No Windows user/device was accessed**, and archive hashes do not authenticate the distributor.
- For owner convenience, exact original inner pilot ZIP bytes were copied (no content changes) to current ChatGPT working output `REA_Web_Synthetic_Windows_Pilot_20261031.zip`; this temporary workspace copy is **not a permanent GitHub release** and not guaranteed to persist in later chats. The durable original remains the GitHub Actions artifact above. Do not upload generated binary to Git history or label it a customer release.
- The user action is **one actual Windows synthetic pilot**: download original pilot ZIP, unpack into NEW EMPTY outer folder; double-click `CHECK_PILOT_WINDOWS.cmd`; extract `demo/approved_pair.zip` to a different NEW EMPTY folder; run `check_windows.cmd` followed by `launch_windows.cmd` only after prerequisite PASS; inspect `127.0.0.1:8000` five rows/search/category/detail, stop, restart; use blank logs **OUTSIDE the hash-sealed kit**. No uploads/real personal data. Python 3.11+ and project requirements may be missing on the user's PC; no auto-install is performed.

## 3. Exact generated runtime audit snapshot

- Downloaded and inspected [Windows D31 artifact #12997246246](https://github.com/hibi89/REA_Web/actions/runs/41096230631/artifacts/12997246246) actual `pip-audit.json` and `app/requirements.txt`.
- Exact audit environment: Windows Python 3.11.9, `pip-audit 2.10.1`, **latest-compatible resolution of version RANGES, not fixed wheel hashes**. Direct requirements: `fastapi>=0.110,<1`, `starlette>=1.3.1,<2`, `uvicorn>=0.27,<1`.
- Scanner recorded **14 resolved distribution entries, each `vulns: []` at that scan**, among them fastapi==0.162.0, starlette==1.10.0, uvicorn==0.54.0, pydantic==2.14.2. This establishes only that scanner found no published vulnerable dependency matching that resolved environment. **It does not prove no vulnerabilities, future installation parity, static security or legal rights.**
- In the actual generated app ZIP, **Python wheels/third-party libraries are NOT bundled**; the user installs Python and resolves requirements separately if authorized. Fable/Astra original/vendor source files are **NOT bundled** in customer ZIP. Still verify owner-authored generated template rights and notices to customers, and assess an exact-version/hashed requirements strategy before first commercial support.
- Official project license declarations observed for relevant upstream projects: FastAPI **MIT** ([official FastAPI license](https://fastapi.tiangolo.com/)), Starlette **BSD-3-Clause** ([PyPI](https://pypi.org/project/starlette/)), Uvicorn **BSD-3-Clause** ([PyPI](https://pypi.org/project/uvicorn/)), Pydantic **MIT** ([PyPI](https://pypi.org/project/pydantic/)). These are project-level declarations, **not an audited bill of materials for a customer-specific resolved package set**. Check the exact used version and legally required notices before re-bundling wheels/EXE.
- Exact nontruncated GitHub tree inspection at pinned SHA found **no named LICENSE/LICENCE/COPYING/NOTICE path** in (a) `hibi89/REA_Web` 203 tree paths, (b) `hibi89/fable5.1_web_catcher@bbe72c0` 97 paths, or (c) `hibi89/astra_web_catcher@b3166b6` 247 paths. **Absence is not proof of no rights**; author/contributor ownership or written license permission must be confirmed. Customer ZIP exclusion reduces the immediate vendor redistribution surface but does not itself license the generator or upstream analysis use.

## 4. Go/no-go — fastest allowed path without scope inflation

| Gate | Verified state | Required action | Owner |
| --- | --- | --- | --- |
| Technical core and synthetic E2E | **PASS** for exact code SHA | Preserve current code, no redundant CI/rebuild | REA lead |
| Actual nondeveloper Windows install/GUI + restart | **NOT_RUN** | Run provided outer/inner pilot; capture actual observations and error codes/time only | User / human Windows operator |
| Pilot input/output integrity | **PASS_HASH_ONLY** | Completed independent ZIP/member/SQLite audit; **not human acceptance** | REA lead |
| License/ownership for own generator/templates | **UNCLEARED** | Owner identifies authorized author/contributors and terms to deliver source; legal check if uncertain | User / rightsholder |
| Original Fable/Astra redistribution | **NOT_GRANTED**; upstream NOT shipped | Keep original code out of customer ZIP; no new imports without rights | REA lead + owner |
| Python runtime third-party packages | **LICENSE DECLARATIONS FOUND**, no pinned env clearance | Confirm exact resolution/license obligations + end-user installation terms; do not falsely say full license approved | REA lead |
| Real customer data / privacy / backup | **NOT_APPROVED** | First paid trial uses explicitly authorized nonsensitive data; review plaintext `data.sqlite`, local storage and no automatic backup | Owner + customer |
| Measured delivery and seller conditions | **NOT_RUN/NOT_APPROVED** | Record 3 real time measurements (no estimates), approve precise 1-page/same-schema scope, pricing, revision, refunds and support terms | User |
| Public production or full merge | **N/A / NOT_APPROVED** | Do not merge Draft PR or deploy/sell until user approval and applicable gates | User |

**Next safe engineering step after human pilot:** address **only actual reproduced** Windows device bugs, then rerun focused smoke and required full tests on the final source SHA. If Windows pilot passes and rights/terms are approved, prepare actual user-facing offer and conditional release; no need to extend backend scope.

**Recorded:** 2026-10-31 KST. Evidence scope: direct GitHub Actions logs, inspected actual artifact ZIP bytes and nested SHA256, pinned repo trees, official license declarations. Does not claim customer permission, operator results, legal certification, release, payment or production deployment.
