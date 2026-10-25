# HANDOFF — REA_Web 2026-10-25

## Exact resume workflow
Read README.md → STATUS.md → docs/17_NEXT_TASK.md → docs/08_BRANCH_POLICY.md. The user may say 'ㄱ' to authorize the next READY safe task. Never claim that asynchronous work was done between turns.

## Repositories and upstream
- REA_Web main bootstrap commit ce7be5e76e3993723659f73552200c96d767e3ac (superseded by this status/config update).
- Fable upstream hibi89/fable5.1_web_catcher @ bbe72c0acd3a3e355062d6bd0d866af33e5274b0. Source branch import/fable51-bbe72c0 @ 7e6f273b359b207fad8f92016226e3058cbcb839; 88 reviewer ZIP source paths with per-path Git blob provenance.
- Astra hibi89/astra_web_catcher @ b3166b67604381a9d2afd41667b65f9a9b103b37. Source branch import/astra-p4-b3166b6 @ f044b66e799289a5a353fdb9cbfdb324e683ffa3. **103 selected files**, including 41 contract modules, not full Astra snapshot. Later codex-p4 @ 274402a3d8eaf33d9ff55bf740208a1dbded3bef is NOT the proven baseline.
- Draft PRs: https://github.com/hibi89/REA_Web/pull/1 and https://github.com/hibi89/REA_Web/pull/2; review-only, unmerged.
- Four readback sentinel blob SHAs matched respective upstream.

## Goals and boundaries
REA_Web = authorized URL/interaction analysis (Fable) → evidence/certainty-preserving adapter → Astra draft/semantic review → customer-owned CSV/JSON mapping → independent local FastAPI/SQLite webapp → actual automated test. No unconditional clone, data harvesting, live production DB, unauthorized network access or sensitive values.

## What to do now
Run tools/verify_vendor_manifests.py on each import branch (or have GitHub Actions run it) to check every imported Git blob SHA. Collect PASS evidence by SHA and add missing test fixtures required by selected Astra tests, without copying private customer data. Review PRs but do not merge until passing checks.

## Delivery phases
P0 sources and confidence, P1 adapter, P2 data safety, P3 minimal generator, P4 orchestration, P5 three examples/Windows, P6 product packaging and 300k scoped pilot. docs/04_ROADMAP.md = rough 60–112 engineering hours for the restricted P0–P6; NOT elapsed time or full universal reverse engineering.

## Source preservation and truthfulness
Upstream test claims cannot be copied as new REA passes. Imported Astra subset may have incomplete fixture coverage; no full repo passing status asserted. Test run must specify commit, command, machine, counts and limitations.

## QA branch handoff
To validate without editing immutable import source branches, use qa/vendor-fable or qa/vendor-astra. Each has top-level tools/verify_vendor_manifests.py and a workflow matching qa/**. Never confuse a submitted workflow with a confirmed PASS; inspect actual run/commit SHA. PRs #1/#2 remain draft and unmerged.

## Current sprint 2026-10-25
MVP-first authorized, see docs/MVP_3DAY_SPRINT_PLAN.md. Day1 actual generated-app code in feature/csv-local-mvp @ c04d47025a00f85f8faf51b40a2bdba135ec861f; GitHub Actions 40197993285 succeeded 9 pytest cases, sample app generated. PR #3 Draft. Day1 browser check, Day2 Fable evidence adapter, Day3 gaps/tests/package. Do not claim original complete Astra/Fable integration or 3-day product ready.


## D1 actual browser acceptance result (2026-10-25)
- feature/csv-local-mvp @ 5515a7286d63211e32d2c577f93f77d61f37ce08 (not merged).
- GitHub Actions: https://github.com/hibi89/REA_Web/actions/runs/40198326369 (job 121183903206): **SUCCESS**, 9 pytest PASS / 1 warning; real Chromium loopback browser: 5 rows, category filter 2, search 1, detail view, reload passed; 0 JS errors and 0 external network requests.
- Demo uses synthetic Korean cafe data; not a real customer/owner site; not Fable→Astra integrated yet; no Windows verification.
Next: implement REA-MVP-D2-01 on feature/evidence-adapter, preserve observed vs inferred; do not silently merge PR #3 until QA/owner review. Upstream source branches remain frozen.
