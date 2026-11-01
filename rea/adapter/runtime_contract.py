"""Compare owner ZIP static declarations against *supplied* runtime OpenAPI evidence.

This module never executes/imports ZIP code and never makes network requests.
Supplied OpenAPI is untrusted unless separately obtained and attested in a
user-authorized isolated runtime. Matching routes do not prove business logic,
response payloads, safe behavior, or that the runtime came from the ZIP.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from rea.adapter.backend_zip import SCHEMA as ZIP_SCHEMA
from rea.adapter.backend_schema import SCHEMA as STATIC_SCHEMA

SCHEMA = "rea.runtime_reconciliation.v0.1"
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_ROUTES = 500
MAX_COMPONENTS = 500
MAX_ISSUES = 200
MAX_PATH_LEN = 200
ALLOWED_METHODS = frozenset(("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE"))
SAFE_PATH = re.compile(r"^/[A-Za-z0-9_./{}-]*$")
SHA256 = re.compile(r"^[a-f0-9]{64}$")
SAFE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")


class InvalidRuntimeEvidence(ValueError):
    """Untrusted, unsupported, oversized or mismatched artifacts."""


def _obj(x, label):
    if not isinstance(x, dict):
        raise InvalidRuntimeEvidence(f"{label} must be object")
    return x


def _array(x, label, limit=MAX_ROUTES):
    if not isinstance(x, list) or len(x) > limit:
        raise InvalidRuntimeEvidence(f"{label} must be bounded array")
    return x


def _route(path):
    return (isinstance(path, str) and len(path) <= MAX_PATH_LEN
            and SAFE_PATH.fullmatch(path) is not None
            and "//" not in path and "/../" not in path and "/./" not in path
            and "?" not in path and "#" not in path)


def _method(method):
    return isinstance(method, str) and method.upper() in ALLOWED_METHODS


def _only_source_key(key):
    return isinstance(key, str) and SAFE_NAME.fullmatch(key) is not None


def _read_json(path: Path) -> dict:
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise InvalidRuntimeEvidence("regular JSON file required")
    if path.stat().st_size > MAX_JSON_BYTES:
        raise InvalidRuntimeEvidence("JSON input exceeds 2 MiB")
    with path.open("rb") as f:
        data = f.read(MAX_JSON_BYTES + 1)
    if len(data) > MAX_JSON_BYTES:
        raise InvalidRuntimeEvidence("JSON input exceeds 2 MiB")
    try:
        parsed = json.loads(data.decode("utf-8-sig"))
    except (UnicodeError, ValueError) as exc:
        raise InvalidRuntimeEvidence("invalid JSON") from exc
    return _obj(parsed, "JSON root")


def _resolved_object(schema: object, components: dict) -> dict | None:
    """Resolve only local, direct $ref / array item / simple object schemas.

    No URL ref, recursive ref, allOf, or user-supplied code is followed.
    """
    if not isinstance(schema, dict):
        return None
    if "$ref" in schema:
        ref = schema["$ref"]
        if not isinstance(ref, str) or not re.fullmatch(r"#/components/schemas/[A-Za-z_][A-Za-z0-9_.-]{0,99}", ref):
            return None
        return _resolved_object(components.get(ref.rsplit("/", 1)[-1]), {}) if ref.rsplit("/", 1)[-1] in components else None
    if schema.get("type") == "array":
        return _resolved_object(schema.get("items"), components)
    props = schema.get("properties")
    if not isinstance(props, dict) or len(props) > 100:
        return None
    required = schema.get("required", [])
    if not isinstance(required, list) or len(required) > 100:
        return None
    if not all(isinstance(x, str) for x in required):
        return None
    return {"properties": props, "required": set(required)}


def _field_mismatch(fields: list, resolved: dict | None) -> bool:
    if resolved is None:
        return True
    props = resolved["properties"]
    primitives = {"str": "string", "int": "integer", "float": "number", "bool": "boolean"}
    for item in fields:
        if not isinstance(item, dict) or not _only_source_key(item.get("name")):
            return True
        name = item["name"]
        if name not in props or not isinstance(props[name], dict):
            return True
        hint = item.get("type")
        actual = props[name].get("type")
        if hint in primitives and actual is not None and actual != primitives[hint]:
            # An integer is legal where a numeric field is declared, not vice versa.
            if not (hint == "float" and actual == "integer"):
                return True
        if item.get("required_hint") is True and name not in resolved["required"]:
            return True
    return False


def reconcile(static_contract: dict, static_schema: dict, openapi: dict) -> dict:
    """Return a bounded, non-secret review, never authorization to generate."""
    contract = _obj(static_contract, "static route contract")
    static = _obj(static_schema, "static schema")
    doc = _obj(openapi, "OpenAPI")
    if contract.get("schema_version") != ZIP_SCHEMA or static.get("schema_version") != STATIC_SCHEMA:
        raise InvalidRuntimeEvidence("unsupported static contract schema")
    sha = _obj(contract.get("input"), "static input").get("sha256")
    if not isinstance(sha, str) or not SHA256.fullmatch(sha) or sha != static.get("backend_sha256"):
        raise InvalidRuntimeEvidence("static contract/schema backend SHA mismatch")
    if contract.get("execution_performed") is not False or static.get("execution_performed") is not False:
        raise InvalidRuntimeEvidence("unexpected static execution flag")
    if not isinstance(doc.get("openapi"), str) or not re.fullmatch(r"3\.(0|1)\.\d+", doc["openapi"]):
        raise InvalidRuntimeEvidence("only OpenAPI 3.0/3.1 supported")
    paths = _obj(doc.get("paths"), "openapi.paths")
    if len(paths) > MAX_ROUTES:
        raise InvalidRuntimeEvidence("too many OpenAPI paths")
    components = _obj(doc.get("components", {}), "openapi.components")
    schemas = _obj(components.get("schemas", {}), "openapi.schemas")
    if len(schemas) > MAX_COMPONENTS:
        raise InvalidRuntimeEvidence("too many schemas")
    static_endpoints = _array(_obj(contract.get("api"), "static api").get("endpoints"), "api.endpoints")
    schema_routes = _array(static.get("routes"), "schema.routes")
    schema_by_key = {}
    for entry in schema_routes:
        e = _obj(entry, "schema route")
        path = e.get("path")
        methods = e.get("methods")
        if not _route(path) or not isinstance(methods, list) or not methods or not all(_method(m) for m in methods):
            raise InvalidRuntimeEvidence("unsafe static schema route")
        for method in methods:
            k = (path, method.upper())
            if k in schema_by_key:
                raise InvalidRuntimeEvidence("ambiguous static schema route")
            schema_by_key[k] = e
    for path, path_ops in paths.items():
        if not _route(path) or not isinstance(path_ops, dict):
            raise InvalidRuntimeEvidence("unsafe OpenAPI path")
    issues = []
    passed = []
    unresolved = []
    checked = set()

    def issue(path, method, code):
        if len(issues) < MAX_ISSUES:
            issues.append({"path": path, "method": method, "code": code})

    if not static_endpoints:
        raise InvalidRuntimeEvidence("empty static API contract cannot be verified")
    for entry in static_endpoints:
        e = _obj(entry, "endpoint")
        path = e.get("path")
        verbs = e.get("methods")
        if not _route(path) or not isinstance(verbs, list) or not verbs or not all(_method(m) for m in verbs):
            raise InvalidRuntimeEvidence("unsafe declared endpoint")
        for method in verbs:
            method = method.upper()
            key = (path, method)
            if key in checked:
                raise InvalidRuntimeEvidence("duplicate declared endpoint")
            checked.add(key)
            info = schema_by_key.get(key)
            if info is None:
                issue(path, method, "STATIC_SCHEMA_ROUTE_MISSING")
                continue
            if e.get("mount") not in ("app_declaration", "local_router_mount_declaration"):
                issue(path, method, "ROUTER_MOUNT_UNVERIFIED")
                continue
            endpoint = paths.get(path, {})
            operation = endpoint.get(method.lower()) if isinstance(endpoint, dict) else None
            if not isinstance(operation, dict):
                issue(path, method, "OPENAPI_OPERATION_MISSING")
                continue
            declared = {p["name"] for p in _array(info.get("parameters", []), "parameters", 64)
                        if isinstance(p, dict) and p.get("location_hint") == "path" and _only_source_key(p.get("name"))}
            runtime_params = operation.get("parameters", [])
            if not isinstance(runtime_params, list) or len(runtime_params) > 64:
                issue(path, method, "OPENAPI_PARAMETERS_INVALID")
                continue
            actual = {p.get("name") for p in runtime_params
                      if isinstance(p, dict) and p.get("in") == "path" and p.get("required") is True
                      and _only_source_key(p.get("name"))}
            path_names = set(re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", path))
            if declared != actual or actual != path_names:
                issue(path, method, "PATH_PARAMETERS_MISMATCH")
                continue
            expected_body = info.get("request_body")
            if expected_body is not None:
                if not isinstance(expected_body, dict) or not isinstance(expected_body.get("fields"), list):
                    issue(path, method, "STATIC_BODY_HINT_INVALID")
                    continue
                req = operation.get("requestBody", {})
                media = req.get("content", {}) if isinstance(req, dict) else {}
                json_schema = media.get("application/json", {}) if isinstance(media, dict) else {}
                body_schema = json_schema.get("schema", {}) if isinstance(json_schema, dict) else {}
                fields = _resolved_object(body_schema, schemas)
                if _field_mismatch(expected_body["fields"], fields):
                    issue(path, method, "REQUEST_FIELDS_MISMATCH")
                    continue
            response = info.get("response", {})
            models = response.get("models", []) if isinstance(response, dict) else []
            if models:
                success_responses = operation.get("responses", {})
                response_entry = success_responses.get("200", {}) if isinstance(success_responses, dict) else {}
                content = response_entry.get("content", {}) if isinstance(response_entry, dict) else {}
                body = content.get("application/json", {}) if isinstance(content, dict) else {}
                response_schema = body.get("schema", {}) if isinstance(body, dict) else {}
                available = _resolved_object(response_schema, schemas)
                expected = [f for model in models if isinstance(model, dict)
                            for f in model.get("fields", [])]
                if _field_mismatch(expected, available):
                    issue(path, method, "RESPONSE_MODEL_FIELDS_MISMATCH")
                    continue
            else:
                unresolved.append({"path": path, "method": method, "reason": "RESPONSE_PAYLOAD_UNVERIFIED"})
            passed.append({"path": path, "method": method, "evidence": "OPENAPI_DECLARATION_MATCH_ONLY"})
    return {
        "schema_version": SCHEMA,
        "status": "MISMATCH" if issues else "DECLARATIONS_MATCH_REVIEW_REQUIRED",
        "generation_allowed": False,
        "runtime_code_executed_by_reconciler": False,
        "runtime_origin_attested": False,
        "backend_sha256": sha,
        "matched_declarations": passed,
        "issues": issues,
        "unresolved": unresolved[:MAX_ISSUES],
        "summary": {"declared_operations": len(checked), "matched": len(passed),
                    "mismatched": len(issues), "unverified_response_shapes": len(unresolved)},
        "limitations": ["supplied_openapi_may_not_come_from_the_scanned_zip",
                        "openapi_does_not_verify_return_values_or_business_logic",
                        "no_auth_secrets_licenses_or_risky_backend_execution_checked",
                        "owner_review_and_separate_isolated_execution_still_required"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review static backend ZIP routes against a separately supplied OpenAPI JSON")
    parser.add_argument("--backend", type=Path, required=True, help="read-only JSON static route report")
    parser.add_argument("--schema", type=Path, required=True, help="read-only JSON static schema report")
    parser.add_argument("--openapi", type=Path, required=True, help="approved runtime OpenAPI JSON file; no URLs accepted")
    parser.add_argument("--out", type=Path, help="NEW file, refuse overwrite")
    args = parser.parse_args(argv)
    try:
        result = reconcile(_read_json(args.backend), _read_json(args.schema), _read_json(args.openapi))
        payload = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.out is None:
            sys.stdout.write(payload)
        else:
            with args.out.open("x", encoding="utf-8") as f:
                f.write(payload)
        return 0 if result["status"] != "MISMATCH" else 3
    except (OSError, InvalidRuntimeEvidence) as exc:
        print("[REA] OpenAPI reconciliation refused: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
