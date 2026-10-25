# REA_Web — STATUS (2026-10-26 KST)

**D10-01 DONE in isolated Draft PR #13; D11-01 NEXT READY.** Main contains dispatch/documentation only. All feature PRs #1–#13 are Draft and unmerged; NO production web app, no sale authorization.

## Verified synthetic engineering
| Phase | Scope | Recorded evidence |
| --- | --- | --- |
| D1 | Single CSV local app | 40198326369, 9 tests + Chromium |
| D2-01/02 | Fable technical observation -> Astra REVIEW_REQUIRED adapter and independent app | 40199741969, 28; 40200704855, 55 |
| D3 | Three browser cases, ZIP, Windows cmd | 40202313506, 68 pytest each OS |
| D4 | Unapproved schema and category summary | 40203444938, 77 each OS |
| D5 | Strict JSON OR CSV input | 40204413087, 111 each OS |
| D6 | Vendor 88 Fable + 103 PARTIAL Astra hashes, ZIP audit | 40205614846, 125 each OS |
| D7 | No-overwrite atomic output, readonly data, error-path regression | 40206549211, 141 each OS |
| D8 | Explicit owner-approved 1-source guided mapping | 40207742776, 164 each OS |
| D9 | Explicit approved same-schema 2-source ROW APPEND only | 40209013017, 181 each OS |
| **D10** | **Three synthetic RC ZIPs, extracted Windows offline self-check, observed dependency metadata** | **[Actions 40210279358](https://github.com/hibi89/REA_Web/actions/runs/40210279358) SUCCESS: Linux and Windows each 188 pytest PASS** (1 nonblocking warning each); eight actual Chromium synthetic apps, Windows CMD→localhost HTTP PASS, Fable 88 and Astra PARTIAL 103 Git blob SHA checks both OS PASS. |

D10 tested feature SHA `1c0b708a3e5d979ad152e89848ef07f800d367c4`, `feature/rc-selfcheck`, [Draft PR #13](https://github.com/hibi89/REA_Web/pull/13), UNMERGED. Artifact **rea-d10-synthetic-rc** ID **12605835407**, with three synthetic demo ZIPs, checksums, browsers/evidence and observed environment metadata. No real customer data.

## D10 added / qualified
- `python -m scripts.d10_make_rc --out NEW_FOLDER` produces exactly three reproducible test-only ZIPs: standalone CSV, owner-approved guided JSON, owner-approved two-file same-schema append. Each includes `check_windows.cmd`, `self_check.py`, Korean Windows guide and original app files/SQLite. No original Fable/Astra vendor sources bundled.
- Windows diagnostic is standard-library-only and makes **no network calls**. Checks extracted-file SHA256 against manifest, Python >=3.11, SQLite readonly and installed FastAPI/Uvicorn. It neither installs dependencies nor starts app or certifies absence of sensitive data; clean nondeveloper Windows human acceptance NOT_RUN.
- `rea.observed_deps` lists exact **CI-observed** installed package versions, reported license metadata and potential notice file names; **14 distributions** observed in both operating systems. Direct FastAPI **0.162.0**, Uvicorn **0.54.0** in this CI, **not customer version locks or legal clearance**. Detailed [D10 review](https://github.com/hibi89/REA_Web/blob/feature/rc-selfcheck/docs/29_RC_WINDOWS_DEPENDENCY_REVIEW.md).
- Original D9 and earlier behavior preserved. First D10 Windows test run failed customer CMD path argument parsing; changed check to script-relative root and reran complete CI to PASS.

## Commercial gates still unresolved
1. Draft 300,000 KRW up-to-two-file promise is **only partially met**: explicit SAME-SCHEMA APPEND, not joins between unlike business tables. No owner-approved scope revision/contract.
2. Source rights/redistribution (Fable/Astra/templates) and exact locked runtime/wheel/NOTICE/transitive licenses not cleared. CI package metadata is not a license grant.
3. Real nondeveloper clean Windows UI installation, three measured mock jobs/manual labor 6–8h, authorized real client/reference/site, privacy/power-loss/backup/full pentest, merchant support/refunds NOT RUN.
4. Customer-facing lightweight GUI/multimode wizard only partially represented by CLI; no live DB, public deployment, paid API or real customer ZIPs used.

## NEXT READY D11-01
Build a **three-case synthetic quote-to-delivery trial and evidence/acceptance scorecard**, with supported features/unsupported scope checked against proposal and G0–G6. Automate reproducible tests and artifact checks but do NOT fabricate elapsed human preparation/correction effort or claim customer acceptance; create a blank manual time-log template instead. No sale until owner scope, copyright/NOTICE, actual Windows/customer approval. See docs/17_NEXT_TASK.md.
