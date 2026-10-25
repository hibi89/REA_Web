# 17 — Dispatcher / next unit (2026-10-25)

**ACTIVE: REA-P0-04 — Vendor checksum and dependency gate**
Branch: integration/develop (or qa/cross-platform for test changes).

Preconditions verified: Fable 88 source snapshot and Astra 103 subset snapshots on separate branches; PR #1/#2 Draft.
1. Run tools/verify_vendor_manifests.py on each import branch. Expect Fable 88/88 and Astra 103/103 if all source bytes preserved. Hosted CI status must be observed, NOT assumed.
2. Verify customer data/secret exclusions and third-party licenses. If Astra tests need omitted fixture files, import those as new versioned additions and update truthful PARTIAL manifest.
3. Isolate Python runtime; run Fable dedicated upstream tests in its own cwd and Astra selected tests in its own cwd, record pass/fail/skip per exact source SHA.
4. Review PR #1/#2 but do NOT merge until passing source gate and owner approval. Draft state is deliberate.
5. Then issue REA-P1-01: Fable evidence → Astra functional draft adapter with 15+ deterministic tests on feature/evidence-adapter.

Stop on evidence, never on arbitrary percentage. Customer operation DB/network/deploy requests require separate explicit approval. 'ㄱ' means proceed on next READY safe bounded unit; all changes get STATUS/HANDOFF/dispatcher update and commit SHA.
