# REA-MVP-D6-01: Pinned provenance, dependencies, redistribution audit

**Status: INSPECTION ONLY. Commercial license clearance: NOT GRANTED.**
Reviewed 2026-10-26 KST. Engineering evidence, not legal advice.

## 1. Exact immutable upstream evidence

| Source | REA import SHA | Upstream ref & manifest | Rights status |
| --- | --- | --- | --- |
| Fable 5.1, 88 copied source files | 7e6f273b359b207fad8f92016226e3058cbcb839 | hibi89/fable5.1_web_catcher @ bbe72c0acd3a3e355062d6bd0d866af33e5274b0; engines/fable51/REA_SOURCE_MANIFEST.md blob 24a588cadb00c6d104d4c7fdd6307453b3df5765; 8 BATCH files | License/redistribution UNKNOWN, not cleared |
| Astra P4 PARTIAL, 103 selected files (41 contract modules) | f044b66e799289a5a353fdb9cbfdb324e683ffa3 | hibi89/astra_web_catcher @ b3166b67604381a9d2afd41667b65f9a9b103b37; engines/astra_p4/REA_SOURCE_MANIFEST.md blob f6eed8afaf8cd4ec58b989acdeeac3223b7dbc89; 9 BATCH files | License/redistribution UNKNOWN, not cleared |

Checked pinned upstream GitHub tree listings: 97 paths Fable and 247 paths
Astra, neither exposed a standard filename LICENSE, LICENCE, COPYING or
NOTICE, including nested paths. Pinned REA snapshot trees likewise showed
no such file. This is a narrow file-discovery result, NOT a legal finding,
not proof of ownership and not authorization to redistribute source. Account
similarity or public GitHub visibility does NOT imply an open-source license.

CI verifies the **actual pinned source bytes** against all batch Git blob
SHA-1 digests (88/88 Fable; 103/103 partial Astra). These are provenance
checks, not legal license grants and not an upstream full-suite test.

### Source-only requirements (not bundled in customer deliverable)
- Fable: engines/fable51/requirements.txt blob
  2242d53149cde4b57350b24e0d3fcc1745627a5e:
  requests>=2.31,<3; beautifulsoup4>=4.12,<5; pytest>=8,<10;
  playwright>=1.50,<2; openai>=3.13,<4; jsonschema>=4.20,<5.
- Partial Astra: engines/astra_p4/requirements.txt blob
  49e2dfbe27e9d542b7b6e48a1dda670f32568e0a:
  fastapi>=0.110,<1; uvicorn>=0.27,<1; pydantic>=2,<3;
  pytest>=8,<10; httpx>=0.27,<1; playwright>=1.50,<2.
- Their original upstream source and dependencies are NOT included in the
  generated application ZIP. Analysis test checkouts remain separate.

## 2. Actual customer-side runtime dependency inventory

The generated app/requirements.txt contains exactly two bounded declarations:

| Direct runtime dependency | Declared range | Locked exact version | License / transitive status |
| --- | --- | --- | --- |
| fastapi | >=0.110,<1 | NO | UNKNOWN, require exact distribution metadata and license/NOTICE review |
| uvicorn | >=0.27,<1 | NO | UNKNOWN, require exact distribution metadata and license/NOTICE review |

These are source requirement strings, NOT copies of Python wheels. Runtime
transitive packages, versions, resolved hashes, security disclosures,
attribution and actual license obligations have NOT been independently
audited. CI installs pytest, pydantic, httpx, playwright for testing,
and uses GitHub Actions checkout/setup-python; they are not shipped in the
generated app ZIP. Successful CI does not resolve commercial licensing.

## 3. Exact ZIP allowlist

Archive consists of generated app Python/SQLite and frontend:
app/app.py, app/data.sqlite, app/README.md, app/requirements.txt,
app/manifest.json, app/schema_preview.json, app/static/index.html,
app/static/app.js, app/static/style.css; Windows README_WINDOWS.md,
launch_windows.cmd, delivery_manifest.json. Optional local-only review:
app/review/fable_review.json and app/review/README.md.

Independent rea.provenance module checks per-file SHA256 against delivery
manifest, exact path allowlist, approved localhost runtime command, two
declared runtime dependencies and NOT_APPROVED schema/review states.
Unauthorised copied vendor engines, original source filenames and .env
files fail even if their manifest SHA256 is recalculated. CI produces
only synthetic screenshots, reports and local examples.

IMPORTANT: app/data.sqlite contains supplied **customer rows**.
No script here reads or certifies those rows as non-sensitive, and
a metadata-only file audit does NOT prove no secrets, personally identifying
information or inappropriate rights. Source file hashes/manifests do not
prove distribution permission. Optional Fable reviewed technical metadata
may need separate sensitive-data review before sharing.

## 4. Pre-sale gate register

| Gate | Assessment | Action required |
| --- | --- | --- |
| Fable 88 + partial Astra 103 content provenance | SHA check executable (Git blob hashes) | Run pinned CI verification; retain reproducible immutable refs |
| Fable/Astra redistribution rights | BLOCKED / NO documented license in pinned tree | Explicit source author/contributor rights/terms and approval; never vendor source blindly |
| Own generated template distribution rights | UNKNOWN | Record ownership, customer redistribution grant, notices and support contract |
| Runtime dependency exact versions/transitives/licenses | NOT ASSESSED | Create reproducible version lock/SBOM, inspect installed dist metadata, license obligations and notices |
| Data rights/privacy | BLOCKED for real customers | Owner-authorized nonsensitive data, retention/deletion strategy, no public uploads |
| 2-file product promise (draft 30만원 offer) | BLOCKED | Test explicit owner-approved join/mapping workflow OR owner-approved change to offer; no silent reduction |
| Clean Windows end-user machine and browser | NOT RUN | Independent nondeveloper clean install, restart/recovery and documentation acceptance |
| Real owner and authorized reference case | NOT RUN | Permission and measured feature/time report |
| Full security/recovery/commercial correction terms | NOT RUN | Risk based tests and written contract before sale |

## 5. Offline commands

Run locally only on synthetic generated ZIPs:

    python -m rea.delivery pack --csv samples/qa_cafe.csv --out /tmp/cafe.zip
    python -m rea.provenance inspect-zip --zip /tmp/cafe.zip --out /tmp/cafe-audit.json
    python -m rea.delivery pack --json samples/qa_products.json --out /tmp/json.zip
    python -m rea.provenance inspect-zip --zip /tmp/json.zip --out /tmp/json-audit.json

For pinned imported vendor checkouts only:

    python -m rea.provenance verify-vendor --vendor fable51 --root checkout-fable
    python -m rea.provenance verify-vendor --vendor astra_p4 --root checkout-astra

Audit JSON explicitly says overall_commercial_clearance=NOT_GRANTED or
commercial_redistribution_cleared=false. No external network request is made
by these Python audit commands. Source checkout is handled separately in CI.

## Next READY
D7 security/recovery robustness validation on local synthetic data, including
failure injection and risk register. Two-file commercial scope remains a
separate owner decision. Clean Windows pilot and real authorization still required.
