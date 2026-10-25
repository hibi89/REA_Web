# 2026-10-25 — 3-day MVP-first override

Owner approved a fast 3-day *working MVP first* experiment. First generate a useful real local app, then compare to original design, add gaps. Defer advanced pentest, scaling, production ops, vendor license audit, premium features; KEEP CSV input validation, no overwrites, SQL parameterization, XSS-safe DOM, loopback-only binding, authorized data boundaries.

## Day 1 — working user-facing slice
- Source branch feature/csv-local-mvp @ c04d47025a00f85f8faf51b40a2bdba135ec861f; Draft PR #3.
- CSV => SQLite => generated independent FastAPI and browser UI; list/search/category filter/detail.
- Actual GitHub Actions run 40197993285, job 121182908018: **9 PASS, 1 warning**, sample CSV 5 rows -> generated app and compileall success.
- Browser click E2E and Windows NOT_RUN.

## Day 2 — Fable to Astra
- Connect pinned Fable result.json (schema_version 1.0, target, api endpoints and charts) to proposed Astra ObservationBundle/FunctionalSpecDraft, retaining observed/inferred/unknown and approval gates. NO assumption of private DB or site source code.
- Keep original source import branches frozen, review only.

## Day 3 — compare & fill
- Compare to docs/02_ARCHITECTURE.md and docs/14_FINAL_DELIVERABLES.md.
- Three synthetic example domains; Chromium loopback E2E, error cases, Windows guide, ZIP/manifest. Record exact PASS/FAIL/SKIP.
- Advanced security, hosting, production DB and licensing issues stay explicitly open until verified.

3 days is an ambitious target, not guaranteed nor an asynchronous promise. Full original v1 roadmap remains below. No customer orders accepted before stated scope's actual acceptance.
