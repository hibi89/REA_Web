# REA_WEB Lite — keyboard-only CSV access: reproduced defect and minimum fix

Checked 2026-10-31 KST. Exact code commit `9cfc01cc5cccaa9768b26bee63149887f43c60ac`; [PR #31](https://github.com/hibi89/REA_Web/pull/31) still Draft / unmerged.

## Reproduction on previous integrated HTML
- Source: REA-generated **synthetic** `cafe_DEMO.html` from prior verified Windows pilot ZIP, rendered using local Chromium Playwright `page.set_content`, not `file://` (local administrative policy blocks that URL scheme; GitHub CI separately verifies true `file://`).
- CSV trigger is `<label class="file-button" role="button" tabindex="0">` with hidden file input; before fix, keyboard focus reached the label, **Enter FAIL**, **Space FAIL** (no native file chooser event), while pointer Click PASS. Actual accessibility/keyboard usability regression.
- After applying only this line in `rea/lite_assets/template.html`: `$('csv-file').closest('label').addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();$('csv-file').click();}});`, the same local Chromium Playwright interaction produced **Enter PASS, Space PASS, pointer Click PASS**. This keeps original CSV semantics and UI untouched.
- Alternative evaluated: replace label with a native button plus hidden input; that would also fix semantics but requires more DOM/CSS changes and creates extra cross-browser risk. Retained label + focused keyboard handler is the bounded minimal change.
- Added `tests/test_lite_keyboard_file_picker.py`: actual seller-built HTML, browser real disk `file://` navigation, focus label, press Enter or Space, expect native file chooser, supply valid reordered-schema CSV and assert two updated rows, no page errors. Intended to run per OS Chromium and Windows Edge using same `REA_BROWSER_CHANNEL=msedge` mechanism.

## Visual smoke results (local, non-authoritative for production)
- 3 exact previously packaged synthetic demo HTML themes (cafe/inventory/office) rendered at **1366x768** and **390x844** using local Linux Chromium and `page.set_content`; all six had `documentElement.scrollWidth === innerWidth` and no browser page errors.
- These visual screenshots are inspection only. No claim for native Windows double-click, real browser extension configurations, customer machine or sale readiness.

## CI state at checkpoint
- Exact SHA `9cfc01cc5cccaa9768b26bee63149887f43c60ac`, [GitHub Actions run 41121776623](https://github.com/hibi89/REA_Web/actions/runs/41121776623) **QUEUED** with conclusion `NONE` as observed at checkpoint. **Do not claim GitHub PASS until both Windows and Ubuntu checks are completed SUCCESS.**
- Previous exact SHA `72f36ed25caf2d3a7b0ee08e53d0291f1bf5a212` had [Windows+Ubuntu 2/2 SUCCESS](https://github.com/hibi89/REA_Web/actions/runs/41119834953) for prior product source, not for new keyboard patch.

## Continuing release gates
- G2 actual independent Windows nondeveloper Chrome+Edge Explorer double-click **NOT_RUN**. G3 code/IP redistributability **NOT_CLEARED**. G4 real customer plaintext-data intake/retention/delete **NOT_APPROVED**. G5 three timed full manual delivery rehearsals **NOT_RUN**. G6 seller price/revision/support/refund conditions **NOT_APPROVED**.
- Original Pro/FastAPI/SQLite source, upstream integration branch and main unchanged, no Vercel or deployed hosted service. No license, customer data, rights or permission modifications. Do not merge Draft PR #31 without explicit owner approval.

## 2026-10-31 05:21 KST verified CI resolution

At exact patched source SHA `9cfc01cc5cccaa9768b26bee63149887f43c60ac`, GitHub [run 41121776623](https://github.com/hibi89/REA_Web/actions/runs/41121776623) completed SUCCESS 2/2 Windows+Ubuntu; Windows Chromium keyboard 2/2 and Microsoft Edge keyboard 2/2; Ubuntu Chromium keyboard 2/2; existing Pro/CSV/JS/packaged HTML regressions PASS. Previous `QUEUED` statement was true at its timestamp but is now superseded. Not a native nondeveloper Windows acceptance.
