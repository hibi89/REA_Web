"""Supervised launch only for the self-authored synthetic project fixture."""
from __future__ import annotations

import hashlib
import http.client
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

from rea.adapter import runtime_supervisor as supervisor
from rea.adapter.runtime_supervisor import UnsafeSupervisor, supervise_trusted_synthetic
from test_project_bundle import SOURCE, package
from test_behavior_probe import fake_http


def fixture(tmp_path: Path, *, source: str = SOURCE):
    z, _ = package(tmp_path, source=source)
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    with zipfile.ZipFile(z) as archive:
        archive.extractall(extracted)
    digest = hashlib.sha256(z.read_bytes()).hexdigest()
    return z, extracted, digest


def run(bundle, **kwargs):
    z, extracted, digest = bundle
    return supervise_trusted_synthetic(z, extracted, expected_bundle_sha256=digest,
                                       developer_authorized_synthetic=True, **kwargs)


def test_actual_supervised_child_challenge_and_apis(tmp_path):
    result = run(fixture(tmp_path))
    assert result["status"] == "SUPERVISED_SYNTHETIC_PASS_REVIEW_REQUIRED"
    assert result["child_pid_challenge_matched"] is True
    assert result["subprocess_started_by_supervisor"] is True
    assert result["runtime_listener_identity_verified_within_host_trust"] is True
    assert result["os_process_isolation_attested"] is False
    assert result["hostile_local_process_protection_attested"] is False
    assert result["customer_zip_execution_authorized"] is False
    assert result["generation_allowed"] is False
    assert result["raw_response_data_retained"] is False
    assert result["observed_statuses"] == {
        "list": 200, "metrics": 200, "detail": 200, "missing_detail": 404,
    }
    assert result["issues"] == [] and result["list_count_observed"] == 2
    assert "X1" not in json.dumps(result)
    assert "Synthetic task" not in json.dumps(result)


def test_refuses_without_explicit_synthetic_authorization(tmp_path, monkeypatch):
    z, folder, digest = fixture(tmp_path)
    calls = []
    monkeypatch.setattr(supervisor.subprocess, "Popen", lambda *a, **kw: calls.append(1))
    with pytest.raises(UnsafeSupervisor, match="authorization"):
        supervise_trusted_synthetic(z, folder, expected_bundle_sha256=digest)
    assert calls == []


def test_refuses_bad_digest_before_spawn(tmp_path, monkeypatch):
    z, folder, _ = fixture(tmp_path)
    calls = []
    monkeypatch.setattr(supervisor.subprocess, "Popen", lambda *a, **kw: calls.append(1))
    with pytest.raises(UnsafeSupervisor, match="integrity"):
        supervise_trusted_synthetic(z, folder, expected_bundle_sha256="0" * 64,
                                    developer_authorized_synthetic=True)
    assert calls == []


def test_refuses_modified_backend_before_spawn(tmp_path, monkeypatch):
    b = fixture(tmp_path)
    (b[1] / "backend/app.py").write_bytes(b"print('unapproved')\n")
    calls = []
    monkeypatch.setattr(supervisor.subprocess, "Popen", lambda *a, **kw: calls.append(1))
    with pytest.raises(UnsafeSupervisor, match="integrity"):
        run(b)
    assert calls == []


def test_refuses_injected_py_or_symlink_before_spawn(tmp_path, monkeypatch):
    b = fixture(tmp_path)
    (b[1] / "backend/injected.py").write_text("print('unapproved')")
    calls = []
    monkeypatch.setattr(supervisor.subprocess, "Popen", lambda *a, **kw: calls.append(1))
    with pytest.raises(UnsafeSupervisor, match="integrity"):
        run(b)
    assert calls == []


def test_rejects_other_local_server_even_if_it_returns_fixture_api(tmp_path, monkeypatch):
    b = fixture(tmp_path)
    with fake_http() as (hijacked_port, calls):
        monkeypatch.setattr(supervisor, "_choose_loopback_port", lambda: hijacked_port)
        with pytest.raises(UnsafeSupervisor, match="identity challenge"):
            run(b, timeout_seconds=1)
    assert "/__rea/provenance" in calls


