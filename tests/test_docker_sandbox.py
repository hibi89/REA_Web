"""Negative safety cases and policy-only Docker simulation; never executes a customer ZIP."""
from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path
import subprocess
import zipfile

import pytest

from rea.adapter import docker_sandbox as sandbox
from rea.adapter.docker_sandbox import UnsafeSandbox, isolate_trusted_synthetic
from test_runtime_supervisor import fixture

IMAGE = "example.invalid/rea-python-fastapi@sha256:" + "a" * 64
GOOD = {"status":"PASS_REVIEW_REQUIRED","observed_statuses":
        {"list":200,"metrics":200,"detail":200,"missing_detail":404},
        "list_count_observed":2,"issues":[]}


def _fake_docker(monkeypatch, receipt=GOOD, *, docker_rc=0, cleanup=True, timeout=False):
    commands=[]
    monkeypatch.setattr(sandbox,"_local_docker",lambda:["/trusted/docker","--host","unix:///var/run/docker.sock"])
    def fake_run(argv, *, timeout):
        commands.append(argv)
        if "image" in argv and "inspect" in argv:
            return subprocess.CompletedProcess(argv,0,json.dumps([IMAGE]),"")
        if "run" in argv:
            if timeout_mode:
                raise subprocess.TimeoutExpired(argv,timeout)
            out=sandbox.PREFIX+json.dumps(receipt)+"\n" if receipt is not None else ""
            return subprocess.CompletedProcess(argv,docker_rc,out,"")
        if "rm" in argv:
            return subprocess.CompletedProcess(argv,0,"","")
        if "container" in argv and "ls" in argv:
            return subprocess.CompletedProcess(argv,0,"" if cleanup else "still-running\n","")
        raise AssertionError(f"unexpected Docker call: {argv}")
    timeout_mode=timeout
    monkeypatch.setattr(sandbox,"_run",fake_run)
    return commands


def call(bundle, **kwargs):
    zip_path,folder,digest=bundle
    options={"image":IMAGE,"developer_authorized_synthetic":True}
    options.update(kwargs)
    return isolate_trusted_synthetic(zip_path,folder,expected_bundle_sha256=digest,**options)


def test_policy_argv_exact_constraints_and_clean_receipt(tmp_path,monkeypatch):
    commands=_fake_docker(monkeypatch)
    result=call(fixture(tmp_path))
    assert result["status"]=="ISOLATED_SYNTHETIC_PASS_REVIEW_REQUIRED"
    assert result["container_removed_confirmed"] is True
    assert result["customer_zip_execution_authorized"] is False
    assert result["generation_allowed"] is False
    assert result["kernel_isolation_independently_attested"] is False
    assert result["raw_response_data_retained"] is False
    assert "X1" not in json.dumps(result)
    argv=next(c for c in commands if "run" in c)
    for must in ("--rm","--pull=never","--network=none","--read-only",
                 "--cap-drop=ALL","--security-opt=no-new-privileges:true",
                 "--security-opt=seccomp=builtin",
                 "--user=65534:65534","--pids-limit=32","--memory=256m",
                 "--memory-swap=256m","--cpus=1","--ipc=none",
                 "--ulimit=nofile=256:256"):
        assert must in argv
    assert any(x.startswith("--mount=type=bind,") and x.endswith(",target=/work,readonly") for x in argv)
    assert IMAGE in argv
    assert "--privileged" not in argv and "--publish" not in argv and "-p" not in argv
    assert not any(x.startswith("--network=host") for x in argv)
    assert commands[-2][-3]=="rm" or "rm" in commands[-2]
    assert "container" in commands[-1] and "ls" in commands[-1]


def test_authorization_refused_before_any_docker_or_zip_execution(tmp_path,monkeypatch):
    monkeypatch.setattr(sandbox,"_local_docker",lambda:pytest.fail("Docker should not be reached"))
    zip_path,folder,digest=fixture(tmp_path)
    with pytest.raises(UnsafeSandbox,match="authorization"):
        isolate_trusted_synthetic(zip_path,folder,expected_bundle_sha256=digest,image=IMAGE)
    with pytest.raises(UnsafeSandbox,match="SHA256"):
        isolate_trusted_synthetic(zip_path,folder,expected_bundle_sha256="bad",image=IMAGE,
                                  developer_authorized_synthetic=True)


