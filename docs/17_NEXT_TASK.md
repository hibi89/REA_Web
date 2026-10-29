# REA_Web — current delivery dispatcher (2026-10-30)

## Follow-up state and next task (2026-10-30)

- Exact feature branch HEAD `64b28c986618c68472649474c6604c2b1fce7372`; 5 commits ahead/0 behind baseline `db6711e`; PR #30 remains draft and unmerged.
- Latest CI connector response: 27 workflows returned, 27 completed SUCCESS. The first-page-only response omitted one expected run, so 28/28 is unconfirmed.
- FastAPI/Starlette/Uvicorn lower and upper supported ranges are enforced by code at 64b. Local isolated guidance 18 PASS; compileall PASS. Full local suite did not complete cleanly in the managed Windows sandbox: 235 PASS/17 SKIP/174 FAIL on first run, dominated by WinError 5; workspace temp retry stalled and was interrupted. Focused D27/D26/guidance ran 18 PASS/9 filesystem-publication FAIL (sandbox `os.link` denial).
- Older sample ZIP and Chromium/Windows receipts are synthetic, some from source `f6e34f6`; rebuild at exact 64b before claiming fresh exact-head delivery/browser acceptance.

## Next independent actions

1. Run full D1-D27 tests on unrestricted Windows to validate hard-link/atomic publication paths; current sandbox run is incomplete.
2. Regenerate synthetic single-source and approved same-schema append ZIPs from exact 64b source. Verify manifest, CRC, extraction, launcher `/health`, query/detail, restart/data persistence, and Chromium UI.
3. Update package vulnerability and license/NOTICE evidence from exact release artifacts. Rights stay NOT_GRANTED until a documented human decision.
4. Keep independent nondeveloper customer Windows acceptance NOT_RUN until actually performed. Keep seller fees, delivery/revision/support/refund terms unapproved until checked in the seller account.

## Release gate

Not approved for listing or customer release. CI, isolated tests, and synthetic samples do not establish human acceptance, customer data authorization, commercial rights, or seller approval.

## Verified remote state

- Repository `hibi89/REA_Web`; branch `feature/d27-windows-python-discovery`; exact HEAD `578442b2bd22bb64a004e77bbd091a17930f614a`.
- Latest exact-head GitHub CI: **28/28 SUCCESS**, including D27 Windows/Linux full regression and D6 supply-chain/security. Runs: D27 PR [#40954859581](https://github.com/hibi89/REA_Web/actions/runs/40954859581), D27 push [#40954852936](https://github.com/hibi89/REA_Web/actions/runs/40954852936), D6 [#40954859774](https://github.com/hibi89/REA_Web/actions/runs/40954859774).
- PR #30 is OPEN / DRAFT / UNMERGED. No merge or force push.
- Generated requirements set Starlette `>=1.3.1,<2`; customer self-check rejects versions below the floor and reports Korean recovery steps for `python` or `py -3`.
- Local focused preflight/guidance tests 13 PASS; compile, local dependency floor/pip check and patch application PASS. Five synthetic extracted ZIPs passed Windows preflight, CRC and manifest checks.
- Human acceptance NOT_RUN; source/dependency redistribution rights NOT_GRANTED; customer data/privacy operations NOT_APPROVED; target 299,000 KRW and seller terms not approved.

## Supported delivery scope

Customer-authorized UTF-8 CSV or flat JSON → preview → explicit field-mapping approval → generated local read-only FastAPI/SQLite app → list/search/category filter/detail → Windows ZIP. Same-schema two-file ROW APPEND requires explicit approval for both. Different-schema JOIN, scraping/site cloning, CRUD, hosting, login/payment and live synchronization are not offered.

## Next independent actions

1. Build a reproducible dependency graph for the generated runtime, including actual resolved versions, transitive edges, license fields and available license/NOTICE file hashes. State clearly that this is inventory evidence, not redistribution approval or a lockfile.
2. Compare the runtime inventory with the optional vendor/source payloads and the repository's undeclared source license; preserve rights as NOT_GRANTED pending rightsholder review.
3. Continue privacy and data-retention review using synthetic fixtures only. ZIPs contain SQLite data in plaintext; do not claim encryption, PII scanning, secure erase or automatic backup.
4. Keep the nondeveloper Windows acceptance form NOT_RUN until a person who did not build the app follows it on a typical Windows setup. Do not infer this from CI.
5. Confirm the seller's category, platform fee, time/cost, delivery/revision/support/refund terms before publishing any listing.

## Release gate

Not approved for listing or customer release. CI and synthetic packages do not grant source rights, authorize customer data, or equal human acceptance. Preserve existing source and customer data; do not force-push or merge PR #30.