def test_sampled_payload_failure_is_not_success(tmp_path):
    # The source still declares the same routes, but the payload has incorrect type.
    altered = SOURCE.replace('"total":2,"completed":1,"pending":1',
                             '"total":"broken","completed":1,"pending":1')
    assert altered != SOURCE
    result = run(fixture(tmp_path, source=altered))
    assert result["status"] == "SYNTHETIC_BEHAVIOR_FAILURE"
    assert "METRICS_INVALID_COUNTS" in result["issues"]
    assert result["child_pid_challenge_matched"] is True
    assert result["generation_allowed"] is False


@pytest.mark.parametrize("timeout", [0, True, 16, 1.2])
def test_bad_wait_limits_rejected(tmp_path,timeout):
    with pytest.raises(UnsafeSupervisor, match="timeout"):
        run(fixture(tmp_path), timeout_seconds=timeout)


def test_environment_scrubs_python_hooks_and_secrets(monkeypatch):
    monkeypatch.setenv("PYTHONPATH", "/tmp/UNAPPROVED")
    monkeypatch.setenv("PYTHONSTARTUP", "/tmp/startup")
    monkeypatch.setenv("GITHUB_TOKEN", "TOP_SECRET")
    d=supervisor._minimal_environment("f" * 64)
    assert all(x not in d for x in ("PYTHONPATH", "PYTHONSTARTUP", "GITHUB_TOKEN"))
    assert d["REA_TRUSTED_SYNTHETIC_ATTEST_TOKEN"] == "f" * 64
    assert d["PYTHONDONTWRITEBYTECODE"] == "1"


def test_child_process_cleanup_after_success(tmp_path, monkeypatch):
    actual = supervisor.subprocess.Popen
    spawned = []
    def recorded(*args, **kwargs):
        proc = actual(*args, **kwargs)
        spawned.append(proc)
        return proc
    monkeypatch.setattr(supervisor.subprocess, "Popen", recorded)
    result = run(fixture(tmp_path))
    assert result["status"] == "SUPERVISED_SYNTHETIC_PASS_REVIEW_REQUIRED"
    assert len(spawned) == 1 and spawned[0].poll() is not None
    assert spawned[0].returncode is not None


def test_cli_no_overwrite_and_secret_free_report(tmp_path):
    b = fixture(tmp_path)
    out = tmp_path / "review.json"
    args = [sys.executable, "-m", "rea.adapter.runtime_supervisor", "--bundle-zip", str(b[0]),
            "--extracted", str(b[1]), "--expected-bundle-sha256", b[2],
            "--out", str(out), "--developer-authorized-synthetic"]
    first = subprocess.run(args, capture_output=True, text=True, timeout=30)
    assert first.returncode == 0, first.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "SUPERVISED_SYNTHETIC_PASS_REVIEW_REQUIRED"
    previous = out.read_bytes()
    second = subprocess.run(args, capture_output=True, text=True, timeout=15)
    assert second.returncode == 2 and out.read_bytes() == previous
    assert "REA_TRUSTED_SYNTHETIC_ATTEST_TOKEN" not in previous.decode("utf-8")


def test_manual_runner_does_not_expose_attestation_endpoint(tmp_path):
    # An ordinary --run-trusted-synthetic launch (without supervisor nonce)
    # must not enable the process challenge interface.
    z, folder, _ = fixture(tmp_path)
    port = supervisor._choose_loopback_port()
    proc = subprocess.Popen([sys.executable, "-E", "-B", str(folder / "runtime_entry.py"),
                             "--run-trusted-synthetic", "--port", str(port)],
                            cwd=folder, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        import time
        deadline = time.monotonic() + 8
        status = None
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                break
            try:
                c = http.client.HTTPConnection("127.0.0.1", port, timeout=.6)
                c.request("GET", "/__rea/provenance")
                r = c.getresponse()
                status = r.status
                r.read()
                c.close()
                break
            except OSError:
                time.sleep(.1)
        assert status == 404
    finally:
        if proc.poll() is None:
            proc.terminate()
            try: proc.wait(timeout=4)
            except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=4)