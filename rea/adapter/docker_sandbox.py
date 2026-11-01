"""Fail-closed Docker isolation for a reviewed SELF-AUTHORED REA synthetic bundle.

The host validates exact ZIP/extracted bytes first. Docker runs a separate
GET-only process challenge inside a network-less container. No customer ZIP
is accepted by this entrypoint, and no host-process fallback is permitted.
Docker daemon/host trust and runtime image provenance remain external gates.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import io
import hashlib
import tempfile
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
import zipfile

from rea.adapter.behavior_probe import (ALLOWED_FILES, MAX_ZIP, UnsafeProbe,
                                        _archive_and_tree, _safe_read)

SCHEMA = "rea.docker_synthetic_sandbox.v0.1"
IMAGE = re.compile(r"^[a-z0-9][a-z0-9._/-]*@sha256:[a-f0-9]{64}$")
SHA = re.compile(r"^[a-f0-9]{64}$")
MAX_SECONDS = 30
PREFIX = "REA_ISOLATED_RESULT:"
PORT = 8766


class UnsafeSandbox(ValueError):
    """Isolation, provenance, container cleanup or synthetic scope refused."""


# This script is authored by REA and runs in the pinned offline image.
# It never reads host files beyond the verified read-only /work mount.
# Response bodies and the challenge are never emitted.
CONTAINER_PROBE = r'''
import hashlib
import http.client
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time

ROOT = Path("/work")
APP = ROOT / "backend" / "app.py"
EXPECTED = sys.argv[1]
NONCE = os.environ["REA_TRUSTED_SYNTHETIC_ATTEST_TOKEN"]
PORT = 8766
MAX_BODY = 256 * 1024
statuses = {}
issues = []
count = 0

def call(key, path):
    connection = http.client.HTTPConnection("127.0.0.1", PORT, timeout=2)
    try:
        connection.request("GET", path, headers={"Accept":"application/json"})
        response = connection.getresponse()
        statuses[key] = response.status
        size = response.getheader("Content-Length")
        if response.status in (301,302,303,307,308) or (size and (not size.isdigit() or int(size)>MAX_BODY)):
            issues.append("UNSAFE_HTTP_RESPONSE")
            return None
        if (response.getheader("Content-Type") or "").split(";",1)[0].strip() != "application/json":
            issues.append("NON_JSON_RESPONSE")
            return None
        body = response.read(MAX_BODY+1)
        if len(body)>MAX_BODY:
            issues.append("OVERSIZED_RESPONSE")
            return None
        return json.loads(body.decode("utf-8"))
    except (OSError, ValueError, UnicodeError):
        issues.append("HTTP_READ_ERROR")
        return None
    finally:
        connection.close()

def field(data, name):
    return data if name=="__root__" else data.get(name) if isinstance(data,dict) else None

def check():
    global count
    if APP.is_symlink() or hashlib.sha256(APP.read_bytes()).hexdigest()!=EXPECTED:
        issues.append("SOURCE_CHANGED")
        return
    config = json.loads((ROOT/"dashboard"/"manifest.json").read_text(encoding="utf-8"))
    binding = config["bindings"]
    proc = None
    try:
        env = {"PATH":os.environ.get("PATH","/usr/local/bin:/usr/bin:/bin"),
               "PYTHONDONTWRITEBYTECODE":"1",
               "REA_TRUSTED_SYNTHETIC_ATTEST_TOKEN":NONCE}
        # Windows-hosted synthetic contract test needs system DLL paths.
        # Actual Docker Linux process has os.name == "posix".
        if os.name == "nt":
            for key in ("SYSTEMROOT","WINDIR","TEMP","TMP","USERPROFILE",
                        "APPDATA","LOCALAPPDATA"):
                if key in os.environ:
                    env[key] = os.environ[key]
        proc = subprocess.Popen([sys.executable,"-E","-B",str(ROOT/"runtime_entry.py"),
                                 "--run-trusted-synthetic","--port",str(PORT)],
                                cwd=str(ROOT),env=env,stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                                shell=False)
        matched = False
        for _ in range(80):
            if proc.poll() is not None:
                break
            con = http.client.HTTPConnection("127.0.0.1",PORT,timeout=.3)
            try:
                con.request("GET","/__rea/provenance",
                            headers={"X-REA-Synthetic-Challenge":NONCE})
                resp = con.getresponse()
                body = resp.read(4097)
                if resp.status==200 and len(body)<=4096:
                    value=json.loads(body.decode("utf-8"))
                    matched=(type(value.get("pid")) is int and value["pid"]==proc.pid
                             and value.get("source_sha256")==EXPECTED
                             and value.get("synthetic_process_challenge_verified") is True
                             and set(value)=={"pid","source_sha256","synthetic_process_challenge_verified"})
                    if matched: break
            except (OSError,ValueError,UnicodeError):
                pass
            finally:
                con.close()
            time.sleep(.1)
        if not matched:
            issues.append("CHILD_CHALLENGE_FAILED")
            return
        listing=call("list",binding["list"]["path"])
        metrics=call("metrics",binding["metrics"]["path"])
        rows=field(listing,binding["list"]["field"])
        numbers=field(metrics,binding["metrics"]["field"])
        if statuses.get("list")!=200 or not isinstance(rows,list) or not rows or len(rows)>200:
            issues.append("LIST_SHAPE_FAILURE")
            return
        count=len(rows)
        display=binding.get("presentation") or {}
        item_fields=display.get("item") or {x:x for x in ("id","name","category","status")}
        metric_fields=display.get("metrics") or {x:x for x in ("total","completed","pending")}
        ident=field(rows[0],item_fields["id"])
        if type(ident) not in (str,int) or not re_id(str(ident)):
            issues.append("INVALID_ITEM_ID")
            return
        if not isinstance(field(rows[0],item_fields["name"]),str):
            issues.append("INVALID_ITEM_NAME")
        vals=[field(numbers,metric_fields[k]) for k in ("total","completed","pending")]
        if statuses.get("metrics")!=200 or any(type(n) is not int or n<0 for n in vals) or vals[0]<count:
            issues.append("INVALID_METRICS")
        detail_binding=binding["detail"]
        placeholder="{"+detail_binding.get("path_param","job_id")+"}"
        detail_path=detail_binding["path"].replace(placeholder,str(ident))
        detail=call("detail",detail_path)
        item=field(detail,detail_binding["field"])
        if statuses.get("detail")!=200 or not isinstance(item,dict) or str(field(item,item_fields["id"]))!=str(ident):
            issues.append("INVALID_DETAIL")
        missing=detail_binding["path"].replace(placeholder,"REA_MISSING_A3F90C")
        call("missing_detail",missing)
        if statuses.get("missing_detail")!=404:
            issues.append("MISSING_DETAIL_NOT_404")
        if proc.poll() is not None:
            issues.append("CHILD_EXITED")
    finally:
        if proc is not None:
            if proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=2)
            else:
                proc.wait(timeout=1)

def re_id(value):
    import re
    return bool(re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9_.-]{0,63}",value))

try:
    check()
except Exception:
    issues.append("ISOLATED_PROBE_EXCEPTION")
print("REA_ISOLATED_RESULT:"+json.dumps({
    "status":"PASS_REVIEW_REQUIRED" if not issues and
       statuses=={"list":200,"metrics":200,"detail":200,"missing_detail":404} else "FAIL",
    "observed_statuses":statuses,"list_count_observed":count,
    "issues":sorted(set(issues))},sort_keys=True,separators=(",",":")))
sys.exit(0 if not issues and
         statuses=={"list":200,"metrics":200,"detail":200,"missing_detail":404} else 3)
'''


def _bounded_capture(argv: list[str], *, timeout: int, env: dict[str,str],
                     max_bytes: int=8192) -> subprocess.CompletedProcess:
    """Hard cap stdout/stderr RAM while a process runs, on Windows and Linux.

    The trusted host may invoke a Docker client which emits unbounded logs.
    capture_output=True followed by a size check is too late to avoid OOM.
    Byte limits apply separately; stop the child as soon as either is exceeded.
    """
    process = subprocess.Popen(
        argv, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, shell=False)
    output = [bytearray(), bytearray()]
    overflow = threading.Event()
    readers = []
    def collect(pipe, index):
        try:
            while True:
                chunk = pipe.read(4096)
                if not chunk:
                    break
                room = max_bytes-len(output[index])
                output[index].extend(chunk[:max(0,room)])
                if len(chunk) > room:
                    overflow.set()
                    break
        except (OSError, ValueError):
            overflow.set()

    try:
        for index,pipe in enumerate((process.stdout,process.stderr)):
            reader = threading.Thread(target=collect,args=(pipe,index),daemon=True)
            reader.start()
            readers.append(reader)
        deadline = time.monotonic()+timeout
        while True:
            if overflow.is_set():
                raise UnsafeSandbox("Docker output exceeded bounded receipt limit")
            if process.poll() is not None and all(not r.is_alive() for r in readers):
                break
            if time.monotonic()>=deadline:
                raise subprocess.TimeoutExpired(argv,timeout)
            time.sleep(0.01)
        if overflow.is_set():
            raise UnsafeSandbox("Docker output exceeded bounded receipt limit")
        return subprocess.CompletedProcess(
            argv,process.returncode,
            output[0].decode("utf-8",errors="replace"),
            output[1].decode("utf-8",errors="replace"))
    finally:
        if process.poll() is None:
            process.kill()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            # Never block the host indefinitely; caller must also confirm
            # daemon-side removal of the named container.
            pass
        for pipe in (process.stdout,process.stderr):
            if pipe:
                try:
                    pipe.close()
                except OSError:
                    pass
        for reader in readers:
            reader.join(timeout=0.3)


def _run(argv: list[str], *, timeout: int) -> subprocess.CompletedProcess:
    # DOCKER_CONTEXT / DOCKER_HOST / arbitrary client config cannot redirect
    # execution to a remote daemon. No shell or host-user credentials inherited.
    env = {"PATH": os.environ.get("PATH", os.defpath),
           "HOME": os.path.expanduser("~")}
    if "run" in argv:
        return _bounded_capture(argv,timeout=timeout,env=env)
    return subprocess.run(argv, env=env, stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, timeout=timeout,
                          shell=False)


def _local_docker() -> list[str]:
    binary = shutil.which("docker")
    if not binary:
        raise UnsafeSandbox("Docker CLI unavailable; no host fallback")
    endpoint = ("npipe:////./pipe/docker_engine" if os.name == "nt"
                else "unix:///var/run/docker.sock")
    return [str(Path(binary).resolve()), "--host", endpoint]


def _validate_image(docker: list[str], image: str) -> None:
    """Read-only daemon/image compatibility gate. NOT a signature or security attestation."""
    if not isinstance(image, str) or not IMAGE.fullmatch(image) or "//" in image:
        raise UnsafeSandbox("explicit trusted immutable image@sha256 required")
    try:
        server = _run(docker+["version","--format","{{json .Server}}"],timeout=7)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise UnsafeSandbox("local Docker engine preflight unavailable") from exc
    if server.returncode != 0 or len(server.stdout)>4096 or len(server.stderr)>4096:
        raise UnsafeSandbox("local Docker engine unavailable or untrusted output")
    try:
        info = json.loads(server.stdout)
    except (ValueError,UnicodeError) as exc:
        raise UnsafeSandbox("invalid local Docker server descriptor") from exc
    # This is a Linux-container-only sandbox. Windows daemon mode and unknown
    # architecture are refused rather than relying on Docker's runtime fallback.
    if (not isinstance(info,dict) or info.get("Os")!="linux"
            or info.get("Arch") not in ("amd64","arm64")):
        raise UnsafeSandbox("local Linux Docker engine/architecture required")
    try:
        result = _run(docker+["image","inspect","--format",
              "{{json .RepoDigests}}|{{json .Os}}|{{json .Architecture}}",
              image],timeout=7)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise UnsafeSandbox("local pinned image inspection unavailable") from exc
    if result.returncode != 0 or len(result.stdout)>4096 or len(result.stderr)>4096:
        raise UnsafeSandbox("pinned image absent or Docker daemon unavailable")
    try:
        parts = result.stdout.strip().split("|")
        if len(parts)!=3:
            raise ValueError("missing image platform fields")
        digests,os_name,architecture = [json.loads(part) for part in parts]
    except (ValueError, UnicodeError) as exc:
        raise UnsafeSandbox("invalid Docker image inspection") from exc
    if not isinstance(digests,list) or image not in digests:
        raise UnsafeSandbox("local image digest provenance cannot be verified")
    if os_name!="linux" or architecture!=info["Arch"]:
        raise UnsafeSandbox("pinned image OS/architecture differs from local Linux engine")


@contextmanager
def _verified_synthetic_mount(bundle_zip: Path, expected_sha256: str):
    """Create an exact, temporary, non-root-readable copy of the approved fixture.

    Never chmod the original owner extraction. Docker's UID 65534 cannot
    traverse typical Python TemporaryDirectory 0700 parents on Linux.
    Synthetic test assets only: the temporary 0755/0644 view is NOT suitable
    for confidential customer data. Always delete after container cleanup.
    """
    try:
        data = _safe_read(Path(bundle_zip), MAX_ZIP)
    except UnsafeProbe as exc:
        raise UnsafeSandbox("source ZIP changed before isolated mount") from exc
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise UnsafeSandbox("source ZIP digest changed before isolated mount")
    with tempfile.TemporaryDirectory(prefix="rea-synthetic-mount-") as temporary:
        root = Path(temporary)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for name in archive.namelist():
                if name not in ALLOWED_FILES or name.startswith("/") or ".." in Path(name).parts:
                    raise UnsafeSandbox("unsafe isolated fixture inventory")
                parts = name.split("/")
                member = root.joinpath(*parts)
                member.parent.mkdir(parents=True, exist_ok=True)
                member.parent.chmod(0o755)
                with member.open("xb") as out:
                    out.write(archive.read(name))
                member.chmod(0o644)
        root.chmod(0o755)
        try:
            # Revalidate all exact bytes, manifest, SHA256SUMS, and approved
            # frontend/backend relationship in the actual Docker mount tree.
            _archive_and_tree(bundle_zip, root, expected_sha256)
        except (UnsafeProbe, OSError, ValueError) as exc:
            raise UnsafeSandbox("staged synthetic mount integrity refused") from exc
        # TemporaryDirectory created this directory with an unpredictable
        # name; do not string-compare Windows canonical and absolute spellings
        # (8.3 aliases and case normalization can differ without a symlink).
        # Reject the actual temporary root being a symlink instead.
        if root.is_symlink():
            raise UnsafeSandbox("staged Docker mount root is a symlink")
        canonical = root.resolve(strict=True)
        if not canonical.is_dir() or any(
                c in str(canonical) for c in (",", chr(10), chr(13))):
            raise UnsafeSandbox("unsafe staged Docker bind path")
        yield canonical


def _container_removed(docker: list[str], name: str) -> bool:
    # --rm normally removes the container. Force-remove on every exit path,
    # then confirm an empty daemon-side exact-name query.
    try:
        _run(docker+["rm","-f",name],timeout=6)
        found = _run(docker+["container","ls","-aq","--filter","name=^/"+name+"$"],timeout=6)
        return found.returncode==0 and not found.stdout.strip()
    except (OSError,subprocess.TimeoutExpired):
        return False


def isolate_trusted_synthetic(bundle_zip: Path, extracted: Path, *,
                              expected_bundle_sha256: str, image: str,
                              developer_authorized_synthetic: bool=False,
                              timeout_seconds: int=20) -> dict:
    """No customer inputs, Docker pulls, host launcher, Internet or auto-approval."""
    if developer_authorized_synthetic is not True:
        raise UnsafeSandbox("explicit self-authored synthetic authorization required")
    if type(timeout_seconds) is not int or not 3 <= timeout_seconds <= MAX_SECONDS:
        raise UnsafeSandbox("bounded execution timeout required")
    if not isinstance(expected_bundle_sha256,str) or not SHA.fullmatch(expected_bundle_sha256):
        raise UnsafeSandbox("independent full bundle SHA256 required")
    folder = Path(extracted)
    if folder.is_symlink() or not folder.is_dir():
        raise UnsafeSandbox("clean real extracted directory required")
    try:
        manifest,_ = _archive_and_tree(Path(bundle_zip),folder,expected_bundle_sha256)
    except (UnsafeProbe,OSError,ValueError) as exc:
        raise UnsafeSandbox("source ZIP/extraction integrity refused") from exc
    if manifest.get("trusted_synthetic_only") is not True:
        raise UnsafeSandbox("customer or non-synthetic source execution forbidden")
    source_sha=hashlib.sha256((folder/"backend"/"app.py").read_bytes()).hexdigest()
    docker = _local_docker()
    _validate_image(docker,image)
    name="rea-synthetic-"+secrets.token_hex(12)
    nonce=secrets.token_hex(32)
    with _verified_synthetic_mount(Path(bundle_zip), expected_bundle_sha256) as canonical:
        cmd=docker+[
        "run","--rm","--name",name,"--pull=never",
        "--network=none","--read-only","--cap-drop=ALL",
        "--security-opt=no-new-privileges:true",
        "--security-opt=seccomp=builtin",
        "--user=65534:65534","--pids-limit=32",
        "--memory=256m","--memory-swap=256m","--cpus=1",
        "--ulimit=nofile=256:256","--ipc=none",
        "--tmpfs=/tmp:rw,nosuid,nodev,noexec,size=16m,mode=1777",
        "--mount=type=bind,source="+str(canonical)+",target=/work,readonly",
        "--workdir=/work","--env=PYTHONDONTWRITEBYTECODE=1",
        "--env=REA_TRUSTED_SYNTHETIC_ATTEST_TOKEN="+nonce,
        "--entrypoint=python",image,
        "-E","-B","-c",CONTAINER_PROBE,source_sha]
        outcome = None
        failure = None
        try:
            try:
                outcome=_run(cmd,timeout=timeout_seconds)
            except (OSError,subprocess.TimeoutExpired) as exc:
                failure=UnsafeSandbox("isolated container invocation failed or timed out")
                failure.__cause__=exc
        finally:
            if not _container_removed(docker,name):
                raise UnsafeSandbox("container cleanup unverified; stop and inspect Docker host")
    if failure is not None:
        raise failure
    assert outcome is not None
    if len(outcome.stdout)>8192 or len(outcome.stderr)>8192:
        raise UnsafeSandbox("unbounded Docker output refused")
    entries=[line[len(PREFIX):] for line in outcome.stdout.splitlines() if line.startswith(PREFIX)]
    if len(entries)!=1:
        raise UnsafeSandbox("isolated verification receipt missing or duplicated")
    try:
        proof=json.loads(entries[0])
    except (ValueError,UnicodeError) as exc:
        raise UnsafeSandbox("invalid isolated receipt") from exc
    if (not isinstance(proof,dict)
            or set(proof)!={"status","observed_statuses","list_count_observed","issues"}
            or proof.get("status") not in ("PASS_REVIEW_REQUIRED","FAIL")
            or not isinstance(proof["observed_statuses"],dict)
            or not set(proof["observed_statuses"]).issubset({"list","metrics","detail","missing_detail"})
            or any(type(value) is not int or not 0 <= value <= 599
                   for value in proof["observed_statuses"].values())
            or not isinstance(proof["issues"],list)
            or len(proof["issues"])>20
            or any(not isinstance(x,str) or not re.fullmatch(r"[A-Z0-9_]{1,64}",x)
                   for x in proof["issues"])
            or type(proof["list_count_observed"]) is not int
            or not 0 <= proof["list_count_observed"] <= 200):
        raise UnsafeSandbox("malformed isolated verification receipt")
    if (proof["status"]=="PASS_REVIEW_REQUIRED" and (proof["issues"] or proof["observed_statuses"]!=
          {"list":200,"metrics":200,"detail":200,"missing_detail":404})):
        raise UnsafeSandbox("inconsistent isolated verification receipt")
    good=(outcome.returncode==0 and proof["status"]=="PASS_REVIEW_REQUIRED"
          and proof["issues"]==[] and proof["observed_statuses"]==
          {"list":200,"metrics":200,"detail":200,"missing_detail":404})
    if outcome.returncode not in (0,3):
        raise UnsafeSandbox("Docker or container execution failed")
    return {
        "schema_version":SCHEMA,
        "status":"ISOLATED_SYNTHETIC_PASS_REVIEW_REQUIRED" if good else "ISOLATED_SYNTHETIC_BEHAVIOR_FAILURE",
        "scope":"SELF_AUTHORED_SYNTHETIC_DOCKER_ONLY",
        "bundle_sha256":expected_bundle_sha256,
        "backend_source_sha256":manifest["original_backend_zip_sha256"],
        "image_ref":image,
        "network_disabled_by_docker_policy":True,
        "readonly_mount_and_rootfs_requested":True,
        "nonroot_capabilities_resources_bounded":True,
        "container_removed_confirmed":True,
        "kernel_isolation_independently_attested":False,
        "customer_zip_execution_authorized":False,
        "business_logic_comprehensively_verified":False,
        "generation_allowed":False,
        "observed_statuses":proof["observed_statuses"],
        "list_count_observed":proof["list_count_observed"],
        "issues":proof["issues"],
        "raw_response_data_retained":False,
    }


def main(argv: list[str] | None=None) -> int:
    p=argparse.ArgumentParser(description="REA Docker isolated SELF-AUTHORED synthetic-only verifier")
    p.add_argument("--bundle-zip",type=Path,required=True)
    p.add_argument("--extracted",type=Path,required=True)
    p.add_argument("--expected-bundle-sha256",required=True)
    p.add_argument("--image",required=True,help="preinstalled trusted image@sha256 digest")
    p.add_argument("--timeout-seconds",type=int,default=20)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--developer-authorized-synthetic",action="store_true")
    args=p.parse_args(argv)
    try:
        if args.out.exists() or args.out.is_symlink():
            raise UnsafeSandbox("output already exists")
        result=isolate_trusted_synthetic(args.bundle_zip,args.extracted,
            expected_bundle_sha256=args.expected_bundle_sha256,image=args.image,
            timeout_seconds=args.timeout_seconds,
            developer_authorized_synthetic=args.developer_authorized_synthetic)
        with args.out.open("x",encoding="utf-8") as file:
            json.dump(result,file,sort_keys=True,indent=2)
            file.write("\n")
        return 0 if result["status"]=="ISOLATED_SYNTHETIC_PASS_REVIEW_REQUIRED" else 3
    except (UnsafeSandbox,OSError) as exc:
        p.exit(2,"[REA] REFUSED: "+str(exc)+"\n")


if __name__=="__main__":
    raise SystemExit(main())
