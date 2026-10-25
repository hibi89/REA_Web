# REA_Web — New chat one-line resume (canonical)

## Trigger
**`[REA_Web 깃헙 레포지토리 보고 작업이어가셈]`**, or **`ㄱ`**. Both mean: inspect GitHub and immediately execute the next safe READY engineering task *in this turn*, without further context, owner's ZIP, branch choice or additional prompts. No autonomous background work.

## Mandatory read/verification order
1. GitHub `hibi89/REA_Web` latest actual main HEAD, `HANDOFF.md`, `STATUS.md`, `AGENTS.md`, `docs/17_NEXT_TASK.md`, `docs/SESSION_RESTART_PROTOCOL.md`.
2. Latest target feature branch HEAD + commits/files; read assigned code, tests, architecture and acceptance.
3. Implement next READY, preserve original vendor/feature branches, run real tests/CI. Record exact tested SHA/OS/PASS/FAIL/SKIP, write STATUS/HANDOFF/NEXT_TASK on main. No empty status-only work.
4. Approval before external network/data, live customer DB, deployment, paid services, rights/security changes, source overwrites. Synthetic offline work and GitHub feature commits already authorized.

## Current checkpoint — 2026-10-25 KST
**D1 CSV webapp DONE**: `feature/csv-local-mvp` @ `5515a7286d63211e32d2c577f93f77d61f37ce08`, 9 tests + actual Chromium PASS ([run 40198326369](https://github.com/hibi89/REA_Web/actions/runs/40198326369)), Draft PR #3.
**D2-01 review-only Fable/Astra adapter DONE**: `feature/evidence-adapter` @ `fda96076de33ebf4f4b6118972a5033a3f703ba9`, 28 tests + actual pinned Astra contract PASS ([run 40199741969](https://github.com/hibi89/REA_Web/actions/runs/40199741969)), Draft PR #4.
**D2-02 CSV-only + optional Fable review + local app DONE**: `feature/orchestrator` @ **`46060b4665560922d0c9cf82b9e5c08971eb9427`**, [Draft PR #5](https://github.com/hibi89/REA_Web/pull/5), [CI 40200704855](https://github.com/hibi89/REA_Web/actions/runs/40200704855) **55 pytest PASS**, true Chromium E2E and both offline CLI modes PASS, PR CI 40200708638 SUCCESS. This is feature-branch verification, **not** a merged/sale-ready product.
**NEXT READY: REA-MVP-D3-01** on `qa/cross-platform`; inspect latest head, base off tested orchestrator branch without force. Three synthetic scenarios, real browser, Windows docs/native NOT_RUN unless executed, ZIP/manifest, original-design gap matrix, acceptance. Details in `docs/17_NEXT_TASK.md`.

## Product boundary
MVP first -> compare preserved target design -> fill meaningful gaps -> final detailed security/reliability/licensing before commercial launch. Minimum safety (no-overwrite, safe CSV, SQL params, XSS-safe DOM, localhost, authorized references) always applies. Customer data CSV-only source; Fable technical clues are inferred and separate `REVIEW_REQUIRED`, never auto-bind schema. Full backend cloning, arbitrarily reproduced websites, live DB/payments/auth or Vercel production excluded from this stage. 300k KRW is a proposed fixed-scope product, not yet for sale.

Fable import `import/fable51-bbe72c0` SHA `7e6f273b...`; Astra P4 partial import `import/astra-p4-b3166b6` SHA `f044b66e...`; both immutable. Main contains docs/dispatch; separate PRs #1–#5 open Draft/unmerged. Refetch actual GitHub at each session.
