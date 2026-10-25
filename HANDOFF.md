# HANDOFF — REA_Web / 2026-10-25 KST

## Instructions for the next assistant
When owner writes **[REA_Web 깃헙 레포지토리 보고 작업이어가셈]**, inspect real GitHub and **perform the next READY development work immediately** without asking for context or another 'ㄱ'. Read `WORKER_START_HERE.md`, `STATUS.md`, `docs/17_NEXT_TASK.md`, `docs/SESSION_RESTART_PROTOCOL.md`; these are the canonical handoff. Future new chat will not contain our current code discussion, so this repository is the source of truth.

## Product and commercial intent
REA_Web is the **Fable 5.1 website technical/evidence analyzer + Astra Web Catcher functional-spec/independent web app engine**. Current customer-value-first MVP = take **customer-provided** clean CSV, generate usable standalone local app; reference URL optional. Avoid OHORA-like indefinite data collection / third-party API quota / unknown production DB complexity. First commercial price hypothesis 300,000 KRW fixed scope (2 screens, 3 simple features), not a 990k complex live DB job. Sale only after acceptance.

## Current technical status, with exact SHAs
- main documentation baseline before this handoff update: `71ed9a4656ef7642a32c335da9c6d664916cabee` (always refetch remote current SHA).
- Day1 generated local app: `feature/csv-local-mvp` @ `5515a7286d63211e32d2c577f93f77d61f37ce08`. Code `rea/mvp.py`, `rea/templates/app.py`, static HTML/CSS/JS, tests `tests/test_mvp.py`, actual Playwright browser `scripts/mvp_browser_smoke.py`. Draft PR #3, unmerged.
- CI run `40198326369`, job `121183903206`: **9 pytest PASS** + synthetic CSV app generation + compileall + real Chromium browser PASS; search, category, detail, reload; zero unexpected external request or JS error. No Windows/browser proof on Windows.
- Fable 88-source import: `import/fable51-bbe72c0` @ `7e6f273b359b207fad8f92016226e3058cbcb839`, pinned upstream `bbe72c0acd3a3e355062d6bd0d866af33e5274b0`, Draft PR #1.
- Astra P4 103-file bounded **partial** import (41 core astra_contracts modules): `import/astra-p4-b3166b6` @ `f044b66e799289a5a353fdb9cbfdb324e683ffa3`, pinned upstream `b3166b67604381a9d2afd41667b65f9a9b103b37`, Draft PR #2.
- Branches: integration/develop, feature/evidence-adapter (D2 next), feature/csv-local-mvp (D1), feature/orchestrator, qa/cross-platform, qa/vendor-fable, qa/vendor-astra; don't force-update feature work or mutate upstream imports.

## Single task to execute next
`REA-MVP-D2-01` on `feature/evidence-adapter`: read pinned Fable source `scanner/models.py`, `scanner/report.py` plus Astra `astra_contracts/observation.py`, `functional_spec.py`; build adapter `rea/adapter/fable_to_astra.py` from real Fable result format to ASTRA **unapproved** observation/spec draft. If no direct evidence, mark inferred/unknown or REVIEW_REQUIRED, never claim true backend/db/formula inference. Add >=15 focused test cases and an example, run real tests/CI, commit, Draft PR, then report. Fable ZIP need not be re-requested: 88 copied files exist on source import branch; redacted fixtures can be generated from source test files.

After that, D2-02 optional report→CSV app flow, D3 3-case Windows/browser/packaging/design-gap checks.

## Way of working
MVP-first target is 3 days (not a guarantee). Prioritize working result rather than huge theoretical scaffolding. Keep minimum non-deferable no overwrite/bounded CSV/SQL/DOM/localhost/authorization. Defer deeper security hardening until after functional proof, but not past customer delivery. Keep statuses PASS/NOT_RUN/BLOCKED accurate and always record commit SHA and work done in main STATUS/HANDOFF/NEXT_TASK.

No user actions are required for current D2 synthetic implementation; don't ask the owner for new data, tools, original ZIP, architecture confirmation or a different prompt. Only request explicit approval for production DB, external deployment or risky irreversible actions.
