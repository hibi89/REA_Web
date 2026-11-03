"""D17 developer-CI-only native Windows *fresh* isolated venv first-run rehearsal.

Never called by creator launcher and never shipped as a package installer.
Installs declared runtime to temporary test venv only, not owner environment.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
# Only project source and PUBLIC synthetic fixtures are copied. No .git/.env/keys.
FIXTURES = ("qa_guided.csv", "qa_pair_extra.json")
RUNTIME_REQUIREMENTS = ("fastapi>=0.110,<1", "uvicorn>=0.27,<1", "pydantic>=2.6,<3")
STATUS = "FRESH_WINDOWS_VENV_REHEARSAL_PASS"


def stage_project(folder: Path) -> None:
    """Stage an exclusive known allowlist, never copy user or vendor contents."""
    folder = Path(folder)
    if folder.exists() or folder.is_symlink():
        raise FileExistsError("Fresh rehearsal project folder must not exist")
    folder.mkdir(parents=True, exist_ok=False)
    shutil.copy2(ROOT / "START_REA_CREATOR.cmd", folder / "START_REA_CREATOR.cmd")
    shutil.copytree(ROOT / "rea", folder / "rea",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (folder / "samples").mkdir()
    for name in FIXTURES:
        shutil.copy2(ROOT / "samples" / name, folder / "samples" / name)
    (folder / "scripts").mkdir()
    (folder / "scripts" / "__init__.py").write_text(
        '"""Synthetic-only D17 UI entrypoint."""\n', encoding="utf-8")
    shutil.copy2(ROOT / "scripts" / "d15_pair_tk_smoke.py",
                 folder / "scripts" / "d15_pair_tk_smoke.py")


def run_command(args: list[str], *, cwd: Path, timeout: int = 90) -> subprocess.CompletedProcess:
    """Run bounded child: UTF-8 for Windows diagnostics, no shell expansion."""
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    return subprocess.run(args, cwd=cwd, env=env, text=True,
                          encoding="utf-8", errors="replace",
                          capture_output=True, timeout=timeout, check=False)


def assert_native(result, *, code: int, marker: str) -> None:
    if result.returncode != code or marker not in result.stdout:
        raise RuntimeError(
            "Unexpected native CMD result expected_code=" + str(code)
            + " actual_code=" + str(result.returncode)
            + " expected_marker=" + marker
            + " observed_markers="
            + ",".join(word for word in ("MISSING_MODULES", "READY", "NO_PYTHON")
                       if word in result.stdout))


def execute(output: Path) -> dict:
    if os.name != "nt":
        raise RuntimeError("Actual Windows cmd.exe required, NOT_RUN elsewhere")
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError("Choose a NEW D17 evidence JSON file path")
    # The explicit CI workflow runs the script. Never run pip from CMD product.
    with TemporaryDirectory(prefix="rea-d17-virgin-venv-") as temp:
        project = Path(temp) / "project"
        stage_project(project)
        venv_dir = project / ".venv"
        created = run_command([sys.executable, "-m", "venv", str(venv_dir)],
                              cwd=project, timeout=120)
        if created.returncode != 0:
            raise RuntimeError("Windows test-only venv setup failed (no owner changes)")
        python = venv_dir / "Scripts" / "python.exe"
        if not python.is_file():
            raise RuntimeError("Fresh venv Python binary missing")
        cfg = (venv_dir / "pyvenv.cfg").read_text(encoding="utf-8").lower()
        if "include-system-site-packages = false" not in cfg:
            raise RuntimeError("Venv must isolate developer site packages")

        # Verify all dependencies are missing before any test-only install.
        check = run_command(["cmd.exe", "/d", "/c",
                             str(project / "START_REA_CREATOR.cmd"), "--check"],
                            cwd=project.parent)
        assert_native(check, code=11, marker="[REA] MISSING_MODULES:")
        missing = [x for x in ("fastapi", "uvicorn", "pydantic") if x in check.stdout]
        if not missing:
            raise RuntimeError("Fresh venv refused for unexpected reason")

        # Explicit developer CI provisioning of the isolated venv. This is NOT
        # part of the shipped CMD or any runtime code and touches no user Python.
        provisioned = run_command([
            str(python), "-m", "pip", "install", "--no-input",
            "--disable-pip-version-check", *RUNTIME_REQUIREMENTS
        ], cwd=project, timeout=180)
        if provisioned.returncode != 0:
            raise RuntimeError("CI-only explicit venv dependency install failed")

        ready = run_command(["cmd.exe", "/d", "/c",
                             str(project / "START_REA_CREATOR.cmd"), "--check"],
                            cwd=project.parent)
        assert_native(ready, code=0, marker="[REA] READY:")

        visual = run_command([
            str(python), "-m", "scripts.d15_pair_tk_smoke",
            "--out", str(Path(temp) / "visual-evidence"),
        ], cwd=project, timeout=120)
        if visual.returncode != 0:
            raise RuntimeError("Fresh venv real Tk pair UI smoke failed, code "
                               + str(visual.returncode))
        if "ACTUAL_TK_TWO_FILE_WIDGETS_PASS" not in visual.stdout:
            raise RuntimeError("Real Tk/ZIP proof not present")
        proof = json.loads((Path(temp) / "visual-evidence" /
                            "two_file_tk_acceptance.json").read_text(encoding="utf-8"))
        if (proof["status"] != "ACTUAL_TK_TWO_FILE_WIDGETS_PASS"
                or proof["both_origins_sha_unchanged"] is not True
                or proof["commercial_clearance"] != "NOT_GRANTED"):
            raise RuntimeError("Fresh venv UI acceptance proof is incomplete")
        receipt = {
            "schema": "rea.d17.fresh_windows_venv.ci.v1",
            "status": STATUS,
            "fresh_venv_isolation": "SYSTEM_SITE_PACKAGES_FALSE",
            "staging": "EXPLICIT_SOURCE_AND_TWO_SYNTHETIC_FIXTURES_ONLY",
            "before_install": "MISSING_MODULES_EXIT_11",
            "manual_ci_only_provisioning": list(RUNTIME_REQUIREMENTS),
            "after_install": "READY_EXIT_0",
            "native_launcher": "START_REA_CREATOR.cmd",
            "actual_two_file_tk_and_zip": proof["status"],
            "sources_preserved": True,
            "customer_data": "NOT_USED",
            "user_device": "NOT_TESTED",
            "network_for_ci_pip_only": True,
            "creator_launcher_autoinstall": False,
            "human_non_developer_acceptance": "NOT_RUN",
            "commercial_clearance": "NOT_GRANTED",
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as f:
            json.dump(receipt, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        return receipt


def main(argv=None):
    p = argparse.ArgumentParser(description="D17 CI-only fresh Windows venv proof")
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args(argv)
    try:
        outcome = execute(args.out)
    except Exception as exc:
        print("D17_FRESH_VENV_NOT_VERIFIED: " + type(exc).__name__, file=sys.stderr)
        return 2
    print(json.dumps({"status": outcome["status"], "before": outcome["before_install"],
                      "after": outcome["after_install"],
                      "gui": outcome["actual_two_file_tk_and_zip"],
                      "human_acceptance": "NOT_RUN"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
