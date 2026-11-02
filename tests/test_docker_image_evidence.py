"""Offline fixture tests; never invokes Docker, remote registries or customer ZIPs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from rea.adapter import docker_image_evidence as ev


def _write(path: Path, data: object) -> bytes:
    body = (json.dumps(data, sort_keys=True).encode("utf-8")
            if not isinstance(data, bytes) else data)
    path.write_bytes(body)
    return body


def fixture(tmp_path):
    artifact_data = {
        "dockerfile": b"FROM scratch\n",
        "wheel_lock": {"wheels": [
            {"name":"fastapi", "version":"1.2.3", "sha256":"a"*64},
            {"name":"uvicorn", "version":"4.5.6", "sha256":"b"*64}]},
        "spdx_sbom": {"spdxVersion":"SPDX-2.3","packages": [
            {"name":"fastapi","versionInfo":"1.2.3","licenseConcluded":"MIT"},
            {"name":"uvicorn","versionInfo":"4.5.6","licenseConcluded":"BSD-3-Clause"}]},
        "signature_receipt": b"UNTRUSTED EXAMPLE SIGNATURE CLAIM",
        "vulnerability_report": b"UNTRUSTED EXAMPLE CVE CLAIM",
        "license_review": b"HUMAN REVIEW STILL REQUIRED",
    }
    manifest = {"schema":ev.SCHEMA,
                "image_ref":"example.invalid/rea-runtime@sha256:"+"c"*64,
                "platform":"linux/amd64", "artifacts": {}}
    for key, value in artifact_data.items():
        name = key + (".json" if isinstance(value, dict) else ".txt")
        body = _write(tmp_path/name, value)
        manifest["artifacts"][key] = {"file":name,"sha256":hashlib.sha256(body).hexdigest()}
    body = _write(tmp_path/"manifest.json", manifest)
    return tmp_path/"manifest.json", hashlib.sha256(body).hexdigest(), manifest


def inspect(tmp_path, manifest_file=None, expected_sha=None):
    if manifest_file is None:
        manifest_file, expected_sha, _ = fixture(tmp_path)
    return ev.inspect_local_evidence(tmp_path, manifest_file,
                      expected_manifest_sha256=expected_sha)


def test_complete_fixture_never_becomes_image_or_license_approval(tmp_path):
    result = inspect(tmp_path)
    assert result["status"] == "EVIDENCE_INVENTORY_REVIEW_REQUIRED"
    assert result["evidence_files_sha256_checked"] == 7
    assert result["wheel_sbom_versions_consistent"] is True
    for key in ("image_execution_authorized", "signature_cryptographically_verified",
                "complete_dependency_closure_verified", "license_rights_approved",
                "docker_engine_isolation_tested", "customer_zip_execution_authorized",
                "commercial_release_authorized"):
        assert result[key] is False
    assert "UNTRUSTED EXAMPLE" not in json.dumps(result)


def test_manifest_independent_sha_mismatch_refused(tmp_path):
    path, _, _ = fixture(tmp_path)
    with pytest.raises(ev.UnsafeEvidence, match="manifest digest"):
        inspect(tmp_path, path, "0"*64)


def test_missing_artifact_sha_refused(tmp_path):
    path, sha, manifest = fixture(tmp_path)
    (tmp_path/manifest["artifacts"]["signature_receipt"]["file"]).write_bytes(b"tampers")
    with pytest.raises(ev.UnsafeEvidence, match="SHA256 mismatch"):
        inspect(tmp_path, path, sha)


def test_symlink_artifact_refused(tmp_path):
    path, sha, manifest = fixture(tmp_path)
    file = tmp_path/manifest["artifacts"]["license_review"]["file"]
    original = file.read_bytes()
    file.unlink()
    outside = tmp_path.parent/(tmp_path.name+"-outside")
    outside.write_bytes(original)
    try:
        file.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted")
    with pytest.raises(ev.UnsafeEvidence, match="inside|symlink"):
        inspect(tmp_path, path, sha)


def test_parent_escape_refused_even_with_a_matching_independent_manifest_digest(tmp_path):
    path, _, manifest = fixture(tmp_path)
    manifest["artifacts"]["dockerfile"]["file"] = "../outside"
    sha = hashlib.sha256(_write(path, manifest)).hexdigest()
    with pytest.raises(ev.UnsafeEvidence, match="unsafe evidence file"):
        inspect(tmp_path, path, sha)


def test_wheel_sbom_version_mismatch_refused(tmp_path):
    path, _, manifest = fixture(tmp_path)
    detail = manifest["artifacts"]["spdx_sbom"]
    file = tmp_path/detail["file"]
    sbom = json.loads(file.read_text())
    sbom["packages"][0]["versionInfo"] = "9.9.9"
    detail["sha256"] = hashlib.sha256(_write(file, sbom)).hexdigest()
    sha = hashlib.sha256(_write(path, manifest)).hexdigest()
    with pytest.raises(ev.UnsafeEvidence, match="wheel lock and SPDX"):
        inspect(tmp_path, path, sha)


def test_unpinned_wheel_refused(tmp_path):
    path, _, manifest = fixture(tmp_path)
    detail=manifest["artifacts"]["wheel_lock"]
    file=tmp_path/detail["file"]
    lock=json.loads(file.read_text())
    lock["wheels"][0]["sha256"]=""
    detail["sha256"]=hashlib.sha256(_write(file,lock)).hexdigest()
    sha=hashlib.sha256(_write(path,manifest)).hexdigest()
    with pytest.raises(ev.UnsafeEvidence, match="unpinned"):
        inspect(tmp_path,path,sha)


def test_oversized_file_refused_without_loading_into_memory(tmp_path):
    path, sha, manifest = fixture(tmp_path)
    file = tmp_path/manifest["artifacts"]["license_review"]["file"]
    with file.open("wb") as stream:
        stream.truncate(ev.MAX_FILE+1)
    with pytest.raises(ev.UnsafeEvidence, match="oversized"):
        inspect(tmp_path,path,sha)


def test_no_overwrite_even_on_valid_evidence(tmp_path):
    path, sha, _=fixture(tmp_path)
    out = tmp_path/"report.json"
    out.write_text("PRESERVE")
    with pytest.raises(SystemExit) as stop:
        ev.main(["--evidence-dir",str(tmp_path),"--manifest",str(path),
                "--expected-manifest-sha256",sha,"--out",str(out)])
    assert stop.value.code == 2
    assert out.read_text()=="PRESERVE"


def test_valid_cli_produces_review_only_no_runtime(tmp_path):
    path,sha,_=fixture(tmp_path)
    out=tmp_path/"review.json"
    assert ev.main(["--evidence-dir",str(tmp_path),"--manifest",str(path),
                    "--expected-manifest-sha256",sha,"--out",str(out)])==0
    obj=json.loads(out.read_text())
    assert obj["image_execution_authorized"] is False
    assert obj["status"] == "EVIDENCE_INVENTORY_REVIEW_REQUIRED"
