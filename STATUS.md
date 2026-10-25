# REA_Web STATUS — 2026-10-26 KST

**D8-01 DONE on verified Draft PR #11; D9-01 READY.** Product is NOT commercially ready. Runnable code in feature branches is UNMERGED; main only dispatch/docs.

## Verified checkpoints
| Unit | Feature | GitHub CI evidence |
| --- | --- | --- |
| D1 | One CSV readonly local app | 40198326369: 9 pytest, Chromium PASS |
| D2-01 | Fable→Astra review-only adapter | 40199741969: 28 pytest PASS |
| D2-02 | Independent app + optional reference review | 40200704855: 55 pytest + Chromium PASS |
| D3 | Three scenarios, Windows CMD, ZIP | 40202313506: 68 pytest each OS |
| D4 | Unapproved lexical schema preview and category counts | 40203444938: 77 pytest each OS |
| D5 | Strict single flat JSON OR CSV input | 40204413087: 111 pytest each OS |
| D6 | Immutable Fable 88 / Astra PARTIAL 103 and ZIP allowlist | 40205614846: 125 pytest each OS |
| D7 | Atomic no-overwrite ZIP/dir and recovery failure injection | 40206549211: 141 pytest each OS |
| **D8-01** | **Private one-file owner preview, explicit mapping, approval & delivery receipt** | **[40207742776](https://github.com/hibi89/REA_Web/actions/runs/40207742776) SUCCESS: 164 pytest on Ubuntu + 164 on Windows, 7 actual Chromium synthetic apps, native Windows CMD/HTTP and vendor 88/103 Git blob tests both OS PASS**. |

D8 exact tested SHA `a6c35688a5d4cbda93274bc0cd21d1aa825fb255` on `feature/guided-intake`, [Draft PR #11](https://github.com/hibi89/REA_Web/pull/11) to integration/develop, unmerged. Synthetic artifacts `rea-d8-synthetic-guided` ID **12604027103**, including 7 screenshots/QA report and example ZIPs. One nonblocking TestClient warning per OS.

## Added in D8
- `python -m rea.guided inspect --csv/--json FILE` prints header names, counts, lexical hints and source SHA256, without printing customer cell values.
- `python -m rea.guided wizard` asks owner to type three DISTINCT source columns for `id/title/category`, displays mapping and requires literal `APPROVE`; CLI `build/pack` also require source fingerprint and explicit approval.
- Strict existing row/column/size limits preserved. Wrong/missing/duplicate mappings and source changed after preview fail closed. Never automatically bind Fable observations.
- `mapping_report.json` in generated app/ZIP tracks local confirmation, selected fields, source hash. Not served over HTTP. D6 ZIP provenance audit cross-checks receipt with manifest. Lexical type inference remains **UNAPPROVED** and local CLI confirmation is NOT verified customer identity/signature.
- Original exact-schema CSV/JSON commands still work without custom mapping, and D1–D7 tests remain green.

## Commercial blockers
- Draft starter price KRW 300,000 proposes **up to TWO files**, but current product still accepts ONE CSV OR JSON only. No approved cross-file relationship, union or join. Cannot market 2-file support.
- Fable/Astra and generated template commercial redistribution rights and direct/transitive dependency exact version/attribution audit unresolved.
- Clean nondeveloper Windows human install, real authorized customer + reference site acceptance, complete GUI, privacy screening, backup/power-loss, full pentest, support/refunds and job time cost NOT RUN.
- No public site, Vercel production, paid calls, real customer DB or external scraping.

## NEXT READY — D9-01
Offline synthetic **two-file explicit same-schema append prototype and honest scope specification**: permit only explicitly owner-selected same-column one-CSV/JSON pair with distinct IDs and no inferred joins, and report limitations; if safety cannot be established, document blocker and proceed with independent license/SBOM tests. This is NOT an authorization to change or publish the 300,000 KRW offer. Require approval and separate customer acceptance before sale. See docs/17_NEXT_TASK.md.
