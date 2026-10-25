# REA_Web — Initial architecture versus MVP functional gap matrix

**MVP-first principle:** produce functioning local output -> compare to original
design -> add valuable missing functions -> advanced security/robustness/
license and clean Windows acceptance before delivery.

Source architecture: docs/02_ARCHITECTURE.md and docs/14_FINAL_DELIVERABLES.md.
This document enumerates IMPLEMENTED functions and PLANNED verification; do
not claim PASS unless matching GitHub CI actually passed.

| Original target | Current implementation | Gap / final condition |
| --- | --- | --- |
| Fable read-only analyzer for authorized sites | Existing Fable source is separately pinned; no live URL access inside REA CLI | PARTIAL; optional integration later with scope/rights checks |
| Fable -> source-grounded observations | Fable 1.0 record marker and API/chart technical counts -> Astra inferred/unknown review | PARTIAL; before/after UI fact evidence and rights not verified |
| Astra FunctionalSpecDraft | Pinned actual Astra contracts on reviewed Fable output | PARTIAL; feature candidates never automatically approved |
| Owner CSV or JSON input | Single UTF-8 BOM-capable CSV with id/title/category, 10MB/10k/20 col limit | PARTIAL; JSON, two-file merge, locale encoding and schema preview absent |
| Semantic schema binding review | Always not_approved; Fable output cannot become owner mapping | MISSING interactive approval UI and owner semantics |
| Independent safe generator | Fresh SQLite + FastAPI local app from customer CSV only | IMPLEMENTED MVP, no external API or website clone |
| Generated UI list/search/filter/detail | Read-only static HTML/CSS/JS + API | IMPLEMENTED; simple aggregates/CRUD unsupported |
| App feature verification | FastAPI TestClient, SQLite, actual Chromium loopback tests | IMPLEMENTED synthetic only; live reference/user validation missing |
| 3 independent sample categories | Cafe, inventory and trends CSV + D3 tests, Chromium runner | Implementation present, actual CI acceptance required |
| Clean Windows use | Windows launch_windows.cmd, Windows CI native API smoke | PARTIAL even if CI passes; nondeveloper clean install/Windows Chromium NOT_RUN |
| Local delivery ZIP/source | Deterministic ZIP of generated app + Windows guide + SHA-256 member manifest | IMPLEMENTED; source-license/commercial package review pending |
| Mode wizard and guided GUI | Python CLI; Fable review is optional JSON input | MISSING |
| Feature parity against real reference | Only synthetic app validation; no real website compared | NOT_RUN, explicit rights required |
| Cost/revision/customer acceptance | 300,000 KRW scope draft; no owner-client pilot | MISSING |
| Security, privacy and licenses | Minimum input bounds, SQL params, local binding, escaping, no destructive overwrite | Advanced review DEFERRED until pre-sale, release BLOCKED |
| Vercel/public hosting | Not configured, local product | OUT OF SCOPE |

## Acceptance gate assessment
G0 vendor hash imports sourced; full license/distribution assessment not done.
G1 inferred vs observed preserved; no directly witnessed UI effects approved.
G2 CSV bounded, no complete owner mapping approval/JSON/two file flow.
G3 functional generated local readonly app on synthetic inputs.
G4 real Chromium D1/D2 passed; D3 three-case results require workflow evidence.
G5 three synthetic cases available; authorized real reference remains NOT_RUN.
G6 package and Windows launcher code available; third-party licenses,
clean Windows/nondeveloper acceptance, recovery and commercial process pending.

**Commercial readiness: NO.** No arbitrary URL clone, private backend recovery,
database ownership assertion, true formula reconstruction or vendor
distribution authorization is claimed.
