"""Strict offline two-file append, NOT a join, inferred relationship or sale approval.

Exactly two owner-authorized sources; same explicitly mapped column set,
combined 10 MiB / 10,000 rows, unique IDs, pinned SHA-256 for each.
No public uploads, original file mutations, reference scans or Fable inference.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile
import zipfile

from rea.guided import preflight
from rea.mvp import DataError, MAX_BYTES, MAX_ROWS, REQUIRED, map_owner_fields, parse_input
from rea.orchestrator import build
from rea.safe_publish import publish_archive, publish_directory
from rea.delivery import (
    _manifest, _members, _zipinfo, verify_delivery,
)

STATE = "OWNER_CONFIRMED_EXPLICIT_APPEND_ONLY"
MODE = "SAME_SCHEMA_ROW_APPEND_NO_JOIN"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _approval(source: Path, mapping: dict[str, str], sha: str, typed: str):
    if typed != "APPROVE":
        raise DataError("Each source needs its own literal APPROVE")
    if (not isinstance(sha, str) or len(sha) != 64
            or any(char not in "0123456789abcdef" for char in sha)):
        raise DataError("Invalid pinned source SHA256")
    if _sha256(source) != sha:
        raise DataError("A source changed after inspection; re-inspect and approve")
    columns, rows = parse_input(source, require_semantics=False)
    normalized, mapped = map_owner_fields(columns, rows, mapping)
    if _sha256(source) != sha:
        raise DataError("A source changed during preflight")
    return normalized, mapped


def preflight_pair(first: Path, second: Path) -> dict:
    """Metadata only; no record samples, paths or cell values printed."""
    first, second = Path(first), Path(second)
    if first.absolute() == second.absolute():
        raise DataError("Two different owner files are required")
    if not first.is_file() or not second.is_file() or first.is_symlink() or second.is_symlink():
        raise DataError("Both owner files must be distinct regular non-symlinks")
    if os.path.samefile(first, second):
        raise DataError("The two inputs refer to the same file")
    if first.stat().st_size + second.stat().st_size > MAX_BYTES:
        raise DataError("Combined source inputs exceed 10 MiB")
    a, b = preflight(first), preflight(second)
    if a["row_count"] + b["row_count"] > MAX_ROWS:
        raise DataError("Combined source inputs exceed 10,000 rows")
    return {
        "mode": MODE, "review_status": "UNAPPROVED",
        "source_count": 2, "combined_rows": a["row_count"] + b["row_count"],
        "sources": [
            {"position": i, "input_kind": doc["source_kind"],
             "sha256": doc["source_sha256"], "row_count": doc["row_count"],
             "columns": [field["name"] for field in doc["fields"]]}
            for i, doc in enumerate((a, b), 1)
        ],
        "owner_approval_required": "APPROVE first, APPROVE second, then APPEND",
        "no_join_or_relation_inference": True,
    }


def _prepare(first: Path, second: Path, mapping: dict[str, str],
             first_sha: str, second_sha: str,
             first_confirm: str, second_confirm: str, append_confirm: str):
    first, second = Path(first), Path(second)
    if append_confirm != "APPEND":
        raise DataError("Combined append requires separate literal APPEND")
    info = preflight_pair(first, second)
    if (first_sha != info["sources"][0]["sha256"]
            or second_sha != info["sources"][1]["sha256"]):
        raise DataError("A source changed since paired preview")
    h1, rows1 = _approval(first, mapping, first_sha, first_confirm)
    h2, rows2 = _approval(second, mapping, second_sha, second_confirm)
    if set(h1) != set(h2):
        raise DataError("Different mapped schemas cannot be appended")
    if len(rows1) + len(rows2) > MAX_ROWS:
        raise DataError("Combined rows exceed 10,000")
    all_rows = rows1 + rows2
    ids = [item["id"] for item in all_rows]
    if len(set(ids)) != len(ids):
        raise DataError("Duplicate id across two owner sources")
    receipt = {
        "schema_version": "rea.two_file_append.v0.1",
        "status": STATE, "mode": MODE,
        "source_count": 2, "rows": len(all_rows),
        "fields": h1, "sources": [
            {"position": i, "input_kind": source["input_kind"],
             "sha256": source["sha256"], "row_count": source["row_count"],
             "source_fields": {target: mapping[target] for target in REQUIRED},
             "confirmed": "APPROVE"}
            for i, source in enumerate(info["sources"], 1)
        ],
        "combined_confirmation": "APPEND",
        "fable_inferred_mapping_used": False,
        "external_join_or_lookup_used": False,
    }
    return h1, all_rows, receipt


def _compose(first: Path, second: Path, work: Path, name: str,
             mapping: dict[str, str], first_sha: str, second_sha: str,
             first_confirm: str, second_confirm: str, append_confirm: str):
    columns, records, receipt = _prepare(
        first, second, mapping, first_sha, second_sha,
        first_confirm, second_confirm, append_confirm)
    source = work / "approved_combined.csv"
    with source.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    if source.stat().st_size > MAX_BYTES:
        raise DataError("Normalized combined CSV exceeds 10 MiB")
    project = work / "app"
    manifest = build(source, project, name)
    if _sha256(first) != first_sha or _sha256(second) != second_sha:
        raise DataError("Owner source changed while generating")
    manifest["source"] = "TWO_OWNER_INPUTS_APPENDED"
    manifest["source_count"] = 2
    manifest["semantic_mapping_status"] = "owner_confirmed_same_schema_append_only"
    manifest["two_file_append"] = receipt
    (project / "append_report.json").write_text(
        json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    (project / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with (project / "README.md").open("a", encoding="utf-8") as readme:
        readme.write(
            "\nTwo distinct owner-confirmed source files were appended as ROWS "
            "after explicit same-schema field mapping. No join, lookup, "
            "relationship inference, or owner signature verification occurred.\n"
        )
    return project, manifest


def build_pair(first: Path, second: Path, output: Path, name: str,
               mapping: dict[str, str], first_sha: str, second_sha: str,
               first_confirm: str, second_confirm: str, append_confirm: str) -> dict:
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError("Output already exists")
    # Validate all inputs and approvals before creating the output parent.
    _prepare(first, second, mapping, first_sha, second_sha,
             first_confirm, second_confirm, append_confirm)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".rea-two-source-", dir=output.parent) as tmp:
        project, manifest = _compose(
            Path(first), Path(second), Path(tmp), name,
            mapping, first_sha, second_sha, first_confirm, second_confirm,
            append_confirm)
        publish_directory(project, output)
    return manifest


def pack_pair(first: Path, second: Path, output: Path, name: str,
              mapping: dict[str, str], first_sha: str, second_sha: str,
              first_confirm: str, second_confirm: str, append_confirm: str) -> dict:
    output = Path(output).absolute()
    if output.suffix.lower() != ".zip":
        raise DataError("Output archive must end with .zip")
    if output.exists() or output.is_symlink():
        raise FileExistsError("Output archive already exists")
    _prepare(first, second, mapping, first_sha, second_sha,
             first_confirm, second_confirm, append_confirm)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".rea-two-source-", dir=output.parent) as tmp:
        work = Path(tmp)
        project, _ = _compose(
            Path(first), Path(second), work, name,
            mapping, first_sha, second_sha, first_confirm, second_confirm,
            append_confirm)
        entries = _members(project)
        proof = _manifest(entries)
        entries["delivery_manifest.json"] = (
            json.dumps(proof, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        ).encode("utf-8")
        stage = work / "complete.zip"
        with zipfile.ZipFile(stage, "x", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9, allowZip64=False) as archive:
            for filename, data in sorted(entries.items()):
                archive.writestr(_zipinfo(filename), data, compress_type=zipfile.ZIP_DEFLATED,
                                 compresslevel=9)
        verify_delivery(stage)
        from rea.provenance import inspect_delivery
        inspect_delivery(stage)  # includes two-file receipt validation
        if _sha256(Path(first)) != first_sha or _sha256(Path(second)) != second_sha:
            raise DataError("Owner source changed before archive publication")
        publish_archive(stage, output)
    return proof


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Owner-approved two-file SAME-SCHEMA ROW APPEND only")
    group = p.add_subparsers(dest="action", required=True)
    for cmd in ("inspect", "build", "pack"):
        sub = group.add_parser(cmd)
        sub.add_argument("--first", type=Path, required=True)
        sub.add_argument("--second", type=Path, required=True)
        if cmd != "inspect":
            sub.add_argument("--out", type=Path, required=True)
            sub.add_argument("--name", default="REA same-schema append")
            sub.add_argument("--id-field", required=True)
            sub.add_argument("--title-field", required=True)
            sub.add_argument("--category-field", required=True)
            sub.add_argument("--first-sha256", required=True)
            sub.add_argument("--second-sha256", required=True)
            sub.add_argument("--approve-first", required=True)
            sub.add_argument("--approve-second", required=True)
            sub.add_argument("--confirm-append", required=True)
    args = p.parse_args(argv)
    try:
        if args.action == "inspect":
            result = preflight_pair(args.first, args.second)
        else:
            mapping = {"id": args.id_field, "title": args.title_field,
                       "category": args.category_field}
            common = (args.first, args.second, args.out, args.name, mapping,
                      args.first_sha256, args.second_sha256,
                      args.approve_first, args.approve_second, args.confirm_append)
            result = build_pair(*common) if args.action == "build" else pack_pair(*common)
    except (OSError, ValueError) as exc:
        p.exit(2, "TWO_FILE_REJECTED: " + str(exc) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
