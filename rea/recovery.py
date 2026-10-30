"""Offline REA ZIP recovery into a NEW local directory, never in-place repair.

Seller/support-side tool. Does not install packages, start a server, authorize
commercial redistribution or certify customer data rights. Standard library only.
Run: python -m rea.recovery --zip owned.zip --out ./new-extracted-folder
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

from rea.customer_self_check import inspect, verify_exact_delivery_tree
from rea.delivery import DeliveryError, MAX_ARCHIVE_BYTES, verify_delivery
from rea.provenance import inspect_delivery
from rea.safe_publish import publish_directory

# A valid <=25MiB uncompressed ZIP has no reason to occupy >51MiB on disk.
# Bound the staging copy even when central-directory metadata is manipulated.
MAX_ARCHIVE_ON_DISK = 2 * MAX_ARCHIVE_BYTES + 1024 * 1024


def restore_delivery(archive: Path, destination: Path) -> dict:
    """Validate, extract and atomically publish without overwriting a target.

    Only integrity and read-only SQLite access are certified. Dependencies,
    Windows launch, seller terms, copyright and customer consent remain open.
    """
    archive = Path(archive).absolute()
    destination = Path(destination).absolute()
    if archive.suffix.lower() != ".zip" or archive.is_symlink() or not archive.is_file():
        raise DeliveryError("Use an existing regular, non-symlink .zip archive")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("Restore destination already exists; choose a NEW folder")
    if archive.stat().st_size > MAX_ARCHIVE_ON_DISK:
        raise DeliveryError("Archive exceeds bounded recovery staging limit")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".rea-recovery-", dir=destination.parent) as temp:
        work = Path(temp)
        snapshot = work / "verified-input.zip"
        digest = hashlib.sha256()
        copied = 0
        with archive.open("rb") as source, snapshot.open("xb") as target:
            for chunk in iter(lambda: source.read(64 * 1024), b""):
                copied += len(chunk)
                if copied > MAX_ARCHIVE_ON_DISK:
                    raise DeliveryError("Archive grew beyond recovery staging limit")
                target.write(chunk)
                digest.update(chunk)

        # Prove the SAME frozen bytes that will be extracted: no second read of
        # the potentially changing owner/archive path after the staging copy.
        manifest = verify_delivery(snapshot)
        inspect_delivery(snapshot)
        restored = work / "restored"
        restored.mkdir()
        with zipfile.ZipFile(snapshot) as zipped:
            zipped.extractall(restored)
        expected = {entry["path"] for entry in manifest["files"]}
        verify_exact_delivery_tree(restored, expected)
        local = inspect(restored)
        if (local["integrity"] != "MATCHED_DELIVERY_MANIFEST_SHA256"
                or local["database"] != "READONLY_OPEN_SUCCESS"):
            raise DeliveryError("Extracted delivery integrity or read-only SQLite check failed")

        app_manifest_path = restored / "app" / "manifest.json"
        if app_manifest_path.stat().st_size > 256 * 1024:
            raise DeliveryError("Generated app manifest exceeds recovery metadata limit")
        app_manifest = json.loads(app_manifest_path.read_text(encoding="utf-8"))
        claimed_rows = app_manifest.get("rows") if isinstance(app_manifest, dict) else None
        if (type(claimed_rows) is not int or not 1 <= claimed_rows <= 10_000
                or claimed_rows != local.get("row_count_only")):
            raise DeliveryError("Generated app row count does not match SQLite")

        # The atomic no-replace primitive ensures an unexpected simultaneous
        # destination creation is never overwritten, even if an empty folder.
        publish_directory(restored, destination)

    return {
        "schema_version": "rea.local_recovery.v0.1",
        "status": "RESTORED_INTEGRITY_AND_READONLY_SQLITE_ONLY",
        "destination_name": destination.name,
        "archive_sha256": digest.hexdigest(),
        "file_count": len(expected),
        "sqlite_row_count": claimed_rows,
        "python_dependencies_accepted": False,
        "native_windows_launch_accepted": False,
        "commercial_clearance": "NOT_GRANTED",
        "source_data_privacy": "NOT_CERTIFIED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline verified ZIP recovery to a new folder (no overwrite)"
    )
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        outcome = restore_delivery(args.zip, args.out)
    except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        parser.exit(2, "RECOVERY_REJECTED: " + type(exc).__name__ + ": " + str(exc) + "\n")
    print(json.dumps(outcome, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
