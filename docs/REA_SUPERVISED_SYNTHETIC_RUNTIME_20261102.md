# REA_WEB trusted synthetic supervised runtime — 2026-11-02 KST

## Problem / scope
The previous bundle behavior probe verified source ZIP hashes and sampled HTTP responses, but did not know whether the localhost server belonged to the process just launched. The new `rea/adapter/runtime_supervisor.py` starts only the **existing self-authored synthetic** project bundle and uses a 256-bit per-launch challenge to associate observed responses with its managed child process. This is a **host-trust-level process handshake**, NOT security-grade process isolation or customer-code authorization.

## Exact sequence
1. Require `--developer-authorized-synthetic` and independent full archive SHA256.
2. Verify exact extracted inventory, SHA256SUMS, source/frontend linkage and original bundle source SHA **before spawning anything**.
3. Select a nonprivileged `127.0.0.1` port, create a one-time random challenge, start only the verified `runtime_entry.py` via `sys.executable -E -B` with explicit argv, `shell=False`, and a scrubbed environment.
4. The generated trusted synthetic runner exposes `GET /__rea/provenance` only if the process receives a valid challenge via its managed environment. Incorrect/missing challenge returns 404; the response includes its PID and expected `backend/app.py` hash. Compare both to the launched child and local verified source. The endpoint is excluded from OpenAPI. Without the managed environment variable it does not exist.
5. Only after a matching challenge, perform existing read-only localhost GET list/metrics/detail/404 behavior checks. Limit response lengths, redirections and data shapes; discard raw responses and the challenge. Record only hashes, statuses, counts, issue codes and conservative verification flags.
6. Always terminate and wait for the child (or kill after timeout), including on failure; never leave a background server. No dependencies installed or outbound network requested by this supervisor.

## Test / CLI (synthetic, no customer ZIP)
```
python -m pytest -q tests/test_runtime_supervisor.py tests/test_behavior_probe.py tests/test_project_bundle.py
python -m rea.adapter.runtime_supervisor \
  --bundle-zip TRUSTED_SYNTHETIC_BUNDLE.zip \
  --extracted CLEAN_EXTRACTED_SYNTHETIC_DIR \
  --expected-bundle-sha256 INDEPENDENT_64_HEX_SHA256 \
  --out NEW_REVIEW.json --developer-authorized-synthetic
```
Requires Python 3.11+, preinstalled FastAPI/Uvicorn, and already-generated approved synthetic bundle. `--out` refuses overwrite. Real owner ZIP never executed by this code. Use the branch CI for real Windows2022 / Ubuntu22.04 verification.

## Verified scope and limitations
- Expected success: `SUPERVISED_SYNTHETIC_PASS_REVIEW_REQUIRED`, `child_pid_challenge_matched=true`, `runtime_listener_identity_verified_within_host_trust=true`.
- Remains **false**: `os_process_isolation_attested`, `hostile_local_process_protection_attested`, `customer_zip_execution_authorized`, `business_logic_comprehensively_verified`, `generation_allowed`.
- **Not a sandbox**: code still runs with the account's privileges, localhost can be observed by a privileged or same-user hostile actor, and no seccomp/user namespaces/network blocking is provided. Do **not** use this launcher for untrusted customer ZIPs, credentials or datasets. A real customer run requires separately approved container/VM isolation with non-root execution, egress/resource limits, source and container-image provenance, and preapproved API paths/credentials.
- Separate the source ZIP verification from process challenge proof. The process challenge does not demonstrate production behavior, third-party reference design fidelity, or legal authorization.

## Rollback and preservation
New module/tests and a synthetic runner extension only; existing Pro/Lite, old feature branch history and Fable/Astra upstream remain unchanged. Git parent before this change is `155a6cc29f27ec93559a569e64145b25e6154dc5`. Never auto-merge, publish or modify permissions.