# REA_WEB Docker isolated synthetic runtime — 2026-11-02 KST

## Architecture decision and scope
A. The previous host subprocess approach is fast but lacks OS permissions/network isolation. It stays for trusted synthetic regression only.
B. The new Docker wrapper is selected for the next engineering step: lower setup overhead than a dedicated VM, while enforcing local image digest, non-root, no outbound networking, read-only source and bounded resources. Requires a locally installed approved image and a trusted Docker daemon. The daemon and host are not protected by this wrapper.
C. Dedicated disposable VM: stronger boundary for genuinely untrusted code, but higher installation/maintenance cost and no existing image or VM policy approved. Not implemented.

New module: rea/adapter/docker_sandbox.py. It uses the original exact ZIP/extracted tree approval routine before launching an isolated self-authored synthetic FastAPI fixture. Existing Pro/Lite and upstream Fable/Astra are untouched. Customer ZIP and externally authored backend code are explicitly NOT authorized.

## Enforced Docker invocation
Docker built-in default seccomp policy is explicitly requested even if the daemon default is unconfined. This does not attest actual kernel policy behavior.
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

## Read-only image candidate and supply-chain acceptance (2026-11-02)
- **Candidate, not approved:** Docker Official Python `3.11.18-slim-bookworm` for a Linux container, subject to a separately captured complete multi-platform manifest digest, exact Linux architecture and final derived-image digest. Official images do **not** include the exact FastAPI/Uvicorn dependency set this probe needs; a dedicated minimal image must be reviewed and built from a fully hashed, version-pinned wheel set. No image pull, build, registry upload, package download or runtime execution was authorized/performed here.
- **Digest is not a signature.** The current runtime verifies only that a local `RepoDigests` entry matches the specified immutable reference. It cannot establish who built the image, whether its dependencies are licensed/secure or whether the running daemon enforces every kernel rule. Before approving execution, inspect exact packages/licenses/SBOM, build provenance, vulnerability audit and signature via an explicitly trusted verification key or verified keyless identity, such as Cosign. Do not confuse a self-supplied `--image` argument with user authorization.
- **Security basis:** Docker's documented `seccomp=builtin` overrides a daemon that has changed its default seccomp profile or set it unconfined. It is now explicitly requested, but enforcement is still **unverified** without a real protected Docker engine and negative tests.
- **Do not base a future trust gate on Docker Content Trust/Notary v1 alone:** Docker documentation states Notary v1 `notary.docker.io` will shut down **2026-12-08**. Use a current signing/provenance process after owner approval; do not alter Docker daemon, registry or GitHub permissions to work around this.
- **Platform distinction:** GitHub Windows Python/Chromium CI runs the synthetic script on the trusted Windows host; it does **not** test Docker Desktop's Linux engine. A Windows physical acceptance requires Docker Desktop Linux-container mode and a preapproved local image, both unverified here.
- Official references (read-only): https://docs.docker.com/reference/cli/docker/container/run/ ; https://hub.docker.com/_/python/tags?name=slim ; https://docs.docker.com/learn/content/prove-where-your-image-came-from/ ; https://docs.docker.com/engine/security/trust/ .

## Synthetic non-root mount fix and real-container gate (2026-11-02)
A user-controlled original archive extraction can reside in a Linux 0700 temporary directory; Docker UID/GID 65534 cannot traverse it, even with `--mount readonly`. The actual Docker bind source is now a **separate ephemeral directory** populated only from the validated ZIP bytes with exact checksum and inventory revalidation. Its root and child directories use 0755 and files 0644 so non-root can read on normal Linux mount semantics. Original ZIP and extraction permissions never change. The staged directory is removed after the Docker removal-check on every success/failure/timeout path; if cleanup cannot be verified the call fails.
**Confidentiality restriction:** the staged copy is temporarily host-world-readable, so this feature must never be reused for real private customer source or credentials. Future customer ZIP runtime requires a separately designed private transfer (for example a dedicated isolated VM/credentialless per-job account). Windows `resolve()` and `absolute()` can yield different spellings; temporary-root symlink detection replaces string equality. Forbidden comma/newline/carriage-return Docker mount delimiters remain blocked.
Evidence: `8901f6acc1aed611bc045d46c5872fe81d4d4483`; [CI #41328474922](https://github.com/hibi89/REA_Web/actions/runs/41328474922) Windows/Linux each 87 tests PASS, including exact staged-tree checks and simulated negative cleanup paths. This is NOT real Docker isolation or kernel enforcement.
