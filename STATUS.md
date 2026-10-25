# REA_Web STATUS — 2026-10-26 KST

**PHASE: D6-01 verified on feature branch; D7-01 READY.** Main is documents/dispatcher only, NOT a merged app. All PRs #1–#9 Draft/unmerged. NOT commercial/production-ready.

## Verified stage history
| Unit | Verified branch | Exact evidence |
| --- | --- | --- |
| D1 owner CSV app | feature/csv-local-mvp 5515a728... | Actions 40198326369, 9 pytest + Chromium PASS |
| D2-01 review-only Fable/Astra adapter | feature/evidence-adapter fda96076... | 40199741969, 28 pytest PASS |
| D2-02 CSV + optional isolated review | feature/orchestrator 46060b46... | 40200704855, 55 pytest + Chromium PASS |
| D3-01 3 domains/ZIP/Windows | qa/cross-platform e88c89f3... | 40202313506, 68 pytest each OS + Chromium PASS |
| D4-01 unapproved schema/category summary | feature/mvp-summary-preview d8e26ed7... | 40203444938, 77 pytest each OS + Chromium PASS |
| D5-01 strict single JSON input | feature/json-intake b1ef76b5... | 40204413087, 111 pytest each OS + Chromium 4 scenarios PASS |
| **D6-01 source/dependency/package audit** | **feature/license-provenance b97443657e46a8f701e12b83bf87f5a0339b224c** | [Actions 40205614846](https://github.com/hibi89/REA_Web/actions/runs/40205614846) **SUCCESS**, **125 pytest PASS on Ubuntu and Windows-latest each** (1 warning each); vendor 88 Fable + 103 partial Astra Git source blobs each OS PASS; Linux real Chromium 4 synthetic apps PASS; Windows native .cmd HTTP PASS. [Draft PR #9](https://github.com/hibi89/REA_Web/pull/9), unmerged. |

## D6 delivered and verified
- New offline rea/provenance.py inspects actual deterministic delivery ZIP: SHA256 members, exact allowed paths, only fastapi/uvicorn declared runtime dependencies, localhost command, unapproved schema/Fable status. Rehashed unexpected engine files or .env are rejected.
- Vendor imported source integrity verified **88/88 and 103/103** against pinned Git blobs (PARTIAL Astra snapshot), not a copyright/license clearance.
- Github upstream pinned commit trees examined: no conventional LICENSE/NOTICE in Fable/Astra source trees; rights and redistribution **UNKNOWN/BLOCKED**, not assumed.
- Generated ZIP ships neither vendor engines nor raw Fable captures; it does carry owner-provided SQLite rows, therefore **cannot certify no PII/secrets or rights**.
- Direct runtime requirements fastapi>=0.110,<1 and uvicorn>=0.27,<1 are ranged NOT LOCKED; resolved exact versions, transitive notices, vulnerability/license obligations **NOT ASSESSED**.
- [D6 detailed source/redistribution risk register](https://github.com/hibi89/REA_Web/blob/feature/license-provenance/docs/25_SOURCE_LICENSE_AUDIT.md); Actions artifact rea-d6-synthetic-provenance ID 12602923880 (4 synthetic screenshots, 2 sample ZIPs, hash and source JSON reports).
- Initial Windows run 40205493975 failed pinned Git blob comparison due to CRLF checkout. Fix Git core.autocrlf false before pinned vendor checkouts; retested PASS both OS on 40205614846. Previous D1–D5 functional source refs unchanged.

## Release blockers
- **Two-input promise unresolved**: draft 300,000 KRW offer includes up to 2 files; implementation accepts one CSV OR one flat JSON input at a time; no owner-approved join/mapping. DO NOT sell as 2-file support.
- Fable/Astra source license/ownership grants and generated-app customer distribution rights unresolved. Runtime package full SBOM, versions and license obligations unresolved.
- Real owner+website authorization/parity, clean nondeveloper Windows install, full security/recovery, operator wizard/mapping, merchant terms/refunds and 6–8h internal cost exercise NOT RUN.
- Vercel/public production URL NOT CONFIGURED. No real customer data or production database touched.

## NEXT READY: REA-MVP-D7-01
Local synthetic **security/recovery failure-injection testing** on a new feature branch derived from verified D6. Preserve minimum input/source protections; test interrupted generation, safe rollback and restore, ZIP tamper/directory traversal/partial write, CSV formula cells, resource limits, loopback service and review isolation; fix verified defects and run CI before D7 DONE. No live customer sources, external deployment or license-clearance claim. Two-file commercial scope remains BLOCKED for owner business rule or approved revision. See docs/17_NEXT_TASK.md.

Resumption trigger ㄱ or [REA_Web 깃헙 레포지토리 보고 작업이어가셈] => inspect latest GitHub and execute NEXT READY unit in the current turn.
