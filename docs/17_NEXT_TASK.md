# REA_Web — SINGLE NEXT READY (2026-10-26 ~02:40 KST)

Trigger ㄱ or [REA_Web 깃헙 레포지토리 보고 작업이어가셈]: refetch actual GitHub main/feature refs and read HANDOFF -> STATUS -> AGENTS -> this dispatcher -> source. Execute next safe unit in same turn; no repeated known questions, no background promises, blind merge/deploy, real customer data or paid calls.

## LAST DONE D16-01 — real evidence
- Source branch feature/windows-creator-launcher SHA **d1ed3bd6d09ecf4cf1acc2102a18916c89b6c587**; [Draft PR #19](https://github.com/hibi89/REA_Web/pull/19) UNMERGED. [GitHub Actions run 40217420084](https://github.com/hibi89/REA_Web/actions/runs/40217420084) completed **SUCCESS** at 2026-10-25 17:40:16 UTC.
- Ubuntu Python 3.11 **283 pytest PASS**, Windows-latest Python 3.11 **283 pytest PASS**, 1 nonblocking warning each (+17 D16 vs D15 266). Linux 8 real synthetic Chromium webapps + 3 real Chromium extracted delivery ZIPs PASS. Windows generated ZIP native .cmd→localhost HTTP PASS. Immutable Fable 88/Astra P4 PARTIAL 103 blob SHA proofs both OS PASS. Actual one-file and two-file synthetic Tk GUI widget flows PASS Linux Xvfb and Windows.
- Root START_REA_CREATOR.cmd is NO-INSTALL offline Windows double-click helper, runs from own repo directory, priority existing .venv then py -3.11 then python; creator_preflight validates Python3.11+, fastapi/uvicorn/pydantic presence and opens transient Tk. --check returns 0 READY or 10 missing Python, 11 missing modules, 12 Tk unavailable, 2 bad args, 13 internal error, does not launch GUI. Actual Windows cmd.exe **READY --check + invalid arg denied + isolated child PATH NO_PYTHON denied PASS**. No pip, admin, registry, PATH persistence or external network. Documentation docs/35_WINDOWS_CREATOR_LAUNCHER.md.
- First D16 Windows CI had 283 pytest PASS but CMD failed UnicodeEncodeError when redirected Korean output under non-UTF8 Windows runner locale. Fixed with process-local chcp 65001 and PYTHONIOENCODING=utf-8 under setlocal; exact later run above ALL GREEN, no bypasses.
- Linux two-file Tk screenshot CAPTURED artifact **12607763677**, Windows real two-file GUI PASS screenshot NOT_CAPTURED artifact **12608182831**. These developer CI observations are NOT actual human nondeveloper clean Windows use/acceptance. No real client/third-party source, commercial deployment, licenses or signed installer.
- Main docs/dispatcher only, PRs #1–#19 Draft/unmerged. No Vercel project or Production URL. Commercial G5/G6 remain BLOCKED: customer/reference permission, 3 timed human jobs, real consumer Windows, redistribution/NOTICE/legal rights, privacy/security/backup, 300k APPEND-only scope and support/refunds.

## NEXT READY D17-01 — fresh Windows isolated user-mode environment rehearsal
Product usability gap: successful creator CI uses a developer-preinstalled dependency environment. A newly prepared local Windows Python environment may lack runtime modules and confuse a novice, even though D16 preflight diagnoses missing modules.

**Architecture choices:**
A. CI-controlled **fresh Windows Python venv onboarding exercise**, first show D16 '--check' reliably REFUSES when packages absent, then CI-only manually install explicitly declared runtime dependencies into isolated venv, run CMD --check and real Tk synthetic one/two-source flows. Evidence includes exact dependencies, offline diagnostic counts and no auto-installer. Most useful/low-risk next test; selected.
B. Bundle/ship self-contained Python EXE or auto-installing bootstrap. Higher licensing, rights, signing, antivirus and update burden. Defer pending owner/legal/human approval.

**D17 bounded execution:**
1. Branch from exact D16 verified source SHA. Inspect current Windows starter CMD/diagnostic code, pip requirements in generated ZIP and D12 installed-distribution evidence; avoid sourcing unknown vendor/customer data.
2. Create reusable **developer-only** native Windows isolated venv first-run CI smoke, without changing launcher to auto-install. Assert environment initially missing modules and fail-closed (code 11), then CI explicitly installs minimal declared deps in that venv, assert --check READY, test actual Tk synthetic GUI/ZIP and local generated ZIP launch as feasible; emit only synthetic redacted machine-readable evidence. Optionally add clear novice directions that distinguish manual package installation from automatic actions. Do not claim machine is a truly clean home Windows device.
3. Full Ubuntu/Windows pytest; genuine Linux 11 Chromium apps, Linux/Windows actual one- and two-source Tk UI, pinned Fable/Astra source blobs, Windows native ZIP/CMD/localhost and previous D16 native launcher ready/negative checks. Fail-closed no auto-install remains invariant.
4. Draft PR UNMERGED; update main HANDOFF/STATUS/NEXT on actual CI result at exact SHA. Production, commercialization, customer data handling, redistribution/NOTICE, security, human Windows and real labor remain BLOCKED.

Avoid creating a release artifact that implies third-party redistribution grants. No payment, client data, public hosting or original source mutation.
