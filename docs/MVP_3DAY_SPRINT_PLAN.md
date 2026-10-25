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

## D2-02 combined integration checkpoint (2026-10-25 KST)
- `feature/orchestrator` SHA `46060b4665560922d0c9cf82b9e5c08971eb9427`; [Draft PR #5](https://github.com/hibi89/REA_Web/pull/5) unmerged.
- [CI 40200704855](https://github.com/hibi89/REA_Web/actions/runs/40200704855): **55 pytest PASS**, 1 warning, two local CLI modes and **actual Chromium** integration browser PASS (filter/search/detail/reload, zero JS or external calls). PR CI 40200708638 SUCCESS.
- Working combined MVP, not production readiness. Next D3 compares first target architecture, three scenarios, Windows/packaging; safety and licensing before commercial sale.

## D3-01 verified cross-platform synthetic acceptance (2026-10-25 KST)
- qa/cross-platform code e88c89f3ec12e61e63d2ca1255736fbf674c6e9e, Draft PR #6. Actions [40202313506](https://github.com/hibi89/REA_Web/actions/runs/40202313506) SUCCESS: **68 pytest PASS each on Ubuntu and Windows-latest**; real Chromium on 3 apps, Windows native CMD launcher + HTTP PASS, reproducible ZIP with SHA-256 verification, screenshot/QA/ZIP artifacts.
- No clean nondeveloper Windows installation, Windows Chromium, live customer/rights, vendor licenses, broad security or production. Original-design gap matrix enumerates next functional priorities; deep pre-sale QA not waived.
