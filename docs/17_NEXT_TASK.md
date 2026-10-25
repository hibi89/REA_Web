# REA_Web dispatcher — SINGLE ACTIVE READY TASK
Updated 2026-10-25 KST. For **[REA_Web 깃헙 레포지토리 보고 작업이어가셈]**, DO this immediately, no extra owner comments/questions.

## ACTIVE: REA-MVP-D2-01 — Fable result -> Astra evidence/spec adapter
**Status: READY** · **Target branch: feature/evidence-adapter** · **Safe authorized scope: offline, synthetic/redacted only**.

### Preparation
1. Read current remote main `WORKER_START_HERE.md`, `STATUS.md`, `HANDOFF.md`, `docs/SESSION_RESTART_PROTOCOL.md`.
2. Fetch current HEAD and source tree of `feature/evidence-adapter` and the pinned source branches: `import/fable51-bbe72c0`, `import/astra-p4-b3166b6`. Do not modify the pinned source branches.
3. Read Fable actual JSON schema and test fixtures: `engines/fable51/scanner/models.py`, `scanner/report.py`, `tests/test_contracts.py`, relevant examples. Read Astra `engines/astra_p4/astra_contracts/observation.py`, `functional_spec.py`, and `tests/test_observation_contract.py`.

### Implementation
- Create small pure Python adapter (suggested path `rea/adapter/fable_to_astra.py`) plus CLI/example and tests.
- Fable static technology detection / XHR candidates / chart-to-API correlations are inference; do NOT auto-promote to witnessed UI actions or to customer-owned database mappings.
- Real observation must carry valid evidence ID/ref/timestamp, source kind and authorization; unknown goes to unresolved or REVIEW_REQUIRED, not invented action. Astra `FunctionalSpecDraft` always `implementation_ready=false`, `db_api_mapping_status=not_started`; generation/production remains blocked.
- Handle missing data, unsafe URLs/secrets, unsupported schema versions, type mismatch, duplicate or ungrounded claims conservatively.
- Target >=15 deterministic tests, use actual pinned schema validators when feasible. CI/test evidence with exact commit SHA; no fake PASS claims.

### Completion
Commit real code to feature branch, open Draft PR into `integration/develop`, and update main `STATUS.md`, `HANDOFF.md` and this file to mark D2-01 DONE with test counts/CI and set D2-02 READY. If env/network prevents test, record NOT_RUN/blocked and continue safe local tests or independent next step without asking for another 'ㄱ'.

## Future queue
- **REA-MVP-D2-02 (NEXT):** Fable analysis mode as optional input to existing CSV→webapp MVP, without requiring URL.
- **REA-MVP-D3-01:** 3 different synthetic data fixtures, true browser E2E, Windows smoke/guide, delivery manifest/ZIP and explicit original-design gap matrix.
- **REA-P0-04 (DEFERRED):** full source-integrity/dependency/license review of import branches before distributing upstream engines to paying clients.
- Advanced security/production auth/hosting/live DB remain excluded/deferred.

## Last known verified
- D1 `feature/csv-local-mvp` @ `5515a7286d63211e32d2c577f93f77d61f37ce08`, Draft PR #3.
- GitHub Actions [40198326369](https://github.com/hibi89/REA_Web/actions/runs/40198326369) actual job passed 9 pytest and Chromium local 5→2→1→detail→reload; no JS/external errors.
- Fable 88 and Astra P4 partial 103 imports; PR #1/#2 still Draft/unmerged.

**Never ask for project details already established here. Never promise unattended work. User's exact restart phrase is itself permission to proceed with D2-01.**
