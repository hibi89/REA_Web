# REA_Web STATUS — 2026-10-26 KST

**D7-01 DONE (feature verified), D8-01 NEXT READY.** Main is documentation/dispatcher, runnable integrated code is on UNMERGED Draft PR #10; not yet commercial/production-ready.

| Unit | Tested capability | Evidence |
| --- | --- | --- |
| D1 | CSV app list/search/filter/detail | CI 40198326369, 9 pytest + Chromium PASS |
| D2-01 | Fable to Astra technical review only | CI 40199741969, 28 pytest |
| D2-02 | Independent CSV app + optional review | CI 40200704855, 55 pytest + Chromium |
| D3 | 3 cases, ZIP, Windows | CI 40202313506, 68 pytest each OS |
| D4 | Schema lexical preview UNAPPROVED and category summary | CI 40203444938, 77 pytest each OS |
| D5 | One CSV or one strict JSON | CI 40204413087, 111 pytest each OS |
| D6 | Pinned 88 Fable / 103 partial Astra Git blob verification and ZIP allowlist | CI 40205614846, 125 pytest each OS |
| **D7-01** | **Atomic no-replace directory/ZIP publication, rollback, SQL query-only, formula as inert text** | **[CI 40206549211](https://github.com/hibi89/REA_Web/actions/runs/40206549211): Ubuntu 141/141 pytest PASS + Windows 141/141 pytest PASS; 5 actual Chromium synthetic cases Linux, native Windows CMD + localhost HTTP, source 88/103 Git blob proofs both OS PASS.** |

D7 tested functional SHA `8e7baa8eb14340eae2e7b46f1cf7b9272799c715`; latest documentation-only branch head `f85b40836ffb1a9343193a8a2fc224249749958d` on `feature/security-recovery`. [Draft PR #10](https://github.com/hibi89/REA_Web/pull/10), unmerged. Both push & PR workflows on latest head verified green. Synthetic Actions artifact `rea-d7-synthetic-recovery` ID 12603349624 has 5 browser screenshots, JSON report and sample ZIP/provenance proof.

D7 changes: Linux renameat2 RENAME_NOREPLACE prevents empty-directory race overwrite; Windows directory rename rejects existing owner target. ZIP is fully verified in private stage before an atomic same-filesystem hardlink into final name (no partial public ZIP). Unsupported OS/filesystem fails closed. Leaf output symlink and stage cleanup failure-tested. SQLite URI mode=ro + PRAGMA query_only=ON. JSON summary reports JSON origin. CSV formula-looking strings rendered only via safe DOM text. docs/26_SECURITY_RECOVERY.md on feature explains boundaries.

**Still BLOCKED / NOT_RUN:** Initial 300,000 KRW proposed TWO files, actual ONE CSV OR JSON; no approved two-file join/mapping or offer revision. Fable/Astra and generated code redistribution rights and full dependency locks/licenses not cleared. Actual authorized customer/website rights, clean Windows nondeveloper, power loss/fsync recovery/backup, privacy screening, penetration security, support/refunds and labor cost study not completed. No Vercel/public deployment or real customer data.

**NEXT D8-01:** guided single-file user preflight and explicit field mapping approval, retaining existing strict CSV/JSON and Fable REVIEW_REQUIRED. No automatic two-file merge or semantic guess. Detailed docs/17_NEXT_TASK.md. User ㄱ initiates the next safe task.
