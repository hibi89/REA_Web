# 01 — Product specification (v0.1)

## Audience
Solo developer/freelancer serving consenting small businesses; long term independently installed business apps. Initial target is a clear customer-provided CSV/JSON; user may additionally supply a reference URL and demonstrate a workflow.

## Main promise
Observe accessible web UI and limited network/schema evidence; show features supported by actual observations; independently implement an agreed list/search/filter/detail/simple CRUD/basic chart workflow against a newly created local database seeded from supplied CSV/JSON; test it; supply source, instructions and a report.

## Three product modes
A — ANALYSIS_ONLY: safe observations and Korean report, no code generation or customer DB writes.
B — SYNTHETIC_PREVIEW: same but runs isolated invented/sanitized fixture data, not production.
C — OWNER_APPROVED_GENERATION: creates local independent app from validated user-provided data and approved semantic mappings; separate step after preview evidence and explicit approval.

## NOT promises
Not a one-click clone of any website. No acquisition of source or hidden backend, automatic reconstruction of original algorithms, WAF/login bypass, arbitrary private API reverse engineering, pixel-perfect copying, large unrestricted crawl, unlimited OCR, payments/ERP, customer database migrations, or unconditional accuracy.

## First narrow vertical
Customer uploads a clean non-sensitive CSV of up to the agreed limit with item_id, title, category, optional numeric measure; tool creates a local app with list/search/category filter/item detail and optional simple basic chart. No connection to customer's live DB.

## Buyer deliverables
Rebuild specification, field map with unknown/approval labels, local executable app source, seeded demo DB, CLI/GUI run instructions, acceptance report, limitations, backup instructions. Offer terms docs/07_KMONG_OFFER.md.

## Success definition
Three fixture domains: catalog/stock, time-series dashboard, work/task board. One owner-provided authorized reference can be examined after local gate proof. Measured automation time, manual correction time, error counts and customer acceptance.
