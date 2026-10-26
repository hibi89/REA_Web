# REA_Web — NEXT READY single dispatcher (2026-10-27 KST)

**Trigger** `ㄱ` or `[REA_Web 깃헙 레포지토리 보고 작업이어가셈]`: refetch latest GitHub HANDOFF → STATUS → AGENTS → this dispatcher → source, then implement the next bounded safe READY unit. Do not ask repeated questions or claim fake human tests, rights or production deployment.

## Latest fully VERIFIED D20 — immutable proof
- Repo public `hibi89/REA_Web`; implementation branch **feature/offline-pilot-selfcheck**, SHA **40dfdd6c4abd9bbe46519134e9854adf5aa63c53**, [Draft PR #23](https://github.com/hibi89/REA_Web/pull/23) OPEN UNMERGED.
- [Real Actions #40355014003](https://github.com/hibi89/REA_Web/actions/runs/40355014003) **COMPLETED SUCCESS Linux + Windows**, Python3.11 **329 pytest PASS per OS**, zero failure/skip, one nonblocking warning each; actual Linux 8+3 Chromium generated apps, actual Tk, Windows native GUI→ZIP→same fresh isolated venv loopback HTTP (5 rows/filter/detail/404), pinned Fable 88/Astra PARTIAL 103 source hashes, original Windows CMD PASS. The **new extracted `CHECK_PILOT_OFFLINE.py`** independently executed on BOTH OS, `OFFLINE_KIT_INTEGRITY_PASS`, eight files, 5 rows, no network, `human_acceptance=NOT_RUN`, `commercial_clearance=NOT_GRANTED`.
- Actions synthetic-only `rea-d20-synthetic-windows-owner-pilot` artifact ID **12665736905**, archive 20,152 bytes (run above). Source: `scripts/d20_offline_kit_check.py`, updated D19 kit publisher, `tests/test_d20_offline_kit_check.py`, `.github/workflows/rea-d20.yml`, `docs/39_OFFLINE_PILOT_SELFCHECK.md`. D19 rollback SHA **990ec2a9421c9a5f34973b2b7584f3c766668ae8** is itself independently verified 313 tests/OS.
- Initial D20 Windows run #40354163531 had 329 pytest PASS but *Windows-specific offline checker step was misplaced in the Linux job*; not accepted. Corrected at tested source SHA above. Do NOT repeat or revert that workflow relocation.
- No Vercel deployment, vendor source alterations, real customer data, installer, paid API, human accepted order, or merge. All Draft PRs kept separate; G5/G6 blocked.

## NEXT READY D21-01 — safe no-install Windows double-click kit check

Goal: reduce genuine operator friction between D20's `python CHECK_PILOT_OFFLINE.py` command and the later required **real nondeveloper Windows trial**, without pretending trial occurred.

Compare:
- **A (recommended):** small native Windows CMD wrapper INCLUDED IN SYNTHETIC KIT that only invokes existing `CHECK_PILOT_OFFLINE.py` using local existing Python3.11+ and preserves its status code. Detect missing Python/Tk? No Tk needed for checker. UTF8 console output local to process, no auto-install or system modification. Safe explicit `--check` or no-argument mode; fail closed if file missing/tampered or Python unavailable. Test with real `cmd.exe` on native Windows, stdout/stderr, correct exit code and SHA/no-overwrite, and full existing CI.
- **B deferred:** signed/self-contained EXE, auto pip/winget, privilege elevation, vendor bundling. Raises licensing/security/update cost; no authorization.
Implementation must not silently mark human acceptance PASS. Refuse unsafe args, never use a global Python alias requiring admin, and work only inside the user's extracted synthetic sample folder. If no reliable native Windows test is available, do NOT claim implementation complete.

Task outline:
1. Branch from **exact D20 verified SHA 40dfdd6c4abd9bbe46519134e9854adf5aa63c53**, no source vendor or customer data changes. Read current `scripts/d19_owner_pilot.py`, `scripts/d20_offline_kit_check.py`, original Windows launcher conventions, workflow and tests.
2. Add bounded CMD wrapper as ninth kit member, with SHA manifest and Windows-language guidance. On use, check local script, use existing `py -3.11` or `python` without installing anything, run `CHECK_PILOT_OFFLINE.py`, preserve its return code and report `MISSING_PYTHON` separately. It must NOT launch actual app or prompt for real customer files.
3. Add Linux source-only tests and actual Windows native `cmd.exe` pass + no Python + tampered script negative tests, original files unchanged, no added network. Run complete Linux/Windows pytest and genuine Linux 8+3 Chromium, Windows Tk/ZIP/local HTTP and pinned provenance proof. Keep Draft PR/unmerged and update main handoff after confirmed CI.
4. If blocked, mark exact failure and skip owner-required actions; no unauthorized install, shipping claim or production deployment.

## Commercial G5/G6 still BLOCKED
Actual authorized client/reference/rights, three human-timed jobs, genuine Windows nondeveloper user accessibility/onboarding, third-party Fable/Astra and dependencies license NOTICE/redistribution, PII/security/backup/recovery, bounded 300,000 KRW SAME-SCHEMA ROW APPEND-only scope and support/refunds. Local app runtime 127.0.0.1; Production/Vercel NOT APPLICABLE.
