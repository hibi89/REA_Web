# REA_Web — 한 문장 재개 안내

User message: **[REA_Web 총괄 깃헙 레포지토리 확인하고 작업하셈]**

## Startup checklist
1. Browse hibi89/REA_Web current remote main HEAD and read README.md, AGENTS.md, STATUS.md, HANDOFF.md, docs/17_NEXT_TASK.md.
2. Inspect branches import/fable51-bbe72c0, import/astra-p4-b3166b6, qa/vendor-fable, qa/vendor-astra, integration/develop, feature/evidence-adapter, feature/csv-local-mvp, feature/orchestrator and qa/cross-platform.
3. Read Draft PRs #1/#2. They are source-provenance staging proposals and should not be merged unless actual QA and owner review pass.
4. If user writes "ㄱ", run the next SAFE, READY task on its designated branch; tests and commit must be real, not summarized as hypothetical success. Do not ask again for project identity or design.
5. When task completes, update source/working branch README or role handoff as appropriate, and master STATUS.md, HANDOFF.md, docs/17_NEXT_TASK.md with tested SHA, result and blockages. Keep source originals untouched and preserve customer data privacy.

## Product contract
Fable evidence → Astra grounded functional spec → user-owned CSV/JSON (no mandatory production DB) → isolated independent webapp → pytest/API/browser regression. Supported scope list/search/filter/detail/simple summary. Initial 300,000 KRW product is a restricted goal pending proof, not a sold or finished offer.

## Latest checkpoint (2026-10-25)
- 23 bootstrap files originally committed on main; source progress and README/QA workflow documented after.
- Fable 88 imported @ 7e6f273b359b207fad8f92016226e3058cbcb839.
- Astra 103 selected imported @ f044b66e799289a5a353fdb9cbfdb324e683ffa3; full Astra not imported.
- QA vendor branches include source-integrity script, workflow; no Actions PASS verified.
- REA_Web final integration application not built; next task REA-P0-04 import QA.
