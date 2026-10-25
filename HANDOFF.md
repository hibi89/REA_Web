# REA_Web — HANDOFF (2026-10-25 KST)

**Read `WORKER_START_HERE.md`, `STATUS.md`, `docs/17_NEXT_TASK.md` and latest real GitHub branch heads before executing. Exact phrase `[REA_Web 깃헙 레포지토리 보고 작업이어가셈]` and `ㄱ` already authorize the next safe READY unit; no other prompt required.**

## 1. Goal / confirmed requirements / technology
REA_Web = Fable 5.1 read-only technical reference analysis + Astra P4 observation/spec review + independent local webapp from customer-supplied CSV. Initial service hypothesis 300,000 KRW limited scope (roughly 2 screens, 3 basic behaviors), not arbitrary-site clone or production DB. FastAPI, SQLite, HTML/CSS/JS, Python 3.11, offline CLI, optional Fable 1.0 JSON. Three-day **target**, not guarantee. Strategy: working MVP → compare original design → valuable gaps → thorough safety/reliability/commercial QA last (minimum safety on from first unit).

## 2. Completed features / changes / rationale
- D1: customer CSV → new SQLite+read-only app list/search/category filter/detail.
- D2-01: conservative Fable 1.0 → Astra P4 review-only evidence and spec; inferred ≠ observed.
- **D2-02:** `rea/orchestrator.py` combines CSV-only output with optional `--fable-result`; CSV still sole source for generated app logic and data, optional reference creates `review/fable_review.json` separately. No automatic semantic mapping/approval. Tested app can be launched on 127.0.0.1.
- Reused original D1/D2 implementation via exact Git blob SHAs; did not overwrite either branch or vendor snapshots. Integration chosen over full vendor tree merge to reduce coupling/time and license/secret risk.

## 3. Tests / commands / proof
Latest `feature/orchestrator` **`46060b4665560922d0c9cf82b9e5c08971eb9427`** at GitHub Actions [40200704855](https://github.com/hibi89/REA_Web/actions/runs/40200704855), Ubuntu Python 3.11, **55 pytest PASS, 0 FAIL, 1 warning**, actual Chromium PASS list/filter/search/detail/reload, zero JS errors/external-origin requests, optional Fable review HTTP 404 from generated site, CSV-only+review CLI PASS and compileall PASS. PR CI [40200708638](https://github.com/hibi89/REA_Web/actions/runs/40200708638) SUCCESS; bootstrap PR 40200708511 SUCCESS.
Commands: `PYTHONPATH=.vendor/astra/engines/astra_p4:. python -m pytest -q tests/test_mvp.py tests/test_adapter.py tests/test_orchestrator.py`; `PYTHONPATH=.vendor/astra/engines/astra_p4:. python scripts/orchestrator_browser_smoke.py`; `python -m rea.orchestrator --csv samples/products.csv --out ./out/demo`; optional `--fable-result samples/fable_record_redacted.json` requires pinned Astra in PYTHONPATH or `--astra-root`.
D1 separately [40198326369](https://github.com/hibi89/REA_Web/actions/runs/40198326369) 9 pytest+Chromium PASS; D2-01 separately [40199741969](https://github.com/hibi89/REA_Web/actions/runs/40199741969) 28 pytest PASS. No full real-customer or Windows proof.

## 4. Complete / active / queued / blockers
D1 DONE (feature), D2-01 DONE (feature), D2-02 DONE/verified (feature only), next D3-01 READY. D3: 3 independent synthetic domains, Windows setup and tests, ZIP/delivery, gap matrix. P0 vendor license review deferred before selling. No external blocker for synthetic D3; Windows host execution may require owner/local environment and should be NOT_RUN if unavailable.

## 5. Error evidence / root cause / attempts / avoid repeats
D2-02 latest CI GREEN; no unresolved functional CI failures. Formatting of local guide code fences fixed with `46060b4` docs-only commit, then CI re-run SUCCESS. Nonblocking GitHub runner Node20 deprecation warning persists. Do not redo identical completed D1/D2 work or claim that static Fable evidence confirms UI behavior. Avoid falsely passing Windows, actual customer DB or full Fable/Astra-engine source distribution.

## 6. Repository / branches / SHAs / important paths
Repo `hibi89/REA_Web`, default `main`. Main at time of this handoff preparation `6a306f37fb7600fd53e53dcf210a286c5c2177d3` (refetch actual HEAD before work); `feature/orchestrator` `46060b4665560922d0c9cf82b9e5c08971eb9427`, Draft [PR #5](https://github.com/hibi89/REA_Web/pull/5) to `integration/develop`. Day1 `feature/csv-local-mvp` `5515a7286d63211e32d2c577f93f77d61f37ce08` (PR #3), D2-01 `feature/evidence-adapter` `fda96076de33ebf4f4b6118972a5033a3f703ba9` (PR #4). Sources Fable `7e6f273...` PR #1 and Astra partial `f044b66...` PR #2. Paths: `rea/orchestrator.py`, `rea/mvp.py`, `rea/adapter/fable_to_astra.py`, `rea/templates/`, `tests/test_orchestrator.py`, `scripts/orchestrator_browser_smoke.py`, `docs/20_ORCHESTRATOR_MVP.md`.

## 7. Production URL / deployment / environment
**Vercel: not configured for this unit, no Production URL, not applicable.** Independent app local only: `python -m uvicorn app:app --host 127.0.0.1 --port 8000` inside generated folder; Python 3.11+, FastAPI, Uvicorn. Optional Fable review validation uses Pydantic>=2 and pinned Astra contracts checkout. No paid AI API or external app. Do not silently create deployment.

## 8. Original source / backups / authentication / do-not-edit
Original Fable repo `hibi89/fable5.1_web_catcher` pinned upstream bbe72c0...; original Astra `hibi89/astra_web_catcher` pinned b3166b6...; Git import source branches immutable. Customer originals never uploaded or altered; synthetic fixtures only. No credentials, tokens or `.env` saved. Existing upstream branches and D1/D2 PRs are recoverable backups. No unapproved production input or external customer data.

## 9. Next priority / procedure / acceptance / approvals
**D3-01 READY**, target `qa/cross-platform` at last checkpoint original baseline (refetch). Branch off tested D2 `feature/orchestrator` only if no unique commits; no force. Create 3 diverse CSV scenarios, all generated app actual browser E2E; compare `docs/02_ARCHITECTURE.md` and `docs/14_FINAL_DELIVERABLES.md` feature by feature; Windows launch/ZIP manifest/receipt, crash/recovery/negative inputs and no-secret regression. Run CI, Draft PR, update main STATUS/HANDOFF/NEXT_TASK with exact results. No owner input required for synthetic; ask approval before customer data, live site, paid services, security/rights changes, production deploy or merge with irreversible impact. Finished commercial product requires Windows/packaging/license/legal and scope evidence.

## 10. KST update time / verification boundary / doc base
Updated **2026-10-25 KST** after checking D2 feature commit `46060b4665560922d0c9cf82b9e5c08971eb9427` and GitHub Actions results. Main docs prepared against main `6a306f37fb7600fd53e53dcf210a286c5c2177d3`; GitHub commit after save is canonical documentation baseline. No Windows/real customer/production assertion. PRs are Draft and unmerged.
