# 02 — Target architecture and boundaries

## Modules and flow
1. FABLE ANALYZER (read-only) → redacted site_scan.json + optional record trace + observed endpoint JSON-schema candidates.
2. REA FABLE ADAPTER → canonical EvidenceBundle with source, observation ID, timestamp, certainty and provenance.
3. ASTRA OBSERVATION/SPEC → FunctionalSpecDraft (list/filter/search/detail/CRUD/basic aggregate).
4. OWNER DATA INTAKE → customer CSV/JSON parser, row/type/shape/size validation, sample-only SQLite import; no arbitrary SQL and no live DB credentials.
5. SEMANTIC MAPPING REVIEW → explicit approved field roles; default unknown blocked; owner consent and source rights recorded without private details in Git.
6. GENERATOR → isolated FastAPI/SQLite/HTML+JS application and restricted template functions only; no execution of model-written arbitrary Python.
7. TEST HARNESS → pure schema + database + actual loopback browser + attack/negative test; final delivery report.

## Contracts
Fable result is **technical evidence**, not an assertion that a site's behavior or backend semantics is known. See docs/09_DATA_CONTRACT.md for adapter JSON, examples and valid status transitions.

## Code layout when imported
engines/fable51/ = pinned standalone upstream snapshot; run scripts with its own isolated environment.
engines/astra_p4/ = pinned upstream snapshot; independent environment and synthetic-only safety constraints intact.
rea/adapter/ = new pure mapping code and tests.
rea/data/ = CSV/JSON normalization and isolated import.
rea/generator/ = restricted template generation.
rea/cli/ = orchestration.
tests/fixtures/ and tests/integration/ = new tests, not copied upstream acceptance claims.
docs/ = plans, QA, handoffs and decision logs.

## Runtime separation
Phase 1 uses temporary subprocesses and explicitly versioned JSON files. Avoid importing both projects into one Python environment until dependency, module and path conflicts are measured. Fable parser may have openai dependency; AI API remains opt-in, never in default tests.
Phase 2 provides local CLI + optional lightweight GUI once the end-to-end data contract is stable.

## Failure semantics
All inputs untrusted. Validate encoding, CSV row/column caps, duplicates, unicode, NaN, inconsistent types, formula injection, output path containment, localhost-only binding. Refuse unknown owner consent, unresolved semantic mappings, private-network arbitrary URL fetch, risky DB mutation. Review and request approval; never treat filename/column similarity as consent.
