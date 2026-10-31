"""Create a synthetic REA Lite owner acceptance kit; no customer data or sale approval.

An atomic, no-overwrite folder containing 3 offline HTMLs, valid/invalid CSV
fixtures, a checksum inventory and a human checklist with all fields blank.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import zipfile

from rea.lite_builder import build
from rea.mvp import source_sha256
from rea.safe_publish import publish_directory

_THEMES = ("cafe", "inventory", "office")
_BASE_CSV = (
    "id,title,category,price\n"
    "S01,Cold Brew,Drink,4000\n"
    "S02,Desk,Office,25000\n"
    "S03,Notebook,Office,9000\n"
)
_VALID_CSV = (
    "id,title,category,price\n"
    "N01,NEW_CHECK_ITEM,Drink,100\n"
    "N02,SECOND_CHECK_ITEM,Office,200\n"
)
_DUPLICATE_CSV = (
    "id,title,category,price\n"
    "D01,Wrong,Drink,100\n"
    "D01,Duplicate,Drink,200\n"
)
_WRONG_HEADER_CSV = "id,title,category,amount\nN01,Wrong column,Drink,100\n"
_CHECKLIST = """REA_WEB Lite — Windows owner acceptance (synthetic data ONLY)

IMPORTANT: Test kit only; not approved for commercial resale.
Do not use client, private, sensitive, or identifiable records.
No installation, server, payment or network is necessary.

