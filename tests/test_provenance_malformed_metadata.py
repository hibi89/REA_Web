"""Rehashed synthetic ZIP metadata must fail provenance with AuditError, never traceback."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

import pytest

from rea.delivery import create_delivery, verify_delivery
from rea.guided import preflight
from rea.provenance import AuditError, inspect_delivery
from rea.two_source import pack_pair, preflight_pair

ROOT = Path(__file__).resolve().parents[1]


def repack(source: Path, target: Path, changes: dict[str, bytes]) -> None:
    """Rehash outer manifest so integrity verification reaches semantic checks."""
    with zipfile.ZipFile(source) as src:
        contents = {name: src.read(name) for name in src.namelist()}
    contents.update(changes)
    inventory = [
        {"path": path, "bytes": len(value),
         "sha256": hashlib.sha256(value).hexdigest()}
        for path, value in sorted(contents.items()) if path != "delivery_manifest.json"
    ]
    contents["delivery_manifest.json"] = json.dumps({
        "schema_version": "rea.delivery.v0.1", "files": inventory,
    }).encode("utf-8")
    with zipfile.ZipFile(target, "x", compression=zipfile.ZIP_DEFLATED) as dst:
        for name, value in sorted(contents.items()):
            dst.writestr(name, value)
    verify_delivery(target)


def base_zip(tmp_path: Path) -> Path:
    original = tmp_path / "source.zip"
    create_delivery(ROOT / "samples/qa_cafe.csv", original)
    return original


@pytest.mark.parametrize("member", [
    "app/manifest.json", "app/schema_preview.json",
])
@pytest.mark.parametrize("payload", [b"[]", b"null", b'"not-object"', b'{"bad":'])
def test_rehashed_nonobject_or_invalid_json_refused_as_audit_error(tmp_path, member, payload):
    original = base_zip(tmp_path)
    archive = tmp_path / "rehashed.zip"
    repack(original, archive, {member: payload})
    with pytest.raises(AuditError, match="metadata"):
        inspect_delivery(archive)


def test_rehashed_duplicate_json_keys_are_rejected(tmp_path):
    original = base_zip(tmp_path)
    archive = tmp_path / "duplicate.zip"
    repack(original, archive, {
        "app/schema_preview.json": b'{"review_status":"UNAPPROVED","review_status":"UNAPPROVED"}',
    })
    with pytest.raises(AuditError, match="Duplicate"):
        inspect_delivery(archive)


def test_rehashed_wrong_input_kind_type_refused(tmp_path):
    original = base_zip(tmp_path)
    with zipfile.ZipFile(original) as zf:
        app = json.loads(zf.read("app/manifest.json"))
    app["input_kind"] = ["customer_supplied_csv"]
    archive = tmp_path / "kind.zip"
    repack(original, archive, {
        "app/manifest.json": json.dumps(app).encode("utf-8"),
    })
    with pytest.raises(AuditError, match="source kind"):
        inspect_delivery(archive)


@pytest.mark.parametrize("bad_fields", [
    [{"id": "id"}],
    {"id": [], "title": "display_name", "category": "group_name"},
    {"id": "sku", "title": 1, "category": "group_name"},
])
def test_rehashed_invalid_mapping_field_types_refused(tmp_path, bad_fields):
    source = ROOT / "samples/qa_guided.csv"
    approved = {"id": "sku", "title": "display_name", "category": "group_name"}
    original = tmp_path / "guided.zip"
    create_delivery(source, original, approved_mapping=approved,
                    expected_source_sha256=preflight(source)["source_sha256"])
    with zipfile.ZipFile(original) as zf:
        app = json.loads(zf.read("app/manifest.json"))
        mapping = json.loads(zf.read("app/mapping_report.json"))
    mapping["source_fields"] = bad_fields
    app["owner_field_mapping"] = mapping
    archive = tmp_path / "modified.zip"
    repack(original, archive, {
        "app/manifest.json": json.dumps(app).encode("utf-8"),
        "app/mapping_report.json": json.dumps(mapping).encode("utf-8"),
    })
    with pytest.raises(AuditError, match="mapping report"):
        inspect_delivery(archive)


def test_rehashed_append_source_fields_nonstring_refused(tmp_path):
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    first.write_text("sku,label,group\nA,Alpha,Food\n", encoding="utf-8")
    second.write_text("sku,label,group\nB,Beta,Food\n", encoding="utf-8")
    info = preflight_pair(first, second)
    a, b = [item["sha256"] for item in info["sources"]]
    original = tmp_path / "paired.zip"
    pack_pair(first, second, original, "Synthetic approved pair",
              {"id": "sku", "title": "label", "category": "group"},
              a, b, "APPROVE", "APPROVE", "APPEND")
    with zipfile.ZipFile(original) as zf:
        app = json.loads(zf.read("app/manifest.json"))
        receipt = json.loads(zf.read("app/append_report.json"))
    receipt["sources"][0]["source_fields"]["id"] = []
    app["two_file_append"] = receipt
    archive = tmp_path / "paired-malformed.zip"
    repack(original, archive, {
        "app/manifest.json": json.dumps(app).encode("utf-8"),
        "app/append_report.json": json.dumps(receipt).encode("utf-8"),
    })
    with pytest.raises(AuditError, match="source confirmation"):
        inspect_delivery(archive)


def test_untampered_synthetic_archive_retains_auditable_status(tmp_path):
    archive = base_zip(tmp_path)
    result = inspect_delivery(archive)
    assert result["delivery_integrity"] == "VERIFIED_SHA256"
    assert result["overall_commercial_clearance"] == "NOT_GRANTED"


@pytest.mark.parametrize("member", [
    "app/manifest.json", "app/schema_preview.json",
])
@pytest.mark.parametrize("value", [b"NaN", b"Infinity", b"-Infinity"])
def test_nonfinite_generated_metadata_rejected(tmp_path, member, value):
    original = base_zip(tmp_path)
    archive = tmp_path / "nonfinite.zip"
    repack(original, archive, {member: b'{"unapproved_extra":' + value + b'}'})
    with pytest.raises(AuditError, match="Non-finite"):
        inspect_delivery(archive)


@pytest.mark.parametrize("member", [
    "app/manifest.json", "app/schema_preview.json",
])
def test_deep_generated_metadata_refused_without_recursion_traceback(tmp_path, member):
    original = base_zip(tmp_path)
    archive = tmp_path / "deep.zip"
    payload = b'{"unapproved_extra":' + b"[" * 1500 + b"0" + b"]" * 1500 + b"}"
    repack(original, archive, {member: payload})
    with pytest.raises(AuditError, match="metadata"):
        inspect_delivery(archive)
