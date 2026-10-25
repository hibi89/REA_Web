# 06 — Rights, privacy and safety rules

- Only analyze URLs/data the client owns or has permission to analyze. Public availability alone does not grant reuse rights. No login/paywall/WAF bypass or private source extraction.
- Reimplement observed *functions*, not brand logos, copyrighted text/assets or look-and-feel identical copies. Use original design and properly licensed assets.
- Fable technical inference cannot establish actual proprietary backend/DB schemas or API calculations; always label unknown. No private API endpoint enumeration, brute force or aggressive crawling.
- Customer provides clean CSV/JSON; ask for redacted sample first; never push customer datasets, screenshots, credentials, .env or downloaded exports into public or private Git.
- Default local readonly scanning, loopback networking and disposable test DB. Production DB access, mutation, credential use or externally reachable deployment require separately scoped explicit permission and backups.
- In-browser recording stores no secret values/cookies/headers/bodies. Redaction is best-effort; manually review any deliverable before sharing.
- Third-party dependencies/licensing: inspect package licenses, attribution, security advisories and distribution terms. No broad legal guarantee.
- Fail closed on missing semantic approval. Never silently override ASTRA GenerationContract blocked status; support a separate explicit approved release contract with verifiable provenance.
- Logs must not include names, emails, account IDs or document contents. Scrub API samples to structure and pseudonyms.
- Cancel and report if an action would overwrite an existing folder, damage a customer DB, violate owner permissions or expose private data.
