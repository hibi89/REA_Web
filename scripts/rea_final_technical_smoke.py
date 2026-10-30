"""Synthetic-only final technical acceptance: four REAL ZIPs -> restore -> HTTP.

Python 3.11+ with developer test dependencies (FastAPI, Starlette, httpx).
Does not reach a network or certify human, legal, privacy or commercial gates.
Run: python -m scripts.rea_final_technical_smoke
Optional: --out NEW_DIR (keep synthetic packages), --native (Windows CMD+HTTP).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from fastapi.testclient import TestClient

from rea.creator_gui import CreatorController
from rea.delivery import create_delivery, verify_delivery
from rea.provenance import inspect_delivery
from rea.recovery import restore_delivery
from rea.safe_publish import publish_directory
from rea.two_source import preflight_pair, pack_pair

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_CASES = ("csv", "json", "owner_mapping", "two_file_append")


def _prepare_packages(stage: Path) -> list[tuple[str, Path, int, str, str]]:
    source = ROOT / "samples"
    packages = stage / "packages"
    packages.mkdir()
    cases = []

    csv = packages / "csv.zip"
    create_delivery(source / "qa_cafe.csv", csv, "Synthetic cafe")
    cases.append(("csv", csv, 4, "C01", "카페라떼"))

    j = packages / "json.zip"
    create_delivery(source / "qa_products.json", j, "Synthetic JSON catalog")
    cases.append(("json", j, 4, "J01", "블렌드"))

    controller = CreatorController()
    owner_source = source / "qa_guided.csv"
    controller.inspect(owner_source)
    approved = packages / "owner-mapping.zip"
    controller.export(
        owner_source, approved, "Synthetic approved mapping",
        {"id": "sku", "title": "display_name", "category": "group_name"},
        True, "APPROVE",
    )  # Synthetic fixture only; not evidence of an actual owner's consent.
    cases.append(("owner_mapping", approved, 3, "S01", "카페라떼"))

    a, b = stage / "first.csv", stage / "second.csv"
    a.write_text("sku,label,group\nA,Alpha,Food\n", encoding="utf-8")
    b.write_text("sku,label,group\nB,Beta,Food\n", encoding="utf-8")
    preview = preflight_pair(a, b)
    hashes = [item["sha256"] for item in preview["sources"]]
    combined = packages / "two-file-append.zip"
    pack_pair(
        a, b, combined, "Synthetic two-file append",
        {"id": "sku", "title": "label", "category": "group"},
        *hashes, "APPROVE", "APPROVE", "APPEND",
    )
    cases.append(("two_file_append", combined, 2, "A", "Alpha"))
    return cases


def _http_assertions(app_root: Path, expected_rows: int, detail_id: str,
                     expected_search: str, module_name: str) -> None:
    """Exercise the actual generated app, not a mocked function or canned JSON."""
    script = app_root / "app.py"
    spec = importlib.util.spec_from_file_location(module_name, script)
    if spec is None or spec.loader is None:
        raise AssertionError("Generated FastAPI app cannot be imported")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with TestClient(module.app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json() == {"status": "ok", "mode": "local_readonly"}
        result = client.get("/api/items")
        assert result.status_code == 200
        assert result.json()["total"] == expected_rows
        assert len(result.json()["items"]) == expected_rows
        assert client.get("/api/items", params={"q": expected_search}).json()["total"] >= 1
        assert client.get("/api/items/" + detail_id).status_code == 200
        assert client.get("/api/items/UNKNOWN_SYNTHETIC_ID").status_code == 404
        categories = client.get("/api/categories")
        assert categories.status_code == 200 and categories.json()["categories"]
        summary = client.get("/api/summary")
        assert summary.status_code == 200
        assert summary.json()["total_items"] == expected_rows
        schema = client.get("/api/schema")
        assert schema.status_code == 200
        assert schema.json()["review_status"] == "UNAPPROVED"
        assert client.get("/").status_code == 200
        js = client.get("/static/app.js")
        assert js.status_code == 200 and "textContent" in js.text
        assert client.post("/api/items", json={"id": "forbidden"}).status_code == 405


def run(*, out: Path | None = None, native: bool = False) -> dict:
    """Four real synthetic delivery pipelines plus recovered FastAPI endpoints."""
    if native and os.name != "nt":
        raise ValueError("--native needs actual Windows CMD; never emulate it")
    out = Path(out).absolute() if out is not None else None
    if out is not None and (out.exists() or out.is_symlink()):
        raise FileExistsError("Technical smoke output must be a NEW directory")
    base = out.parent if out is not None else None
    with tempfile.TemporaryDirectory(prefix=".rea-final-smoke-", dir=base) as temp:
        stage = Path(temp) / "result"
        stage.mkdir()
        results = []
        for index, (case_id, archive, rows, detail_id, search) in enumerate(
                _prepare_packages(stage)):
            assert case_id == SYNTHETIC_CASES[index]
            proof = verify_delivery(archive)
            audit = inspect_delivery(archive)
            assert audit["overall_commercial_clearance"] == "NOT_GRANTED"
            assert proof["schema_version"] == "rea.delivery.v0.1"
            recovered = stage / "restored" / case_id
            recovery = restore_delivery(archive, recovered)
            assert recovery["sqlite_row_count"] == rows
            assert recovery["commercial_clearance"] == "NOT_GRANTED"
            _http_assertions(recovered / "app", rows, detail_id, search,
                             f"rea_final_smoke_{case_id}")
            if native:
                check = subprocess.run(
                    ["cmd.exe", "/d", "/c", str(recovered / "check_windows.cmd"),
                     "--check"],
                    cwd=recovered, check=False, capture_output=True, timeout=90,
                )
                if check.returncode != 0:
                    raise AssertionError(f"Windows prerequisite check failed: {case_id}")
            results.append({
                "case": case_id,
                "rows": rows,
                "zip_member_count": recovery["file_count"] + 1,
                "recovery_integrity": "PASS",
                "generated_inprocess_http": "PASS",
                "windows_cmd_prerequisites": "PASS" if native else "NOT_RUN",
            })

        if native:
            # Real localhost process+Windows CMD smoke is separate from TestClient.
            from scripts.windows_native_smoke import main as windows_smoke
            windows_smoke()

        report = {
            "schema_version": "rea.final_technical_smoke.v0.1",
            "classification": "SYNTHETIC_ONLY_NOT_CUSTOMER_ACCEPTANCE",
            "status": "PASS_SYNTHETIC_TECHNICAL_ONLY",
            "case_count": len(results),
            "cases": results,
            "native_windows_launcher": "PASS" if native else "NOT_RUN",
            "human_windows_acceptance": "NOT_RUN",
            "runtime_dependency_license_clearance": "NOT_GRANTED",
            "commercial_clearance": "NOT_GRANTED",
            "seller_final_approval": "NOT_APPROVED",
        }
        (stage / "technical_smoke_report.json").write_text(
            json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        if out is not None:
            publish_directory(stage, out)
        return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Four-case synthetic REA technical E2E")
    parser.add_argument("--out", type=Path, help="Optional NEW folder for synthetic outputs")
    parser.add_argument("--native", action="store_true",
                        help="Real Windows CMD checks and native localhost smoke")
    args = parser.parse_args(argv)
    try:
        report = run(out=args.out, native=args.native)
    except (OSError, ValueError, AssertionError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"FAIL_SYNTHETIC_TECHNICAL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
