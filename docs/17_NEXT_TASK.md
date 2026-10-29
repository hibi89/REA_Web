# REA_Web — current delivery dispatcher (2026-10-30)

## Verified baseline

- `feature/d27-windows-python-discovery` at D27 source SHA `6ca9a03bcb3619fd4d1ea9922cf2e4a1557ec225`.
- Draft PR [#30](https://github.com/hibi89/REA_Web/pull/30), OPEN and UNMERGED.
- GitHub Actions [#40378905450](https://github.com/hibi89/REA_Web/actions/runs/40378905450) COMPLETED SUCCESS on both jobs: Linux 412 pytest PASS / 4 SKIP / 1 warning; Windows 426 pytest PASS / 1 warning. Linux Chromium 8+3 synthetic browser scenarios and Windows native CMD/ZIP localhost flows passed. D27 Windows PATH fallback suite: 3 PASS. Synthetic artifact `rea-d27-synthetic-windows-owner-pilot`, ID **12678683196**; checker says human acceptance NOT_RUN and commercial clearance NOT_GRANTED.
- Original feature SHA does not include the local Korean diagnostics follow-up described below.

## Current local unit — customer-readable Windows package diagnostics

**Scope:** make the extracted delivery ZIP understandable to a Korean Windows user without changing the approved runtime boundary. `check_windows.cmd` remains offline and read-only; a new `--customer-check` option prints concise next steps. Default self-check output remains JSON for scripts. Launch preflight failures and unsafe port messages explain recovery. The embedded ZIP manual covers new-folder extraction, `python` then `py -3` selection, same-interpreter optional package setup, localhost-only run/stop/restart, port collision, corrupted ZIP, access-denied paths, UTF-8 input and data preservation.

**Local validation:** `python -m pytest -q tests/test_customer_guidance.py` **9 passed**, including occupied-port refusal and generated CMD failure-pause contract; modified Python modules compile. An actual Windows `cmd.exe` invocation against an extracted, manifest-verified synthetic ZIP occupied a loopback port and returned code 2, `REA_LOCAL_PORT_UNAVAILABLE`, Korean recovery steps, alternate-port command, and visible pause. A free-port HTTP run after the new probe is **NOT_CONFIRMED** in this sandbox because no API response was obtained. The Windows sandbox denies the delivery publisher's `os.link` (WinError 5); for the launcher-content test only the isolated test harness used `os.replace`, so the production hard-link publish path is still unverified here. Current exact-head D27 CI remains queued and is not a pass.

## Next independent work

1. Continue past queued exact-head D1–D27 CI when it is not actionable; recheck it later. On a normal Windows runner, verify fresh ZIP publishing without substitution, free-port HTTP search/filter/detail, Ctrl+C and rerun persistence after the occupied-port change.
2. Review product scope against current functions: customer-provided UTF-8 CSV/flat JSON, explicit mapping approval, one source or explicit same-schema two-file ROW APPEND, list/search/category filter/detail, local SQLite/FastAPI ZIP. Do not promise SQL joins, CRUD, hosting, login/payment, scraping or data collection.
3. Keep actual nondeveloper human Windows acceptance, three manually measured service jobs, source/data rights, dependency/vendor redistribution NOTICE, privacy/security/backup/recovery and buyer agreement/refund/support terms BLOCKED until the owner supplies genuine evidence. No synthetic test can clear them.

## Release decision

**Not ready to list as an approved commercial service.** Proposed price is 299,000 KRW, but binding acceptance scope, support/refund terms, actual customer rights and G5/G6 evidence remain unapproved. Keep all PRs Draft/unmerged and do not publish a website or accept a customer order from these test results.

