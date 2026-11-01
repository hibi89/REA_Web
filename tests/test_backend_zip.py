"""Static ZIP contract checks: positive fixture, attack boundaries and no code execution."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import stat
import subprocess
import sys
import zipfile

import pytest
from rea.adapter.backend_zip import UnsafeBackendZip, inspect_backend_zip

FIXTURE = '''from fastapi import FastAPI, HTTPException
app = FastAPI(title="Fixture")
@app.get("/api/health")
def health(): return {"ok": True}
@app.get("/api/jobs")
def jobs(): return []
@app.get("/api/jobs/{job_id}")
def detail(job_id: str): return job_id
@app.get("/api/metrics")
def metrics(): return {}
@app.post("/api/preview")
def preview(): return {}
'''


def archive(path: Path, files: dict[str, str | bytes]) -> Path:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, contents in files.items():
            z.writestr(name, contents)
    return path


def test_endpoints_and_hash_deterministic(tmp_path):
    z = archive(tmp_path / "backend.zip", {"app.py": FIXTURE, "README.md": "safe"})
    a = inspect_backend_zip(z)
    assert a == inspect_backend_zip(z)
    assert a["input"] == {"sha256": hashlib.sha256(z.read_bytes()).hexdigest(), "members": 2, "python_files": 1}
    assert a["status"] == "REVIEW_REQUIRED" and a["generation_allowed"] is False
    assert a["execution_performed"] is False
    assert a["framework_hints"] == ["FastAPI"]
    assert {(e["path"], tuple(e["methods"])) for e in a["api"]["endpoints"]} == {
        ("/api/health", ("GET",)), ("/api/jobs", ("GET",)),
        ("/api/jobs/{job_id}", ("GET",)), ("/api/metrics", ("GET",)),
        ("/api/preview", ("POST",)),
    }
    assert all(e["verification"] == "STATIC_DECLARATION_ONLY" for e in a["api"]["endpoints"])


def test_never_executes_code(tmp_path):
    marker = tmp_path / "MUST_NOT_EXIST.txt"
    body = "from fastapi import FastAPI\napp=FastAPI()\n" + f"open({str(marker)!r}, 'w').write('bad')\n" + '@app.get("/ok")\ndef ok(): return True\n'
    z = archive(tmp_path / "backend.zip", {"app.py": body})
    assert inspect_backend_zip(z)["api"]["declared_endpoint_count"] == 1
    assert not marker.exists()


@pytest.mark.parametrize("name", ["../escape.py", "dir/../escape.py", "/abs/app.py", "C:/windows.py", "bad\\app.py", "./app.py", "a//b.py"])
def test_unsafe_member_path_rejected(tmp_path, name):
    z = archive(tmp_path / "bad.zip", {name: FIXTURE})
    with pytest.raises(UnsafeBackendZip): inspect_backend_zip(z)


def test_duplicate_member_rejected(tmp_path):
    z = tmp_path / "bad.zip"
    with zipfile.ZipFile(z, "w") as out:
        out.writestr("app.py", FIXTURE)
        out.writestr("app.py", FIXTURE)
    with pytest.raises(UnsafeBackendZip): inspect_backend_zip(z)


def test_symlink_member_rejected(tmp_path):
    z = tmp_path / "bad.zip"
    with zipfile.ZipFile(z, "w") as out:
        info = zipfile.ZipInfo("app.py")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        out.writestr(info, "target")
    with pytest.raises(UnsafeBackendZip): inspect_backend_zip(z)


def test_symbolic_link_source_rejected(tmp_path):
    z = archive(tmp_path / "backend.zip", {"app.py": FIXTURE})
    link = tmp_path / "link.zip"
    link.symlink_to(z)
    with pytest.raises(UnsafeBackendZip): inspect_backend_zip(link)


def test_no_api_from_comments_or_strings(tmp_path):
    body = '# @app.get("/not-real")\nx="@app.get(\\"/fake\\")"\n'
    z = archive(tmp_path / "backend.zip", {"app.py": body})
    assert inspect_backend_zip(z)["api"]["endpoints"] == []


def test_api_router_static_mount(tmp_path):
    body = '''from fastapi import FastAPI, APIRouter
app=FastAPI()
r=APIRouter(prefix="/api")
@r.api_route("/items", methods=["GET", "POST"])
def items(): pass
app.include_router(r, prefix="/v1")
'''
    z = archive(tmp_path / "backend.zip", {"app.py": body})
    e = inspect_backend_zip(z)["api"]["endpoints"][0]
    assert e["path"] == "/v1/api/items" and e["methods"] == ["GET", "POST"]
    assert e["mount"] == "local_router_mount_declaration"


def test_unmounted_router_not_marked_reachable(tmp_path):
    body = '''from fastapi import APIRouter
r=APIRouter(prefix="/api")
@r.post("/not-mounted")
def f(): pass
'''
    z = archive(tmp_path / "backend.zip", {"app.py": body})
    assert inspect_backend_zip(z)["api"]["endpoints"][0]["mount"] == "router_mount_unverified"


def test_dynamic_route_is_unresolved_not_guessed(tmp_path):
    body = '''from fastapi import FastAPI
app=FastAPI()
ROOT="/api"
@app.get(ROOT + "/something")
def f(): pass
'''
    z = archive(tmp_path / "backend.zip", {"app.py": body})
    result = inspect_backend_zip(z)
    assert result["api"]["endpoints"] == [] and result["api"]["unresolved_declarations"] == 1


def test_reject_file_and_total_size_limit(tmp_path):
    z = archive(tmp_path / "backend.zip", {"app.py": "x" * (2 * 1024 * 1024 + 1)})
    with pytest.raises(UnsafeBackendZip): inspect_backend_zip(z)


def test_bad_zip_rejected(tmp_path):
    z = tmp_path / "backend.zip"
    z.write_bytes(b"not a zip")
    with pytest.raises(UnsafeBackendZip): inspect_backend_zip(z)


def test_cli_json_and_no_overwrite(tmp_path):
    z = archive(tmp_path / "backend.zip", {"app.py": FIXTURE})
    out = tmp_path / "contract.json"
    command = [sys.executable, "-m", "rea.adapter.backend_zip", str(z), "--out", str(out)]
    one = subprocess.run(command, text=True, capture_output=True)
    assert one.returncode == 0, one.stderr
    result = json.loads(out.read_text(encoding="utf-8"))
    assert result["api"]["declared_endpoint_count"] == 5
    before = out.read_bytes()
    two = subprocess.run(command, text=True, capture_output=True)
    assert two.returncode == 2 and out.read_bytes() == before
