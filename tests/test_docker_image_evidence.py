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

@pytest.mark.parametrize("bad", [
    "example.invalid/../other@sha256:"+"c"*64,
    "example.invalid/.hidden@sha256:"+"c"*64,
    "example.invalid/another..part@sha256:"+"c"*64,
    "example.invalid/a//b@sha256:"+"c"*64,
    "example.invalid/a/@sha256:"+"c"*64,
])
def test_noncanonical_repository_refused_even_with_matching_manifest_hash(tmp_path, bad):
    path, _, manifest = fixture(tmp_path)
    manifest["image_ref"] = bad
    sha = hashlib.sha256(_write(path, manifest)).hexdigest()
    with pytest.raises(ev.UnsafeEvidence, match="invalid immutable"):
        inspect(tmp_path, path, sha)


def test_too_deep_json_refused_as_evidence_error(tmp_path):
    path, _, manifest = fixture(tmp_path)
    detail = manifest["artifacts"]["spdx_sbom"]
    nested = b"["*10000 + b"0" + b"]"*10000
    detail["sha256"] = hashlib.sha256(_write(tmp_path/detail["file"], nested)).hexdigest()
    sha = hashlib.sha256(_write(path, manifest)).hexdigest()
    with pytest.raises(ev.UnsafeEvidence, match="invalid UTF-8"):
        inspect(tmp_path, path, sha)


def test_duplicate_spdx_package_refused_even_if_same_version(tmp_path):
    path, _, manifest = fixture(tmp_path)
    detail = manifest["artifacts"]["spdx_sbom"]
    file = tmp_path / detail["file"]
    doc = json.loads(file.read_text())
    doc["packages"].append({"name":"FastAPI", "versionInfo":"1.2.3",
                            "licenseConcluded":"NOASSERTION"})
    detail["sha256"] = hashlib.sha256(_write(file,doc)).hexdigest()
    sha = hashlib.sha256(_write(path, manifest)).hexdigest()
    with pytest.raises(ev.UnsafeEvidence, match="duplicate or ambiguous"):
        inspect(tmp_path, path, sha)


def test_oversized_spdx_inventory_refused_before_processing(tmp_path):
    path, _, manifest = fixture(tmp_path)
    detail = manifest["artifacts"]["spdx_sbom"]
    file = tmp_path / detail["file"]
    doc = json.loads(file.read_text())
    doc["packages"] = doc["packages"] * 2100
    detail["sha256"] = hashlib.sha256(_write(file,doc)).hexdigest()
    sha = hashlib.sha256(_write(path, manifest)).hexdigest()
    with pytest.raises(ev.UnsafeEvidence, match="invalid SPDX"):
        inspect(tmp_path, path, sha)

@pytest.mark.parametrize("case", ["manifest", "descriptor", "wheel_lock", "spdx_sbom"])
def test_duplicate_json_object_key_refused_even_with_matching_all_hashes(tmp_path, case):
    path, _, manifest = fixture(tmp_path)
    if case == "manifest":
        body = path.read_bytes().replace(
            b'"platform": "linux/amd64"',
            b'"platform": "linux/arm64", "platform": "linux/amd64"', 1)
        assert body != path.read_bytes()
        path.write_bytes(body)
    elif case == "descriptor":
        body = path.read_bytes().replace(
            b'"file": "dockerfile.txt"',
            b'"file": "other.txt", "file": "dockerfile.txt"', 1)
        assert body != path.read_bytes()
        path.write_bytes(body)
    else:
        detail = manifest["artifacts"][case]
        file = tmp_path / detail["file"]
        if case == "wheel_lock":
            body = file.read_bytes().replace(
                b'"name": "fastapi"',
                b'"name": "evildoer", "name": "fastapi"', 1)
        else:
            body = file.read_bytes().replace(
                b'"licenseConcluded": "MIT"',
                b'"licenseConcluded": "NOASSERTION", "licenseConcluded": "MIT"', 1)
        assert body != file.read_bytes()
        file.write_bytes(body)
        detail["sha256"] = hashlib.sha256(body).hexdigest()
        _write(path, manifest)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ev.UnsafeEvidence, match="invalid|duplicate|ambiguous"):
        inspect(tmp_path, path, sha)

@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_nonstandard_json_constants_refused_even_with_sha_match(tmp_path, constant):
    path, _, manifest = fixture(tmp_path)
    detail = manifest["artifacts"]["spdx_sbom"]
    file = tmp_path / detail["file"]
    body = file.read_bytes().replace(b'"spdxVersion": "SPDX-2.3"',
           b'"unreviewedEvidence": ' + constant.encode() + b', "spdxVersion": "SPDX-2.3"', 1)
    assert body != file.read_bytes()
    file.write_bytes(body)
    detail["sha256"] = hashlib.sha256(body).hexdigest()
    sha = hashlib.sha256(_write(path, manifest)).hexdigest()
    with pytest.raises(ev.UnsafeEvidence, match="invalid|nonstandard"):
        inspect(tmp_path, path, sha)
