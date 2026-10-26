"""D18 Windows CI-only fresh isolated venv: REAL Tk -> ZIP -> localhost HTTP.

The shipped creator launcher never installs dependencies, calls this script,
uploads customer files, or opens any public interface.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory

from scripts.d17_windows_fresh_venv import (
    RUNTIME_REQUIREMENTS, assert_native, run_command, stage_project,
)

STATUS = "D18_FRESH_WINDOWS_GUI_ZIP_HTTP_PASS"
PROBE = Path(__file__).resolve().parent / "d18_http_probe.py"


def execute(output: Path) -> dict:
    if os.name != "nt":
        raise RuntimeError("Native Windows required; not emulated")
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError("D18 evidence cannot overwrite an existing file")
    with TemporaryDirectory(prefix="rea-d18-fresh-win-http-") as temp:
        project = Path(temp) / "project"
        stage_project(project)  # existing D17 allowlist: no vendor, secrets or real client
        shutil.copy2(PROBE, project / "scripts" / "d18_http_probe.py")
        venv_dir = project / ".venv"
        python = venv_dir / "Scripts" / "python.exe"
        make = run_command([sys.executable, "-m", "venv", str(venv_dir)],
                           cwd=project, timeout=120)
        if make.returncode != 0 or not python.is_file():
            raise RuntimeError("Failed to create isolated native Windows venv")
        cfg = (venv_dir / "pyvenv.cfg").read_text(encoding="utf-8").lower()
        if "include-system-site-packages = false" not in cfg:
            raise RuntimeError("Windows venv is not isolated")

        def check_cmd():
            return run_command(["cmd.exe", "/d", "/c",
                                str(project / "START_REA_CREATOR.cmd"), "--check"],
                               cwd=project.parent)

        assert_native(check_cmd(), code=11, marker="[REA] MISSING_MODULES:")
        # Only this temporary CI venv gets dependencies; no owner installations.
        install = run_command([str(python), "-m", "pip", "install", "--no-input",
                               "--disable-pip-version-check", *RUNTIME_REQUIREMENTS],
                              cwd=project, timeout=180)
        if install.returncode != 0:
            raise RuntimeError("Temporary CI-only venv provisioning failed")
        assert_native(check_cmd(), code=0, marker="[REA] READY:")

        ui_folder = Path(temp) / "real-tk-evidence"
        visual = run_command([
            str(python), "-m", "scripts.d15_pair_tk_smoke",
            "--out", str(ui_folder), "--retain-synthetic-zip-for-d18",
        ], cwd=project, timeout=120)
        if visual.returncode != 0 or "ACTUAL_TK_TWO_FILE_WIDGETS_PASS" not in visual.stdout:
            raise RuntimeError("Actual fresh-venv Tk approvals and generated ZIP failed")
        gui = json.loads((ui_folder / "two_file_tk_acceptance.json").read_text(encoding="utf-8"))
        if (gui.get("status") != "ACTUAL_TK_TWO_FILE_WIDGETS_PASS"
                or gui.get("both_origins_sha_unchanged") is not True):
            raise RuntimeError("Unverified Tk source/destination evidence")

        archive = ui_folder / "synthetic_pair_d18.zip"
        if not archive.is_file():
            raise RuntimeError("Fresh Tk GUI produced no ZIP for HTTP probe")
        http_report = Path(temp) / "http-evidence.json"
        run = run_command([
            str(python), "-m", "scripts.d18_http_probe",
            "--archive", str(archive),
            "--ui-report", str(ui_folder / "two_file_tk_acceptance.json"),
            "--out", str(http_report),
        ], cwd=project, timeout=90)
        if run.returncode != 0 or "FRESH_VENV_TK_ZIP_LOCALHOST_HTTP_PASS" not in run.stdout:
            raise RuntimeError("Same-venv ZIP extraction and HTTP smoke failed")
        proof = json.loads(http_report.read_text(encoding="utf-8"))
        if (proof.get("status") != "FRESH_VENV_TK_ZIP_LOCALHOST_HTTP_PASS"
                or proof.get("binding") != "127.0.0.1"
                or proof.get("rows") != 5
                or proof.get("server_cleanup") != "CONFIRMED"
                or proof.get("temporary_extraction") != "REMOVED"
                or proof.get("commercial_clearance") != "NOT_GRANTED"):
            raise RuntimeError("HTTP/cleanup proof does not satisfy D18 contract")

        evidence = {
            "schema": "rea.d18.fresh_windows_http.ci.v1",
            "status": STATUS,
            "fresh_venv": "SYSTEM_SITE_PACKAGES_FALSE",
            "native_windows": True,
            "before_install": "MISSING_MODULES_EXIT_11",
            "ci_only_dependency_provisioning": list(RUNTIME_REQUIREMENTS),
            "after_install": "READY_EXIT_0",
            "real_tk_gui": gui["status"],
            "gui_zip_approved_append": "APPROVE_APPROVE_APPEND",
            "same_interpreter": "GUI_ZIP_HTTP_SAME_VENV",
            "http_contract": proof["status"],
            "binding": "127.0.0.1",
            "rows": 5,
            "server_cleanup": "CONFIRMED",
            "synthetic_scratch_cleanup": "CONFIRMED_ON_SUCCESSFUL_CONTEXT_EXIT",
            "human_non_developer_acceptance": "NOT_RUN",
            "customer_data": "NOT_USED",
            "commercial_clearance": "NOT_GRANTED",
        }
        # Output is path-free metadata; the ZIP exists only inside temp.
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as handle:
            json.dump(evidence, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
        return evidence


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="D18 native fresh Windows CI E2E")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        proof = execute(args.out)
    except Exception as exc:
        print("D18_FRESH_WINDOWS_NOT_VERIFIED: " + type(exc).__name__, file=sys.stderr)
        return 2
    print(json.dumps({"status": proof["status"], "rows": proof["rows"],
                      "loopback": proof["binding"], "human": "NOT_RUN"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
