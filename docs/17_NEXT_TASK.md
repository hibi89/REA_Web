# 17 — Dispatcher (single READY task)

**ACTIVE TASK:** REA-P0-02 — Import Fable 5.1 pinned source (if already imported with SHA verification, switch to REA-P0-03 Astra snapshot).

STATUS: READY. Branch: import/fable51-bbe72c0. Target: source paths under engines/fable51; pinned source bbe72c0acd3a3e355062d6bd0d866af33e5274b0; review ZIP source has 88 files.
Acceptance: content copied without modification; original file set/hash matches; zero root CI workflow overwrite; no sensitive customer data or secrets. Record imported count, test status NOT_RUN and remote SHA.

NEXT AFTER VERIFIED:
REA-P0-03 on import/astra-p4-b3166b6: Astra p4 stable module snapshot with provenance and clear partial/full declaration, then REA-P0-04 dependency isolation. Do not jump straight to app generation before this gate.

If user sends 'ㄱ', proceed with the next authorized READY task; report blockers and continue to the next independent safe task when possible. Do not promise background execution.
