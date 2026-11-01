"""Review-only typed FastAPI request/response declarations from a backend ZIP.

Never imports, extracts, or executes source. Model and route hints are neither
OpenAPI nor proof of runtime behavior. Owner approval and sandbox HTTP verification
remain mandatory before generated UI integration.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import zipfile

from rea.adapter.backend_zip import (
    _zip_members, inspect_backend_zip, UnsafeBackendZip,
)

SCHEMA = "rea.backend_schema.v0.1"
MAX_DECLARATIONS = 500
MAX_FIELDS = 64
MAX_TEXT = 64
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z_0-9]{0,63}$")
PRIMITIVES = frozenset({"str", "int", "float", "bool", "bytes", "None"})
WRAPPERS = frozenset({"list", "List", "set", "Set", "tuple", "Tuple", "dict", "Dict",
                      "Optional", "Union", "Sequence", "Annotated"})


class UnsafeSchema(ValueError):
    """The ZIP changed, schema input is unsafe, or the request is unsupported."""


def _name(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Name) and IDENTIFIER.fullmatch(node.id):
        return node.id
    if isinstance(node, ast.Attribute) and IDENTIFIER.fullmatch(node.attr):
        return node.attr
    return None


def _type(node: ast.AST | None, known: set[str], depth: int = 0) -> str | None:
    """Only an allowlisted grammar; never serialize source expressions/defaults."""
    if depth > 4:
        return None
    atom = _name(node)
    if atom and atom in (PRIMITIVES | WRAPPERS | known):
        return atom
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        lhs, rhs = _type(node.left, known, depth + 1), _type(node.right, known, depth + 1)
        return f"{lhs} | {rhs}" if lhs and rhs else None
    if isinstance(node, ast.Subscript):
        base = _name(node.value)
        if base not in WRAPPERS:
            return None
        if base == "Annotated":
            # Annotated[T, Query(...)] retains only T, not arbitrary metadata.
            if not isinstance(node.slice, ast.Tuple) or not node.slice.elts:
                return None
            return _type(node.slice.elts[0], known, depth + 1)
        if base == "Literal":
            return None
        parts = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
        if len(parts) > 3:
            return None
        child = [_type(x, known, depth + 1) for x in parts]
        if all(child):
            value = f"{base}[{', '.join(child)}]"
            return value if len(value) <= 120 else None
    return None


def _default_kind(node: ast.AST | None) -> str:
    if node is None:
        return "required"
    if isinstance(node, ast.Call) and _name(node.func) == "Field":
        if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value is ...:
            return "required"
        if any(k.arg == "default" and isinstance(k.value, ast.Constant) and k.value.value is ... for k in node.keywords):
            return "required"
        if not node.args and not any(k.arg in ("default", "default_factory") for k in node.keywords):
            return "required"
    return "optional_or_defaulted"


def _models(tree: ast.Module) -> dict[str, dict]:
    """Model declarations are accepted only for a syntactic BaseModel parent."""
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)
               and IDENTIFIER.fullmatch(n.name) and any(_name(b) == "BaseModel" for b in n.bases)]
    known = {n.name for n in classes}
    models: dict[str, dict] = {}
    for node in classes[:MAX_DECLARATIONS]:
        fields: list[dict] = []
        for member in node.body:
            if not isinstance(member, ast.AnnAssign) or not isinstance(member.target, ast.Name):
                continue
            key = member.target.id
            if key.startswith("_") or not IDENTIFIER.fullmatch(key):
                continue
            if len(fields) >= MAX_FIELDS:
                break
            annotation = _type(member.annotation, known)
            fields.append({"name": key, "type": annotation or "unknown",
                           "required_hint": _default_kind(member.value) == "required"})
        models[node.name] = {"model": node.name, "fields": fields,
                             "evidence": "LOCAL_BASEMODEL_AST_DECLARATION",
                             "runtime_verified": False}
    return models


def _route_function_hints(node: ast.FunctionDef | ast.AsyncFunctionDef,
                          models: dict[str, dict], route: str, decorator: ast.Call | None) -> dict:
    """Only matching declaration/line hints, no response body inference."""
    known = set(models)
    names = [arg for arg in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
             if IDENTIFIER.fullmatch(arg.arg) and arg.arg not in ("self", "cls")]
    defaults = ([None] * max(0, len(node.args.posonlyargs) + len(node.args.args) - len(node.args.defaults))
                + list(node.args.defaults) + list(node.args.kw_defaults))
    parameters: list[dict] = []
    body: dict | None = None
    for arg, default in zip(names, defaults):
        annotation = _type(arg.annotation, known)
        if arg.arg in re.findall(r"\{([A-Za-z_][A-Za-z_0-9]*)\}", route):
            location = "path"
        elif annotation in models:
            location = "body_model"
        elif annotation is None:
            location = "unresolved"
        else:
            location = "query_or_dependency"
        item = {"name": arg.arg, "type": annotation or "unknown", "location_hint": location,
                "required_hint": default is None}
        parameters.append(item)
        if location == "body_model" and body is None:
            body = models[annotation]
    response_annotation = _type(node.returns, known)
    response_source = "return_annotation" if response_annotation else "unknown"
    if decorator is not None:
        expression = next((kw.value for kw in decorator.keywords if kw.arg == "response_model"), None)
        declared = _type(expression, known)
        if declared:
            response_annotation = declared
            response_source = "response_model_declaration"
    referenced = re.findall(r"\b[A-Za-z_][A-Za-z_0-9]*\b", response_annotation or "")
    model_names = sorted(set(referenced).intersection(models))
    return {
        "parameters": parameters[:MAX_FIELDS],
        "request_body": body,
        "response": {"type_hint": response_annotation or "unknown", "source": response_source,
                     "models": [models[k] for k in model_names],
                     "runtime_verified": False},
        "verification": "STATIC_AST_HINT_ONLY",
    }


def inspect_backend_schema(source: Path) -> dict:
    """Reopen the bounded source ZIP and tie route hints to original ZIP SHA.

    Existing path, member and compression defenses are reused. Reject a ZIP
    changed between static route inspection and this schema inspection.
    """
    source = Path(source)
    baseline = inspect_backend_zip(source)
    try:
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        with os.fdopen(os.open(source, flags), "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise UnsafeSchema("backend source changed")
            initial = os.fstat(stream.fileno())
            with zipfile.ZipFile(stream) as archive:
                infos = _zip_members(archive)
                files: dict[str, tuple[ast.Module, dict[str, dict]]] = {}
                for item in infos:
                    if item.is_dir() or not item.filename.lower().endswith(".py"):
                        continue
                    try:
                        tree = ast.parse(archive.read(item).decode("utf-8-sig"), filename=item.filename)
                    except (SyntaxError, ValueError, UnicodeError):
                        continue
                    files[item.filename] = (tree, _models(tree))
            stream.seek(0)
            digest = hashlib.sha256()
            for chunk in iter(lambda: stream.read(65536), b""):
                digest.update(chunk)
            if digest.hexdigest() != baseline["input"]["sha256"]:
                raise UnsafeSchema("ZIP changed during schema scan")
            if os.fstat(stream.fileno()).st_size != initial.st_size:
                raise UnsafeSchema("ZIP changed during schema scan")
    except (OSError, zipfile.BadZipFile, EOFError) as exc:
        raise UnsafeSchema("schema scan could not verify source") from exc
    routes = []
    for endpoint in baseline["api"]["endpoints"]:
        filename = endpoint["source"]
        record = {"path": endpoint["path"], "methods": endpoint["methods"],
                  "source": filename, "line": endpoint["line"], "mount": endpoint["mount"],
                  "verification": "STATIC_AST_HINT_ONLY"}
        parsed = files.get(filename)
        if parsed is not None:
            tree, models = parsed
            node = next((n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                         and n.lineno == endpoint["line"]), None)
            if node is not None:
                decorators = []
                for dec in node.decorator_list:
                    if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Attribute):
                        continue
                    declared_path = dec.args[0] if dec.args else next(
                        (x.value for x in dec.keywords if x.arg == "path"), None)
                    if (isinstance(declared_path, ast.Constant)
                            and isinstance(declared_path.value, str)
                            and endpoint["path"].endswith(declared_path.value)
                            and dec.func.attr in ("get", "post", "put", "patch", "delete", "api_route")):
                        decorators.append(dec)
                # One undecidable decorated function must not borrow the other
                # route's response_model declaration.
                matching = decorators[0] if len(decorators) == 1 else None
                record.update(_route_function_hints(node, models, endpoint["path"], matching))
        record.setdefault("parameters", [])
        record.setdefault("request_body", None)
        record.setdefault("response", {"type_hint": "unknown", "source": "unknown", "models": [],
                                       "runtime_verified": False})
        routes.append(record)
    return {
        "schema_version": SCHEMA,
        "status": "REVIEW_REQUIRED",
        "generation_allowed": False,
        "execution_performed": False,
        "backend_sha256": baseline["input"]["sha256"],
        "routes": routes,
        "limitations": ["static_annotations_only", "models_imported_from_other_modules_not_resolved",
                        "query_dependency_disambiguation_not_verified", "default_values_not_exported",
                        "no_runtime_openapi_or_response_payload_verification"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="REA read-only FastAPI ZIP static schema review")
    parser.add_argument("zip_file", type=Path)
    parser.add_argument("--out", type=Path, help="NEW JSON file, no overwrite")
    args = parser.parse_args(argv)
    try:
        result = inspect_backend_schema(args.zip_file)
        output = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.out is None:
            print(output, end="")
        else:
            with args.out.open("x", encoding="utf-8") as handle:
                handle.write(output)
            print(f"[REA] review-only static schema written: {args.out}")
        return 0
    except (UnsafeBackendZip, UnsafeSchema, OSError, ValueError) as exc:
        print(f"[REA] REFUSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