def test_tampered_tree_refused_before_docker(tmp_path,monkeypatch):
    b=fixture(tmp_path)
    (b[1]/"backend/app.py").write_text("print('tampered')",encoding="utf-8")
    monkeypatch.setattr(sandbox,"_local_docker",lambda:pytest.fail("Docker should not start"))
    with pytest.raises(UnsafeSandbox,match="integrity"):
        call(b)


@pytest.mark.parametrize("image",["python:3.11","sha256:"+"a"*64,
   "example.invalid/rea:latest","--privileged@sha256:"+"a"*64,
   "example.invalid/rea@sha256:"+"B"*64,
   "example.invalid//rea@sha256:"+"a"*64])
def test_unpinned_or_malformed_image_denied(tmp_path,monkeypatch,image):
    b=fixture(tmp_path)
    commands=_fake_docker(monkeypatch)
    with pytest.raises(UnsafeSandbox,match="image"):
        call(b,image=image)
    assert not any("run" in c for c in commands)


def test_missing_image_digest_in_local_inspect_refused(tmp_path,monkeypatch):
    b=fixture(tmp_path)
    commands=[]
    monkeypatch.setattr(sandbox,"_local_docker",lambda:["/trusted/docker","--host","unix:///var/run/docker.sock"])
    def response(argv,*,timeout):
        commands.append(argv)
        return subprocess.CompletedProcess(argv,0,json.dumps(["elsewhere@sha256:"+"b"*64]),"")
    monkeypatch.setattr(sandbox,"_run",response)
    with pytest.raises(UnsafeSandbox,match="digest provenance"):
        call(b)
    assert len(commands)==1


def test_behavior_failure_does_not_become_pass(tmp_path,monkeypatch):
    broken=dict(GOOD,status="FAIL",issues=["INVALID_METRICS"])
    commands=_fake_docker(monkeypatch,broken,docker_rc=3)
    result=call(fixture(tmp_path))
    assert result["status"]=="ISOLATED_SYNTHETIC_BEHAVIOR_FAILURE"
    assert result["issues"]==["INVALID_METRICS"]
    assert "rm" in commands[-2] and "container" in commands[-1]


def test_docker_timeout_forces_container_removal(tmp_path,monkeypatch):
    commands=_fake_docker(monkeypatch,timeout=True)
    with pytest.raises(UnsafeSandbox,match="timed out"):
        call(fixture(tmp_path),timeout_seconds=4)
    assert any("rm" in x for x in commands)
    assert "container" in commands[-1]


def test_unverified_cleanup_refuses_even_successful_receipt(tmp_path,monkeypatch):
    _fake_docker(monkeypatch,cleanup=False)
    with pytest.raises(UnsafeSandbox,match="cleanup unverified"):
        call(fixture(tmp_path))


@pytest.mark.parametrize("response",[
    None,{"status":"PASS_REVIEW_REQUIRED","issues":[],"list_count_observed":2,
          "observed_statuses":{"list":200}},
    {"status":"PASS_REVIEW_REQUIRED","issues":[],"list_count_observed":2,
     "observed_statuses":GOOD["observed_statuses"],"raw_data":"SHOULD_NOT_LEAK"},
])
def test_missing_forged_or_incomplete_receipt_fails_closed(tmp_path,monkeypatch,response):
    _fake_docker(monkeypatch,response)
    with pytest.raises(UnsafeSandbox,match="receipt|container"):
        call(fixture(tmp_path))


@pytest.mark.parametrize("bad",[0,1,2,True,31,10.5])
def test_invalid_timeout_does_not_start_container(tmp_path,monkeypatch,bad):
    monkeypatch.setattr(sandbox,"_local_docker",lambda:pytest.fail("Docker should not start"))
    with pytest.raises(UnsafeSandbox,match="timeout"):
        call(fixture(tmp_path),timeout_seconds=bad)


def test_cli_refuses_output_overwrite_without_touching_existing(tmp_path,monkeypatch):
    b=fixture(tmp_path)
    out=tmp_path/"review.json"
    out.write_text("KEEP",encoding="utf-8")
    args=["--bundle-zip",str(b[0]),"--extracted",str(b[1]),
          "--expected-bundle-sha256",b[2],"--image",IMAGE,
          "--out",str(out),"--developer-authorized-synthetic"]
    with pytest.raises(SystemExit) as exc:
        sandbox.main(args)
    assert exc.value.code==2
    assert out.read_text(encoding="utf-8")=="KEEP"


