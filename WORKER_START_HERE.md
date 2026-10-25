# REA_Web — NEW CHAT ZERO-QUESTION RESUME ENTRYPOINT

## EXACT USER TRIGGER
**[REA_Web 깃헙 레포지토리 보고 작업이어가셈]**

The exact sentence above is a **standing instruction to immediately inspect this repository and EXECUTE the next READY engineering task**, not merely to summarize, ask what to do, or generate an unrelated plan. Do NOT require the owner to re-explain the project, attach a Fable ZIP again, specify a branch, or say 'ㄱ' separately. The trigger itself authorizes the next **bounded, safe, local/synthetic** task. No autonomous/background work occurs between user prompts.

## First tool actions every new session (mandatory)
1. Open the connected GitHub repository **hibi89/REA_Web**, fetch **current remote main HEAD**, and read in order:
   - `WORKER_START_HERE.md` (this file)
   - `STATUS.md`, `HANDOFF.md`, `docs/17_NEXT_TASK.md`
   - `docs/SESSION_RESTART_PROTOCOL.md`, `AGENTS.md`, `docs/MVP_3DAY_SPRINT_PLAN.md`
   - `docs/02_ARCHITECTURE.md`, `docs/08_BRANCH_POLICY.md`, `docs/14_FINAL_DELIVERABLES.md` as needed for assigned work.
2. Inspect the HEAD **and any actual changes since that HEAD** on the designated feature branch before writing. Read its README/tests and relevant source files; do not overwrite other work.
3. Verify current PR/CI status for claims you make. NEVER infer PASS from workflow YAML or past-turn logs.
4. Implement the **single latest READY task** on its designated branch, run available real checks, commit/push using GitHub, record results in `STATUS.md`, `HANDOFF.md`, and `docs/17_NEXT_TASK.md` (on main; merge/rebase only if conflict-safe). Include the commit SHA and NOT_RUN/blocked facts. If blocked, record concrete cause, switch to next independent safe item.
5. Respond only with actual completed changes, exact tests, verified URLs/SHAs, blockers, and next step. No questions already answered in these files.

## Current highest priority — ACTIVE at 2026-10-25 KST
**REA-MVP-D2-01: Fable 5.1 -> Astra evidence/functional-spec adapter**
- Write new integration adapter and deterministic tests on `feature/evidence-adapter` (currently only initial docs, HEAD before fast-forward `a4098bb15e3348250c8e6f255acbca6f0eb18fc2`).
- Input: redacted **Fable 5.1** result JSON: website technical evidence, observed UI/recorded interaction facts, `api.endpoints`, chart/API association hypotheses. Preserve exact observed/inferred/unknown distinction.
- Output: validated **Astra P4** ObservationBundle / FunctionalSpecDraft or explicitly **REVIEW_REQUIRED**, with evidence links, no fabricated confirmed UI behavior, unapproved data bindings and production generation blocked.
- Deliver: real Python implementation, positive/negative tests, a redacted synthetic example and a CLI/demo invocation. Use source schemas of `engines/fable51/` on `import/fable51-bbe72c0` and `engines/astra_p4/astra_contracts/` on `import/astra-p4-b3166b6`; imported code remains on separate, unmerged source branches. A redacted example may be built from the checked-in Fable test fixtures if earlier user-provided ZIP is unavailable in the new conversation.
- Next: REA-MVP-D2-02 optional Fable analysis report to CSV→app builder; REA-MVP-D3-01 3 examples, Windows guide, browser E2E, packaging and design-gap comparison.

## Last verified working result — do not lose
- Standalone CSV→SQLite→FastAPI+HTML/CSS/JS generator exists on `feature/csv-local-mvp` **`5515a7286d63211e32d2c577f93f77d61f37ce08`**; Draft **PR #3** to integration/develop (NOT merged).
- GitHub Actions `https://github.com/hibi89/REA_Web/actions/runs/40198326369`, job `121183903206`: **9 pytest PASSED** (1 warning); actual Chromium E2E PASS on **five synthetic Korean café rows**, filter to two, search to one, click detail, reload, zero JS errors and zero external-origin calls.
- It is a **CSV MVP only**, not yet integrated with Fable/Astra, no Windows, real customer DB/API or sale-ready verification.
- Fable pinned 88/88 source paths in `import/fable51-bbe72c0` @ `7e6f273b359b207fad8f92016226e3058cbcb839`. Astra P4 **103-file PARTIAL** snapshot (41 contract modules) in `import/astra-p4-b3166b6` @ `f044b66e799289a5a353fdb9cbfdb324e683ffa3`. Draft PRs **#1/#2** not merged.

## Non-negotiable intent and constraints
- Owner's chosen repository/product name: **REA_Web**. Keep Fable/Astra upstream independent, combine by adapter rather than blindly merging.
- **3-day MVP-first sprint**, code that creates real user-visible results first; compare to original architecture and fill gaps after. This is an **aggressive target**, NOT a guaranteed 3-day finish or background task.
- **30만원 (300,000 KRW)** narrow Kr몽 product hypothesis: customer provides clean CSV/JSON; up to 2 screens / 3 simple features / no default data collection. Do not offer unlimited production database integration.
- Do not postpone essential no-overwrite, bounds, SQL parameterization, output escaping, consent, localhost-only and no customer secrets. Advanced hardening/Windows/three examples may follow MVP core, but cannot be represented as already completed.
- If user sends **'ㄱ'** in any session, execute next safe READY task immediately. If the exact restart sentence is used, it **already means 'ㄱ'**.
- For full contract, architecture, branch policy, honest verification rules: `docs/SESSION_RESTART_PROTOCOL.md`.

**At any future session, latest actual GitHub HEADs and dispatch docs override this historical snapshot.**
