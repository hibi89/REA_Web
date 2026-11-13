# SITECRAFT AX — P50 local synthetic vertical slice

Product module: rea/sitecraft_ax.py. It accepts a local versioned JSON contract,
a SHA256-pinned synthetic HTML reference and a separately SHA256-pinned
owner-approved synthetic CSV. The **real frozen Fable 5.1 static scanner**
reads the reference from one local loopback GET. Astra P4 gives a conservative
REVIEW_REQUIRED draft; no inferred site behavior is approved. The original
REA Pro FastAPI/SQLite builder creates an app from CSV only.

Contract fields: schema=sitecraft.p50.synthetic.v1, product=SITECRAFT AX,
mode=synthetic_local_static_only, reference_html and reference_sha256,
owner_csv and owner_sha256, mapping with id/title/category,
permission=YES_OWNER_AUTHORIZED_LOCAL_FIXTURE,
approval=APPROVE_SYNTHETIC_ONLY,
external_network_allowed=false, commercial_release_allowed=false.
No unknown fields, public URLs, or source asset copying. This synthetic token
is NOT authenticated customer approval or legal permission.

CLI: python -m rea.sitecraft_ax --contract scope.json --out NEW_FOLDER
--fable-root .vendor/fable/engines/fable51
--astra-root .vendor/astra/engines/astra_p4

QA: python -m pytest -q tests/test_sitecraft_ax_p50.py
tests/test_website_rebuild_p50.py tests/test_orchestrator.py

P50 is an **engineering synthetic acceptance milestone** only, once exact
source Actions on Ubuntu and Windows pass. It is NOT a certified 50 percent
of the user final blueprint. Official final completion stays UNASSESSED until
approved scoring and traceable 100 percent baseline. P70 real browser 3-site
parity, P85 responsive security, P95 authorized customer reference,
actual Fable Record, owner review and QA, P100 customer delivery and
production acceptance remain separate. RELEASE HOLD throughout.

Never modify source customer site, expose customer data, use a paid API,
call public websites, or deploy without separate authorization. Existing
REA_Web and data2web_studio remain unchanged.
