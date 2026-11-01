"""Negative safety cases and policy-only Docker simulation; never executes a customer ZIP."""
from __future__ import annotations

import hashlib
import json
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
    return isolate_trusted_synthetic(zip_path,folder,expected_bundle_sha256=digest,
          image=IMAGE,developer_authorized_synthetic=True,**kwargs)


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
