# 12 — Risk register

| Risk | Severity | Detection/mitigation | Stop condition |
| --- | --- | --- | --- |
| Incorrect inferred source behavior | high | evidence certainty + human review | unknown treated as observed |
| Fable output/Astra schema mismatch | high | versioned adapter schema tests | dropped field/provenance |
| Latest Astra Windows regression | high | isolate and classify 96 failed/108 errors before merge | untriaged platform regression |
| Customer DB/data corruption | critical | no prod DB in starter; copy-on-write temporary DB | unapproved mutation |
| Licensing/copyright | high | no proprietary assets; component license audit | unlicensed copy |
| Browser/crawl access issues | medium | allowed target and timeout, no bypass | unauthorized access |
| Secret in reports | high | allowlisted fields + manual redaction review | raw auth/cookie/customer values |
| Complexity/scope creep | high | 2 screens/3 features; 6–8h target | feature request outside contract |
| Packaging/environment variance | medium | clean Windows acceptance test | cannot launch on target OS |
| False commercial claim | high | label preview, exact PASS/NOT_RUN | claiming clone/100% automation |

Issue management uses short reproducible evidence and decision log, not speculative green status.
