"""D19 developer-only, synthetic-only Windows operator pilot ZIP builder.

Uses exactly two pinned repository fixtures; no user path argument for source.
Creates deterministic, bounded, no-overwrite, local-only delivery artifacts.
The literal test approvals do NOT grant rights for real customer data.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import zipfile

from rea.delivery import MAX_ARCHIVE_BYTES, _safe, _zipinfo, verify_delivery
from rea.provenance import inspect_delivery
from rea.safe_publish import publish_archive
from rea.two_source import pack_pair

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = {
    "qa_guided.csv": "86bee9d74d474baf502cffbfd3071568337812744d143f432dc04b79554025f2",
    "qa_pair_extra.json": "e40182bafa08c90629908d6566433839e054fe37b6bc057ed175b870476d1a9d",
}
MAPPING = {"id": "sku", "title": "display_name", "category": "group_name"}
SCHEMA = "rea.d19.synthetic_owner_pilot.v1"
KIT_STATUS = "SYNTHETIC_ONLY_NOT_HUMAN_ACCEPTED"
MEMBER_NAMES = frozenset({
    "sources/qa_guided.csv",
    "sources/qa_pair_extra.json",
    "demo/approved_pair.zip",
    "README_WINDOWS.txt",
    "HUMAN_PILOT_BLANK.csv",
    "MANUAL_TIME_LOG_BLANK.csv",
    "CHECK_PILOT_OFFLINE.py",
    "MANIFEST.json",
})

GUIDE = """REA_Web D19 OFFLINE WINDOWS PILOT — SYNTHETIC DATA ONLY
================================================================
THIS IS NOT A COMMERCIAL RELEASE OR REAL CLIENT ACCEPTANCE.
No real customer data, browsing of external sites, or user secrets are needed.
This kit contains a demo ZIP and two public fake-data inputs. Do not upload
private files or share a real customer's generated app ZIP (which contains data).

WINDOWS OPERATOR — MANUAL CHECKLIST (complete EMPTY logs yourself):
1. Keep the original kit ZIP unchanged. Extract this kit to a NEW local folder.
   The SHA256 hashes in MANIFEST.json describe the files inside the kit;
   generating them does not prove supplier identity or legal permission.
2. Confirm sources/ contains qa_guided.csv (3 rows), qa_pair_extra.json
   (2 rows). Never replace these with real or confidential files.
3. In the extracted kit root (BEFORE launching the web app) run:
       python CHECK_PILOT_OFFLINE.py
   This Python stdlib-only integrity check does NOT install packages or call
   the network; it returns OFFLINE_KIT_INTEGRITY_PASS only for exact hashes.
   A hash does NOT establish authenticity or legal/redistribution permission.
   If it fails, STOP and do not launch the demo. Then extract
   demo/approved_pair.zip to ANOTHER NEW, empty local folder.
   Its root must have check_windows.cmd, launch_windows.cmd and app/.
4. Open Command Prompt in the extracted demo root. Run:
       check_windows.cmd
   Python 3.11+ and FastAPI/Uvicorn/Pydantic are NOT bundled.
   A missing-dependencies result means the environment is not ready.
   Do not run as administrator. No automatic package installation occurs.
   Any optional user installation is a SEPARATE decision and may use Internet.
5. If local prerequisites are met, in the same extracted demo root run:
       launch_windows.cmd
   Visit ONLY http://127.0.0.1:8000/ in a browser. The launch command
   binds 127.0.0.1, not an external/public interface. If port 8000 is
   already used, stop and inspect locally; do not expose a public port.
6. Look for EXACTLY FIVE synthetic items S01–S05 in the local list.
   Search for 콜드브루 -> S05; filter 음료 -> S01, S02, S05;
   open S04 detail -> 초코케이크. Never log source cell data.
7. Press Ctrl+C in Command Prompt and confirm the local server stops.
   Note any accessibility, font, browser or setup problems in the EMPTY
   HUMAN_PILOT_BLANK.csv. Do not enter a real customer's personal data.
