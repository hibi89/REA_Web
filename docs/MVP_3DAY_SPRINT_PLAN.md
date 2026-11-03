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

## D1 actual browser acceptance result (2026-10-25)
- feature/csv-local-mvp @ 5515a7286d63211e32d2c577f93f77d61f37ce08 (not merged).
- GitHub Actions: https://github.com/hibi89/REA_Web/actions/runs/40198326369 (job 121183903206): **SUCCESS**, 9 pytest PASS / 1 warning; real Chromium loopback browser: 5 rows, category filter 2, search 1, detail view, reload passed; 0 JS errors and 0 external network requests.
- Demo uses synthetic Korean cafe data; not a real customer/owner site; not Fable→Astra integrated yet; no Windows verification.

## Day 2 evidence-adapter verified checkpoint (2026-10-25 22:55 KST)
- Feature `feature/evidence-adapter` @ `fda96076de33ebf4f4b6118972a5033a3f703ba9`; Draft PR #4, unmerged. [CI run 40199741969](https://github.com/hibi89/REA_Web/actions/runs/40199741969): **28 pytest PASS** on Ubuntu Python 3.11, actual pinned Astra contract validation and CLI anti-approval PASS.
- No verified whole-product Fable→Astra→CSV end-to-end run yet; D2-02 orchestrator remains READY. Windows and 3-case browser/packaging remain D3.
