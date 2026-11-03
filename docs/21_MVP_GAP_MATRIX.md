# REA_Web — Initial architecture versus MVP functional gap matrix

**MVP-first principle:** produce functioning local output -> compare to original
design -> add valuable missing functions -> advanced security/robustness/
license and clean Windows acceptance before delivery.

Source architecture: docs/02_ARCHITECTURE.md and docs/14_FINAL_DELIVERABLES.md.
Implementation and D4 synthetic verification are grounded by GitHub Actions run 40203444938. This remains a feature-only Draft PR, not a commercial acceptance.

| Original target | Current implementation | Gap / final condition |
| --- | --- | --- |
| Fable read-only analyzer for authorized sites | Existing Fable source is separately pinned; no live URL access inside REA CLI | PARTIAL; optional integration later with scope/rights checks |
| Fable -> source-grounded observations | Fable 1.0 record marker and API/chart technical counts -> Astra inferred/unknown review | PARTIAL; before/after UI fact evidence and rights not verified |
| Astra FunctionalSpecDraft | Pinned actual Astra contracts on reviewed Fable output | PARTIAL; feature candidates never automatically approved |
| Owner CSV or JSON input | One UTF-8 BOM-capable CSV OR one strict flat string-valued JSON array with id/title/category; 10MB/10k/20 col limit | PARTIAL; D4 lexical preview and D5 single JSON now present; two-file mapping/merge and locale encoding remain absent |
| Semantic schema binding review | Always not_approved; Fable output cannot become owner mapping | MISSING interactive approval UI and owner semantics; D4 preview explicitly UNAPPROVED |
| Independent safe generator | Fresh SQLite + FastAPI local app from customer CSV only | IMPLEMENTED MVP, no external API or website clone |
| Generated UI list/search/filter/detail | Read-only static HTML/CSS/JS + API | IMPLEMENTED; D4 category count summary is CSV-only (77 pytest on each OS, real Chromium 3 cases), advanced aggregate formulas and CRUD unsupported |
| App feature verification | FastAPI TestClient, SQLite, actual Chromium loopback tests | IMPLEMENTED synthetic only; live reference/user validation missing |
| 3 independent sample categories | Cafe, inventory and trends CSV + D3 tests, Chromium runner | VERIFIED in 40202313506 (synthetic only) |
| Clean Windows use | Windows launch_windows.cmd, Windows CI native API smoke | Windows-latest native launcher/HTTP PASS; nondeveloper clean install/Windows Chromium NOT_RUN |
| Local delivery ZIP/source | Deterministic ZIP of generated app + Windows guide + SHA-256 member manifest | IMPLEMENTED; source-license/commercial package review pending |
| Mode wizard and guided GUI | Python CLI; Fable review is optional JSON input | MISSING |
| Feature parity against real reference | Only synthetic app validation; no real website compared | NOT_RUN, explicit rights required |
| Cost/revision/customer acceptance | 300,000 KRW scope draft; no owner-client pilot | MISSING |
| Security, privacy and licenses | Minimum input bounds, SQL params, local binding, escaping, no destructive overwrite | Advanced review DEFERRED until pre-sale, release BLOCKED |
| Vercel/public hosting | Not configured, local product | OUT OF SCOPE |

## Acceptance gate assessment
G0 vendor hash imports sourced; full license/distribution assessment not done.
G1 inferred vs observed preserved; no directly witnessed UI effects approved.
G2 CSV/flat JSON bounded + UNAPPROVED lexical schema preview in D4/D5; no complete owner mapping approval or two-file flow.
G3 functional generated local readonly app on synthetic inputs.
G4 D4 Actions 40203444938: Linux and Windows 77 pytest each, real Chromium 3 synthetic domains with summary/schema/filter/search/detail/reload PASS. Native Windows .cmd HTTP PASS.
G5 three synthetic cases available; authorized real reference remains NOT_RUN.
G6 package and Windows launcher code available; third-party licenses,
clean Windows/nondeveloper acceptance, recovery and commercial process pending.

**Commercial readiness: NO.** No arbitrary URL clone, private backend recovery,
database ownership assertion, true formula reconstruction or vendor
distribution authorization is claimed.

## D4-01 verified customer-visible incremental gap fill (2026-10-25 KST)
- Draft PR #7 on feature/mvp-summary-preview, source SHA d8e26ed7d60ad86f64e35aefb3825655d6e19d25.
- [CI 40203444938](https://github.com/hibi89/REA_Web/actions/runs/40203444938): **77 pytest PASS** on Ubuntu AND Windows-latest; Linux Chromium three domains schema and category summary + original list/search/filter/detail/reload PASS; Windows-native CMD/HTTP PASS. Each OS had one nonblocking TestClient warning.
- Category totals are SQL COUNT from copied owner CSV, not a reconstructed website metric. `schema_preview.json` contains only CSV header names, lexical types and missing/present counts; review_status is UNAPPROVED. The preview is not direct customer field mapping, a commercial validation gate or an authorization to use real customer data.
- Remaining near-term high-value gaps: reconcile initial product's advertised two-file/JSON scope with the actual one-file CSV implementation; complete source/license redistribution review and pre-sale security/recovery/clean Windows tests before accepting customer orders.

## D5-01 validated bounded JSON and scope exception (2026-10-25 KST)
- [CI 40204213281](https://github.com/hibi89/REA_Web/actions/runs/40204213281): **110 pytest PASS on Ubuntu and Windows-latest**, four actual Chromium synthetic app cases (3 CSV + 1 JSON), Windows ZIP CMD/HTTP PASS, two deterministic synthetic sample ZIPs passed hashes. One nonblocking warning on each OS.
- Flat JSON array of string objects (id/title/category mandatory) shares strict row validator with CSV. One input only; original JSON not bundled. See docs/24_JSON_INTAKE_SCOPE.md.
- Original 300,000 KRW proposal **up to 2 CSV/JSON** is **not fully implemented**. Two-file semantic join/union has no approved rule. Do not advertise as supported or silently delete the commitment. Requires explicit owner-reviewed product scope decision and testing before sale.
