# REA WEB Lite — commercial release gates (2026-10-31)

**Status: TECHNICAL CI & SYNTHETIC PACKAGING PASS / NOT APPROVED FOR SALE.** Code/test SHA `91c1d113f81f0b144ba217820e6f0ca4b2350166`; [Windows and Ubuntu workflow success](https://github.com/hibi89/REA_Web/actions/runs/41116194878). Browser CI is automation, not a real customer acceptance result.

| Gate | Acceptance evidence | State |
|---|---|---|
| G0 source integrated with genuine Pro parser | 5 Python integration tests + SHA/APPROVE, browser tests on exact source | PASS (CI) |
| G1 raw file open and persistence automation | Windows/Ubuntu Chromium 3 themes, CSV failure retention, update, exported file:// reopen | PASS (CI) |
| G2 independent nondeveloper Windows Chrome + Edge | double-click actual generated HTML, offline, no Python, valid/malformed CSV, save, close, reopen, screenshot, elapsed time | NOT_RUN |
| G3 source and redistribution rights | confirm REA generator authorship + derivative rights; license for any shipped third-party code/assets; exact NOTICE requirements | NOT_CLEARED |
| G4 authorized customer data, privacy | only customer-owned/authorized input; plaintext embedded warning; intake path, retention duration, deletion receipt, support data boundaries | NOT_APPROVED |
| G5 actual operational cost | three real seller CLI synthetic inspect/build jobs per OS and ZIP integrity: PASS; three human timed full deliveries incl. mapping review, QA, revisions: NOT_RUN | PARTIAL: automated 3× PASS / human NOT_RUN |
| G6 product sale contract | owner approves Lite vs Pro scope, customer guide, price, revision count, support response, refund/cancellation rules | NOT_APPROVED |
| G7 formal release | human signoff, no public sensitive data, checklist and rollback, controlled merge/packaging | BLOCKED |

## Windows trial procedure (synthetic data only)

1. On local Windows, use a new test directory. Generate a Lite HTML from `examples/lite_cafe.csv` using seller Python (or use already generated synthetic `examples/cafe_DEMO.html`).
2. With network disconnected if practical, open the local HTML directly by Windows Explorer double-click in Chrome and Edge; check search/category/sort/details and `file://` URL. Observe that no localhost service or credentials are required.
3. Select an invalid duplicate-ID/scheme-changed CSV: error appears and original items persist. Then choose a valid same-schema CSV: new rows appear.
4. Click **변경 내용 HTML로 저장**; confirm a distinct new HTML file downloads. Close browser, reopen the newly saved HTML and confirm the new data survives. Original HTML and CSV must remain byte unchanged.
5. Record browser/version, PASS/FAIL, elapsed seconds, sanitized screenshots/error messages only. Never use real customer data for this trial.

## Product disclosure candidates (owner approval required)

- Lite is an offline, read-only catalog. No cloud, account, synchronization, QR or multiuser collaboration.
- CSV refresh does **not** rewrite the initial HTML. The customer must save a new HTML to preserve refresh results.
- The HTML includes plaintext record values. Sensitive/personal data or sharing the HTML can leak records. Do not claim encryption.
- For delivery, establish a permitted source file, approved mapping and licensed input; prohibit third-party confidential content without written permission.
- No fixed price, guarantee, response time, refund promise or legal license granted by this document. Owner must approve before listing.

## Rollback and source preservation

The Lite branch is a separate unmerged Draft PR #31 over Pro branch `feature/d27-windows-python-discovery`; source/test checkpoint `91c1d113f81f0b144ba217820e6f0ca4b2350166`. The unchanged parent commit `97b6e5cab7b8ffb4e1ee7f5e593021f4dac2598d` and Git history provide source recovery. Never force-push, modify original Pro/SQLite/customer content, or enable a deployed service without approval.

## 2026-10-31 04:42 KST additional proof

See [cross-OS three synthetic seller CLI deliveries](61_LITE_CROSS_OS_DELIVERY_EVIDENCE_20261031.md) at code SHA `202e4dbab9153c4f3003170e8881576d75c63b0c`, CI run [41117124085](https://github.com/hibi89/REA_Web/actions/runs/41117124085) Windows+Ubuntu 2/2 SUCCESS. This completes a machine reproducibility sub-gate, but not manual human timed deliveries or rights/terms approval. Prefer newly integrated Windows artifact #13007070338 over earlier standalone demo pilot.
