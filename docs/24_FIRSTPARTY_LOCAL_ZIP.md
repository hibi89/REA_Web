> **2026-11-03 KST verified extractor:** Native Windows/Ubuntu source SHA b7516e11188a8318ab69876b140e33ce3d8d8a6f Actions 41656100350 static each 167 PASS/2 SKIP and 41656101659 Chromium/local ZIP each 165 PASS/2 SKIP, all SUCCESS. After `verify`, use `python -m rea.adapter.local_delivery unpack --zip APPROVED_LOCAL.zip --out NEW_PRIVATE_APP --owner-confirmed-extraction`. The output is a brand-new private app directory. The command verifies generated JS/HTML/CSS/static and exact Windows CMD/requirements against REA's original source in addition to hashes and SQLite quick_check; it never runs extracted code. Initial Windows WinError 32/5 from sqlite3 connection left open was fixed by explicit close at this SHA. This does not establish legal ownership, customer acceptance or commercial release; ZIP/extracted data.sqlite remains plaintext.

> **2026-11-03 KST verified SHA 280b1676:** ZIP pack/verify tests PASS Windows/Ubuntu Actions 41653360352, each OS 159 PASS/2 SKIP, source static 41653360320 each 167 PASS/2 SKIP. Real CI owns synthetic 130-row data and tests identical ZIP hashes, extracted local SELF_CHECK, native Windows CMD --check, corruption rejection. Initial Windows LF/CRLF failure at 2af167e1 corrected. ZIP contains plaintext SQLite data; no commercial release authorization.

# REA first-party local app ZIP — Technical preview (RELEASE HOLD)

The exporter accepts ONLY an integrity-checked REA-owned generated local app;
it never runs arbitrary customer backend code, accesses external URLs,
installs dependencies, or deploys a service.

1. Build a local app as documented in docs/23_FIRSTPARTY_LOCAL_COMPLETE_APP.md.
2. Check the generated app with: python NEW_LOCAL_APP/SELF_CHECK.py --check
3. Explicitly package into a new path:
   python -m rea.adapter.local_delivery pack --app NEW_LOCAL_APP --out NEW_DELIVERY.zip --owner-confirmed-packaging
4. Verify the archive:
   python -m rea.adapter.local_delivery verify --zip NEW_DELIVERY.zip
5. Extract to a PRIVATE new folder. Check RUN_LOCAL_WINDOWS.cmd --check
   before starting the localhost service. Python and dependencies must already exist.

The ZIP contains plaintext data.sqlite with the actual approved customer rows.
It excludes raw CSV/JSON and Fable report, but must not be shared or uploaded
without the source owner's explicit permission and data handling terms.
SHA256/SQLite checks detect accidental alteration, NOT cryptographic publisher
identity, an anti-malware guarantee, or legal authorization.

Physical Windows customer acceptance, rights, third-party package licenses,
privacy/deletion, invoice/support terms, real customer backend ZIP isolation,
and Production deployment remain UNVERIFIED. Commercial RELEASE HOLD.
