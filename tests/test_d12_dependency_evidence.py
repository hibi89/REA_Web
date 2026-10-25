"""D12 positive, negative, conditional, path and non-distribution evidence tests."""
from __future__ import annotations

from email.message import Message
import hashlib
from importlib import metadata
import json
from pathlib import Path
import subprocess
import sys

import pytest

from rea.dependency_evidence import audit_environment, _legal_evidence
from rea.delivery import create_delivery
from rea.provenance import inspect_delivery


class FakeDist:
    def __init__(self, root, version="1.2.3", requires=(), files=(),
                 expression=None, declared_files=()):
        self.root = root
        self.version = version
        self.requires = list(requires)
        self.files = None if files is None else [Path(p) for p in files]
        self.metadata = Message()
        if expression is not None:
            self.metadata["License-Expression"] = expression
        for item in declared_files:
            self.metadata["License-File"] = item

    def locate_file(self, relative):
        return self.root / str(relative)

    def read_text(self, filename):
        return "Name: fake\nVersion: " + self.version + "\n"


def fake_lookup(dists):
    def lookup(name):
        if name not in dists:
            raise metadata.PackageNotFoundError(name)
        return dists[name]
    return lookup


def test_actual_ci_roots_are_observations_not_license_clearance():
    report = audit_environment()
    observed = {d["name"]: d for d in report["installed_distributions"]}
    assert observed["fastapi"]["version"]
    assert observed["uvicorn"]["version"]
    assert report["classification"] == "DEVELOPER_CI_INSTALLED_ENVIRONMENT_ONLY"
    assert report["commercial_license_clearance"] == "NOT_GRANTED"
    assert report["legal_compliance_status"] == "UNKNOWN"
    assert report["installed_metadata_hashes_are_not_wheel_archive_hashes"]
    assert report["wheel_downloads_or_hash_verification"] == "NOT_RUN_NO_NETWORK"
    assert report["network_calls_made_by_auditor"] == 0
    assert report["customer_zip_unchanged"] is True


def test_reachable_base_transitive_versions_and_candidate_are_sorted(tmp_path):
    a = FakeDist(tmp_path, requires=["z_child>=2", "a_child==1"])
    b = FakeDist(tmp_path, version="2.1")
    c = FakeDist(tmp_path, version="1")
    r = audit_environment(("a_root>=1",), fake_lookup({
        "a-root": a, "z-child": b, "a-child": c}))
    assert [d["name"] for d in r["installed_distributions"]] == [
        "a-child", "a-root", "z-child"]
    assert r["candidate_constraints"] == [
        "a-child==1", "a-root==1.2.3", "z-child==2.1"]
    assert all(e["status"] == "VERSION_SATISFIES_DECLARATION"
               for e in r["requirement_edges"])
    assert "NOT_A_LOCK" in r["candidate_constraints_status"]


def test_inactive_extra_and_platform_are_separately_reported(tmp_path):
    dist = FakeDist(tmp_path, requires=[
        'unused_extra>=1; extra == "benchmark"',
        'unused_platform>=1; sys_platform == "imaginary_os"',
        "needed>=1",
    ])
    r = audit_environment(("root>=1",), fake_lookup({
        "root": dist, "needed": FakeDist(tmp_path)}))
    statuses = {e["to"]: e["status"] for e in r["requirement_edges"]}
    assert statuses["unused-extra"] == "SKIPPED_OPTIONAL_EXTRA"
    assert statuses["unused-platform"] == "SKIPPED_ENVIRONMENT_MARKER"
    assert statuses["needed"] == "VERSION_SATISFIES_DECLARATION"
    assert not any(d["name"].startswith("unused") for d in r["installed_distributions"])


def test_missing_and_incompatible_version_are_not_silent(tmp_path):
    r = audit_environment(("root==3",), fake_lookup({
        "root": FakeDist(tmp_path, version="1", requires=["missing>=1"]),
    }))
    assert {e["status"] for e in r["requirement_edges"]} == {
        "VERSION_CONFLICT", "MISSING"}
    assert {"MISSING", "VERSION_CONFLICT"} <= set(r["unresolved_resolution_issues"])
    assert any(d["status"] == "MISSING" for d in r["installed_distributions"])


def test_unparseable_transitive_requirement_is_visible(tmp_path):
    r = audit_environment(("root",), fake_lookup({
        "root": FakeDist(tmp_path, requires=["@ invalid !"]),
    }))
    assert "UNPARSEABLE_REQUIREMENT" in r["unresolved_resolution_issues"]


