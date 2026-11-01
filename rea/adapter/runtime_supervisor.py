"""Supervise a SELF-AUTHORED synthetic REA bundle and challenge its local process.

This does NOT isolate arbitrary owner code. Only the existing trusted synthetic
profile may be launched. The independent bundle digest, exact extracted files,
child process and challenge-response must all match. Process-bound challenge
reduces accidental localhost server confusion, but is not OS attestation, and
cannot defend against a privileged/same-user hostile host process.
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time

from rea.adapter.behavior_probe import UnsafeProbe, _archive_and_tree, probe_trusted_bundle

SCHEMA = "rea.supervised_runtime.v0.1"
MAX_ATTEST_RESPONSE = 4096
MAX_WAIT_SECONDS = 15


class UnsafeSupervisor(ValueError):
    """The requested run could not be safely associated with the trusted fixture."""


def _choose_loopback_port() -> int:
    """Choose a free nonprivileged loopback port; challenge handles a bind race."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        value = sock.getsockname()[1]
    if value < 1024:
        raise UnsafeSupervisor("nonprivileged loopback port unavailable")
    return value


def _attest(port: int, nonce: str, expected_pid: int, expected_source_sha: str) -> bool:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=0.6)
    try:
        conn.request("GET", "/__rea/provenance", headers={
            "X-REA-Synthetic-Challenge": nonce,
            "Accept": "application/json",
            "Cache-Control": "no-store",
        })
        resp = conn.getresponse()
        if resp.status != 200 or (resp.getheader("Content-Type") or "").split(";", 1)[0] != "application/json":
            return False
        data = resp.read(MAX_ATTEST_RESPONSE + 1)
        if len(data) > MAX_ATTEST_RESPONSE:
            return False
        value = json.loads(data.decode("utf-8"))
        return (isinstance(value, dict)
                and type(value.get("pid")) is int
                and value["pid"] == expected_pid
                and value.get("source_sha256") == expected_source_sha
                and value.get("synthetic_process_challenge_verified") is True
                and set(value) == {"pid", "source_sha256", "synthetic_process_challenge_verified"})
    except (OSError, TimeoutError, ValueError, http.client.HTTPException):
        return False
    finally:
        conn.close()


def _minimal_environment(nonce: str) -> dict[str, str]:
    # Preserve native Python/DLL/system paths only, not arbitrary Python/env hooks.
    allowed = {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "HOME", "USERPROFILE",
               "APPDATA", "LOCALAPPDATA",
               "LANG", "LC_ALL", "LC_CTYPE"}
    env = {k: v for k, v in os.environ.items() if k.upper() in allowed}
    env["REA_TRUSTED_SYNTHETIC_ATTEST_TOKEN"] = nonce
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def supervise_trusted_synthetic(bundle_zip: Path, extracted: Path, *,
                                expected_bundle_sha256: str,
                                developer_authorized_synthetic: bool = False,
                                timeout_seconds: int = 10) -> dict:
    """Start and stop only a checked local synthetic server; record no response values.

    Does not download dependencies, run arbitrary ZIPs, open external networks,
    change production, or execute state-changing API calls. The child is not a
    sandbox, so the trusted self-authored restriction remains mandatory.
    """
    if developer_authorized_synthetic is not True:
        raise UnsafeSupervisor("explicit trusted synthetic authorization required")
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= MAX_WAIT_SECONDS:
        raise UnsafeSupervisor("bounded timeout required")
    source = Path(bundle_zip)
    folder = Path(extracted)
    # Full inventory, SHA256SUMS, source approval and frontend bindings before start.
    try:
        manifest, _ = _archive_and_tree(source, folder, expected_bundle_sha256)
    except (UnsafeProbe, OSError) as exc:
        raise UnsafeSupervisor("trusted synthetic bundle integrity refused") from exc
    if manifest.get("trusted_synthetic_only") is not True:
        raise UnsafeSupervisor("non-synthetic code execution denied")
    runner = folder / "runtime_entry.py"
    if runner.is_symlink() or not runner.is_file():
        raise UnsafeSupervisor("trusted runtime entry missing")
    expected_app_sha = hashlib.sha256((folder / "backend" / "app.py").read_bytes()).hexdigest()
    port = _choose_loopback_port()
    nonce = secrets.token_hex(32)
    process = None
    try:
        process = subprocess.Popen(
            [sys.executable, "-E", "-B", str(runner), "--run-trusted-synthetic", "--port", str(port)],
            cwd=str(folder), env=_minimal_environment(nonce), stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            shell=False,
        )
        deadline = time.monotonic() + timeout_seconds
        attested = False
        while time.monotonic() < deadline:
            if process.poll() is not None:
                break
            if _attest(port, nonce, process.pid, expected_app_sha):
                attested = True
                break
            time.sleep(0.10)
        if not attested:
            raise UnsafeSupervisor("synthetic child identity challenge failed or timed out")
        result = probe_trusted_bundle(
            source, folder, expected_bundle_sha256=expected_bundle_sha256,
            port=port, developer_authorized_synthetic=True,
        )
        if process.poll() is not None:
            raise UnsafeSupervisor("synthetic child exited during API verification")
        return {
            "schema_version": SCHEMA,
            "status": ("SUPERVISED_SYNTHETIC_PASS_REVIEW_REQUIRED" if result["status"] == "PASS_REVIEW_REQUIRED"
                       else "SYNTHETIC_BEHAVIOR_FAILURE"),
            "scope": "SELF_AUTHORED_SYNTHETIC_LOCAL_ONLY",
            "bundle_sha256": expected_bundle_sha256,
            "backend_source_sha256": manifest["original_backend_zip_sha256"],
            "subprocess_started_by_supervisor": True,
            "child_pid_challenge_matched": True,
            "runtime_listener_identity_verified_within_host_trust": True,
            "os_process_isolation_attested": False,
            "hostile_local_process_protection_attested": False,
            "customer_zip_execution_authorized": False,
            "business_logic_comprehensively_verified": False,
            "generation_allowed": False,
            "observed_statuses": result["observed_statuses"],
            "list_count_observed": result["list_count_observed"],
            "issues": result["issues"],
            "raw_response_data_retained": False,
        }
    finally:
        if process is not None:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=4)
            else:
                process.wait(timeout=1)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="REA reviewed self-authored synthetic process supervisor")
    p.add_argument("--bundle-zip", type=Path, required=True)
    p.add_argument("--extracted", type=Path, required=True)
    p.add_argument("--expected-bundle-sha256", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--developer-authorized-synthetic", action="store_true")
    args = p.parse_args(argv)
    try:
        if args.out.exists() or args.out.is_symlink():
            raise UnsafeSupervisor("report output already exists")
        result = supervise_trusted_synthetic(
            args.bundle_zip, args.extracted, expected_bundle_sha256=args.expected_bundle_sha256,
            developer_authorized_synthetic=args.developer_authorized_synthetic,
        )
        with args.out.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
        return 0 if result["status"] == "SUPERVISED_SYNTHETIC_PASS_REVIEW_REQUIRED" else 3
    except (UnsafeSupervisor, OSError) as exc:
        p.exit(2, "[REA] REFUSED: " + str(exc) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())