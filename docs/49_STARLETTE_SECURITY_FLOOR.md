# Starlette Windows security floor

Date reviewed: 2026-10-30

## Change

Generated customer applications now declare the direct runtime requirements:

- FastAPI: `>=0.110,<1`
- Starlette: `>=1.3.1,<2`
- Uvicorn: `>=0.27,<1`

The floor is deliberately a minimum range, not an exact version pin. The generated customer's read-only preflight checks the installed Starlette release before allowing launch. It does not install or update packages. If the installed release is too old, the Korean customer guidance points to the optional same-interpreter upgrade command.

## Rationale

Starlette's official advisories report multiple issues in earlier releases, including a Windows `StaticFiles` UNC-path behavior that can trigger an SMB connection while resolving an attacker-controlled path. The Windows UNC issue is fixed in 1.1.0. The form parsing denial-of-service advisory is fixed in 1.3.1, so 1.3.1 is the minimum floor used here.

- [GHSA-wqp7-x3pw-xc5r: Windows UNC path handling](https://github.com/advisories/GHSA-wqp7-x3pw-xc5r)
- [GHSA-82w8-qh3p-5jfq: multipart/form parsing denial of service](https://github.com/Kludex/starlette/security/advisories/GHSA-82w8-qh3p-5jfq)
- [FastAPI version guidance](https://github.com/fastapi/fastapi/blob/master/docs/en/docs/deployment/versions.md) advises users to let FastAPI choose a compatible Starlette version. This package adds a lower security floor without pinning an exact Starlette release; generated requirements must continue to resolve in CI.

## Limits

The floor does not lock or independently audit the full transitive dependency graph. A passing local preflight confirms package presence and the minimum versions only; it does not verify licenses, customer acceptance, or commercial rights. Fresh-environment resolution and the project's Windows CI must pass before this change is described as validated.
