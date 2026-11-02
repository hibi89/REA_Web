## New offline evidence review tool — 2026-11-02 KST

Added `rea/adapter/docker_image_evidence.py` and 10 tests in `tests/test_docker_image_evidence.py`. This is a read-only, local artifact inventory; it cannot contact Docker, run an image, install packages, access a registry or inspect a customer ZIP.

Manifest format: JSON object with exactly `schema` (`rea.docker_image_evidence.v0.1`), `image_ref` (immutable repository@sha256 digest), `platform` (`linux/amd64` or `linux/arm64`), and `artifacts`. The `artifacts` object needs exactly `dockerfile`, `wheel_lock`, `spdx_sbom`, `signature_receipt`, `vulnerability_report`, and `license_review`. Each has `file` (basename in a single local evidence directory) and `sha256` (64 lower-case hex). An independently supplied SHA256 of the complete manifest is mandatory.

Wheel lock JSON is `{"wheels":[{"name":"fastapi","version":"EXACT_PIN","sha256":"EXACT_WHEEL_SHA"}, {"name":"uvicorn","version":"EXACT_PIN","sha256":"EXACT_WHEEL_SHA"}]}` with other transitive wheels as needed. SPDX JSON must use `spdxVersion: SPDX-2.3` and package entries containing `name`, `versionInfo`, `licenseConcluded`; locked Python versions are cross-matched with SPDX packages. These strings are format examples, NOT known-good versions/hashes/licenses.

Command, after acquiring the actual independently sourced evidence:
```bash
python -m rea.adapter.docker_image_evidence --evidence-dir APPROVED_REVIEW_FOLDER --manifest APPROVED_REVIEW_FOLDER/manifest.json --expected-manifest-sha256 EXACT_INDEPENDENT_MANIFEST_SHA256 --out NEW_REPORT.json
```

Checks: every artifact+manifest SHA256, 2 MiB file cap, exact allowlisted artifacts, no duplicate names/traversal/symlinks, required pinned FastAPI/Uvicorn packages and wheel-to-SPDX name/version consistency. No overwriting output.

Even structurally consistent evidence produces `EVIDENCE_INVENTORY_REVIEW_REQUIRED`, **not approval**. Signature cryptographic verification, complete dependency closure, license grants, independent CVE verification, Linux daemon isolation and any image/customer ZIP execution authorization are all explicitly `false`. A self-supplied signature receipt/SBOM is not trusted cryptographic proof. Owner authorization and genuine independently verified image/daemon evidence remain separate prerequisites.

Local Python3.13: `python -m pytest -q tests/test_docker_image_evidence.py` → **10 PASS / 0 FAIL**. Exact code/test Git blob SHA matches remote GitHub file SHA. New Windows/Ubuntu CI and real Docker **UNVERIFIED**; RELEASE HOLD. No actual image provenance artifact was supplied.
# REA_WEB: Docker image supply-chain decision and synthetic isolation approval gate

Updated: 2026-11-02 KST. Status: **NOT APPROVED / NO IMAGE EXECUTED / RELEASE HOLD**.

## Decision and evidence boundary

**A — minimal, immutable Docker runtime (conditional preference):** use a digest-pinned Linux/amd64 or Linux/arm64 base, audited pinned Python wheels and a separately signed, derived image. Low operating overhead, but the Docker daemon and host remain in the trust boundary. Existing code explicitly requires an installed exact `repository@sha256:<64 lowercase hex>` reference and does not pull or build it.

**B — ephemeral dedicated VM:** stronger isolation for a future untrusted customer ZIP, but installation/operations and owner review cost are higher. Prefer for non-synthetic privately licensed owner code until a threat model and protected transfer are approved. Neither approach has been executed on a real isolation engine in this unit.

The Docker Hub **Docker Official Image** `python:3.11-slim-bookworm` is a **candidate base only**. This tag is mutable and cannot be treated as an approved digest. The current prototype additionally needs FastAPI and Uvicorn, which must be included in a separately reviewed derived runtime image. Do not invent an image digest from the short Docker Hub display; distinguish manifest-list digest from architecture-specific manifest. No digest for the derived runtime, signed provenance, keyless signer identity, dependency closure, SBOM, approved Linux daemon or commercial distribution rights has been independently verified.

