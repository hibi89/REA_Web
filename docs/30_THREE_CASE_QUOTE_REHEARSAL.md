# D11-01 — Three synthetic quote-to-delivery rehearsals

**TEST ONLY. No orders accepted; no actual clients or human sign-off.**
This work exercises three independent customer-like fixtures from proposal to
source check, ZIP, Windows selfcheck and a browser check against the EXTRACTED
packaged application, while keeping untested real-world gates visibly blocked.

## Three simulated quotes (KRW 300,000 each is ONLY a price hypothesis)

| Synthetic case | Input | Screens explicitly quoted | Features explicitly quoted (3 max) | Expected records | Not included |
| --- | --- | --- | --- | --- | --- |
| cafe | qa_cafe.csv, UTF-8 | 1 responsive index + in-page panels | list, search, category_filter | 4 | POS sync, payment, Fable inferred formula |
| inventory | qa_inventory.csv, UTF-8 | 1 responsive index + in-page panels | list, search, detail | 5 | multiuser roles, purchase orders, live stock |
| trends | qa_trends.csv, UTF-8 | 1 responsive index + in-page panels | list, category_filter, simple_summary | 5 | predictive analytics, cross-source relations, API sync |

All three are **synthetic**, have no real ownership or site authorization,
and use only one existing prevalidated exact-schema CSV each. The generated
HTML may contain additional already-built functions: those functions are not
part of each quoted feature contract and are NOT feature-isolated. At most 2
screens and 3 selected features per hypothetical quote. Quote validation rejects
unsupported features, repeated features, excessive screens and non-fixture paths.
No automatically inferred semantic mapping or fictitious ownership claim.

## Reproduce on a clean *developer* environment

    python -m scripts.d11_rehearsal --out ./rehearsal_synthetic

This generates an exclusively published, no-overwrite directory containing:

- cafe.zip, inventory.zip and trends.zip, **real deterministic local apps**
- acceptance_scorecard.json, machine-readable quote, checksum, extracted
  Python/SQLite self-check and G0-G6 **SUBCHECK** status by case
- MANUAL_TIME_LOG_BLANK.csv, **column-header-only**, no invented minutes
- README_KO.md with exclusions and manual-timing instructions

Run actual browser acceptance (requires pip-installed Playwright+Chromium):

    python scripts/d11_browser_rehearsal.py --rehearsal ./rehearsal_synthetic --report-dir ./d11_browser_proof

This script verifies exactly the *contracted three features* for each case
against its unpacked ZIP running on 127.0.0.1. It checks basic UI, real browser,
selected filter/search/detail/summary as applicable, reload, non-served review
files, no JS alerts/errors and no unexpected external requests. Saves three
synthetic screenshots, browser_acceptance.json and an updated
combined_acceptance_scorecard.json. The base packaging scorecard intentionally
keeps G4 `PARTIAL_AWAITING_BROWSER` until this browser script passes.
The browser script upgrades G4 to `PASS_SYNTHETIC_SUBCHECK` only, **never G5/G6**.

## G0-G6 means what was actually examined, not a commercial certificate

| Gate | Status in D11 | Not yet cleared |
| --- | --- | --- |
| G0 imports | PARTIAL | Pinned Fable 88 and Astra PARTIAL 103 source hashes separately verified in CI, third-party reuse rights unknown |
| G1 technical observations | PARTIAL | Existing inferred-only synthetic checks; no live authorized reference or customer backend |
| G2 customer intake | PARTIAL | Synthetic caps/CSV/JSON and explicit mapping supported, no signed customer source authorization/locale import verification |
| G3 local generated app | PASS_SYNTHETIC_SUBCHECK | Real customized multi-screen customer acceptance |
| G4 real Chromium | PASS_SYNTHETIC_SUBCHECK **after external ZIP browser script** | Production customer browsers, accessibility, clean human install |
| G5 3-case + 1 authorized real reference | BLOCKED | Authorized real reference, actual customer acceptance and **measured manual labor** |
| G6 consumer delivery | BLOCKED | Clean nondeveloper Windows person, backup/restart after power loss, source/license/NOTICE grants, actual support/correction/refund terms |

The total `overall_g0_g6_release` remains BLOCKED on every result.
Passing CI is NOT permission to publish a KRW 300k offer or claim 6-8 hours
of hands-on labor. The exact supported 2-file mode remains explicit same-schema
ROW APPEND only; unlike-table joins or broad imports are unsupported.

## Manual time log: NO fabricated measurements

MANUAL_TIME_LOG_BLANK.csv contains **only headers**:
case_id, operator, prep_start/end/minutes, build_start/end/minutes,
correction_start/end/minutes, QA_start/end/minutes,
delivery_start/end/minutes, total_manual_minutes, notes,
actual_owner_signoff.

A human completes one separate row per case, records when actions were
actually performed and how many minutes each took, notes corrected defects,
and signs off separately before comparing total human effort to the draft
6-8h target. Automated GitHub Actions duration IS NOT evidence of human
labor or customer willingness to pay. No labor measurements were made here.

## Remaining release blockers
- Owner-approved exact 300k two-file/screen/feature contract, whether to
  restrict to same-schema append, one correction and refund/cancellation terms
- Generated templates and Fable/Astra source redistribution rights, exact
  runtime dependency pin/NOTICE/license attribution, CVE/license security review
- Nondeveloper clean Windows setup, actual authorized non-sensitive reference,
  privacy/sensitive-data handling, customer support, backup/power-loss and
  full security, optional full guided GUI
- Real customer acceptance and three human-measured end-to-end jobs

D11 CI must pass actual Linux and Windows full D1-D11 pytest, existing eight
Chromium synthetic sites, THREE NEW extracted-ZIP Chromium contracts, Windows
native CMD and isolated package diagnostics, immutable upstream source SHA
verifications and synthetic delivery audit. Do not mark D11 done without a
completed green Actions run and a matching verified source commit.
