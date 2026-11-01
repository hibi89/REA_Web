# REA_WEB Docker isolated synthetic runtime — 2026-11-02 KST

## Architecture decision and scope
A. The previous host subprocess approach is fast but lacks OS permissions/network isolation. It stays for trusted synthetic regression only.
B. The new Docker wrapper is selected for the next engineering step: lower setup overhead than a dedicated VM, while enforcing local image digest, non-root, no outbound networking, read-only source and bounded resources. Requires a locally installed approved image and a trusted Docker daemon. The daemon and host are not protected by this wrapper.
C. Dedicated disposable VM: stronger boundary for genuinely untrusted code, but higher installation/maintenance cost and no existing image or VM policy approved. Not implemented.

New module: rea/adapter/docker_sandbox.py. It uses the original exact ZIP/extracted tree approval routine before launching an isolated self-authored synthetic FastAPI fixture. Existing Pro/Lite and upstream Fable/Astra are untouched. Customer ZIP and externally authored backend code are explicitly NOT authorized.

## Enforced Docker invocation
- Local Docker Engine socket only; remote DOCKER_HOST/DOCKER_CONTEXT are not inherited.
- Require an exact separately reviewed image@sha256 digest already present locally; compare local RepoDigests. No automatic pull, package install, privileged run or daemon configuration.
- --network=none, no published ports, GET-only HTTP to container-internal 127.0.0.1.
- --read-only, --user=65534:65534, --cap-drop=ALL, no-new-privileges, read-only verified bind mount, bounded noexec tmpfs.
- Memory 256 MiB, memory swap capped, 32 PIDs, 1 CPU, 256 file descriptors, IPC none; execution timeout up to 30 seconds.
- Synthetic source digest + ephemeral PID/challenge check performed inside the container. Basic bounded list/metrics/detail/not-found GET checks; no raw payload values in reports.
- --rm plus forced removal on any exit/timeout and a daemon-side check for no remaining named container. Unverified cleanup is a hard failure. No fallback to host subprocess.
- JSON always states generation_allowed=false, customer_zip_execution_authorized=false, kernel_isolation_independently_attested=false. Docker arguments alone do not prove actual kernel/daemon isolation or container image trust.

## Invocation (only after provisioning an approved pinned image)
Python 3.11+, preinstalled FastAPI and Uvicorn are required INSIDE the chosen image. Do not assume an arbitrary Python base image meets this.

    python -m rea.adapter.docker_sandbox --bundle-zip TRUSTED_SYNTHETIC.zip --extracted CLEAN_SYNTHETIC_FOLDER --expected-bundle-sha256 EXACT_SHA256 --image APPROVED_IMAGE@sha256:PINNED_DIGEST --out NEW_REPORT.json --developer-authorized-synthetic

Negative policy and mock-Docker test suite:

    python -m pytest -q tests/test_docker_sandbox.py

These tests simulate Docker CLI responses and verify that command flags, image integrity checks, timeout cleanup and refusal paths are correct. They do not prove that an actual Docker daemon enforced those limits. No approved image digest has yet been supplied and no real Docker isolated process is verified in this milestone.

## Failures, recovery and release gates
Missing Docker/socket/image, invalid digest, modified ZIP/tree, missing approval: refuse before launch. Negative HTTP or runtime crash: return failure, never weaken limits. Timeout: kill Docker CLI, force-remove random container name, verify absence; if daemon cleanup cannot be confirmed, stop and require operator inspection. Do not log source ZIP, credentials, token or response bodies; never push real customer code to public GitHub.

Next: owner-approved pinned runtime image build/origin/license audit, then real Linux + Windows Docker synthetic integration and negative network/file/CPU/memory/pid/failure recovery checks. Actual owner ZIP running requires additional explicit consent, source rights, image attestation, threat modeling and protected execution environment. Real reference-URL design fidelity, customer auth/database semantics and human Windows acceptance remain unverified. Commercial production and release HOLD; Vercel N/A.

Rollback: previous branch commit in Git history. No force push, merge, upstream mutation, permission change, paid service or customer data.
