# HANDOFF — REA_Web

2026-10-25 bootstrap handoff. Read README.md and docs/17_NEXT_TASK.md first.

### Project
Repository: hibi89/REA_Web. Goal: authorized Fable analysis → grounded Astra functional specification → user-provided CSV/JSON mapping → isolated independent local web app → actual tests.

### Sources
- Fable review ZIP nested 112 entries and source 88; baseline bbe72c0acd3a3e355062d6bd0d866af33e5274b0.
- Astra main dc23ee604d02513c890615a3a98440c1ea8a5270; active development codex-p4-20261019 274402a3d8eaf33d9ff55bf740208a1dbded3bef; feature stable snapshot b3166b67604381a9d2afd41667b65f9a9b103b37.
- Do not merge 200+ Astra commits blindly; synthetic-only modules are NOT general website-to-app generation.
- Existing upstream repositories must not be modified.

### Architecture
Input: authorized URL/browser observation and optional sample CSV/JSON. Adapter: evidence, certainty, inferred behavior, sanitized API schema → proposed spec. Review gate: approve data roles/formulas and allowed operations. Generation: local isolated FastAPI/SQLite + simple UI first. Verify: pytest + browser click/keyboard + original-vs-output behavior matrix.

### Constraints
No mandatory internet crawler/real DB/hidden APIs; no data collection service; no unrestricted customer scope. Keep artifact modes ANALYSIS_ONLY / SYNTHETIC_PREVIEW / OWNER_APPROVED_GENERATION separate.

### Resume
1. Verify main & branches and imported file checksums.
2. Read current docs/17_NEXT_TASK.md READY task.
3. Work on designated feature branch; run tests before asserting completion.
4. Update STATUS/HANDOFF/NEXT_TASK with command, PASS/FAIL/SKIP, commit SHA, blockers.
