# REA_Web local commercialization follow-up — 2026-10-30

## Remote source baseline

- Repository: `hibi89/REA_Web`, branch `feature/d27-windows-python-discovery`.
- D27 source SHA: `6ca9a03bcb3619fd4d1ea9922cf2e4a1557ec225`; Draft PR #30 remains open/unmerged.
- Actions [#40378905450](https://github.com/hibi89/REA_Web/actions/runs/40378905450): Linux 412 passed / 4 skipped / 1 warning; Windows 426 passed / 1 warning. Run completed successfully for both jobs.
- Linux Chromium 8 synthetic apps + 3 extracted delivery ZIP browser cases passed. Windows native CMD fallback, integrity refusal, ZIP-to-loopback HTTP, and Tk/fresh-venv flows passed. Synthetic owner pilot artifact ID `12678683196`; its manifest states human acceptance `NOT_RUN` and commercial clearance `NOT_GRANTED`.
- The supplied source snapshot has no `.git`. Before editing, local file blob hashes matched the remote D27 branch for all changed existing source files: root `README.md`, `STATUS.md`, `HANDOFF.md`, `WORKER_START_HERE.md`, `docs/07_KMONG_OFFER.md`, `docs/17_NEXT_TASK.md`, `docs/46_WINDOWS_PYTHON_DISCOVERY.md`, `rea/customer_self_check.py`, `rea/delivery.py`, and `tests/test_d27_python_discovery.py`.

## Local changes in isolated work copy

| File | Change | Reason |
| --- | --- | --- |
| `rea/customer_self_check.py` | Add `--customer-check` Korean summary, clean-extract recovery actions, actionable unsafe-port message and UTF-8 output; keep default JSON contract. Require the delivered acceptance checklist in fresh packages. | Customers need understandable diagnostics and a checklist without weakening default integrations. |
| `rea/delivery.py` | Generated checker invokes customer-readable mode; generated CMD sets UTF-8 output; embedded Windows README documents setup, recovery, run/stop/restart and privacy; add `ACCEPTANCE_CHECKLIST.md` to every ZIP. | The actual delivered ZIP needs actionable instructions and a review checklist. |
| `tests/test_customer_guidance.py` | Add focused summary/recovery/port output, generated asset contract, and acceptance checklist content checks. | Cover wording and fail-closed messaging without packaging side effects. |
| `tests/test_d27_python_discovery.py` | Assert generated check command uses customer-readable mode and its guide includes recovery content. | Keep D27 Windows fallback packaging assertions aligned with the new generated files. |
| `README.md` | Replace stale D2 overview with current product scope, 299,000 KRW as an unapproved target, current CI evidence, limitations, and guide links. | Prevent stale project instructions from appearing current. |
| `STATUS.md` | Add current D27 CI outcome and separate local work status above historical entries. | Preserve old record while making current evidence visible. |
| `HANDOFF.md` | Add verified remote D27 baseline, isolated-copy work notes, and safe next gates above historical handoff. | Preserve original timeline and avoid confusing old READY task with current work. |
| `WORKER_START_HERE.md` | Add current status override and links to the follow-up log/dispatcher. | New sessions should not resume superseded D2 instructions. |
| `docs/17_NEXT_TASK.md` | Replace obsolete D2 dispatcher with current D27 evidence, local follow-up status and remaining independent/release gates. | Keep the canonical next action accurate. |
| `docs/46_WINDOWS_PYTHON_DISCOVERY.md` | Append exact completed D27 CI evidence. | Distinguish verified D27 behavior from the new unverified local delta. |
| `docs/07_KMONG_OFFER.md` | Replace stale 300,000 KRW/D5 draft with the user-requested 299,000 KRW proposed scope and implemented limits. | Avoid promising two screens, joins, or unverified commercial readiness. |
| `docs/47_LOCAL_COMMERCIALIZATION_FOLLOWUP.md` | Record file-level change rationale, baseline evidence, validation and blockers. | Provide a durable change ledger. |

All edits are in `E:\REA_Web_Kmong\REA_Web-feature-d27-windows-python-discovery-work-20261030`, an isolated copy. The original `REA_Web-feature-d27-windows-python-discovery` remains the source snapshot and is not the worktree.

## Validation actually performed

- **PASS:** `python -m pytest -q tests/test_customer_guidance.py` — **8 passed locally**.
- **PASS:** `python -m compileall -q rea tests/test_customer_guidance.py tests/test_d27_python_discovery.py`.
- **PASS:** static generated-asset contract check verified the checklist/manual link, customer-check mode, UTF-8 console setup and absence of CMD port expansion.
- **BLOCKED locally:** `python -m pytest -q tests/test_d27_python_discovery.py` — all 3 cases failed before reaching their assertions because Windows denied the generator's intentional atomic `os.rename`/`os.link` publication (`WinError 5: Access denied`) in both sandbox temp and project-local paths. This environment-level denial is not counted as a product test pass or a CI failure. No test was skipped or weakened.
- **NOT RUN for this local delta:** full regression, generated ZIP extraction after the changes, Windows CMD execution on a customer machine, browser E2E of a newly generated ZIP, a real nondeveloper user pilot, or new-source GitHub CI.
- The earlier D27 green run is evidence for the unmodified baseline SHA only; it cannot be used to claim these changes passed CI.
- **PASS:** `git apply --check` and `git apply` succeeded against a fresh copy of the original D27 files; all **12** resulting Git blob hashes equal the modified work copy.

## Commercial and delivery status

The current implementation can generate one-source CSV/flat JSON apps and explicitly approved same-schema two-source ROW APPEND deliveries. It does not implement cross-schema JOIN, public hosting, login/payment, general CRUD, scraping or live DB migration. The requested **299,000 KRW** price is a target only. Actual customer rights, source/dependency redistribution terms, privacy/security/backup review, human acceptance, three real labor measurements, and signed scope/support/correction/refund terms remain **NOT CLEARED**.

## GitHub reflection state and durable bundle

The original folder has no `.git`. The GitHub connector created normal child commits on the existing branch; PR #30 stays Draft/unmerged. The patch is `E:\REA_Web_Kmong\REA_Web_Kmong_D27_followup_20261030\REA_Web_kmong_followup.patch`. The original/modified file bundle is under `E:\REA_Web_Kmong\REA_Web_Kmong_D27_followup_20261030\files` and is also archived as `E:\REA_Web_Kmong\REA_Web_Kmong_D27_followup_20261030.zip`. These deliverables survive cleanup of the temporary work copy.

## Follow-up CI findings and fixes (2026-10-30)

- The initial follow-up head `0fd8008f9f3a9126e1ec017a7d9d11bff65bafe4` was tested by Actions run [#40906386284](https://github.com/hibi89/REA_Web/actions/runs/40906386284). Full D1-D27 regression failed on both Linux and Windows: **80 failed, 340 passed, 4 skipped, 1 warning** on Linux. The failures traced to the new checklist not being admitted by the existing ZIP provenance allowlist, a port-error compatibility token, and the D27 guide wording assertion. This is a real integration regression, not an environment-only CI issue.
- Fixed the allowlist/required member and restored `unsafe REA_WEB_PORT` in the actionable Korean error. Commits: `4343c68b180645c22eb88bee460722a6ce946c79` (allowlist), `bf4e6f75a5a60cb1971179aa7edf0d7ac3662b6b` (port token), and `8dbb50438aa45a4a752d906605731564122c1f19` (normalize allowlist).
- Restored the D27 guide's explicit interpreter phrase in `370f70e3df2719ad37fdcd004c2f7b4a223f9f45`, added stable NOT_RUN/NOT_GRANTED markers to the customer-readable successful preflight, and made Windows Unicode fixture assertions explicitly decode UTF-8. The branch also contains normal follow-up commits `93f5c93f03aa2b87d7c17136ba8a343f1333db0a`, `c103d78e39814e515e3fe0bbc2e63d3671c6114c`, `2fafff59fb7370f2e9f5c5d5d33092ad0d592d19`, and `3e31a34831f96fe20b9b2eaff0d8a7747b0aa617` for those edits.
- Local D24/D27 native Windows focused suite: **32 passed**. Local full regression, with `PYTHONUTF8=1`, completed **406 passed, 22 skipped, 6 blocked**; the six blocked security tests require creating symbolic links, and Windows returned `WinError 1314` at fixture setup before reaching product assertions. No assertions were disabled.
- Generated three deterministic synthetic deliveries, verified ZIP hashes and extracted self-checks, and ran the extracted ZIPs in real local Chromium: **3/3 PASS** for list/search/filter/detail/summary as contracted, reload persistence, zero JavaScript errors, zero dialogs, and zero external requests. This is automation against synthetic fixtures, not human/customer acceptance. Screens and JSON receipts are preserved in the follow-up bundle.
- At the time of this update PR #30 is still Draft/open/unmerged and latest-head D27 Actions run [#40908092345](https://github.com/hibi89/REA_Web/actions/runs/40908092345) is queued on Linux and Windows. Do not mark those exact-head CI checks verified until both jobs complete.
- `python -m compileall -q rea scripts tests` and focused customer guidance tests: **8 passed**. The PR check runs queued on latest code after the initial failure; no actual nondeveloper customer machine or manual recovery review was performed.