## Read-only supply-chain checks before approval

| Item | Minimum evidence needed | 2026-11-02 verified state |
| --- | --- | --- |
| Source | Official base URL, exact immutable manifest and target OS/architecture; derived Dockerfile digest and reproducible build provenance | Official Python listing located; exact approved base/derived digest **missing** |
| Signature | Cosign verification against a **separately trusted key** or explicit expected certificate identity and OIDC issuer, with claims bound to the same manifest digest; retain redacted verification receipt | **NOT VERIFIED**; `RepoDigests` equality is not signature |
| Python packages | `fastapi`, `uvicorn` and full transitive closure pinned by exact version **and** wheel sha256; install only with `--require-hashes --only-binary=:all:` in owner-approved build | **MISSING**; installation and download prohibited now |
| OS packages and license | Complete SBOM of final derived image including Debian OS packages, Python dependencies, SPDX license details and redistributability review | **MISSING**; FastAPI upstream lists MIT, but no complete license audit |
| CVE and provenance | Vulnerability report against **exact digest**, signed build attestations, trusted build actor and recorded exception policy | **MISSING** |
| Runtime | Approved Docker Linux engine, daemon endpoint trust, exact local image preinstall and permission review | **NOT VERIFIED** |
| Isolation negatives | Real disposable self-authored synthetic checks for egress refusal, read-only root and bind, nonroot and capability drops, seccomp, CPU/memory/PIDs, output flood, timeout and container removal | **NOT RUN**; mocked CLI and trusted-host tests only |

No field in this table is authorization to pull/build/install an image, change Docker permissions or run an untrusted ZIP. Even a complete self-supplied SBOM is not proof of a cryptographically bound provenance chain.

## Conditional real-engine acceptance plan (requires fresh owner approval)

1. Confirm the reviewed, signed derived `image@sha256` and Docker daemon from an independently trusted source without modifying existing settings.
2. Provision image **only under separate approval**; record daemon OS/arch, image immutable identity, signature, SBOM and dependencies without storing secrets or private customer content in the repository.
3. Run only a reproducible self-authored synthetic fixture in a disposable sandbox. Independently test outbound TCP/DNS denied, root and source writes denied, effective UID 65534, no capabilities, default seccomp requested and enforced, memory/PIDs/CPU boundaries, output-overflow termination, CLI timeout and daemon-side exact-name cleanup. Record both pass and expected-denial evidence, host OS and exact SHA.
4. On a single unexpected access, escape, unverified removal, permission issue or unverified digest: **STOP**; do not fall back to a host process or weaken policy.
5. Require separate owner approval and a private per-job transfer/isolation design for any real customer backend ZIP; existing synthetic 0755/0644 staging is host-world-readable and **not** suitable for private code.

## Current actual code/testing checkpoint

- Previous combined functional SHA: `6dd99240cd9273715242b7cba8a8ebd380ba0559` — Windows/Ubuntu 100 PASS each with 3 green workflows (historical).
- Current changes: `rea/adapter/docker_sandbox.py` directs **all** Docker CLI commands through bounded live `Popen` capture, 4096 bytes per preflight/cleanup stream, 8192 per `run` stream; failed cleanup capture is explicitly unverified. Regression tests added to `tests/test_docker_sandbox.py`.
- Code/test commit: `62f6752dc1effa3984d9235161d0fced5f38ebee`. **CI for this exact SHA not yet observed; do not inherit old green status.**
- Docker engine/container/host isolation and signature checks: **NOT RUN**.

Sources to recheck on owner approval:
- Docker Official Python tags: https://hub.docker.com/_/python/tags?name=3.11-slim-bookworm
- Sigstore verify: https://docs.sigstore.dev/cosign/verifying/verify/
- pip secure installs: https://pip.pypa.io/en/stable/topics/secure-installs/
- FastAPI MIT license: https://github.com/fastapi/fastapi
- Docker run: https://docs.docker.com/reference/cli/docker/container/run/

Operationally, `RELEASE HOLD` continues; no Pro/Lite, upstream Fable/Astra or customer ZIP change and no production deployment.
