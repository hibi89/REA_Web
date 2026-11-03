# REA_Web D22 — Machine evidence vs human operator acceptance (2026-10-27)

## Goal

Ensure CI PASS, SHA verification and synthetic app completeness are NEVER silently represented as a real nondeveloper Windows user acceptance, business clearance, or a measured billable job. Existing pinned pilot kit logs are intentionally header-only. Editing them INSIDE the verified kit invalidates the SHA check: this is correct, not a packaging defect.

## Choice

**A chosen**: a short immutable human-only card **OPERATOR_ONE_PAGE_WINDOWS.txt** is bundled in the synthetic kit, with external-copy instructions. Machine records remain part of the sealed ZIP and **always report human_acceptance=NOT_RUN**.

**B deferred**: auto-submitting real user logs, uploading telemetry, filling labor time with synthetic estimates, remote-agent Windows operation, EXE installers or automatic acceptance. These need explicit user input, private processing policies, signing or real third-party rights.

## User workflow

1. Obtain the synthetic-only owner pilot ZIP from a trusted source. Extract to a new local directory. No customer data.
2. Read OPERATOR_ONE_PAGE_WINDOWS.txt.
3. Run CHECK_PILOT_WINDOWS.cmd (double-click) or CHECK_PILOT_WINDOWS.cmd --check; existing Python3.11+ required, never auto-installed. Machine integrity pass checks 10 SHA-pinned files but is not customer/human acceptance.
4. **BEFORE any notes**, COPY HUMAN_PILOT_BLANK.csv and MANUAL_TIME_LOG_BLANK.csv out of the sealed kit to a **separate private working folder**, ideally with identifying names; NEVER modify the copies inside the verified kit. Do not upload completed private logs to public GitHub, CI artifacts or chats.
5. Follow the short manual list/search/category/detail/start/stop checklist using the publicly synthetic 3+2 rows and note what actually happened, with elapsed setup, correction and QA time. Do not invent successful outcomes or metrics. Human acceptance is meaningful only after an actual person performs the steps.
6. Failed hash / missing Python / missing checker must stop the pilot. Even human PASS cannot grant redistribution/privacy/license/commercial permissions.

## Files

- `scripts/d22_operator_one_page.txt`: immutable one-page operator handoff and externally copied record instructions.
- `scripts/d19_owner_pilot.py`: ten-member strict ZIP allowlist, SHA and full comparison of fixed card, operator contract reminder in Windows README.
- `scripts/d20_offline_kit_check.py`: ten-member external-file and source SHA verification; no new runtime packages, network, or disk writes.
- `tests/test_d22_human_evidence_separation.py`: SHA/reproducibility, actual external-copy behavior preserving kit validity, edited-inside refusal, no fake human results.
- `.github/workflows/rea-d22.yml`: retains D21 Linux/Windows pytest, Chromium 8+3, Windows native GUI→ZIP→HTTP, CMD and pinned Fable/Astra SHA proofs. D22 artifact remains synthetic-only.

## Stop and release gates

AI and GitHub Actions may confirm only code/system checks. Real nondeveloper Windows GUI accessibility, three timed service jobs, personal-data/owner rights, vendor-dependency NOTICE and redistribution, backups/security, and agreed KRW 300,000 SAME-SCHEMA ROW APPEND scope/support/refund remain G5/G6 **BLOCKED**, with production/Vercel **N/A**. Feature stays as a Draft PR unmerged until separately authorized.
