# HANDOFF — REA_Web / current handoff (2026-10-30)

## Verified remote D27 baseline

- Branch: `feature/d27-windows-python-discovery`, exact D27 source `6ca9a03bcb3619fd4d1ea9922cf2e4a1557ec225`.
- Draft PR [#30](https://github.com/hibi89/REA_Web/pull/30) is OPEN, unmerged. Do not merge it as part of packaging work.
- Exact GitHub Actions [#40378905450](https://github.com/hibi89/REA_Web/actions/runs/40378905450) SUCCESS: Linux **412 pass / 4 skip / 1 warning**; Windows **426 pass / 1 warning**. Linux synthetic Chromium 8+3 and Tk; Windows native CMD D27 Python-path fallback, D24 port injection refusal, D25 archive inventory refusal, D26 readable pause, generated ZIP localhost HTTP and fresh isolated venv app proof all passed. Synthetic-only artifact **12678683196** says `human_acceptance=NOT_RUN`, `commercial_clearance=NOT_GRANTED`.
- Source snapshot verification: local `rea/delivery.py`, `tests/test_d27_python_discovery.py`, `docs/46_WINDOWS_PYTHON_DISCOVERY.md` and `STATUS.md` blob hashes matched the D27 branch files when copied into the isolated task folder. There is no `.git` in the provided source snapshot.

## Current local follow-up (not part of D27 proof)

Implementing readable Korean prerequisite output for the shipped ZIP, recovery instructions, a focused report-renderer test and current status documentation. Run isolated tests and compile checks. The D27 Windows workflow does not verify these changes until a new branch commit runs CI. Keep the original source folder untouched; work only in `REA_Web-feature-d27-windows-python-discovery-work-20261030`.

## Next gates

1. Finish the local package usability delta, run tests that do not require denied filesystem operations, and prepare a GitHub-applicable `.patch` plus changed-file bundle.
2. If repository write access is available, create a normal fast-forward commit on the existing D27 branch using its current head as parent; never force-update the ref. Keep PR #30 Draft and unmerged. Verify new CI before claiming the follow-up passed.
3. Real human Windows pilot and all G5/G6 business/legal checks remain blocked until evidence exists. Do not fabricate human acceptance, labor logs, client permissions, redistribution license or 299,000 KRW agreement.

---

## Historical handoff below (2026-10-25)

## Latest D2 checkpoint (2026-10-25 22:55 KST)
**REA-MVP-D2-01 DONE on feature only**. Feature SHA `fda96076de33ebf4f4b6118972a5033a3f703ba9`; Draft PR [#4](https://github.com/hibi89/REA_Web/pull/4), unmerged. Real GitHub Actions [CI run 40199741969](https://github.com/hibi89/REA_Web/actions/runs/40199741969) SUCCESS: **28/28 pytest**, pinned Astra validation and CLI approval-block check PASS on Ubuntu Python 3.11. PR CI run 40199766677 SUCCESS. `rea/adapter/fable_to_astra.py` adds read-only Fable schema v1.0 → review-only Astra candidate mapping, synthetic demo and tests; do **not** state functional UI, real backend, API ownership or chart lineage as observed. Windows, real customer data, cross-branch E2E, full vendor license audit, production service all NOT_RUN. No Vercel deployment for this unit (not applicable).

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
**REA-MVP-D2-02** `READY`, start automatically on exact trigger or `ㄱ`. Prefer `feature/orchestrator` after checking latest branch HEAD and the previous two feature branches. Use Fable report as **optional** analysis input to existing CSV→local app flow; leave website URL optional, require customer-provided CSV, retain `REVIEW_REQUIRED` and no automatic semantic mapping. Implement/test true synthetic demo, create Draft PR, and update main docs with exact proof. Only one unit per turn; next D3 three-example/browser/Windows/packaging/design-gap checks.

Do **not** repeat D2-01. Earlier section was historical. Source import branches remain pinned, partial Astra subset unchanged.

## Way of working
MVP-first target is 3 days (not a guarantee). Prioritize working result rather than huge theoretical scaffolding. Keep minimum non-deferable no overwrite/bounded CSV/SQL/DOM/localhost/authorization. Defer deeper security hardening until after functional proof, but not past customer delivery. Keep statuses PASS/NOT_RUN/BLOCKED accurate and always record commit SHA and work done in main STATUS/HANDOFF/NEXT_TASK.

No user actions are required for current D2 synthetic implementation; don't ask the owner for new data, tools, original ZIP, architecture confirmation or a different prompt. Only request explicit approval for production DB, external deployment or risky irreversible actions.