8. If you separately test the creator UI, in a trusted repository checkout
   run START_REA_CREATOR.cmd --check, then open START_REA_CREATOR.cmd.
   Select BOTH included source files, map sku/display_name/group_name to
   id/title/category, check BOTH synthetic-only rights indicators, enter
   APPROVE for each and APPEND at the end, and choose a NEW ZIP path.
   These are demo tokens, NOT genuine third-party data rights or consent.
   The demo ZIP bundled here is generated without a human GUI session.

RECORDING RULES:
- HUMAN_PILOT_BLANK.csv has a HEADER ONLY. Record what actually happened.
- MANUAL_TIME_LOG_BLANK.csv has a HEADER ONLY. Do not invent human labor hours.
- Success must be marked only after a real nondeveloper Windows session.
- STOP if inputs are sensitive, unexpected software is requested, or the
  environment requires administrator/global configuration changes.
- No production/Vercel website, login, payment, public hosting or DB sync.
- APPEND is strictly SAME-SCHEMA ROW APPEND; never a relational JOIN.
- Commercial permission, third-party licenses/NOTICE, privacy/backup and
  customer contract/support/refund conditions are NOT cleared by the pilot.
"""

# Headers only. These files must remain blank of outcomes until human work.
HUMAN_LOG = (
    "operator_session_date_kst,windows_version,python_version,"
    "first_run_check_result,launch_result,localhost_200,five_rows,"
    "hangul_search_s05,category_three,detail_s04,server_stopped,"
    "gui_two_source_optional,accessibility_notes,error_type,"
    "human_acceptance,comments\n"
)
TIME_LOG = (
    "case_id,preparation_minutes,environment_setup_minutes,"
    "generation_minutes,manual_qa_minutes,correction_minutes,"
    "delivery_minutes,source_rights_verified_by_human,notes\n"
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_fixture_bytes(name: str, source: Path) -> bytes:
    """Accept only pinned committed bytes; undo exact Git Windows CRLF conversion.

    Original checkout files stay unchanged. Any change beyond newline style
    is rejected and cannot enter the bundled synthetic demo.
    """
    if name not in FIXTURES or not source.is_file() or source.is_symlink():
        raise ValueError("Committed synthetic fixture missing or is a symlink")
    if source.stat().st_size > 1_000_000:
        raise ValueError("Fixture SHA mismatch: refusing oversized source")
    data = source.read_bytes()
    if sha(data) != FIXTURES[name]:
        data = data.replace(b"\r\n", b"\n")
    if sha(data) != FIXTURES[name]:
        raise ValueError("Fixture SHA mismatch: refusing non-synthetic data")
    return data


def _sources() -> tuple[Path, Path]:
    files = tuple(ROOT / "samples" / name for name in FIXTURES)
    for name, source in zip(FIXTURES, files):
        canonical_fixture_bytes(name, source)
    return files


def _json(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _payloads(work: Path) -> dict[str, bytes]:
    first_original, second_original = _sources()
    # Stage ONLY canonical pinned fixture bytes into scratch. Git checkout can
    # transform LF to CRLF on Windows; no original file is modified or trusted
    # without a second exact hash check after staging.
    fixture_folder = work / "fixtures"
    fixture_folder.mkdir()
    staged = []
    for name, original in zip(FIXTURES, (first_original, second_original)):
        path = fixture_folder / name
        with path.open("xb") as handle:
            handle.write(canonical_fixture_bytes(name, original))
        if sha(path.read_bytes()) != FIXTURES[name]:
            raise ValueError("Staged synthetic fixture SHA mismatch")
        staged.append(path)
    first, second = staged
    embedded = work / "approved_pair.zip"
    pack_pair(first, second, embedded, "REA D19 synthetic pilot",
              MAPPING, FIXTURES[first.name], FIXTURES[second.name],
              "APPROVE", "APPROVE", "APPEND")
    verify_delivery(embedded)
    provenance = inspect_delivery(embedded)
    if (provenance["two_file_append_receipt_present"] is not True
            or provenance["overall_commercial_clearance"] != "NOT_GRANTED"):
        raise ValueError("Demo ZIP has invalid source or rights metadata")
    return {
        "sources/qa_guided.csv": canonical_fixture_bytes(first.name, first),
        "sources/qa_pair_extra.json": canonical_fixture_bytes(second.name, second),
        "demo/approved_pair.zip": embedded.read_bytes(),
        "README_WINDOWS.txt": GUIDE.encode("utf-8"),
        "HUMAN_PILOT_BLANK.csv": HUMAN_LOG.encode("utf-8"),
        "MANUAL_TIME_LOG_BLANK.csv": TIME_LOG.encode("utf-8"),
        "CHECK_PILOT_OFFLINE.py": (
            Path(__file__).resolve().parent / "d20_offline_kit_check.py"
        ).read_bytes(),
    }


def _manifest(payloads: dict[str, bytes]) -> dict:
    return {
        "schema": SCHEMA,
        "status": KIT_STATUS,
        "source_policy": "EXACT_TWO_PINNED_PUBLIC_SYNTHETIC_FIXTURES",
        "approval_tokens": "SYNTHETIC_DEMO_ONLY_NOT_EXTERNAL_CONSENT",
        "dataset_rows": 5,
        "mode": "SAME_SCHEMA_ROW_APPEND_NO_JOIN",
        "network_runtime": "MANUAL_LOCAL_127.0.0.1_ONLY",
        "real_human_acceptance": "NOT_RUN",
        "manual_labor_measurements": "BLANK_NOT_RUN",
        "customer_data": "NOT_USED",
        "commercial_clearance": "NOT_GRANTED",
        "files": [
            {"path": name, "bytes": len(data), "sha256": sha(data)}
            for name, data in sorted(payloads.items())
        ],
    }


def build_kit(output: Path) -> dict:
    output = Path(output).absolute()
    if output.suffix.lower() != ".zip":
        raise ValueError("Pilot kit output must be a .zip")
    if output.exists() or output.is_symlink():
        raise FileExistsError("Never overwrite an existing pilot kit")
    _sources()  # fail before creating a destination folder
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".rea-d19-synthetic-", dir=output.parent) as tmp:
        work = Path(tmp)
        payloads = _payloads(work)
        if sum(len(v) for v in payloads.values()) > MAX_ARCHIVE_BYTES:
            raise ValueError("Pilot kit content exceeds safe size limit")
        meta = _manifest(payloads)
        payloads["MANIFEST.json"] = _json(meta)
        if set(payloads) != MEMBER_NAMES:
            raise ValueError("Pilot allowlist mismatch")
        stage = work / "ready.zip"
        with zipfile.ZipFile(stage, mode="x", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9, allowZip64=False) as zf:
            for name, data in sorted(payloads.items()):
                zf.writestr(_zipinfo(name), data, compress_type=zipfile.ZIP_DEFLATED,
                            compresslevel=9)
        verify_kit(stage)
        publish_archive(stage, output)
    return {"status": KIT_STATUS, "kit_sha256": sha(output.read_bytes()),
            "files": len(MEMBER_NAMES), "rows": 5,
            "human_acceptance": "NOT_RUN", "commercial_clearance": "NOT_GRANTED"}


def verify_kit(path: Path) -> dict:
    path = Path(path)
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError("Invalid pilot ZIP")
    with zipfile.ZipFile(path) as zf:
        infos = zf.infolist()
        names = [i.filename for i in infos]
        if (len(names) != len(MEMBER_NAMES) or len(set(names)) != len(names)
                or set(names) != MEMBER_NAMES or any(not _safe(name) for name in names)
                or sum(i.file_size for i in infos) > MAX_ARCHIVE_BYTES):
            raise ValueError("Unsafe/extra/duplicate/missing pilot ZIP members")
        if any((i.external_attr >> 16) & 0o170000 == 0o120000 for i in infos):
            raise ValueError("Symlink pilot ZIP entry forbidden")
        meta = json.loads(zf.read("MANIFEST.json"))
        if (meta.get("schema") != SCHEMA or meta.get("status") != KIT_STATUS
                or meta.get("source_policy") != "EXACT_TWO_PINNED_PUBLIC_SYNTHETIC_FIXTURES"
                or meta.get("approval_tokens") != "SYNTHETIC_DEMO_ONLY_NOT_EXTERNAL_CONSENT"
                or meta.get("mode") != "SAME_SCHEMA_ROW_APPEND_NO_JOIN"
                or meta.get("dataset_rows") != 5
                or meta.get("network_runtime") != "MANUAL_LOCAL_127.0.0.1_ONLY"
                or meta.get("real_human_acceptance") != "NOT_RUN"
                or meta.get("manual_labor_measurements") != "BLANK_NOT_RUN"
                or meta.get("commercial_clearance") != "NOT_GRANTED"
                or meta.get("customer_data") != "NOT_USED"):
            raise ValueError("Pilot manifest safety/acceptance invariant mismatch")
        rows = meta.get("files")
        if not isinstance(rows, list) or len(rows) != len(MEMBER_NAMES) - 1:
            raise ValueError("Invalid member inventory")
        indexed = {}
        for row in rows:
            if (not isinstance(row, dict) or row.get("path") in indexed
                    or row.get("path") not in MEMBER_NAMES - {"MANIFEST.json"}):
                raise ValueError("Invalid inventory member")
            indexed[row["path"]] = row
        if set(indexed) != MEMBER_NAMES - {"MANIFEST.json"}:
            raise ValueError("Incomplete inventory")
        for name, row in indexed.items():
            data = zf.read(name)
            if row.get("bytes") != len(data) or row.get("sha256") != sha(data):
                raise ValueError("Pilot member hash/length mismatch")
        for name, expected in FIXTURES.items():
            if sha(zf.read("sources/" + name)) != expected:
                raise ValueError("Pilot fixture changed from committed synthetic original")
        if zf.read("CHECK_PILOT_OFFLINE.py") != (
                Path(__file__).resolve().parent / "d20_offline_kit_check.py"
            ).read_bytes():
            raise ValueError("Offline pilot checker was modified")
        for name, expected in {
            "README_WINDOWS.txt": GUIDE,
            "HUMAN_PILOT_BLANK.csv": HUMAN_LOG,
            "MANUAL_TIME_LOG_BLANK.csv": TIME_LOG,
        }.items():
            if zf.read(name) != expected.encode("utf-8"):
                raise ValueError("Pilot guide or BLANK human record altered")
        # This check runs against the *shipped inner ZIP*, not a developer file.
        with TemporaryDirectory(prefix="rea-d19-inspect-") as tmp:
            inner = Path(tmp) / "synthetic.zip"
            inner.write_bytes(zf.read("demo/approved_pair.zip"))
            verify_delivery(inner)
            audit = inspect_delivery(inner)
            if (audit["two_file_append_receipt_present"] is not True
                    or audit["overall_commercial_clearance"] != "NOT_GRANTED"):
                raise ValueError("Inner ZIP is not approved synthetic APPEND delivery")
            with zipfile.ZipFile(inner) as inner_zf:
                info = json.loads(inner_zf.read("app/append_report.json"))
                if (info.get("mode") != "SAME_SCHEMA_ROW_APPEND_NO_JOIN"
                        or info.get("rows") != 5
                        or [x.get("row_count") for x in info["sources"]] != [3, 2]
                        or [x.get("sha256") for x in info["sources"]]
                           != list(FIXTURES.values())
                        or [x.get("confirmed") for x in info["sources"]]
                           != ["APPROVE", "APPROVE"]
                        or info.get("combined_confirmation") != "APPEND"):
                    raise ValueError("Inner ZIP source/consent evidence mismatch")
    return {"schema": SCHEMA, "status": KIT_STATUS,
            "kit_sha256": sha(path.read_bytes()), "verified_members": len(MEMBER_NAMES),
            "rows": 5, "human_acceptance": "NOT_RUN"}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="D19 pinned-fixture-only Windows demo kit")
    sub = p.add_subparsers(dest="action", required=True)
    b = sub.add_parser("build")
    b.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("verify")
    c.add_argument("--zip", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        result = build_kit(args.out) if args.action == "build" else verify_kit(args.zip)
    except (ValueError, OSError, zipfile.BadZipFile, RuntimeError, KeyError, TypeError) as exc:
        print("D19_PILOT_NOT_VERIFIED: " + type(exc).__name__, file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
