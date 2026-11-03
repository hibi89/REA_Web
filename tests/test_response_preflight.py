"""End-to-end offline CLI integration against existing static review output.

Only self-authored synthetic examples. No customer ZIP, network, Docker or secrets.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from rea.adapter.frontend_bridge import SCHEMA as REVIEW_SCHEMA, make_review
from rea.adapter.response_preflight import (
    INPUT_SCHEMA, SCHEMA, UnsafeSyntheticPreflight, review_synthetic_samples,
)
from tests_static_fixture import BACKEND, FABLE
from test_response_contract import BINDINGS, sample


def fixture_files(tmp_path):
    # Real source of this review: the existing, independent Fable/backend bridge.
    backend = copy.deepcopy(BACKEND)
    # The declared synthetic endpoint must match the explicitly mapped token.
    backend["api"]["endpoints"][2]["path"] = "/api/jobs/{ticket_id}"
    review = make_review(FABLE, backend, copy.deepcopy(BINDINGS))
    fixture = {
        "schema_version": INPUT_SCHEMA,
        "synthetic_only": True,
        "review_schema_version": REVIEW_SCHEMA,
        "backend_sha256": review["backend"]["sha256"],
        "selected_id": "A-1",
        "completed_statuses": ["done"],
        "pending_statuses": ["pending"],
        "list_coverage": "complete",
        "samples": {
            role: {**record, "body": record["body"].decode("utf-8")}
            for role, record in sample().items()
        },
    }
    review_path, sample_path = tmp_path / "review.json", tmp_path / "synthetic.json"
    review_path.write_text(json.dumps(review), encoding="utf-8")
    fixture["review_sha256"] = hashlib.sha256(review_path.read_bytes()).hexdigest()
    sample_path.write_text(json.dumps(fixture), encoding="utf-8")
    return review, fixture, review_path, sample_path


def invoke(review_path, sample_path, *args):
    return subprocess.run([
        sys.executable, "-m", "rea.adapter.response_preflight",
        "--review", str(review_path), "--samples", str(sample_path),
        "--synthetic-only", *map(str, args),
    ], capture_output=True, text=True, timeout=12)


def assert_refused(result):
    assert result.returncode == 2, (result.returncode, result.stderr)
    output = json.loads(result.stdout)
    assert output["status"] == "SYNTHETIC_PREFLIGHT_REFUSED"
    assert output["generation_allowed"] is False
    assert output["release_allowed"] is False
    assert output["customer_runtime_verified"] is False
    assert result.stderr == ""


def test_real_make_review_output_connects_to_synthetic_preflight_cli(tmp_path):
    review, fixture, rp, sp = fixture_files(tmp_path)
    report_path = tmp_path / "safe_report.json"
    previous = (rp.read_bytes(), sp.read_bytes())
    result = invoke(rp, sp, "--out", report_path)
    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary == json.loads(report_path.read_text(encoding="utf-8"))
    assert summary == review_synthetic_samples(
        review, fixture, review_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
    assert summary["schema_version"] == SCHEMA
    assert summary["status"] == "SYNTHETIC_PREFLIGHT_REVIEW_REQUIRED"
    assert summary["review_status"] == "OWNER_REVIEW_REQUIRED"
    assert summary["sample_contract_status"] == "SYNTHETIC_SHAPES_MATCH_REVIEW_REQUIRED"
    assert summary["sample_rows"] == 2
    assert summary["checked_roles"] == ["list", "metrics", "detail"]
    for flag in ("generation_allowed", "release_allowed", "customer_runtime_verified",
                 "source_rights_verified", "execution_performed", "network_performed"):
        assert summary[flag] is False
    assert (rp.read_bytes(), sp.read_bytes()) == previous
    assert "A-1" not in result.stdout
    assert fixture["review_sha256"] not in result.stdout
    assert "Synthetic" not in result.stdout
    assert "example.org" not in result.stdout
    assert "tickets" not in result.stdout
    assert str(tmp_path) not in result.stdout


def test_stdout_mode_produces_sanitized_deterministic_report_no_files(tmp_path):
    _, _, rp, sp = fixture_files(tmp_path)
    before = set(tmp_path.iterdir())
    first, second = invoke(rp, sp), invoke(rp, sp)
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout
    assert set(tmp_path.iterdir()) == before


def test_report_never_overwrites_file_or_leaks_fixture(tmp_path):
    _, _, rp, sp = fixture_files(tmp_path)
    out = tmp_path / "existing.json"
    out.write_bytes(b"KEEP_ORIGINAL")
    result = invoke(rp, sp, "--out", out)
    assert_refused(result)
    assert out.read_bytes() == b"KEEP_ORIGINAL"


def test_missing_explicit_synthetic_only_flag_is_refused(tmp_path):
    _, _, rp, sp = fixture_files(tmp_path)
    result = subprocess.run([
        sys.executable, "-m", "rea.adapter.response_preflight",
        "--review", str(rp), "--samples", str(sp),
    ], capture_output=True, text=True, timeout=12)
    assert result.returncode != 0
    assert "SYNTHETIC_PREFLIGHT_REVIEW_REQUIRED" not in result.stdout


@pytest.mark.parametrize("mutate", [
    lambda x: x.update(synthetic_only=False),
    lambda x: x.pop("synthetic_only"),
    lambda x: x.update(schema_version="not-a-synthetic-fixture"),
    lambda x: x.update(extra="cannot be silently ignored"),
    lambda x: x.update(list_coverage="paginated"),
    lambda x: x.update(selected_id="B-2"),
    lambda x: x.update(pending_statuses=["done", "pending"]),
    lambda x: x["samples"]["metrics"].update(status=401),
    lambda x: x["samples"]["list"].update(content_type="text/html"),
    lambda x: x["samples"].pop("detail"),
    lambda x: x["samples"]["metrics"].update(body='{"all_count":4,"success_count":1,"queued_count":1}'),
    lambda x: x["samples"]["detail"].update(body='{"ticket":"A-1","task":"Synthetic report","department":"audit","phase":"done","duration_ms":{"nested":1}}'),
    lambda x: x["samples"]["metrics"].update(body='{"all_count":2,"all_count":2,"success_count":1,"queued_count":1}'),
    lambda x: x["samples"]["metrics"].update(body='{"all_count":NaN,"success_count":1,"queued_count":1}'),
    lambda x: x["samples"]["detail"].update(body='{"refresh_token":"SENSITIVE_TEST_SENTINEL"}'),
])
def test_bad_synthetic_example_rejected_without_file_output(tmp_path, mutate):
    _, fixture, rp, sp = fixture_files(tmp_path)
    mutate(fixture)
    sp.write_text(json.dumps(fixture), encoding="utf-8")
    out = tmp_path / "should_not_exist.json"
    result = invoke(rp, sp, "--out", out)
    assert_refused(result)
    assert not out.exists()
    assert "SENSITIVE_TEST_SENTINEL" not in result.stdout + result.stderr
    assert "A-1" not in result.stdout
    assert str(tmp_path) not in result.stdout


@pytest.mark.parametrize("mutate", [
    lambda x: x.update(generation_allowed=True),
    lambda x: x.update(status="FRONTEND_SOURCE_GENERATED_NOT_RUNTIME_VERIFIED"),
    lambda x: x["backend"].update(runtime_verified=True),
    lambda x: x["backend"].update(response_schema_verified=True),
    lambda x: x["backend"].update(sha256="not-a-sha"),
    lambda x: x.update(bindings=None),
    lambda x: x["bindings"]["presentation"]["item"].update(name="<script>"),
    lambda x: x.update(schema_review={"status": "APPROVED"}),
])
def test_forged_static_review_not_treated_as_approval(tmp_path, mutate):
    review, fixture, rp, sp = fixture_files(tmp_path)
    mutate(review)
    rp.write_text(json.dumps(review), encoding="utf-8")
    fixture["review_sha256"] = hashlib.sha256(rp.read_bytes()).hexdigest()
    sp.write_text(json.dumps(fixture), encoding="utf-8")
    assert_refused(invoke(rp, sp))


def test_duplicate_top_level_json_key_refused(tmp_path):
    _, _, rp, sp = fixture_files(tmp_path)
    value = sp.read_text(encoding="utf-8")
    sp.write_text(value.replace('"synthetic_only": true,', '"synthetic_only": true, "synthetic_only": true,', 1),
                  encoding="utf-8")
    assert_refused(invoke(rp, sp))


def test_malformed_utf8_and_oversized_file_refused(tmp_path):
    _, _, rp, sp = fixture_files(tmp_path)
    sp.write_bytes(b"\xff\xfeUNSAFE")
    assert_refused(invoke(rp, sp))
    sp.write_bytes(b"x" * (4 * 1024 * 1024 + 1))
    assert_refused(invoke(rp, sp))


def test_same_input_path_and_directory_refused(tmp_path):
    _, _, rp, sp = fixture_files(tmp_path)
    assert_refused(invoke(rp, rp))
    assert_refused(invoke(rp, tmp_path))


def test_symlink_input_refused_when_supported(tmp_path):
    _, _, rp, sp = fixture_files(tmp_path)
    link = tmp_path / "review_link.json"
    try:
        link.symlink_to(rp)
    except (OSError, NotImplementedError):
        # Windows runner may prohibit creating symlinks; code still checks them.
        return
    assert_refused(invoke(link, sp))


def test_review_plan_is_never_mutated_on_rejected_sample(tmp_path):
    review, fixture, rp, sp = fixture_files(tmp_path)
    fixture["samples"]["metrics"]["status"] = 403
    before = copy.deepcopy(review)
    with pytest.raises(UnsafeSyntheticPreflight):
        review_synthetic_samples(
            review, fixture, review_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
    assert review == before


def test_synthetic_api_error_values_never_echoed_to_cli_result(tmp_path):
    _, fixture, rp, sp = fixture_files(tmp_path)
    fixture["samples"]["list"]["body"] = '{"api_key":"TOP_SECRET_SHOULD_NOT_APPEAR"}'
    sp.write_text(json.dumps(fixture), encoding="utf-8")
    output = invoke(rp, sp)
    assert_refused(output)
    assert "TOP_SECRET_SHOULD_NOT_APPEAR" not in output.stdout + output.stderr


@pytest.mark.parametrize("tamper", [
    lambda b: b + b" ",
    lambda b: b.replace(b"OWNER_REVIEW_REQUIRED", b"OWNER_REVIEW_REQUIREX"),
    lambda b: b.replace(b'"generation_allowed": false', b'"generation_allowed": true'),
])
def test_changed_review_bytes_refused_even_if_semantically_equivalent(tmp_path, tamper):
    _, _, rp, sp = fixture_files(tmp_path)
    rp.write_bytes(tamper(rp.read_bytes()))
    assert_refused(invoke(rp, sp))


@pytest.mark.parametrize("tamper", [
    lambda x: x.update(review_sha256="0" * 64),
    lambda x: x.update(review_sha256=x["review_sha256"].upper()),
    lambda x: x.update(review_sha256="not-a-sha256"),
    lambda x: x.pop("review_sha256"),
    lambda x: x.update(review_schema_version="rea.frontend_bridge.v0.0"),
    lambda x: x.update(backend_sha256="0" * 64),
    lambda x: x.pop("backend_sha256"),
    lambda x: x.pop("review_schema_version"),
    lambda x: x.update(schema_version="rea.synthetic_response_samples.v0.1"),
])
def test_wrong_review_identity_version_or_legacy_envelope_refused(tmp_path, tamper):
    _, fixture, rp, sp = fixture_files(tmp_path)
    tamper(fixture)
    sp.write_text(json.dumps(fixture), encoding="utf-8")
    assert_refused(invoke(rp, sp))


def test_other_valid_review_with_same_roles_is_not_interchangeable(tmp_path):
    _, fixture, rp, sp = fixture_files(tmp_path)
    original = rp.read_bytes()
    changed = json.loads(original)
    changed["backend"]["sha256"] = "a" * 64
    rp.write_text(json.dumps(changed), encoding="utf-8")
    assert_refused(invoke(rp, sp))
    # Updating only the file fingerprint does not override the binding to the
    # exact reviewed backend SHA.
    fixture["review_sha256"] = hashlib.sha256(rp.read_bytes()).hexdigest()
    sp.write_text(json.dumps(fixture), encoding="utf-8")
    assert_refused(invoke(rp, sp))


def test_review_digest_matches_exact_file_not_reparsed_canonical_object(tmp_path):
    _, fixture, rp, sp = fixture_files(tmp_path)
    # Whitespace is part of the exact source artifact.
    rp.write_text(json.dumps(json.loads(rp.read_text()), indent=2), encoding="utf-8")
    assert_refused(invoke(rp, sp))
    fixture["review_sha256"] = hashlib.sha256(rp.read_bytes()).hexdigest()
    sp.write_text(json.dumps(fixture), encoding="utf-8")
    assert invoke(rp, sp).returncode == 0


def test_review_and_sample_source_are_read_only_when_digest_check_fails(tmp_path):
    _, fixture, rp, sp = fixture_files(tmp_path)
    original = rp.read_bytes()
    fixture["review_sha256"] = "f" * 64
    sp.write_text(json.dumps(fixture), encoding="utf-8")
    before = (rp.read_bytes(), sp.read_bytes())
    report = tmp_path / "never_write_report.json"
    assert_refused(invoke(rp, sp, "--out", report))
    assert (rp.read_bytes(), sp.read_bytes()) == before
    assert rp.read_bytes() == original
    assert not report.exists()
