# 03 — Source inventory and provenance

## Fable 5.1
- Repository: https://github.com/hibi89/fable5.1_web_catcher
- Commit: bbe72c0acd3a3e355062d6bd0d866af33e5274b0.
- Provided reviewer ZIP in conversation: outer ZIP with one inner ZIP; inner contains 88 source/ files, 20 examples/, 2 test_logs/, 2 manifest JSONs = 112 entries. Source manifest claims sensitive scan PASS and examples are redacted fixtures; source folder is NOT a complete git clone.
- Local manifest review: 110/110 SHA/length checks PASS; 16 Git blob hashes independently matched GitHub source at exact commit in earlier verification.
- Essential runnable entry: source/scan.py, scanner/, requirements.txt; Fable workflow files remain inside vendor path and should not execute as REA_Web top-level Actions.
- Baseline historical CI: Step5 Windows 123/123, headed Chromium 23/23 and public smoke 4/4 per upstream STATUS; not REA_Web integration evidence.

## Astra Web Catcher
- Repository: https://github.com/hibi89/astra_web_catcher
- Main SHA dc23ee604d02513c890615a3a98440c1ea8a5270: BookHarbor and CareerWay standalone examples, NOT the general observer/generator.
- P4 proof feature SHA b3166b67604381a9d2afd41667b65f9a9b103b37, source modules astra_contracts, fixtures and p4 browser scripts. Hosted full Python 940 pass/2 skip (historical), synthetic owner isolation; not actual customer DB or generic generation.
- P4 developer SHA 274402a3d8eaf33d9ff55bf740208a1dbded3bef: includes personal synthetic pipeline and Windows client preview; Windows whole suite has unresolved FAIL/ERROR and GitHub full CI for latest commits NOT established.
- Prefer importing the verified P4 feature baseline to an immutable snapshot and document codex delta separately. No direct main merge with source import.

## Source safety
Sources are owned by same repository owner but any third-party packages, brand assets, screenshots, reference data and license must be reviewed before customer redistribution. Do not import stored customer account data, tokens, private PDFs, original screenshots, caches, ZIP review artifacts or generated test databases.

## Verification checklist
Source commit pinned → each imported path SHA verified via exact Git blob or content hash → redaction scan → upstream baseline tests rerun under isolated environment → integration tests new results. Repository import itself != upstream tests or product complete.

## REA_Web actual import evidence (2026-10-25)
- Fable import: 88/88 reviewer-ZIP source entries under engines/fable51 on import/fable51-bbe72c0 @ 7e6f273b359b207fad8f92016226e3058cbcb839, 8 batch Git blob manifests. Draft PR #1 → integration/develop.
- Astra import: bounded 103-file subset (all 41 astra_contracts modules, scripts/synthetic fixtures/tests/demo app files) under engines/astra_p4 on import/astra-p4-b3166b6 @ f044b66e799289a5a353fdb9cbfdb324e683ffa3, 9 batch Git blob manifests. Draft PR #2 → integration/develop.
- Remote readback confirmed four sentinel Git blob hashes match their pinned upstream. All-file automated checking configured in tools/verify_vendor_manifests.py; actual Actions PASS not yet observed.
- No main/develop vendor source merge or REA integration test was performed. Full Astra clone still required if future tests need omitted fixture paths.