def test_requested_extras_never_claim_complete_resolution(tmp_path):
    r = audit_environment(("root",), fake_lookup({
        "root": FakeDist(tmp_path, requires=["dep[fast]>=1"]),
        "dep": FakeDist(tmp_path),
    }))
    assert "EXTRAS_NOT_FULLY_EXPANDED" in r["unresolved_resolution_issues"]
    edge = next(e for e in r["requirement_edges"] if e.get("to") == "dep")
    assert edge["extras_resolution"] == "NOT_RECURSIVELY_AUDITED_REVIEW_REQUIRED"


def test_sha256_legal_bytes_only_and_declared_metadata_hash(tmp_path):
    legal = tmp_path / "licenses" / "LICENSE.md"
    legal.parent.mkdir()
    legal.write_text("A test license, not a grant.\n", encoding="utf-8")
    dist = FakeDist(tmp_path, files=["licenses/LICENSE.md"], expression="MIT",
                    declared_files=["licenses/LICENSE.md"])
    r = _legal_evidence(dist)
    assert r["declared_license_expression"] == "MIT"
    assert r["legal_file_evidence"][0]["sha256"] == hashlib.sha256(legal.read_bytes()).hexdigest()
    assert r["legal_file_evidence"][0]["byte_count"] == len(legal.read_bytes())
    assert "A test license" not in json.dumps(r)
    assert r["installed_metadata_sha256"] and len(r["installed_metadata_sha256"]) == 64
    assert r["license_compliance_verdict"] == "UNKNOWN_NOT_GRANTED"


def test_missing_legal_file_remains_unknown(tmp_path):
    r = _legal_evidence(FakeDist(tmp_path, files=["NOTICE.txt"]))
    assert r["legal_file_evidence"][0]["status"] == "FILE_MISSING"
    assert "sha256" not in r["legal_file_evidence"][0]


def test_oversized_legal_file_not_read(tmp_path):
    f = tmp_path / "LICENSE"
    f.write_bytes(b"x" * 1_000_001)
    r = _legal_evidence(FakeDist(tmp_path, files=["LICENSE"]))
    assert r["legal_file_evidence"][0]["status"] == "FILE_TOO_LARGE_NOT_READ"


def test_absolute_or_parent_path_in_declared_metadata_is_not_read(tmp_path):
    r = _legal_evidence(FakeDist(tmp_path, files=["../LICENSE", "/LICENSE"]))
    assert all(f["status"] == "UNSAFE_RELATIVE_PATH"
               for f in r["legal_file_evidence"])


def test_metadata_without_record_file_list_marked_incomplete(tmp_path):
    r = audit_environment(("root",), fake_lookup({
        "root": FakeDist(tmp_path, files=None),
    }))
    assert "LEGAL_FILE_METADATA_INCOMPLETE" in r["unresolved_resolution_issues"]
    assert r["installed_distributions"][0]["file_list_available"] is False


def test_direct_conditional_roots_rejected(tmp_path):
    with pytest.raises(ValueError, match="unconditional"):
        audit_environment(('root; extra == "test"',), fake_lookup({}))


def test_report_does_not_enter_or_mutate_customer_zip(tmp_path):
    root = Path(__file__).resolve().parents[1]
    zip_path = tmp_path / "synthetic-delivery.zip"
    create_delivery(root / "samples" / "qa_cafe.csv", zip_path)
    before = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    report = audit_environment()
    assert report["commercial_license_clearance"] == "NOT_GRANTED"
    assert hashlib.sha256(zip_path.read_bytes()).hexdigest() == before
    assert inspect_delivery(zip_path)["overall_commercial_clearance"] == "NOT_GRANTED"


def test_cli_creates_developer_json_and_refuses_overwrite(tmp_path):
    out = tmp_path / "ci-evidence.json"
    cmd = [sys.executable, "-m", "rea.dependency_evidence", "--out", str(out)]
    first = subprocess.run(cmd, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["commercial_license_clearance"] == "NOT_GRANTED"
    content = out.read_bytes()
    second = subprocess.run(cmd, capture_output=True, text=True)
    assert second.returncode != 0
    assert out.read_bytes() == content


def test_missing_license_evidence_is_explicitly_unknown(tmp_path):
    r = audit_environment(("root",), fake_lookup({
        "root": FakeDist(tmp_path),
    }))
    assert "NO_LEGAL_FILES_DISCOVERED" in r["unresolved_resolution_issues"]
    assert "NO_LICENSE_DECLARATION" in r["unresolved_resolution_issues"]
    assert r["legal_compliance_status"] == "UNKNOWN"
