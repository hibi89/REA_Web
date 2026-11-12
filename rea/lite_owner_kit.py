"""REA Lite seller one-command offline HTML + ZIP candidate.

The caller must have reviewed the source SHA, field mapping, and plaintext risks.
No installation, customer-network transfer, overwrite, or sale authorization.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from rea.lite_builder import build_lite, THEMES
from rea.lite_delivery import DeliveryError, package_lite, verify_lite_zip
from rea.mvp import DataError, source_sha256


HTML_NAME = "REA_Lite.html"
ZIP_NAME = "REA_Lite_Delivery.zip"
CONTRACT = "REA_LITE_OWNER_KIT_V1"


def _owned_remove(path: Path, fingerprint: tuple[int, int] | None) -> None:
    """Only delete a file newly created by this invocation, never a swapped file."""
    if fingerprint is None or path.is_symlink():
        return
    try:
        stat = path.stat(follow_symlinks=False)
        if (stat.st_dev, stat.st_ino) == fingerprint:
            path.unlink()
    except FileNotFoundError:
        pass


def _identity(path: Path) -> tuple[int, int]:
    st = path.stat(follow_symlinks=False)
    return st.st_dev, st.st_ino


def build_owner_kit(source: Path, output_directory: Path, *, mapping: dict[str, str],
                    expected_source_sha256: str, confirm: str,
                    acknowledge_plaintext: str, theme: str = "office",
                    name: str = "REA Lite") -> dict:
    """Never publish a partial HTML+ZIP pair, never reuse existing outputs."""
    source, output_directory = Path(source), Path(output_directory)
    if confirm != "APPROVE" or acknowledge_plaintext != "ACK_PLAINTEXT_LOCAL_DATA":
        raise DeliveryError("OWNER_REVIEW_AND_PLAINTEXT_ACK_REQUIRED")
    if not output_directory.is_absolute() or not output_directory.is_dir():
        raise DeliveryError("EXISTING_ABSOLUTE_OUTPUT_DIRECTORY_REQUIRED")
    html_path = output_directory / HTML_NAME
    zip_path = output_directory / ZIP_NAME
    for target in (html_path, zip_path):
        if target.exists() or target.is_symlink():
            raise DeliveryError("OUTPUT_FILE_ALREADY_EXISTS")
    # build_lite and package_lite separately recheck all source hashes and paths.
    html_identity: tuple[int, int] | None = None
    zip_identity: tuple[int, int] | None = None
    try:
        first = build_lite(source, html_path, mapping=mapping,
                           expected_sha256=expected_source_sha256,
                           confirmation=confirm, theme=theme, name=name)
        html_identity = _identity(html_path)
        packaged = package_lite(html_path, zip_path,
                                expected_html_sha256=first["html_sha256"],
                                acknowledge=acknowledge_plaintext)
        zip_identity = _identity(zip_path)
        second = verify_lite_zip(zip_path)
        if second != packaged or second["html_sha256"] != first["html_sha256"]:
            raise DeliveryError("INDEPENDENT_PACKAGE_RECHECK_FAILED")
        if source_sha256(source) != expected_source_sha256:
            raise DeliveryError("OWNER_SOURCE_CHANGED_DURING_DELIVERY")
        if (not html_path.is_file() or html_path.is_symlink()
                or _identity(html_path) != html_identity
                or not zip_path.is_file() or zip_path.is_symlink()
                or _identity(zip_path) != zip_identity):
            raise DeliveryError("OUTPUT_REPLACED_DURING_DELIVERY")
        return {"contract": CONTRACT,
                "status": "UNSIGNED_LOCAL_OWNER_KIT_CREATED_RELEASE_HOLD",
                "source_sha256": first["source_sha256"],
                "html_sha256": first["html_sha256"],
                "rows": first["rows"],
                "columns": len(first["fields"]),
                "theme": first["theme"],
                "html_file": HTML_NAME,
                "delivery_zip": ZIP_NAME,
                "sale_approved": False,
                "buyer_accepted": False,
                "buyer_windows_verified": False,
                "source_data_embedded_plaintext": True,
                "remote_transfer": False,
                "original_source_modified": False}
    except Exception:
        _owned_remove(zip_path, zip_identity)
        _owned_remove(html_path, html_identity)
        raise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build a reviewed offline REA Lite owner kit")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--id-field", required=True)
    parser.add_argument("--title-field", required=True)
    parser.add_argument("--category-field", required=True)
    parser.add_argument("--confirm", required=True)
    parser.add_argument("--acknowledge-plaintext", required=True)
    parser.add_argument("--theme", choices=THEMES, default="office")
    parser.add_argument("--name", default="REA Lite")
    args = parser.parse_args(argv)
    try:
        result = build_owner_kit(
            args.source, args.out_dir,
            mapping={"id": args.id_field, "title": args.title_field,
                     "category": args.category_field},
            expected_source_sha256=args.source_sha256, confirm=args.confirm,
            acknowledge_plaintext=args.acknowledge_plaintext,
            theme=args.theme, name=args.name)
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 0
    except (DataError, DeliveryError, OSError, ValueError):
        # No raw customer cell data, trace, absolute file path or tokens in CLI errors.
        print("REA_LITE_OWNER_KIT_BLOCKED")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
