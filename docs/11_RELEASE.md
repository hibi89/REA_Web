# 11 — Delivery, packaging and release

### First release v0.1
A sanitized sample CSV/JSON → standalone generated local application, two screens / three features max, SQLite seed and one-command run, output in fresh directory; generated project tests; Korean report and runbook; no production DB.

### Release gate
Pinned input SHAs, dependency and license inventory, security scan, test matrix G0–G6, Windows clean profile launch, source code + input contract + generated app manifest + test results. If any required gate fails, label preview rather than release.

### Package contents
- source/ generated independent app (customer owns supplied input data, licensed code terms defined before sale)
- docs/README_KO.md with Windows launch/backup/uninstall instructions
- reports/OBSERVATION.md, DATA_MAPPING.md, ACCEPTANCE.md, LIMITATIONS.md
- manifest.json with SHA256 per shipped file and tool provenance
- tests/ minimal runnable verification
No secrets, live customer data duplication beyond explicitly permitted output, raw session exports, reference logos, source ZIP of unrelated upstream tools.

### Support
Reproducible failure intake: generated version/hash, OS, sanitized sample, no credentials. Restrict one correction batch in starter offer. Extended deployment/support priced separately.

### Validation status
No REA releases, tags, installers or customer product artifacts have been verified as of bootstrap.
