"""REA_Web P50: true pinned Fable static scan -> actual Astra draft -> Pro app.

SYNTHETIC-LOCAL-FIRST ONLY: a single owner-provided HTML file is served over
loopback to the actual pinned Fable static scanner. No real/public URL scanning,
no inferred UI behavior approval, no original site source copying, and no
customer data transferred. Customer-owned CSV alone defines the new app.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from threading import Thread

from rea.adapter.fable_to_astra import project_fable, verify_astra
from rea.mvp import DataError, source_sha256
from rea.orchestrator import build
from rea.safe_publish import publish_directory

MAX_FIXTURE = 256 * 1024
SHA = re.compile(r"^[0-9a-f]{64}$")
CATEGORIES = ("navigation", "search", "list", "detail")


class WebsiteReviewError(ValueError):
    """User action or evidence is insufficient. Fail without publishing."""


class StructuralHints(HTMLParser):
    """Only count static HTML tags/attrs. Never store values or scripts."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = {"nav": 0, "a": 0, "table": 0, "form": 0,
                     "input_search": 0, "article": 0}

    def handle_starttag(self, tag, attrs):
        if tag in self.tags:
            self.tags[tag] += 1
        if tag == "input" and any(k == "type" and str(v).lower() == "search"
                                  for k, v in attrs):
            self.tags["input_search"] += 1


def _fixture(path: Path, expected_hash: str) -> tuple[bytes, str, dict]:
    if not SHA.fullmatch(expected_hash):
        raise WebsiteReviewError("Explicit 64-hex fixture SHA256 is required")
    if path.is_symlink() or not path.is_file():
        raise WebsiteReviewError("Only an existing regular, non-symlink local HTML fixture is allowed")
    if path.suffix.lower() not in {".html", ".htm"}:
        raise WebsiteReviewError("Only local HTML fixtures are supported")
    if not 0 < path.stat().st_size <= MAX_FIXTURE:
        raise WebsiteReviewError("Fixture length outside safe bound")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as stream:
            content = stream.read(MAX_FIXTURE + 1)
    except OSError as exc:
        raise WebsiteReviewError("Fixture cannot be opened safely") from exc
    if not content or len(content) > MAX_FIXTURE:
        raise WebsiteReviewError("Fixture changed length")
    digest = hashlib.sha256(content).hexdigest()
    if digest != expected_hash:
        raise WebsiteReviewError("Fixture SHA mismatch")
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise WebsiteReviewError("Fixture must be UTF-8") from exc
    hints = StructuralHints()
    hints.feed(decoded)
    hints.close()
    if not any(hints.tags.values()):
        raise WebsiteReviewError("No structural HTML tags were found")
    if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise WebsiteReviewError("Fixture modified during inspection")
    return content, digest, hints.tags


