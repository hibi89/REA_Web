# REA_Web — ACTIVE SPRINT DISPATCH 2026-10-25

MVP-first override approved: working CSV->webapp first, fill original design gaps after. Minimum data/path/sanitization guardrails are NOT deferrable.

## Completed and verified
REA-MVP-D1-01: source feature/csv-local-mvp @ c04d47025a00f85f8faf51b40a2bdba135ec861f, Draft PR #3. Hosted run 40197993285: 9 passed, 1 warning, 5-row CSV sample generated and compileall passed. No real browser click or Windows proof.
Source snapshots remain unmerged: Fable 88, Astra 103 selected.

## READY queue
1. REA-MVP-D1-02 on feature/csv-local-mvp: actual browser E2E search/category/detail + CSV edge safety; verify GitHub Actions and keep Draft until passing.
2. REA-MVP-D2-01 on feature/evidence-adapter: Fable JSON result -> Astra-grounded observation/function-spec draft preserving certainty, 15+ tests, no fabrication.
3. REA-MVP-D2-02: combine Fable analysis mode optionally with standalone CSV builder.
4. REA-MVP-D3-01: 3 synthetic sample verticals, Windows smoke, architecture gap matrix, packaging report.
5. Full vendored upstream QA deferred behind MVP but required before distributing those engines to customers.

User shorthand 'ㄱ' means next READY safe task. Avoid live production DB, unauthorized site access, secret collection, external hosting and unbounded scope. Update STATUS, HANDOFF and dispatcher after actual commits/tests.
