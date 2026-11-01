"""Behavior-level GET checks on SELF-AUTHORED fixture; uploaded ZIP never executed."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
from urllib.request import urlopen
import zipfile

import pytest

from rea.adapter.behavior_probe import UnsafeProbe, probe_trusted_bundle
from test_project_bundle import package


def fixture_bundle(tmp_path):
    archive, _ = package(tmp_path)
    clean = tmp_path / "unpacked"
    clean.mkdir()
    with zipfile.ZipFile(archive) as z:
        z.extractall(clean)
    return archive, clean, hashlib.sha256(archive.read_bytes()).hexdigest()


class _Handler(BaseHTTPRequestHandler):
    routes = {}
    observations = None

    def do_GET(self):
        self.observations.append(self.path)
        status, content, ctype = self.routes.get(self.path, (404, {"detail":"missing"}, "application/json"))
        body = (json.dumps(content, ensure_ascii=False).encode("utf-8")
                if not isinstance(content, bytes) else content)
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@contextmanager
def fake_http(*, replace=None):
    routes = {
        "/api/jobs": (200, {"items": [
            {"id":"X1","name":"Sensitive DO_NOT_SAVE","category":"audit","status":"done"},
            {"id":"X2","name":"pending","category":"quality","status":"pending"}]}, "application/json"),
        "/api/metrics": (200,{"total":2,"completed":1,"pending":1},"application/json"),
        "/api/jobs/X1": (200,{"id":"X1","name":"Sensitive DO_NOT_SAVE","category":"audit","status":"done"}, "application/json"),
        "/api/jobs/REA_MISSING_A3F90C": (404,{"detail":"missing"}, "application/json"),
    }
    routes.update(replace or {})
    class Handler(_Handler):
        pass
    Handler.routes = routes
    Handler.observations = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_port, Handler.observations
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def probe(bundle, port, **kw):
    archive, clean, digest = bundle
    return probe_trusted_bundle(archive, clean, expected_bundle_sha256=digest,
                                port=port, developer_authorized_synthetic=True,**kw)


def test_actual_extract_and_local_source_sha(tmp_path):
    bundle=fixture_bundle(tmp_path)
    with fake_http() as (port, called):
        review=probe(bundle,port)
    assert review["status"] == "PASS_REVIEW_REQUIRED"
    assert review["bundle_and_extracted_bytes_match"] is True
    assert review["runtime_process_identity_attested"] is False
    assert review["raw_response_data_retained"] is False
    assert review["list_count_observed"] == 2
    assert review["observed_statuses"] == {"list":200,"metrics":200,"detail":200,"missing_detail":404}
    assert review["issues"] == []
    assert called == ["/api/jobs","/api/metrics","/api/jobs/X1","/api/jobs/REA_MISSING_A3F90C"]
    assert "DO_NOT_SAVE" not in json.dumps(review)


def test_refuse_without_developer_authorization_before_http(tmp_path):
    b=fixture_bundle(tmp_path)
    with fake_http() as (port, called):
        with pytest.raises(UnsafeProbe,match="authorization"):
            probe_trusted_bundle(b[0],b[1],expected_bundle_sha256=b[2],port=port)
        assert called == []


def test_refuse_bad_independent_digest_before_http(tmp_path):
    b=fixture_bundle(tmp_path)
    with fake_http() as (port, called):
        with pytest.raises(UnsafeProbe,match="digest"):
            probe_trusted_bundle(b[0],b[1],expected_bundle_sha256="0"*64,
                                 port=port,developer_authorized_synthetic=True)
        assert called == []


def test_refuse_tampered_file_before_http(tmp_path):
    b=fixture_bundle(tmp_path)
    (b[1]/"dashboard/app.js").write_bytes((b[1]/"dashboard/app.js").read_bytes()+b"\nINJECT")
    with fake_http() as (port, called):
        with pytest.raises(UnsafeProbe,match="size cap|mismatch"):
            probe(b,port)
        assert called == []


def test_refuse_injected_file_before_http(tmp_path):
    b=fixture_bundle(tmp_path)
    (b[1]/"backend/evil.py").write_text("print('bad')")
    with fake_http() as (port, called):
        with pytest.raises(UnsafeProbe,match="unexpected"):
            probe(b,port)
        assert called == []


def test_refuse_symlink_before_http(tmp_path):
    b=fixture_bundle(tmp_path)
    file=b[1]/"dashboard/app.js"; target=tmp_path/"real.js"
    file.rename(target)
    try: file.symlink_to(target)
    except OSError: pytest.skip("local platform denies symlink")
    with fake_http() as (port, called):
        with pytest.raises(UnsafeProbe,match="symlink"):
            probe(b,port)
        assert called == []


def test_bad_port_type_and_privileged_port(tmp_path):
    b=fixture_bundle(tmp_path)
    for invalid in (None, True, "8766", 80, 65536, -1):
        with pytest.raises(UnsafeProbe,match="port"):
            probe(b,invalid)


@pytest.mark.parametrize("replacement,expected_issue",[
    ({"/api/jobs":(503,{"message":"offline"},"application/json")}, "LIST_UNEXPECTED_HTTP_STATUS"),
    ({"/api/jobs":(200,b"notjson", "application/json")}, "LIST_INVALID_JSON"),
    ({"/api/jobs":(200,{"items":[]}, "application/json")}, "LIST_UNSUPPORTED_SHAPE_OR_SIZE"),
    ({"/api/jobs":(200,{"items":[{"id":"X1","name":"a"}]}, "application/json")}, "LIST_ITEM_DISPLAY_FIELDS_MISSING"),
    ({"/api/jobs":(302,b"", "text/plain")}, "LIST_REDIRECT_DENIED"),
    ({"/api/jobs":(200,b"<h1>secret</h1>", "text/html")}, "LIST_NON_JSON_RESPONSE"),
    ({"/api/jobs":(200,b"x"* (256*1024+3), "application/json")}, "LIST_RESPONSE_TOO_LARGE"),
    ({"/api/metrics":(200,{"total":"2","completed":1,"pending":1}, "application/json")}, "METRICS_INVALID_COUNTS"),
    ({"/api/metrics":(200,{"total":1,"completed":1,"pending":1}, "application/json")}, "METRICS_INCONSISTENT_TOTAL"),
    ({"/api/jobs/X1":(200,{"id":"X2","name":"x","category":"x","status":"x"}, "application/json")}, "DETAIL_ID_MISMATCH"),
    ({"/api/jobs/REA_MISSING_A3F90C":(200,{"id":"REA_MISSING_A3F90C"}, "application/json")}, "MISSING_DETAIL_UNEXPECTED_HTTP_STATUS"),
])
def test_fail_closed_for_bad_api_behavior(tmp_path,replacement,expected_issue):
    b=fixture_bundle(tmp_path)
    with fake_http(replace=replacement) as (port,_):
        result=probe(b,port)
    assert result["status"]=="FAIL"
    assert expected_issue in result["issues"]
    assert "secret" not in json.dumps(result).lower()
    assert result["generation_allowed"] is False


def test_local_server_unreachable_returns_sanitized_failure(tmp_path):
    b=fixture_bundle(tmp_path)
    with socket.socket() as s:
        s.bind(("127.0.0.1",0)); port=s.getsockname()[1]
    result=probe(b,port)
    assert result["status"]=="FAIL"
    assert "LIST_LOCAL_HTTP_UNREACHABLE" in result["issues"]


def test_cli_never_overwrites(tmp_path):
    b=fixture_bundle(tmp_path)
    out=tmp_path/"review.json"
    cmd=[sys.executable,"-m","rea.adapter.behavior_probe","--bundle-zip",str(b[0]),"--extracted",str(b[1]),
         "--expected-bundle-sha256",b[2],"--port","8766","--out",str(out)]
    p=subprocess.run(cmd,text=True,capture_output=True)
    assert p.returncode==2 and not out.exists()
    with fake_http() as (port,called):
        cmd[cmd.index("--port")+1]=str(port)
        p=subprocess.run(cmd+["--developer-authorized-synthetic"],text=True,capture_output=True)
        assert p.returncode==0,p.stderr
        old=out.read_bytes()
        p=subprocess.run(cmd+["--developer-authorized-synthetic"],text=True,capture_output=True)
        assert p.returncode==2 and out.read_bytes()==old
        assert len(called)==4


def test_actual_approved_runner_live_http_end_to_end(tmp_path):
    """Trusted authored fixture only; not an arbitrary user backend execution."""
    b=fixture_bundle(tmp_path)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1",0)); port=sock.getsockname()[1]
    process=subprocess.Popen([sys.executable,"runtime_entry.py","--run-trusted-synthetic","--port",str(port)],
                             cwd=b[1],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
    try:
        for _ in range(80):
            if process.poll() is not None:
                raise AssertionError("trusted synthetic fixture exited early")
            try:
                with urlopen(f"http://127.0.0.1:{port}/api/jobs",timeout=.5) as r:
                    if r.status==200: break
            except OSError:
                time.sleep(.1)
        else: pytest.fail("trusted fixture localhost unavailable")
        result=probe(b,port)
        assert result["status"]=="PASS_REVIEW_REQUIRED",result
    finally:
        process.terminate()
        try:process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill(); process.communicate(timeout=5)