def _fable_scan(html: bytes, scanner_root: Path, out: Path) -> tuple[dict, int]:
    """Invoke the real Fable 5.1 scanner, constrained to one loopback page."""
    scanner = scanner_root / "scan.py"
    if scanner_root.is_symlink() or not scanner.is_file():
        raise WebsiteReviewError("Pinned Fable scan.py checkout is required")

    class FixtureHandler(BaseHTTPRequestHandler):
        calls = 0

        def do_GET(self):
            type(self).calls += 1
            if self.path != "/":
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(html)

        def log_message(self, *_args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    server.daemon_threads = True
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/"
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        result = subprocess.run(
            [sys.executable, str(scanner), url, "--timeout", "3", "--out", str(out)],
            cwd=scanner_root, env=env, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=25, check=False,
        )
        if result.returncode != 0:
            raise WebsiteReviewError("Pinned Fable static scan failed (no output published)")
        data = json.loads((out / "result.json").read_text(encoding="utf-8"))
        if (FixtureHandler.calls != 1 or data.get("schema_version") != "1.0"
                or data.get("scan_mode") != "static"
                or data.get("target", {}).get("status_code") != 200
                or data.get("target", {}).get("input_url") != url):
            raise WebsiteReviewError("Fable returned unexpected scan scope or request count")
        return data, FixtureHandler.calls
    except (OSError, subprocess.TimeoutExpired, UnicodeError, json.JSONDecodeError) as exc:
        raise WebsiteReviewError("Fable static scan unavailable") from exc
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def _astra_draft(scan: dict, tag_counts: dict, astra_root: Path) -> tuple[dict, dict]:
    if astra_root.is_symlink() or not (astra_root / "astra_contracts" / "observation.py").is_file():
        raise WebsiteReviewError("Pinned Astra P4 contracts checkout is required")
    sys.path.insert(0, str(astra_root.resolve()))
    from astra_contracts.observation import ObservationBundle
    from astra_contracts.functional_spec import derive_spec

    # Exact existing Fable -> Astra conservative technical adapter.
    projected = verify_astra(project_fable(scan, source_ref="fable_result.json"))
    if (projected["status"] != "REVIEW_REQUIRED"
            or projected["generation_allowed"] or projected["implementation_ready"]
            or projected["astra_contract_validation"] != "NO_UI_OBSERVATIONS"):
        raise WebsiteReviewError("Fable/Astra review state is unsafe")

    potential = [
        ("nav", "navigation", "Static navigation markup present"),
        ("input_search", "search", "Search input markup present"),
        ("table", "list", "Static table markup present"),
        ("article", "detail", "Article markup present"),
    ]
    observations = []
    for tag, feature, claim in potential:
        if tag_counts.get(tag, 0):
            observations.append({
                "id": f"ob_{len(observations)+1:04d}", "feature": feature,
                "title": claim, "claim": claim + "; runtime effect unobserved",
                "certainty": "inferred", "evidence_ids": [],
                "action": None, "before": {}, "after": {},
            })
    if not observations:
        observations.append({
            "id": "ob_0001", "feature": "navigation",
            "title": "Behavior unknown", "claim": "Static HTML reveals no supported interactive behavior",
            "certainty": "unknown", "evidence_ids": [],
            "action": None, "before": {}, "after": {},
        })
    bundle = ObservationBundle.model_validate({
        "schema_version": "1.0",
        "site_url": projected["source"]["site_origin"],
        "scope": "Owner-authorized single local static fixture: inferred, no browser actions",
        "recorded_at": scan["scanned_at"], "evidence": [], "observations": observations,
    })
    draft = derive_spec(bundle)
    if (draft.implementation_ready or draft.candidate_features
            or draft.db_api_mapping_status != "not_started"
            or any(x.status != "pending" for x in draft.approval_gates)):
        raise WebsiteReviewError("Astra tried to promote static markup to approved behavior")
    return projected, draft.model_dump(mode="json")


def rebuild_local_fixture(
    fixture_html: Path, owner_csv: Path, out: Path, *,
    fixture_sha256: str, owner_sha256: str,
    id_field: str, title_field: str, category_field: str,
    fixture_permission: str, owner_approval: str,
    fable_root: Path, astra_root: Path,
) -> dict:
    """Real, bounded local static Fable + Astra -> independent Pro app.

    Owner approval authorizes a local dataset mapping only. It NEVER approves
    inferred reference site semantics or grants site-content usage rights.
    """
    if fixture_permission != "YES_LOCAL_FIXTURE" or owner_approval != "APPROVE":
        raise WebsiteReviewError("Explicit fixture scope and owner data approval required")
    if not SHA.fullmatch(owner_sha256):
        raise WebsiteReviewError("Explicit owner CSV SHA256 is required")
    mapping = {"id": id_field, "title": title_field, "category": category_field}
    if len(set(mapping.values())) != 3 or not all(isinstance(v, str) and v for v in mapping.values()):
        raise WebsiteReviewError("Three distinct owner-mapped fields are required")
    fixture_html = Path(fixture_html)
    owner_csv = Path(owner_csv)
    out = Path(out).absolute()
    if out.exists() or out.is_symlink():
        raise FileExistsError("Target already exists; no overwrite allowed")
    html, html_digest, hints = _fixture(fixture_html, fixture_sha256)
    if owner_csv.suffix.lower() != ".csv" or source_sha256(owner_csv) != owner_sha256:
        raise WebsiteReviewError("Owner CSV changed or source SHA mismatch")
    if not out.parent.exists() or out.parent.is_symlink():
        raise WebsiteReviewError("Parent output directory must already exist and not be symlinked")

    with tempfile.TemporaryDirectory(prefix=".rea-website-p50-", dir=out.parent) as temp:
        scratch = Path(temp)
        fable_result, fable_calls = _fable_scan(html, Path(fable_root), scratch / "fable")
        projected, spec = _astra_draft(fable_result, hints, Path(astra_root))
        # The old production app generator remains independent of reference
        # site semantics. Only the explicitly approved customer CSV is input.
        app = scratch / "new-app"
        manifest = build(
            owner_csv, app, "REA reviewed independent app",
            fable_result=scratch / "fable" / "result.json",
            astra_root=Path(astra_root),
            approved_mapping=mapping, expected_source_sha256=owner_sha256,
        )
        if source_sha256(owner_csv) != owner_sha256:
            raise WebsiteReviewError("Owner data changed during build")
        if _fixture(fixture_html, fixture_sha256)[1] != html_digest:
            raise WebsiteReviewError("Fixture changed during build")
        summary = {
            "schema_version": "rea.website.p50.v1",
            "input_kind": "authorized_local_static_html_only",
            "fixture_sha256": html_digest, "fable_scan_mode": "static",
            "fable_actual_scanner": True, "fable_http_requests": fable_calls,
            "fable_technical_counts": projected["technical_finding_counts"],
            "fable_astra_validation": projected["astra_contract_validation"],
            "astra_site_spec": spec,
            "reference_behavior_status": "REVIEW_REQUIRED",
            "site_inferred_behavior_approved": False,
            "new_app_source": "separately_approved_customer_csv_only",
            "owner_source_sha256": owner_sha256,
            "owner_mapping_confirmed": True,
            "commercial_release": "HOLD",
        }
        review = app / "review"
        review.mkdir(exist_ok=True)
        (review / "website_p50_review.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        manifest["reference_review"] = {
            "status": "REVIEW_REQUIRED",
            "technical_fable_scanned": True,
            "astra_static_hypotheses_only": True,
            "used_for_app_data": False,
        }
        (app / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        if out.exists() or out.is_symlink():
            raise FileExistsError("Target occupied while building")
        publish_directory(app, out)
    return {"status": "P50_SYNTHETIC_REVIEW_HOLD", "output": out.name,
            "rows": manifest["rows"], "fable_real_static_scan": True,
            "astra_draft_unapproved": True, "fable_requests": fable_calls}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Local owner HTML -> real Fable static -> Astra review -> Pro app")
    p.add_argument("--fixture-html", type=Path, required=True)
    p.add_argument("--fixture-sha256", required=True)
    p.add_argument("--owner-csv", type=Path, required=True)
    p.add_argument("--owner-sha256", required=True)
    p.add_argument("--id-field", required=True)
    p.add_argument("--title-field", required=True)
    p.add_argument("--category-field", required=True)
    p.add_argument("--fixture-permission", required=True, choices=["YES_LOCAL_FIXTURE"])
    p.add_argument("--owner-approval", required=True, choices=["APPROVE"])
    p.add_argument("--fable-root", type=Path, required=True)
    p.add_argument("--astra-root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args(argv)
    try:
        result = rebuild_local_fixture(
            a.fixture_html, a.owner_csv, a.out,
            fixture_sha256=a.fixture_sha256, owner_sha256=a.owner_sha256,
            id_field=a.id_field, title_field=a.title_field,
            category_field=a.category_field, fixture_permission=a.fixture_permission,
            owner_approval=a.owner_approval, fable_root=a.fable_root,
            astra_root=a.astra_root,
        )
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as exc:
        p.exit(2, f"REA_WEBSITE_P50_HOLD: {type(exc).__name__}: {exc}\n")
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
