# 2026-10-30 generated Windows delivery and recovery recheck

## Source and test boundary

- Existing synthetic ZIPs were generated from the D27 code at `f6e34f604cc2769f06927af8b9cd5ac6aad998f4`. The branch subsequently received documentation-only commit `5f3fdeb3dfa6e60c52d2543cf787338697d7d4fb`; no runtime code changed after the CI-tested SHA.
- Rechecked on native Windows with Python 3.11.9 using synthetic fixtures only. No customer files were opened or used. All extraction and temporary state was kept outside the user source folder.

## Current sample ZIP retest

Each existing package was independently re-opened, CRC-checked, manifest-verified, extracted under a Korean path, passed through `check_windows.cmd --check`, launched with actual `cmd.exe`, queried at loopback `/health`, and searched through `/api/items`.

| Package | SHA-256 | Search | Result |
| --- | --- | --- | --- |
| `cafe_current_head_20261030.zip` | `0537f5aa9e13ff8bb383f952d887d5f81d321541519c16f45c9afe34e47600e7` | `카페`, 1 row | PASS |
| `inventory_current_head_20261030.zip` | `1cf77d78676c4fbccd52974985885963de1655b160c8e38d264377834c78edca` | `SSD`, 1 row | PASS |
| `trends_current_head_20261030.zip` | `04ae5fba14a5188d30011b743e4858feafaf12f2838939954a8efd76f35081b8` | `K-네일`, 2 rows | PASS |

All three contain `ACCEPTANCE_CHECKLIST.md`; its UTF-8 contents include the search, category, detail, stop/restart and ROW APPEND checks. Its SHA-256 matches the delivery manifest in every archive. Raw source CSV files are absent from the packages. Each package preflight, health and search test returned PASS, with runtime binding `127.0.0.1`.

## Error recovery checks on an extracted package

- Occupied loopback port: actual `cmd.exe` returned code 2 with `REA_LOCAL_PORT_UNAVAILABLE` and `set REA_WEB_PORT=8765`; the app server did not start on the occupied port.
- Unsafe port value `8000&echo BAD`: launch was rejected with code 2; the `BAD` command text was not executed or printed.
- These checks used a synthetic cafe package. They do not prove every customer Windows policy or third-party security tool behaves the same way.

## Current-head and human acceptance boundary

- D27 run `40937387608` and D3 run `40937387910` were SUCCESS for Windows and Linux on source SHA `f6e34f604cc2769f06927af8b9cd5ac6aad998f4`. The later commit `5f3fdeb` only added QA documentation. No workflow run was returned for that docs-only commit.
- This retest is machine verification only. Customer nondeveloper acceptance remains **NOT_RUN**; commercial/source/dependency redistribution clearance remains **NOT_GRANTED**. The checklists are blank recording forms until a human actually performs and dates each item.
