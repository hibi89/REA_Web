# REA_Web dispatcher — SINGLE ACTIVE READY task (2026-10-26 KST)

Exact user trigger ㄱ or [REA_Web 깃헙 레포지토리 보고 작업이어가셈]: inspect CURRENT remote main + HANDOFF.md + STATUS.md + AGENTS.md + this file and immediately perform next bounded safe engineering unit. No user reprompt or background execution.

## D6-01 DONE, actual verification
- Branch feature/license-provenance source SHA b97443657e46a8f701e12b83bf87f5a0339b224c, [Draft PR #9](https://github.com/hibi89/REA_Web/pull/9) UNMERGED, based on D5 b1ef76b5....
- [GitHub Actions 40205614846](https://github.com/hibi89/REA_Web/actions/runs/40205614846) **SUCCESS**: **125 pytest PASS on Linux and Windows each** (one nonblocking warning per OS); actual Git blob checks **88 Fable + 103 Astra partial** both OS PASS; four synthetic Chromium apps Linux PASS; real Windows CMD HTTP PASS. Synthetic artifact rea-d6-synthetic-provenance ID 12602923880 includes vetted ZIPs and metadata report files.
- Initial D6 CI 40205493975 Windows SHA failure caused by Git auto CRLF; fixed core.autocrlf false **before** both vendor checkouts; exact retry 40205614846 success. Never count failed run as verified.
- New rea/provenance.py, tests/test_d6_provenance.py, docs/25_SOURCE_LICENSE_AUDIT.md and .github/workflows/rea-d6.yml. SHA256 + allowlist rejects vendor sources/.env even with recomputed manifest. Customer data.sqlite may contain owner-sensitive cells; not a no-secrets certification.
- SOURCE RIGHTS: No conventional LICENSE/COPYING/NOTICE found for pinned Fable/Astra upstream tree; redistribution NOT CLEARED. Runtime FastAPI/Uvicorn exact versions, transitive licenses NOT ASSESSED. DRAFT 30만원 **2-file** promise remains BLOCKED: current one CSV OR one JSON only.

## ACTIVE READY: REA-MVP-D7-01 — synthetic security & recovery failure injection
Create NEW conflict-free feature branch from actual latest D6 branch, no force-push or vendor/import modification. Keep high-value MVP functionality. Do not access real customer data or sites.
1. Inspect current rea/mvp.py, orchestrator.py, delivery.py, provenance.py, FastAPI generated template and tests. Read docs/05_ACCEPTANCE.md and docs/25_SOURCE_LICENSE_AUDIT.md. Run only local synthetic/coded tests.
2. Identify and test actual failure/abort modes: source CSV/JSON malformed/size/duplicate, existing output and interrupted/stale stage; ZIP corruption/duplicate/traversal, overwrite race and cleanup; path-symlink redirection; read-only SQLite and API/manifest/review nonexposure; loopback-only launch; CSV formula cells should remain inert if displayed/exported. Do not assert GUI tests on Windows without browser evidence.
3. Fix demonstrable defects minimally, preserve functional CSV/JSON, Fable review-only, deterministic ZIP and D6 strict auditor. Use temp directories and local synthetic data. Add tests/negative cases with real assertions, not placeholder pass or security certification.
4. Run Linux+Windows real pytest, actual Chromium regressions, package audit and vendor 88/103 source verification in CI, Windows CMD/HTTP, record exact source SHA/tests/proof. Draft PR to integration/develop, no merge.
5. Update main STATUS/HANDOFF/NEXT_TASK and work breakdown. Mark incomplete licenses, 2-file owner mapping/contract, real customer/reference rights, nondeveloper clean Windows, exact dependency licenses and any remaining security risks as BLOCKED/NOT_RUN. Do not claim sale readiness.

## After D7
D8 clean Windows end-user workflow & bounded guided mapping if safe, owner-approved two-file business relationship/contract resolution, strict dependency lock/license/notice review, real authorized customer/parity acceptance and commercial terms. Sale remains blocked until applicable G0–G6 gates pass.
