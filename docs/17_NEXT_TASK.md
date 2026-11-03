# REA_Web dispatcher — SINGLE ACTIVE READY TASK
Updated 2026-10-25 22:55 KST. The exact trigger **[REA_Web 깃헙 레포지토리 보고 작업이어가셈]** or **ㄱ** authorizes immediate execution of the next safe synthetic development unit. Do not ask the owner to resupply the Fable ZIP or approve normal offline development.

## Last task DONE: REA-MVP-D2-01
- `feature/evidence-adapter` @ `fda96076de33ebf4f4b6118972a5033a3f703ba9`; [Draft PR #4](https://github.com/hibi89/REA_Web/pull/4), unmerged.
- Source file `rea/adapter/fable_to_astra.py`; test `tests/test_adapter.py`; sample `samples/fable_record_redacted.json`; docs `docs/19_FABLE_ASTRA_ADAPTER.md`; workflow `.github/workflows/rea-adapter.yml`.
- Pinned vendor source unchanged. [CI run 40199741969](https://github.com/hibi89/REA_Web/actions/runs/40199741969) Ubuntu Python 3.11 **28 PASS**, zero failed/skipped; actual Astra Pydantic contract validation, CLI rejection of automatic approval and compileall PASS. PR run 40199766677 SUCCESS. Local standalone **24 PASS / 2 SKIP** before CI; skipped actual Astra import is covered by CI.
- These are synthetic unit/contract tests; no real website, customer data, Windows, whole product E2E or production deployment. Output stays `REVIEW_REQUIRED`.

## ACTIVE READY: REA-MVP-D2-02 — optional report + local CSV app orchestration
**Status: READY** · **Target: feature/orchestrator** · **Scope: offline/synthetic only**.

1. Read latest remote `main` HEAD, `WORKER_START_HERE.md`, `STATUS.md`, `HANDOFF.md`, this file, and `docs/SESSION_RESTART_PROTOCOL.md`.
2. Read source and tested SHAs on `feature/csv-local-mvp` (Day1 `5515a7286d63211e32d2c577f93f77d61f37ce08`) and `feature/evidence-adapter` (D2-01 `fda96076de33ebf4f4b6118972a5033a3f703ba9`), plus current `feature/orchestrator`. Do not force-update unique commits or merge unreviewed vendors.
3. Add a small deterministic CLI/orchestrator that takes **customer-supplied CSV** and optionally Fable analysis/report. CSV-only flow must remain usable, and analysis must only generate a report requiring review; it must never automatically map Fable API/tech/record-marker guesses to customer fields or authorize generation on the basis of the Fable scan.
4. Generate a separate independent localhost FastAPI/SQLite+HTML app using the already tested CSV MVP code, with no source overwrites, live requests, DB credentials, unapproved files, or new external deployment. Avoid copying entire vendor trees.
5. Run focused unit/negative tests plus synthetic vertical acceptance, verify checks on GitHub Actions, open Draft PR to `integration/develop`, record exact SHA/OS/pass counts and any NOT_RUN items. Update `STATUS.md`, `HANDOFF.md`, this dispatcher, and `WORKER_START_HERE.md` on main after the unit.

## Queue
- **REA-MVP-D3-01:** 3 synthetic domains, actual browser E2E of orchestrated output, Windows smoke/instructions, packaging/manifest, original-design gap and acceptance matrix.
- **REA-P0-04 (DEFERRED):** full vendor provenance/license and distribution review before sale.
- Complex auth, real DB, production deploy, payment and advanced pentest are out of this current unit.

One task per turn; truthfully differentiate tests, GitHub CI, Windows and real browser checks. No asynchronous work.