1. Extract this ZIP to a NEW folder. Keep the original ZIP unchanged.
2. Double-click cafe.html in regular Windows Chrome or Edge (file://).
   Confirm 3 rows; search for Cold Brew; open the detail panel.
3. Choose duplicate_id.csv and click 'CSV 검증 후 적용'.
   Confirm a rejection and that all THREE original records remain.
4. Choose wrong_columns.csv and click the same action.
   Confirm a rejection and no data changes.
5. Choose valid_update.csv and click the same action.
   Confirm TWO records, including NEW_CHECK_ITEM.
6. Click '갱신된 HTML 다운로드'. Open the NEW downloaded HTML.
   Confirm TWO rows and NEW_CHECK_ITEM after reopening.
7. Optionally double-click inventory.html and office.html and verify
   their distinct themes. Do not modify the original HTMLs.
8. Run no command as administrator and do not disable Windows security.
   If browser policy blocks file://, record BLOCKED; never bypass policy.

RECORD BY THE PERSON WHO ACTUALLY RAN THESE STEPS:
Date/time KST: ______________________
Browser and version: ________________
Windows version: ____________________
Chrome/Edge file opening: PASS / FAIL / BLOCKED / NOT_RUN
Search/detail: PASS / FAIL / NOT_RUN
Invalid CSV retained old data: PASS / FAIL / NOT_RUN
Valid CSV applied: PASS / FAIL / NOT_RUN
New HTML download and reopen: PASS / FAIL / NOT_RUN
Any error (no private paths/data): _______________
Total human elapsed minutes: ________ or NOT_MEASURED
Acceptance decision: PASS / FAIL / BLOCKED / NOT_RUN

No field above is automatically populated or considered PASS by the builder.
This package cannot confer copyright/license/privacy or sales approval.
"""
_README = """REA Lite | Synthetic Windows Acceptance Pack

Open CHECKLIST_KO.txt for the exact owner-facing steps.
The three HTML files work offline with no Python or server for the customer.
These records are synthetic. Never upload private or client data for a test.
valid_update.csv has the original column order; duplicate_id.csv and
wrong_columns.csv must be rejected without changing the current records.
The original HTML must remain unchanged after an update; use Download
updated HTML to preserve the replacement records in a NEW file.
The embedded data is base64-encoded PLAINTEXT, not encrypted.
SHA256SUMS.txt verifies all files except SHA256SUMS.txt itself.
The human checklist remains entirely unfilled until a real operator runs it.
"""
_FILES = frozenset({
    "cafe.html", "inventory.html", "office.html",
    "valid_update.csv", "duplicate_id.csv", "wrong_columns.csv",
    "README_FIRST.txt", "CHECKLIST_KO.txt", "MANIFEST.json", "SHA256SUMS.txt",
})
_RE_DATA = re.compile(rb'<script id="rea-data" type="application/octet-stream">([^<]+)</script>')


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def verify_kit(folder: Path) -> dict:
    """Check fixed inventory, checksums and actual embedded synthetic records."""
    folder = Path(folder)
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError("Kit must be a regular directory")
    names = {p.name for p in folder.iterdir()}
    if names != _FILES or any(not p.is_file() or p.is_symlink() for p in folder.iterdir()):
        raise ValueError("Unexpected or missing kit files")
    expected = {}
    for line in (folder / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        if not match or match[2] in expected:
            raise ValueError("Invalid checksum inventory")
        expected[match[2]] = match[1]
    if set(expected) != names - {"SHA256SUMS.txt"}:
        raise ValueError("Checksum inventory incomplete")
    for name, sha in expected.items():
        if _sha((folder / name).read_bytes()) != sha:
            raise ValueError(f"Integrity mismatch: {name}")
    manifest = json.loads((folder / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest != {
        "schema": "rea.lite.owner.acceptance.synthetic.v1",
        "synthetic_only": True,
        "human_windows_acceptance": "NOT_RUN",
        "commercial_release": "NOT_APPROVED",
        "themes": list(_THEMES),
        "embedded_rows_per_html": 3,
    }:
        raise ValueError("Manifest/approval flags invalid")
    for theme in _THEMES:
        html = (folder / f"{theme}.html").read_bytes()
        m = _RE_DATA.search(html)
        if not m or b"connect-src 'none'" not in html:
            raise ValueError(f"Missing embedded data/offline CSP in {theme}")
        data = json.loads(base64.b64decode(m[1], validate=True))
        if data.get("theme") != theme or len(data.get("records", [])) != 3:
            raise ValueError(f"Invalid synthetic data in {theme}")
        if data["records"][0]["id"] != "S01" or data["records"][0]["title"] != "Cold Brew":
            raise ValueError(f"Unexpected synthetic fixture in {theme}")
    return {"status": "SYNTHETIC_OWNER_KIT_VERIFIED",
            "files": len(_FILES), "html_themes": len(_THEMES),
            "human_windows_acceptance": "NOT_RUN", "commercial_release": "NOT_APPROVED"}


def build_kit(destination: Path) -> dict:
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"Kit destination exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".rea-lite-owner-kit-", dir=destination.parent))
    try:
        src = stage / "source.csv"
        src.write_text(_BASE_CSV, encoding="utf-8", newline="")
        digest = source_sha256(src)
        for theme in _THEMES:
            build(src, stage / f"{theme}.html", name=f"REA Lite Synthetic {theme}",
                  theme=theme, approval="APPROVE", expected_source_sha256=digest)
        src.rename(stage / "base.csv.tmp")
        (stage / "base.csv.tmp").unlink()
        for filename, data in (
            ("valid_update.csv", _VALID_CSV),
            ("duplicate_id.csv", _DUPLICATE_CSV),
            ("wrong_columns.csv", _WRONG_HEADER_CSV),
            ("README_FIRST.txt", _README),
            ("CHECKLIST_KO.txt", _CHECKLIST),
        ):
            (stage / filename).write_text(data, encoding="utf-8", newline="\n")
        manifest = {
            "schema": "rea.lite.owner.acceptance.synthetic.v1",
            "synthetic_only": True,
            "human_windows_acceptance": "NOT_RUN",
            "commercial_release": "NOT_APPROVED",
            "themes": list(_THEMES),
            "embedded_rows_per_html": 3,
        }
        (stage / "MANIFEST.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        hashes = [f"{_sha((stage / name).read_bytes())}  {name}" for name in sorted(_FILES - {"SHA256SUMS.txt"})]
        (stage / "SHA256SUMS.txt").write_text("\n".join(hashes) + "\n", encoding="utf-8")
        verification = verify_kit(stage)
        publish_directory(stage, destination)
        return verification
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def archive_kit(folder: Path, zip_path: Path) -> None:
    """Create a fresh ZIP, refuse overwrite, read back every member."""
    verify_kit(folder)
    zip_path = Path(zip_path).absolute()
    if zip_path.exists() or zip_path.is_symlink():
        raise FileExistsError(f"ZIP destination exists: {zip_path}")
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "x", compression=zipfile.ZIP_DEFLATED) as z:
        for name in sorted(_FILES):
            z.write(folder / name, arcname=name)
    with zipfile.ZipFile(zip_path) as z:
        if set(z.namelist()) != _FILES or z.testzip() is not None:
            raise ValueError("ZIP inventory or CRC failed")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build synthetic-only Windows owner acceptance kit")
    ap.add_argument("--out", type=Path, required=True, help="NEW output folder")
    ap.add_argument("--zip", dest="zip_path", type=Path, help="NEW ZIP path")
    args = ap.parse_args(argv)
    if args.zip_path and (args.zip_path.exists() or args.zip_path.is_symlink()):
        ap.error("ZIP already exists")
    result = build_kit(args.out)
    if args.zip_path:
        archive_kit(args.out, args.zip_path)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
