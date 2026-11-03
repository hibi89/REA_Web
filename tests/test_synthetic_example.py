"""Self-authored v0.2 example round-trip: no customer code or real HTTP."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from rea.adapter.synthetic_example import create_example, make_example, FAKE_ROWS
from rea.adapter.response_preflight import INPUT_SCHEMA


def cli(*args):
    return subprocess.run([sys.executable, *map(str, args)],
                          capture_output=True, text=True, timeout=15)


def test_example_bytes_reproducible_and_pinned_to_exact_review():
    one_review, one_samples = make_example()
    two_review, two_samples = make_example()
    assert one_review == two_review and one_samples == two_samples
    review = json.loads(one_review)
    samples = json.loads(one_samples)
    assert samples["schema_version"] == INPUT_SCHEMA
    assert samples["synthetic_only"] is True
    assert samples["review_sha256"] == hashlib.sha256(one_review).hexdigest()
    assert samples["review_schema_version"] == review["schema_version"]
    assert samples["backend_sha256"] == review["backend"]["sha256"]
    assert samples["backend_sha256"] == "e" * 64
    assert review["generation_allowed"] is False
    assert len(samples["samples"]) == 3
    assert list(samples["samples"]) == ["detail", "list", "metrics"]  # deterministic order
    assert len(FAKE_ROWS) == 2


def test_example_generated_without_side_effect_to_existing_paths(tmp_path):
    before = set(tmp_path.iterdir())
    target = tmp_path / "v02_demo"
    assert not target.exists()
    create_example(target)
    assert target.is_dir()
    assert set(p.name for p in target.iterdir()) == {"review.json", "synthetic_samples.json"}
    assert before == set()
    expected = make_example()
    assert (target / "review.json").read_bytes() == expected[0]
    assert (target / "synthetic_samples.json").read_bytes() == expected[1]


def test_real_cli_end_to_end_synthetic_preflight(tmp_path):
    target = tmp_path / "v02"
    generated = cli("-m", "rea.adapter.synthetic_example", "--out", target)
    assert generated.returncode == 0, generated.stderr
    generation_report = json.loads(generated.stdout)
    assert generation_report["status"] == "SELF_AUTHORED_SYNTHETIC_EXAMPLE_READY"
    assert generation_report["release_allowed"] is False
    assert generation_report["execution_performed"] is False
    assert generation_report["network_performed"] is False
    report_path = tmp_path / "preflight_report.json"
    result = cli("-m", "rea.adapter.response_preflight",
                 "--review", target / "review.json",
                 "--samples", target / "synthetic_samples.json",
                 "--synthetic-only", "--out", report_path)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report == json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "SYNTHETIC_PREFLIGHT_REVIEW_REQUIRED"
    assert report["sample_rows"] == 2
    assert report["generation_allowed"] is False
    assert report["release_allowed"] is False
    assert report["customer_runtime_verified"] is False
    assert report["source_rights_verified"] is False
    assert report["network_performed"] is False
    assert report["execution_performed"] is False
    for raw in ("EXAMPLE-001", "Synthetic check", "example.org",
                json.loads((target / "synthetic_samples.json").read_text())["review_sha256"],
                str(tmp_path)):
        assert raw not in result.stdout


def test_second_generation_refuses_overwrite_with_original_bytes_preserved(tmp_path):
    target = tmp_path / "example"
    create_example(target)
    before = {p.name: p.read_bytes() for p in target.iterdir()}
    failed = cli("-m", "rea.adapter.synthetic_example", "--out", target)
    assert failed.returncode == 2
    assert "example.org" not in failed.stdout + failed.stderr
    assert {p.name: p.read_bytes() for p in target.iterdir()} == before


def test_existing_empty_directory_not_replaced(tmp_path):
    target = tmp_path / "keep"
    target.mkdir()
    with pytest.raises(FileExistsError):
        create_example(target)
    assert target.is_dir()
    assert not list(target.iterdir())


def test_missing_parent_refused_without_creating_unrequested_path(tmp_path):
    target = tmp_path / "missing" / "example"
    failed = cli("-m", "rea.adapter.synthetic_example", "--out", target)
    assert failed.returncode == 2
    assert not target.parent.exists()


def test_symbolic_link_target_not_overwritten_when_supported(tmp_path):
    existing = tmp_path / "real"
    existing.mkdir()
    link = tmp_path / "alias"
    try:
        link.symlink_to(existing, target_is_directory=True)
    except (OSError, NotImplementedError):
        return
    failed = cli("-m", "rea.adapter.synthetic_example", "--out", link)
    assert failed.returncode == 2
    assert link.is_symlink()
    assert not list(existing.iterdir())


def test_changed_review_from_generated_example_denied(tmp_path):
    target = tmp_path / "fixture"
    create_example(target)
    reviewed = target / "review.json"
    reviewed.write_bytes(reviewed.read_bytes() + b" ")
    result = cli("-m", "rea.adapter.response_preflight",
                 "--review", reviewed, "--samples", target / "synthetic_samples.json",
                 "--synthetic-only")
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "SYNTHETIC_PREFLIGHT_REFUSED"


def test_modified_synthetic_metrics_are_rejected(tmp_path):
    target = tmp_path / "fixture"
    create_example(target)
    sample_path = target / "synthetic_samples.json"
    data = json.loads(sample_path.read_text(encoding="utf-8"))
    metric_record = data["samples"]["metrics"]
    metric_body = json.loads(metric_record["body"])
    metric_body["total"] = 999
    metric_record["body"] = json.dumps(metric_body)
    sample_path.write_text(json.dumps(data), encoding="utf-8")
    result = cli("-m", "rea.adapter.response_preflight", "--review",
                 target / "review.json", "--samples", sample_path, "--synthetic-only")
    assert result.returncode == 2
    assert json.loads(result.stdout)["generation_allowed"] is False


def test_no_implicit_frontend_or_backend_runtime_artifacts(tmp_path):
    target = tmp_path / "fixture"
    create_example(target)
    assert sorted(p.name for p in target.iterdir()) == ["review.json", "synthetic_samples.json"]
    assert not (target / "app.js").exists()
    assert not (target / "app.py").exists()
    assert not (target / "index.html").exists()
    assert not (target / "Dockerfile").exists()
