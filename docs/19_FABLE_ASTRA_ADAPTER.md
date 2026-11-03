# D2-01 adapter — synthetic, review-only

Fable 5.1 \`result.json\` (schema_version=1.0) -> technical **counts** and
provisional Astra \`ObservationBundle\` / \`FunctionalSpecDraft\`.

## Local commands

\`\`\`bash
# Analysis preview only (Astra validation NOT_RUN)
python -m rea.adapter.fable_to_astra samples/fable_record_redacted.json --preview-only

# Put the pinned import snapshot's engines/astra_p4 on PYTHONPATH first,
# or supply an explicit path to an independent checkout:
python -m rea.adapter.fable_to_astra samples/fable_record_redacted.json \
  --astra-root /path/to/import-astra/engines/astra_p4
python -m pytest -q tests/test_adapter.py
\`\`\`

The adapter never downloads a website, includes API paths or query values in
the result, accesses a DB, overwrites files, or approves code generation. It
preserves the SHA-256 of the local input for traceability. Record click/change
markers become **inferred** navigation/filter *hypotheses* with unknown effect;
only the pinned Astra module may validate and derive their draft spec.
Static/runtime scans (without manual record markers) yield no UI bundle/spec.
A supplied output is always \`REVIEW_REQUIRED\` and \`generation_allowed=false\`.
The SHA, local source file, permission, and actual UI behavior must be
independently reviewed before any customer mapping/generation.

**Limitations:** Fable doesn't record before/after UI state in these markers;
unknown business formula, actual backend, ownership, API lineage and rights
remain unresolved. Filename in evidence is a logical relative reference to
the retained Fable input; keep it beside any exported review packet.
