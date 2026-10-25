# REA_Web dispatcher — single ACTIVE READY task (2026-10-25 KST)

**When user types `ㄱ` or `[REA_Web 깃헙 레포지토리 보고 작업이어가셈]`, read real remote main + `WORKER_START_HERE.md`/`STATUS.md`/`HANDOFF.md` and execute this next bounded safe task immediately.** No more planning-only replies or context re-asking.

## Completed checkpoint: REA-MVP-D2-02
- `feature/orchestrator` SHA `46060b4665560922d0c9cf82b9e5c08971eb9427`, [Draft PR #5](https://github.com/hibi89/REA_Web/pull/5), unmerged.
- Copied exact source Git blobs from Day1 and D2-01 into one feature branch, added `rea/orchestrator.py` + tests + browser smoke + offline guide and CI. No vendor modification.
- GitHub Actions [40200704855](https://github.com/hibi89/REA_Web/actions/runs/40200704855) SUCCESS: **55 pytest PASS**, 1 warning, actual Chromium PASS, CSV-only and optional Fable CLI PASS, compileall PASS. PR CI [40200708638](https://github.com/hibi89/REA_Web/actions/runs/40200708638) SUCCESS.
- CSV-only app works without Fable; optional redacted recorded Fable JSON creates **unserved** separate `REVIEW_REQUIRED` report validated by actual pinned Astra contracts, never sources data/business logic from Fable. Original Fable source not bundled.
- **Not completed**: Windows, 3-domain examples, actual customer/site acceptance, advanced security/license audit, packaging and commercial readiness.

## ACTIVE: REA-MVP-D3-01 — Design gap + 3 domain, Windows/delivery smoke
**Status: READY. Target `qa/cross-platform`; use verified `feature/orchestrator` as implementation base only after inspecting both actual remote HEADs. No force.**

1. Read current `main`, `feature/orchestrator` and `qa/cross-platform`, then `docs/02_ARCHITECTURE.md`, `docs/05_ACCEPTANCE.md`, `docs/14_FINAL_DELIVERABLES.md`.
2. Create **three independent synthetic CSV datasets** (e.g. cafe catalog, inventory/tasks, trend records) each with `id,title,category` + extra fields. Add code/tests generating app for each and checking API expected counts/lookup/search/filters. Include one optional Fable report mode, without making it mandatory or connecting to live URLs.
3. Run real Chromium local browser E2E for all three and exercise failure/empty/bad cases. Keep exact evidence and check no JS exception, no cross-origin calls or accidental publication of Fable review.
4. Create a Windows-oriented launcher/README with exact safe loopback command. Windows native run, if not executable from current tool environment, mark **NOT_RUN** (do not claim PASS). Create versioned delivery ZIP/manifest with reproducible file list/hash, self-contained generated app and clear limitations.
5. Compare implementation to original `docs/02_ARCHITECTURE.md` & `docs/14_FINAL_DELIVERABLES.md` in a structured **done/partial/missing/deferred feature matrix**; fill low-risk functional gaps if MVP valuable. Advanced pen-test/license review deferred but record pending release gates.
6. Run unit+E2E CI, open Draft PR, update `STATUS.md`, `HANDOFF.md`, this dispatcher on main with SHA and exact test/NOT_RUN; do not merge incomplete vendor imports, change environment secrets or deploy without approval.

## After D3
REA-P0-04: review license/provenance/dependencies before customer distribution. Final packaging, reliability/recovery, actual clean Windows validation, safe data and export, commercial acceptance before sale. Do not promise arbitrary clone/live DB.

**One READY task at a time; no background execution.** 
