# REA WEB Lite — exact-source synthetic delivery reproducibility
Checked: 2026-10-31 04:42 KST. Original Pro functionality and customer data unchanged.

## Authoritative sources and verdict
- Repository `hibi89/REA_Web`, branch `feature/lite-offline-html-integration`, exact **code SHA** `202e4dbab9153c4f3003170e8881576d75c63b0c`.
- [GitHub Actions run #41117124085](https://github.com/hibi89/REA_Web/actions/runs/41117124085): **2/2 SUCCESS** (Windows + Ubuntu); no pending/failure/cancel in checked run.
- Each OS: 15/15 Node CSV, 7/7 synthetic Node DOM, 5/5 actual `rea.mvp` parser integration Python, 3/3 real Chromium on-disk `file://` browser scenarios (3 themes, bad CSV retention, CSV update, download/reopen), three separate **automated synthetic inspect→build CLI** rehearsals and source no-overwrite checks.
- CI invokes `python scripts/lite_delivery_rehearsal.py --out-dir lite_delivery_output` from the actual repo checkout. `inspect` returns owner source SHA/columns/rows, and `build` uses that exact hash plus `APPROVE` and mapping. Input file sha unchanged before/after, repeated output rejected, packaged HTML self-contained (no external URLs); output ZIP and SHA256SUMS verified.
- **No real customer data, independent Windows nondeveloper pilot, merchant license grant, privacy consent or selling approval.** Three timed runs are CLI-only measurements on hosted runners, NOT human end-to-end delivery durations.

## Reproducibility inventory

| Theme | Rows | Windows HTML SHA256 | Ubuntu HTML SHA256 | Same |
|---|---:|---|---|---|
| cafe | 3 | `341d2bf021a745fd45ff7c887b1711eebf6ec28d7418fbedfbe4eb3a4488111e` | same | YES |
| inventory | 3 | `4d68e19edfe37f1bd4f2fd9a133529aac6f099f36ad53b6c0be0f9469b686404` | same | YES |
| office | 2 | `968d6cfe6f30b867326a727867f759d64f497d346361fd1d43498d79c51be634` | same | YES |

| Theme | Windows inspect ms | Windows build ms | Ubuntu inspect ms | Ubuntu build ms |
|---|---:|---:|---:|---:|
| cafe | 172.05 | 80.94 | 109.57 | 48.84 |
| inventory | 77.63 | 79.19 | 46.48 | 47.38 |
| office | 77.76 | 82.88 | 43.87 | 44.56 |

These times exclude human mapping review, revisions, intake, manual browser acceptance, customer communication and packaging signoff; not a delivery-time quote.

## Real GitHub Actions artifacts

- [Windows artifact #13007070338](https://github.com/hibi89/REA_Web/actions/runs/41117124085/artifacts/13007070338): wrapper ZIP contains synthetic customer pilot ZIP and JSON report. Extracted pilot ZIP **21922 bytes SHA256 `e63de48ce51bedd9930f32383ed329c722b043adac65d48d64ec90d97a232b02`**, 10 members, 9 SHA256SUMS entries verified and ZIP CRC good.
- [Ubuntu artifact #13004944630](https://github.com/hibi89/REA_Web/actions/runs/41117124085/artifacts/13004944630): extracted pilot ZIP **21915 bytes SHA256 `7e37fe26a2e778bdc1292d42fe4ad796c6ca66d57c09133fbb8b3c104d37968b`**, 10 members, 9 SHA256SUMS entries verified and ZIP CRC good.
- Container check compared both reports and three HTML SHAs: **3/3 byte-identical HTML across OS**, although ZIP archive SHA differs due archive packaging metadata. Do not claim byte-identical entire ZIPs.
- Customer-side pilot package includes three self-contained HTMLs, three original synthetic source CSVs, a valid 5-row cafe update CSV, invalid duplicate ID CSV, README, SHA256SUMS. It is **not approved for sale**.

## Remaining gates
1. Human Windows Explorer double-click Chrome/Edge directly on those exact artifact HTML files, search/filter, malformed CSV retention, valid five-row update, new HTML save and reopen, no server, record browser versions and *actual human elapsed time*. NOT_RUN.
2. Confirm source original/provenance, redistribution and notices, plaintext data authorization/intake/retention/deletion, support/refunds/revisions and approved price. NOT_APPROVED.
3. Perform three *human* timed mock deliveries including mapping review and revisions. Automated CLI timings cannot close this.
4. Draft PR #31 remains unmerged. No Vercel/Production because Lite is an offline HTML; original Pro PR #30 not altered.

Rollback: Pro inherited parent `97b6e5cab7b8ffb4e1ee7f5e593021f4dac2598d` is unchanged; this Lite work lives on a separate branch. No force push, data overwrite or customer inputs.
