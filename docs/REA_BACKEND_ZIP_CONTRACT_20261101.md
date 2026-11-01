# REA_WEB backend ZIP contract inspector — 2026-11-01

## Purpose
The intended REA_WEB product takes a **user-authorized backend source ZIP** plus a separate **reference URL/Fable report**, then designs an **independent** frontend that connects to the existing backend. The old offline CSV catalogue is not the target for this feature.

This change supplies only the **first isolated integration unit**: a ZIP static inspector and normalized **endpoint declaration** contract. It never starts the backend, imports its modules, extracts files, accesses URLs, executes scripts, reads environment variables, or changes original customer source.

## How to test (Python 3.11+)
```powershell
python -m rea.adapter.backend_zip C:\\path\\backend.zip --out C:\\path\\contract-new.json
python -m pytest -q tests/test_backend_zip.py
```
The destination JSON **must not already exist**. Without --out, the JSON is printed. The user's prior synthetic FastAPI test ZIP contains GET /api/health, GET /api/jobs, GET /api/jobs/{job_id}, GET /api/metrics, and POST /api/preview, all recognized as **static declarations only**. The inspector's local test is not proof of generated frontend integration.

## Contract meaning and constraints
- `schema_version: rea.backend_contract.v0.1`, `status: REVIEW_REQUIRED`, `generation_allowed: false`, `execution_performed: false`.
- Endpoint records retain relative source file path, line, HTTP method, route and static mount status. Runtime authorization, parameter type/contracts, database, and response schema are **not** inferred.
- Same-file FastAPI `app=FastAPI()` and `router=APIRouter(prefix="...")` literal route decorators can be recognized. Router mounts across modules, dynamic paths, hidden router inclusion, async import effects and conditional declarations remain **unresolved/unverified**. Even direct app route declarations require runtime verification.
- Source ZIP is checked read-only with no extraction: regular non-symlink source, 25 MiB archive cap, 1,000 member cap, 20 MiB total inflation cap, 2 MiB Python file cap, compression ratio cap, duplicate/casefold names, unsafe/absolute/traversal paths, link/special members and encrypted entries refused. A higher-level module still needs a controlled sandbox before ever starting backend code.
- Owner ZIP and URLs are independent inputs. Fable findings may inform **visual design**, but must not be treated as observed backend code, private API schemas, licensed visual assets, or approved customer data mappings.
- The inspector does **not** deploy, create a dashboard, modify Pro/Lite, approve bindings, or authorize commercial use.

## Next integration unit
1. Build a typed mapping/review step joining sanitized Fable visual findings to approved local backend endpoint declarations. Never autoapprove guessed API contracts.
2. Generate an **original** dashboard frontend in a temporary isolated project using the normalized contract and explicit owner-confirmed binding.
3. Exercise the synthetic backend via real HTTP in isolation and verify browser UI/Network/Console. Do not claim completion based on ZIP introspection.
