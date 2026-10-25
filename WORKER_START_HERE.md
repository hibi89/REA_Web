# REA_Web — One-line restart protocol (2026-10-26 KST)

**Trigger:** ㄱ or [REA_Web 깃헙 레포지토리 보고 작업이어가셈] means read actual hibi89/REA_Web main HEAD, HANDOFF.md, STATUS.md, AGENTS.md and docs/17_NEXT_TASK.md, then **execute NEXT READY work now**, no further approval for safe offline synthetic dev. No background tasks between turns.

## Latest verified work
D1 CSV app 9 pytest + Chromium; D2-01 Fable/Astra review 28; D2-02 combined 55; D3 local ZIP+3 Chromium/Windows 68 each OS; D4 schema/category counts 77 each OS; D5 single JSON and CSV 111 each OS.
**D6-01 DONE:** feature/license-provenance SHA b97443657e46a8f701e12b83bf87f5a0339b224c, [Draft PR #9](https://github.com/hibi89/REA_Web/pull/9), [CI 40205614846](https://github.com/hibi89/REA_Web/actions/runs/40205614846) SUCCESS: Linux+Windows **125 tests PASS each**, Fable **88** and partial Astra **103** Git blobs matched on both, Chromium 4 synthetic apps PASS, Windows .cmd HTTP PASS. Synthetic audit reports + ZIPs in Actions artifact rea-d6-synthetic-provenance ID 12602923880.
Fable/Astra licenses NOT cleared (no standard LICENSE/NOTICE found on pinned trees); ZIP excludes original vendor engines but data.sqlite contains user rows. Direct FastAPI/Uvicorn dependencies unpinned and full transitive license/rights not assessed. Main docs dispatch only, PRs #1–#9 Draft/unmerged; no Vercel/prod URL.
Commercial draft up to TWO input files remains NOT IMPLEMENTED: only one CSV OR JSON accepted. Owner-approved multi-file rule/contract change required, not silent narrowing. No real customer sources, clean Windows human pilot, security clearance or release.

## NEXT READY D7-01
New feature branch from tested D6; offline synthetic **security/recovery/error-path testing**, add fixes and rigorous Linux/Windows/Chromium CI, do not vendor or touch external data. Specific test plan docs/17_NEXT_TASK.md; update main handoff and evidence after each unit. Preserve 3-day MVP-first strategy without implying completed sale process.
