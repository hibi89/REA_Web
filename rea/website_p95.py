"""REA_Web P95 limited workflow: Fable Record intake -> human review -> sealed delivery.

Localhost + local synthetic artifacts only. Does NOT infer behavior from Fable
manual action markers, prove rights, permit live scanning or commercial release.
The existing P85 pipeline performs the actual authorized synthetic browser
observation and independent Pro-app generation; this layer adds a usable local
review workbench and deterministic portable delivery with independent verifier.
"""
from __future__ import annotations

import hashlib
import hmac
from html import escape
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import stat
from typing import Any
import zipfile

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from rea.website_rebuild import WebsiteReviewError

MAX_JSON = 2 * 1024 * 1024
MAX_FILE = 12 * 1024 * 1024
MAX_PACKAGE = 45 * 1024 * 1024
HEX = re.compile(r"^[a-f0-9]{64}$")
SAFE_IDENTIFIER = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,110}$")
ALLOWED_RECORDED = {"click", "change"}
APP_DECISIONS = {"approve_synthetic_proposal", "hold", "reject"}
HTML = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>REA_Web | 소유자 근거 검토</title></head>
<body><main><h1>REA_Web · 로컬 근거 검토</h1>
<p>관찰·추정·권리·구현승인을 분리합니다. 참고 웹사이트의 코드와 저작권을 자동 승인하지 않습니다.</p>
<p id="status" role="status">패킷 확인 중</p>
<section><h2>검토 항목</h2><ul id="features"></ul></section>
<section><h2>판정 기록</h2>
<label>검토자 표시명 <input id="reviewer" maxlength="80" autocomplete="off"></label>
<label>판정 <select id="decision"><option value="hold">보류</option>
<option value="approve_synthetic_proposal">합성 기능 제안 검토 승인</option>
<option value="reject">반려</option></select></label>
<label>판정 사유 <textarea id="reason" maxlength="1200"></textarea></label>
<button id="save" type="button">검토 기록 저장</button></section>
<pre id="out"></pre><footer>로컬 합성 검토 의견 저장 전용. 배포·외부 접근·권리 승인 불가.</footer>
<script src="/review.js" defer></script></main></body></html>"""
JS = r"""(() => {
'use strict';
let packet = null, token = null;
const el = id => document.getElementById(id);
fetch('/api/packet',{cache:'no-store'}).then(r => {
  if (!r.ok) throw Error('검토 패킷 접근 실패');
  return r.json();
}).then(data => {
  packet = data.packet; token = data.session_token;
  el('status').textContent = '근거 SHA: ' + packet.review_digest.slice(0,16) +
    ' · 기능 후보: ' + packet.features.length + ' · 모든 항목은 검토 보류';
  for (const feature of packet.features) {
    const node = document.createElement('li');
    node.textContent = feature.feature + ' · 증거 ' + feature.evidence_count +
      '개 · ' + feature.review_status;
    el('features').append(node);
  }
}).catch(e => { el('status').textContent = e.message; });
el('save').addEventListener('click', async () => {
  if (!packet || !token) return;
  const reviewer = el('reviewer').value.trim();
  const reason = el('reason').value.trim();
  if (reviewer.length < 2 || reason.length < 10) {
    el('out').textContent = '검토자와 사유(10자 이상)를 입력하세요'; return;
  }
  const body = {
    schema_version:'rea.website.p95.review.v1',
    packet_sha256:packet.packet_sha256,
    review_digest:packet.review_digest,
    reviewer_claimed_label:reviewer,
    decision:el('decision').value,
    rationale:reason
  };
  try {
    const r = await fetch('/api/decisions',{
      method:'POST',headers:{'Content-Type':'application/json','X-REA-Review-Token':token},
      credentials:'same-origin',body:JSON.stringify(body)});
    const result = await r.json();
    if (!r.ok) throw Error(result.detail || '저장 실패');
    el('out').textContent = '검토 기록 ID: '+result.record_id+
      '\n권리/상용 출시: ' + result.commercial_release +
      '\n법적 승인 검증: false';
  } catch(e) { el('out').textContent = String(e.message); }
});
})();"""


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _limited_file(path: Path, limit: int = MAX_JSON) -> bytes:
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise WebsiteReviewError("Regular bounded local input required (symlink forbidden)")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
    with os.fdopen(os.open(path, flags), "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise WebsiteReviewError("Not a regular file")
        raw = handle.read(limit + 1)
    if not raw or len(raw) > limit or path.is_symlink():
        raise WebsiteReviewError("Input empty, modified or oversized")
    return raw


def _json_file(path: Path) -> dict:
    try:
        data = json.loads(_limited_file(path), parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (UnicodeError, ValueError, OSError) as exc:
        raise WebsiteReviewError("Invalid local JSON input") from exc
    if not isinstance(data, dict):
        raise WebsiteReviewError("Top-level JSON object required")
    return data


def inspect_fable_record(record_file: Path, *, expected_sha256: str) -> dict:
    """Safe subset of original frozen Fable 5.1 record schema.

    Interaction markers are activity hints and NEVER evidence of a causal
    feature or reviewer permission. Store only counts/hashes (no raw URLs).
    """
    if not HEX.fullmatch(expected_sha256):
        raise WebsiteReviewError("Full pinned record SHA256 required")
    raw = _limited_file(record_file)
    if not hmac.compare_digest(hashlib.sha256(raw).hexdigest(), expected_sha256):
        raise WebsiteReviewError("Stale or tampered Fable Record SHA")
    try:
        data = json.loads(raw)
    except (UnicodeError, ValueError) as exc:
        raise WebsiteReviewError("Invalid Fable Record JSON") from exc
    if (not isinstance(data, dict) or data.get("schema_version") != "1.0" or
        data.get("scan_mode") != "record"):
        raise WebsiteReviewError("Fable 5.1 actual Record schema/mode required")
    record = data.get("record")
    if not isinstance(record, dict):
        raise WebsiteReviewError("Missing Fable record block")
    origins = record.get("allowed_origins")
    if (not isinstance(origins, list) or len(origins) != 1 or
        not isinstance(origins[0], str) or
        not re.fullmatch(r"http://127\.0\.0\.1:\d{2,5}", origins[0])):
        raise WebsiteReviewError("Record import restricted to single explicit loopback origin")
    # The original scanner permits various termination cases. An unfinished
    # or failed session is not a verifiable capture for review.
    if record.get("stop_reason") not in {"enter", "browser_closed", "max_duration"}:
        raise WebsiteReviewError("Record session incomplete or unsafe")
    if not isinstance(record.get("interactions"), list) or len(record["interactions"]) > 2000:
        raise WebsiteReviewError("Record interaction bounds invalid")
    markers = record["interactions"]
    for marker in markers:
        if (not isinstance(marker, dict) or marker.get("type") not in ALLOWED_RECORDED
                or not isinstance(marker.get("at_ms"), int)
                or not re.fullmatch(r"[a-z][a-z0-9-]{0,30}", str(marker.get("tag", "")))
                or not isinstance(marker.get("selector"), str)
                or len(marker["selector"]) > 250):
            raise WebsiteReviewError("Unsupported Record interaction marker")
    pages = record.get("pages")
    if not isinstance(pages, list) or len(pages) > 100:
        raise WebsiteReviewError("Record page bound invalid")
    for page in pages:
        if not isinstance(page, dict) or page.get("allowed") is not True:
            raise WebsiteReviewError("Out-of-scope page in record")
    if record.get("scope") != "allowed_origin_main_frames_only":
        raise WebsiteReviewError("Record scope not confirmed")
    return {
        "schema_version": "rea.fable.record_intake.v1",
        "fable_record_sha256": expected_sha256,
        "record_mode": "record",
        "same_origin_pages": len(pages),
        "interaction_marker_count": len(markers),
        "evidence_grade": "MANUAL_MARKERS_ONLY_NOT_CAUSAL",
        "recorded_ui_behavior_approved": False,
        "content_reproduction_authorized": False,
        "status": "REVIEW_REQUIRED",
    }


def make_packet(p85_receipt: dict, fable_record_summary: dict | None = None):
    if (p85_receipt.get("schema_version") != "rea.website.p85.v1" or
            p85_receipt.get("production_release") != "HOLD" or
            p85_receipt.get("site_approval") is not False):
        raise WebsiteReviewError("P85 review receipt was not in fail-closed state")
    review_digest = p85_receipt.get("review_digest")
    if not isinstance(review_digest, str) or not HEX.fullmatch(review_digest):
        raise WebsiteReviewError("Missing exact P85 review digest")
    from rea.website_p70 import _digest
    if _digest(p85_receipt.get("subject")) != review_digest:
        raise WebsiteReviewError("P85 subject fingerprint mismatch")
    spec = p85_receipt.get("astra_spec_draft")
    if not isinstance(spec, dict) or spec.get("implementation_ready") is not False:
        raise WebsiteReviewError("Expected unapproved Astra P4 draft")
    candidates = spec.get("candidate_features")
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= 20:
        raise WebsiteReviewError("Missing or unbounded Astra feature candidates")
    features = []
    for feature in candidates:
        if (not isinstance(feature, dict) or
                feature.get("review_status") != "requires_review" or
                feature.get("feature") not in {"search", "filter", "detail", "navigation", "list"}):
            raise WebsiteReviewError("Unreviewed/unsupported feature")
        evidence = feature.get("evidence")
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= 10:
            raise WebsiteReviewError("No bounded referenced evidence")
        features.append({"feature": feature["feature"], "review_status": "requires_review",
                         "evidence_count": len(evidence)})
    if fable_record_summary is not None:
        if fable_record_summary.get("status") != "REVIEW_REQUIRED":
            raise WebsiteReviewError("Imported record may not grant approval")
    packet = {
        "schema_version": "rea.website.p95.packet.v1",
        "review_digest": review_digest, "features": features,
        "fable_record": fable_record_summary or {"status": "NOT_PROVIDED"},
        "code_generation_authorized": False,
        "commercial_release": "HOLD",
    }
    packet["packet_sha256"] = _hash(packet)
    return packet


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = Field(pattern=r"^rea\.website\.p95\.review\.v1$")
    packet_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    review_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    reviewer_claimed_label: str = Field(min_length=2, max_length=80)
    decision: str
    rationale: str = Field(min_length=10, max_length=1200)


def create_review_app(packet: dict, directory: Path) -> FastAPI:
    """Bounded owner UI; reviewer opinion is NOT external/legal authorization."""
    folder = Path(directory)
    if folder.is_symlink() or not folder.is_dir():
        raise WebsiteReviewError("Existing real local decision folder required")
    if packet.get("packet_sha256") != _hash({k: v for k, v in packet.items() if k != "packet_sha256"}):
        raise WebsiteReviewError("Review packet tampered")
    secret = secrets.token_urlsafe(32)
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def boundary(request: Request, call_next):
        host = request.headers.get("host", "").split(":")[0].lower()
        if host not in {"127.0.0.1", "localhost", "testserver"}:
            return PlainTextResponse("Localhost only", status_code=403)
        origin = request.headers.get("origin")
        if origin and origin != "http://" + request.headers.get("host", ""):
            return PlainTextResponse("External origin forbidden", status_code=403)
        answer = await call_next(request)
        answer.headers["Cache-Control"] = "no-store"
        answer.headers["Content-Security-Policy"] = (
            "default-src 'none'; script-src 'self'; style-src 'none'; "
            "connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        answer.headers["X-Content-Type-Options"] = "nosniff"
        answer.headers["X-Frame-Options"] = "DENY"
        return answer

    @app.get("/", response_class=HTMLResponse)
    def home():
        return HTMLResponse(HTML)

    @app.get("/review.js")
    def script():
        return PlainTextResponse(JS, media_type="application/javascript")

    @app.get("/api/packet")
    def get_packet():
        return {"packet": packet, "session_token": secret,
                "permission_to_reconstruct": False}

    @app.post("/api/decisions")
    async def decide(request: Request, x_rea_review_token: str | None = Header(default=None)):
        if not x_rea_review_token or not hmac.compare_digest(x_rea_review_token, secret):
            raise HTTPException(403, "Invalid local session token")
        if request.headers.get("content-type", "").split(";")[0] != "application/json":
            raise HTTPException(415, "JSON body required")
        try:
            if int(request.headers.get("content-length", "0") or "0") > MAX_JSON:
                raise HTTPException(413, "Review submission too large")
        except ValueError:
            raise HTTPException(400, "Invalid content length")
        raw = await request.body()
        if len(raw) > MAX_JSON:
            raise HTTPException(413, "Review too large")
        try:
            decision = Decision.model_validate_json(raw)
        except ValidationError as exc:
            raise HTTPException(422, "Invalid review input") from exc
        if (decision.decision not in APP_DECISIONS or
                decision.packet_sha256 != packet["packet_sha256"] or
                decision.review_digest != packet["review_digest"]):
            raise HTTPException(422, "Stale packet or invalid decision")
        if folder.is_symlink() or not folder.is_dir():
            raise HTTPException(409, "Review folder changed")
        item = {
            **decision.model_dump(),
            "schema_version": "rea.website.p95.record.v1",
            "reviewer_identity_verified": False,
            "site_use_license_verified": False,
            "reference_behavior_verified_external": False,
            "code_generation_authorized": False,
            "commercial_release": "HOLD",
        }
        identifier = secrets.token_hex(12)
        dest = folder / f"{identifier}.json"
        try:
            # Exclusive create prevents rewriting prior owner opinions.
            with dest.open("x", encoding="utf-8") as output:
                output.write(json.dumps(item, ensure_ascii=False, indent=2) + "\n")
        except OSError as exc:
            raise HTTPException(409, "Cannot save review, no other files changed") from exc
        return {"record_id": identifier, "decision": decision.decision,
                "commercial_release": "HOLD", "authorization_verified": False}
    return app


def _package_members(root: Path):
    if root.is_symlink() or not root.is_dir():
        raise WebsiteReviewError("Existing regular app folder required")
    result = []
    total = 0
    for source in sorted(root.rglob("*")):
        if source.is_symlink():
            raise WebsiteReviewError("Symlink in app output")
        relative = source.relative_to(root).as_posix()
        if source.is_dir():
            continue
        if (not source.is_file() or not SAFE_IDENTIFIER.fullmatch(source.name)
                or any(not SAFE_IDENTIFIER.fullmatch(x) for x in source.relative_to(root).parts)):
            raise WebsiteReviewError("Unsafe output file name")
        data = _limited_file(source, MAX_FILE)
        total += len(data)
        if total > MAX_PACKAGE:
            raise WebsiteReviewError("Delivery package too large")
        result.append((relative, data))
    required = {"app.py", "manifest.json", "data.sqlite", "README.md"}
    if not required.issubset({p for p, _ in result}):
        raise WebsiteReviewError("Required independent app files absent")
    return result


def create_delivery_zip(app_path: Path, record_path: Path, output_zip: Path, *,
                        quote_label: str) -> dict:
    """Create-only deterministic zip with independently verifiable member hashes."""
    if not 2 <= len(quote_label.strip()) <= 80:
        raise WebsiteReviewError("Local quote scope label must be 2..80 chars")
    record = _json_file(record_path)
    if (record.get("schema_version") != "rea.website.p95.record.v1" or
            record.get("decision") != "approve_synthetic_proposal" or
            record.get("commercial_release") != "HOLD" or
            record.get("site_use_license_verified") is not False or
            record.get("reviewer_identity_verified") is not False):
        raise WebsiteReviewError("Only reviewed synthetic proposal can be packaged; never sale-approved")
    members = _package_members(Path(app_path))
    manifest = json.loads(next(contents for name, contents in members if name == "manifest.json"))
    if manifest.get("website_p85", {}).get("commercial_release") != "HOLD":
        raise WebsiteReviewError("Missing original P85 commercial hold")
    reviewed = next((contents for name, contents in members
                    if name == "review/p85_evidence_and_visual_diff.json"), None)
    if not reviewed:
        raise WebsiteReviewError("P85 evidence review required")
    p85 = json.loads(reviewed)
    if (p85.get("review_digest") != record.get("review_digest") or
            p85.get("production_release") != "HOLD"):
        raise WebsiteReviewError("Review digest and evidence do not match")
    if p85.get("human_review") != "PENDING_EXPLICIT_SYNTHETIC_OWNER_APPROVAL":
        raise WebsiteReviewError("Original Astra review must remain unapproved")

    out = Path(output_zip)
    if out.suffix.lower() != ".zip" or out.exists() or out.is_symlink() or out.parent.is_symlink():
        raise WebsiteReviewError("New, non-symlink .zip destination required")
    if not out.parent.is_dir():
        raise WebsiteReviewError("Existing output parent required")
    record_bytes = _canonical(record)
    members.append(("p95/reviewer_opinion.json", record_bytes))
    manifest_delivery = {
        "schema_version": "rea.website.delivery.v1",
        "scope": "synthetic_local_only",
        "quote_label": quote_label.strip(),
        "price": "PENDING_OWNER_APPROVAL",
        "commercial_release": "HOLD",
        "site_use_license_verified": False,
        "reviewer_identity_verified": False,
        "contents": {name: {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
                     for name, raw in sorted(members)},
    }
    members.append(("p95/delivery_manifest.json", _canonical(manifest_delivery)))
    try:
        with out.open("xb") as handle:
            with zipfile.ZipFile(handle, "w", compression=zipfile.ZIP_STORED) as archive:
                for name, raw in sorted(members):
                    info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_STORED
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, raw)
        verdict = verify_delivery_zip(out)
        if verdict["status"] != "VERIFIED_SYNTHETIC_RELEASE_HOLD":
            raise WebsiteReviewError("Delivery verification failed")
    except Exception:
        # Only delete the newly created delivery on a failed local publish.
        # The owner input files and prior outputs are untouched.
        if out.is_file() and not out.is_symlink():
            out.unlink()
        raise
    return verdict


def verify_delivery_zip(path: Path) -> dict:
    raw = _limited_file(path, MAX_PACKAGE + 2 * 1024 * 1024)
    import io
    with zipfile.ZipFile(io.BytesIO(raw), "r") as z:
        info = z.infolist()
        if not 1 <= len(info) <= 110 or len({x.filename for x in info}) != len(info):
            raise WebsiteReviewError("Invalid archive member count/duplicate")
        if sum(x.file_size for x in info) > MAX_PACKAGE + MAX_JSON:
            raise WebsiteReviewError("Archive uncompressed size exceeded")
        for x in info:
            p = PurePosixPath(x.filename)
            if (p.is_absolute() or x.filename.startswith("/") or "\\" in x.filename or
                    any(part in ("", ".", "..") or not SAFE_IDENTIFIER.fullmatch(part)
                        for part in p.parts) or x.is_dir() or
                    x.file_size > MAX_FILE or x.compress_type != zipfile.ZIP_STORED):
                raise WebsiteReviewError("Unsafe archive member")
        files = {x.filename: z.read(x.filename) for x in info}
    if "p95/delivery_manifest.json" not in files or "p95/reviewer_opinion.json" not in files:
        raise WebsiteReviewError("Missing delivery integrity evidence")
    data = json.loads(files.pop("p95/delivery_manifest.json"))
    record = json.loads(files["p95/reviewer_opinion.json"])
    if (data.get("schema_version") != "rea.website.delivery.v1" or
            data.get("commercial_release") != "HOLD" or
            data.get("site_use_license_verified") is not False or
            data.get("price") != "PENDING_OWNER_APPROVAL" or
            record.get("commercial_release") != "HOLD"):
        raise WebsiteReviewError("Unexpected release/price/approval state")
    declared = data.get("contents")
    if not isinstance(declared, dict) or set(declared) != set(files):
        raise WebsiteReviewError("Manifest files mismatch")
    for name, value in declared.items():
        if (hashlib.sha256(files[name]).hexdigest() != value.get("sha256") or
                len(files[name]) != value.get("bytes")):
            raise WebsiteReviewError("Tampered or truncated package member")
    return {
        "status": "VERIFIED_SYNTHETIC_RELEASE_HOLD",
        "zip_sha256": hashlib.sha256(raw).hexdigest(),
        "files": len(files), "commercial_release": "HOLD",
        "price": "PENDING_OWNER_APPROVAL",
        "rights_verified": False,
    }


def main(argv: list[str] | None = None) -> int:
    """Direct, local-first operator CLI; never invokes a remote URL or an LLM."""
    import argparse
    parser = argparse.ArgumentParser(description="REA_Web local synthetic review and delivery")
    actions = parser.add_subparsers(dest="action", required=True)
    review = actions.add_parser("review", help="Run human-opinion UI bound to loopback")
    review.add_argument("--p85-receipt", type=Path, required=True)
    review.add_argument("--decisions", type=Path, required=True)
    review.add_argument("--fable-record", type=Path)
    review.add_argument("--fable-record-sha256")
    review.add_argument("--port", type=int, default=8019)
    pack = actions.add_parser("package", help="New ZIP from existing synthetic Pro app")
    pack.add_argument("--app", type=Path, required=True)
    pack.add_argument("--decision", type=Path, required=True)
    pack.add_argument("--out", type=Path, required=True)
    pack.add_argument("--scope", required=True)
    verify = actions.add_parser("verify", help="Verify existing ZIP without extraction")
    verify.add_argument("--zip", type=Path, required=True)
    check = actions.add_parser("record-check", help="Read-only Fable Record intake")
    check.add_argument("--record", type=Path, required=True)
    check.add_argument("--sha256", required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "record-check":
            value = inspect_fable_record(args.record, expected_sha256=args.sha256)
        elif args.action == "verify":
            value = verify_delivery_zip(args.zip)
        elif args.action == "package":
            value = create_delivery_zip(args.app, args.decision, args.out,
                                        quote_label=args.scope)
        else:
            if not 1024 <= args.port <= 65535:
                parser.error("--port must be 1024..65535")
            if bool(args.fable_record) != bool(args.fable_record_sha256):
                parser.error("--fable-record and --fable-record-sha256 must be supplied together")
            record = (inspect_fable_record(args.fable_record,
                        expected_sha256=args.fable_record_sha256)
                      if args.fable_record else None)
            packet = make_packet(_json_file(args.p85_receipt), record)
            folder = args.decisions
            if folder.is_symlink() or not folder.is_dir():
                raise WebsiteReviewError("--decisions requires existing real folder")
            app = create_review_app(packet, folder)
            import uvicorn
            print(f"Local synthetic opinion UI: http://127.0.0.1:{args.port}/",
                  flush=True)
            print("Review is NOT license/identity or deployment approval.",
                  flush=True)
            uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
            return 0
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        parser.exit(2, f"REA_P95_HOLD: {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