def _run_isolated_probe_on_trusted_host(bundle, *, replacement_source_sha=None):
    """Exercise the exact embedded container script using self-authored fixture.

    This validates Python/HTTP subprocess logic, NOT container/OS isolation.
    """
    import os
    import secrets
    import sys
    from rea.adapter.runtime_supervisor import _choose_loopback_port
    _, folder, _ = bundle
    script = sandbox.CONTAINER_PROBE
    script = script.replace('ROOT = Path("/work")', 'ROOT = Path(' + repr(str(folder)) + ')')
    script = script.replace("PORT = 8766", "PORT = " + str(_choose_loopback_port()))
    source_sha = hashlib.sha256((folder/"backend"/"app.py").read_bytes()).hexdigest()
    env = {"PATH": os.environ.get("PATH",os.defpath),
           "PYTHONDONTWRITEBYTECODE":"1",
           "REA_TRUSTED_SYNTHETIC_ATTEST_TOKEN":secrets.token_hex(32)}
    # The parent test process needs the same minimal OS-provided DLL paths
    # that the previously verified host supervisor preserves on Windows.
    for key in ("SYSTEMROOT","WINDIR","TEMP","TMP","USERPROFILE",
                "APPDATA","LOCALAPPDATA"):
        if key in os.environ:
            env[key] = os.environ[key]
    result=subprocess.run([sys.executable,"-E","-B","-c",script,
                   replacement_source_sha or source_sha],
                   cwd=folder, env=env, capture_output=True,text=True,timeout=18)
    assert len(result.stdout)<8192, "unbounded probe output"
    lines=[line for line in result.stdout.splitlines() if line.startswith(sandbox.PREFIX)]
    assert len(lines)==1, (result.returncode,result.stderr[-300:])
    return result, json.loads(lines[0][len(sandbox.PREFIX):])


def test_container_probe_python_compiles_without_docker():
    compile(sandbox.CONTAINER_PROBE, "<rea-trusted-synthetic-container-probe>", "exec")


def test_embedded_container_probe_real_synthetic_http_without_docker(tmp_path):
    result,receipt=_run_isolated_probe_on_trusted_host(fixture(tmp_path))
    assert result.returncode==0, result.stderr[-300:]
    assert receipt==GOOD
    assert "Synthetic task" not in result.stdout
    assert "X1" not in result.stdout
    assert "REA_TRUSTED_SYNTHETIC_ATTEST_TOKEN" not in result.stdout


def test_embedded_probe_source_digest_mismatch_is_fail_closed(tmp_path):
    result,receipt=_run_isolated_probe_on_trusted_host(
          fixture(tmp_path),replacement_source_sha="0"*64)
    assert result.returncode==3
    assert receipt["status"]=="FAIL"
    assert "SOURCE_CHANGED" in receipt["issues"]
    assert receipt["observed_statuses"]=={}


def test_embedded_probe_wrong_metrics_refused_on_actual_http(tmp_path):
    from test_project_bundle import SOURCE
    bad=SOURCE.replace('"total":2,"completed":1,"pending":1',
                       '"total":"broken","completed":1,"pending":1')
    assert bad!=SOURCE
    result,receipt=_run_isolated_probe_on_trusted_host(fixture(tmp_path,source=bad))
    assert result.returncode==3
    assert receipt["status"]=="FAIL"
    assert "INVALID_METRICS" in receipt["issues"]


@pytest.mark.parametrize("bad_receipt",[
    {"status":"FAIL","issues":["OK"],"list_count_observed":0,
     "observed_statuses":{"secret_auth_token":200}},
    {"status":"FAIL","issues":["OK"],"list_count_observed":0,
     "observed_statuses":{"list":True}},
    {"status":"FAIL","issues":["RAW_SECRET_VALUE=token"],"list_count_observed":0,
     "observed_statuses":{}},
    {"status":"FAIL","issues":["ERROR"]*21,"list_count_observed":0,
     "observed_statuses":{}},
])
def test_reject_untrusted_container_receipt_secret_or_unbounded_fields(
        tmp_path,monkeypatch,bad_receipt):
    _fake_docker(monkeypatch,bad_receipt,docker_rc=3)
    with pytest.raises(UnsafeSandbox,match="malformed"):
        call(fixture(tmp_path))


