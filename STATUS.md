# REA_Web — STATUS (2026-10-25 KST)

**CURRENT PHASE: D2-02 combined synthetic MVP VERIFIED on feature branch, D3-01 READY.**
Current main is a documentation/dispatch baseline, **not a merged or releasable app**.

## Verified work
| Unit | Branch + SHA | Evidence |
|---|---|---|
| D1 CSV→SQLite→FastAPI+HTML/CSS/JS local app | `feature/csv-local-mvp` `5515a7286d63211e32d2c577f93f77d61f37ce08` | [CI 40198326369](https://github.com/hibi89/REA_Web/actions/runs/40198326369): 9 pytest PASS, true Chromium PASS |
| D2-01 Fable 1.0 → Astra review-only adapter | `feature/evidence-adapter` `fda96076de33ebf4f4b6118972a5033a3f703ba9` | [CI 40199741969](https://github.com/hibi89/REA_Web/actions/runs/40199741969): 28 pytest PASS; actual Astra contracts PASS |
| **D2-02 CSV-only and optional Fable review combined** | `feature/orchestrator` **`46060b4665560922d0c9cf82b9e5c08971eb9427`** | [CI 40200704855](https://github.com/hibi89/REA_Web/actions/runs/40200704855): **55 pytest PASS, 1 warning**, actual Chromium PASS, two CLI modes/compileall PASS; [PR #5](https://github.com/hibi89/REA_Web/pull/5) Draft; PR CI 40200708638 SUCCESS |

D2 copies the exact pinned Git blobs of the independently tested CSV generator/templates/tests and review-only adapter/tests; original source branches/import branches remain unchanged. Both CSV-only and optional previously recorded Fable JSON run **offline**. Fable report is **not** an app-data source nor approval of mappings; `REVIEW_REQUIRED` always. Outputs: working local app with optional separate unserved `review/fable_review.json`. No live site or customer credentials accessed.

## Sources / branch policy
- Fable source immutable snapshot: `import/fable51-bbe72c0` @ `7e6f273b359b207fad8f92016226e3058cbcb839` (88 imported files).
- Astra P4 immutable **PARTIAL** snapshot: `import/astra-p4-b3166b6` @ `f044b66e799289a5a353fdb9cbfdb324e683ffa3` (103 selected files; 41 contract modules).
- Open Draft PRs #1–#5; **unmerged**, no code shipped to main/develop or production, no Vercel deployment (not applicable).
- Commit Author/Committer resolved as hibi89, `godls5898@gmail.com` for latest D2 feature commit. Avoid forced ref changes.

## Next READY — REA-MVP-D3-01
Use `qa/cross-platform` after verifying HEAD, base implementation off tested `feature/orchestrator` source (never force-push if unique commits), create 3-domain fixtures, browser E2E/Windows smoke instructions, distribution ZIP and manifest, architecture-to-MVP gap matrix and acceptance checklist. Maintain the MVP-first order before final safety/reliability/license checks. See `docs/17_NEXT_TASK.md`.

## NOT_DONE / NOT_RUN
- Clean Windows execution and nondeveloper setup NOT_RUN.
- Three-domain independent acceptance NOT_RUN.
- Customer data/authorized real reference site NOT_RUN; evidence rights and mapping approval not established.
- License/provenance redistribution review, advanced security/recovery, public service hosting and sale readiness NOT_DONE.
- No original backend/DB reconstruction, complex auth/payment/real DB, no arbitrary-URL 1:1 clone.
- Node.js checkout/setup actions show nonblocking deprecation warning; **not** a functional test failure.

New-chat trigger `[REA_Web 깃헙 레포지토리 보고 작업이어가셈]` or `ㄱ`: execute next READY unit, verify current remote first, update STATUS/HANDOFF/NEXT_TASK after each unit.
