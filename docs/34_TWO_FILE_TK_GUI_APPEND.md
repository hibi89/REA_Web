# D15 — Optional two-file offline Tk GUI: SAME-SCHEMA ROW APPEND

## Product boundary
This extends the prior one-file GUI by adding a distinct **"2파일 행 추가(APPEND)"** window; existing one-file CSV/flat JSON mode and CLI stay unchanged. No new localhost web server or customer upload. Input one or two distinct local owner files, never inferred joins, mismatched-schema reconciliation, arbitrary API/site scanning, foreign data or production database.

A. Extend existing stdlib Tk UI using D9 audited `rea.two_source.pack_pair`: no new server, lower maintenance/privacy risk. **Selected**.
B. Introduce a localhost browser upload wizard: more visual styling but increased session, upload and security surface. **Not implemented**.

## Real single-window vs second-window flow
Run on a developer-controlled local Python environment with Tk GUI and runtime dependencies:

    python -m rea.creator_gui

For one input, continue existing D13 workflow, do not click the optional pair button.

For a pair:
1. Click "별도 기능: 같은 컬럼 2파일 행 추가(APPEND)" to open a separate local window.
2. Choose two **different** authorized nonsensitive UTF-8 CSV or flat JSON files; verify both source SHA256 snippets, column names and row counts. The GUI shows no row/cell data. Both original column sets must match (ordering may differ). Invalid or missing files, symlinks, same file/hardlink, more than 10MiB combined and 10k combined rows are rejected by D9 backend.
3. Explicitly assign three different source column names to canonical `id`, `title`, `category`; no default mapping and no Fable/Astra business assumption. All source columns must match in both files. No join or lookup.
4. For **each** file separately: check the owner-rights box and type exactly `APPROVE`. Then type the distinct exact final token `APPEND` before selecting a new, non-existing output ZIP. Mapping/name/output changes clear approval tokens; changing source invalidates inspection entirely.
5. Click generate. The existing D9 `pack_pair` checks both full source hashes, duplicate IDs across files, schema and limits, stages an independent local app, audits ZIP manifest and atomically publishes without intentional overwrite. Both files' data rows appear in the resulting `app/data.sqlite`, though originals are not copied as raw source files. Approvals are cleared after success, so a second click is denied.

## CI and evidence
- Pure controller tests positive CSV+JSON combined ZIP, explicit per-file rights, two separate APPROVE tokens plus APPEND, invalid/missing mapping, changed SHA first/second, different schemas, cross-file duplicate ID, same file/symlink, no-overwrite and no reuse.
- `scripts/d15_pair_tk_smoke.py` opens actual Tk root, clicks actual main-window pair button to spawn Toplevel, invokes real source-choice buttons with fixed **committed synthetic** fixture paths, real inspect button, real comboboxes, checkbox/Entry typing, preapproval refusal, single missing-second approval refusal, final archive generation and second-use refusal. Screenshot when Pillow and display capture work; recorded receipt includes no customer cells.
- Linux CI uses real Xvfb display and also repeats D14 one-file visual test; Windows desktop probe attempts real two-file interaction or honestly emits `GUI_NOT_AVAILABLE_NOT_RUN`. Import-only is **not** a GUI E2E pass.
- Existing Ubuntu/Windows full pytest, Linux 8+3 Chromium synthetic local apps, native Windows extracted ZIP CMD/localhost HTTP, pinned Fable 88/Astra P4 PARTIAL 103 proofs preserved.

## Release and ownership restrictions
The 300,000 KRW offer remains a **hypothesis**, not an approved promise or order. Successful synthetic CI does NOT validate source licenses/NOTICE/ownership, real customer's reference, 3 measured human work cycles, clean nondeveloper Windows first-run, install/updater, backup/power-loss, security/privacy, accessibility or support/refund policy. G5/G6 commercial release remains **BLOCKED**. D15 does not merge draft PRs or deploy/host.