def test_docker_client_environment_does_not_inherit_remote_target_or_secrets(
        monkeypatch):
    monkeypatch.setenv("DOCKER_HOST","tcp://unapproved.example:2375")
    monkeypatch.setenv("DOCKER_CONTEXT","unauthorized")
    monkeypatch.setenv("DOCKER_TLS_VERIFY","1")
    monkeypatch.setenv("GITHUB_TOKEN","SECRET_VALUE")
    captured={}
    def intercept(argv, **kwargs):
        captured.update(kwargs)
        return subprocess.CompletedProcess(argv,0,"","")
    monkeypatch.setattr(sandbox.subprocess,"run",intercept)
    sandbox._run(["/fixed/docker","version"],timeout=3)
    assert captured["shell"] is False
    assert captured["timeout"]==3
    assert captured["stdin"]==subprocess.DEVNULL
    assert captured["env"].keys() <= {"PATH","HOME"}
    assert not any(x in captured["env"] for x in
                   ("DOCKER_HOST","DOCKER_CONTEXT","DOCKER_TLS_VERIFY",
                    "GITHUB_TOKEN"))


def test_original_private_directory_is_unchanged_and_docker_uses_clean_staging(
        tmp_path, monkeypatch):
    bundle = fixture(tmp_path)
    extracted = bundle[1]
    extracted.chmod(0o700)
    old_mode = stat.S_IMODE(extracted.stat().st_mode)
    source_before = (extracted / "backend" / "app.py").read_bytes()
    _fake_docker(monkeypatch)
    real_run = sandbox._run
    stage_seen = []
    def inspect(argv, *, timeout):
        if "run" in argv:
            mount = next(x for x in argv if x.startswith("--mount=type=bind,"))
            staged = Path(mount.split("source=",1)[1].split(",target=/work,readonly",1)[0])
            stage_seen.append(staged)
            assert staged != extracted
            assert staged.is_dir()
            assert (staged/"backend"/"app.py").read_bytes() == source_before
            assert set(p.relative_to(staged).as_posix() for p in staged.rglob("*") if p.is_file()) == (
                set(p.relative_to(extracted).as_posix() for p in extracted.rglob("*") if p.is_file()))
            if os.name != "nt":
                assert stat.S_IMODE(staged.stat().st_mode) == 0o755
                assert stat.S_IMODE((staged/"backend").stat().st_mode) == 0o755
                assert stat.S_IMODE((staged/"backend"/"app.py").stat().st_mode) == 0o644
        return real_run(argv, timeout=timeout)
    monkeypatch.setattr(sandbox, "_run", inspect)
    assert call(bundle)["status"] == "ISOLATED_SYNTHETIC_PASS_REVIEW_REQUIRED"
    assert stage_seen and not stage_seen[0].exists()
    assert stat.S_IMODE(extracted.stat().st_mode) == old_mode
    assert (extracted/"backend"/"app.py").read_bytes() == source_before


@pytest.mark.parametrize("simulation", ["timeout","negative_response","cleanup_failed"])
def test_staged_source_removed_even_on_failure(tmp_path, monkeypatch, simulation):
    bundle = fixture(tmp_path)
    _fake_docker(monkeypatch, timeout=simulation=="timeout",
                 cleanup=simulation!="cleanup_failed",
                 receipt=GOOD if simulation!="negative_response" else
                     dict(GOOD, status="FAIL", issues=["INVALID_METRICS"]),
                 docker_rc=3 if simulation=="negative_response" else 0)
    old = sandbox._run
    paths = []
    def capture(argv, *, timeout):
        if "run" in argv:
            paths.append(Path(next(x for x in argv if x.startswith("--mount=type=bind,"))
                              .split("source=",1)[1].split(",target=/work,readonly",1)[0]))
        return old(argv,timeout=timeout)
    monkeypatch.setattr(sandbox,"_run",capture)
    if simulation == "negative_response":
        assert call(bundle)["status"] == "ISOLATED_SYNTHETIC_BEHAVIOR_FAILURE"
    else:
        with pytest.raises(UnsafeSandbox,match="timed out|cleanup unverified"):
            call(bundle,timeout_seconds=4)
    assert len(paths)==1 and not paths[0].exists()
