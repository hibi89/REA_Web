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
