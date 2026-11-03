"""Offline, bounded synthetic JSON response-contract acceptance preflight.

No ZIP reading, code execution, HTTP, filesystem writes, or customer authentication.
A passing self-authored sample does not establish runtime truth, customer rights,
tenant isolation, data safety, or permission to generate/deploy.
"""
from __future__ import annotations

import json
import math
import re

from rea.adapter.frontend_bridge import BridgeError, _valid_bindings

SCHEMA = "rea.response_acceptance.v0.1"
MAX_BODY = 1024 * 1024
MAX_ROWS = 10000
MAX_DEPTH = 8
SECRET_NAME = re.compile(
    r"(?:^|_)(?:password|passwd|token|secret|credential|cookie|authorization|"
    r"session|private_key|api_key|access_key)(?:$|_)", re.IGNORECASE
)
STATUS_NAME = re.compile(r"^[a-zA-Z0-9_-]{1,32}$")


class InvalidResponseContract(ValueError):
    """Static shape or permission assumption was rejected without body disclosure."""


def auth_effect(role: str, status: int) -> str:
    """Client policy contract, not a server authorization implementation."""
    if role not in ("list", "metrics", "detail") or type(status) is not int or not 100 <= status <= 599:
        raise InvalidResponseContract("invalid role or HTTP status")
    if status == 200:
        return "READ_OK"
    if status == 401 or (status == 403 and role in ("list", "metrics")):
        return "CLEAR_PROTECTED_VIEW"
    if role == "detail":
        return "DETAIL_ONLY_ERROR"
    return "GLOBAL_API_ERROR"


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    value = {}
    for key, entry in pairs:
        if key in value:
            raise InvalidResponseContract("duplicate JSON object key")
        value[key] = entry
    return value


def _no_constant(_: str) -> object:
    raise InvalidResponseContract("nonstandard JSON number")


def _inspect_tree(value: object) -> None:
    stack = [(value, 0)]
    count = 0
    while stack:
        current, depth = stack.pop()
        count += 1
        if count > 100000 or depth > MAX_DEPTH:
            raise InvalidResponseContract("JSON structure exceeds limits")
        if isinstance(current, dict):
            if len(current) > 256:
                raise InvalidResponseContract("too many JSON object fields")
            for key, child in current.items():
                if not isinstance(key, str) or len(key) > 128:
                    raise InvalidResponseContract("invalid JSON field name")
                normalized = re.sub(r"[^a-zA-Z0-9]+", "_", key).lower()
                if SECRET_NAME.search(normalized):
                    raise InvalidResponseContract("potential credential field in response")
                stack.append((child, depth + 1))
        elif isinstance(current, list):
            if len(current) > MAX_ROWS:
                raise InvalidResponseContract("JSON array exceeds limit")
            stack.extend((child, depth + 1) for child in current)
        elif isinstance(current, float) and not math.isfinite(current):
            raise InvalidResponseContract("nonfinite JSON number")


def _parse_sample(sample: object) -> object:
    if not isinstance(sample, dict) or set(sample) != {"status", "content_type", "body"}:
        raise InvalidResponseContract("sample must specify status, content_type, body")
    if type(sample["status"]) is not int or sample["status"] != 200:
        raise InvalidResponseContract("sample HTTP status is not 200")
    mime = sample["content_type"]
    if not isinstance(mime, str) or len(mime) > 128:
        raise InvalidResponseContract("invalid response media type")
    media = mime.split(";", 1)[0].strip().lower()
    if media != "application/json" and not (media.startswith("application/") and media.endswith("+json")):
        raise InvalidResponseContract("sample is not JSON")
    body = sample["body"]
    if isinstance(body, str):
        try:
            body = body.encode("utf-8")
        except UnicodeError as exc:
            raise InvalidResponseContract("invalid UTF-8 JSON sample") from exc
    if not isinstance(body, bytes) or len(body) > MAX_BODY:
        raise InvalidResponseContract("JSON body is missing or exceeds 1 MiB")
    try:
        parsed = json.loads(body.decode("utf-8"), object_pairs_hook=_unique_pairs,
                            parse_constant=_no_constant)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise InvalidResponseContract("malformed JSON sample") from exc
    _inspect_tree(parsed)
    return parsed


def _selected(value: object, field: str, role: str) -> object:
    if field == "__root__":
        return value
    if not isinstance(value, dict) or field not in value:
        raise InvalidResponseContract(role + ": declared wrapper field absent")
    return value[field]


def _string(value: object, label: str, limit: int = 512) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise InvalidResponseContract(label + ": expected nonempty bounded text")
    return value


def _status_groups(values: object, name: str) -> set[str]:
    if not isinstance(values, (list, tuple)) or not 1 <= len(values) <= 8:
        raise InvalidResponseContract(name + ": explicit status group required")
    if any(not isinstance(v, str) or not STATUS_NAME.fullmatch(v) for v in values):
        raise InvalidResponseContract(name + ": unsafe status label")
    if len(values) != len(set(values)):
        raise InvalidResponseContract(name + ": repeated status label")
    return set(values)


def validate_synthetic_response_contract(
    bindings: dict, samples: dict, *, selected_id: str,
    completed_statuses: list[str], pending_statuses: list[str],
    list_coverage: str,
) -> dict:
    """Validate explicitly mapped self-authored JSON examples without retaining values.

    Only a COMPLETE list is supported here: paginated/filtered data requires
    separate owner-defined count semantics and must not be marked accepted.
    """
    try:
        checked = _valid_bindings(bindings)
    except (BridgeError, TypeError, KeyError) as exc:
        raise InvalidResponseContract("invalid owner field or route binding") from exc
    if "presentation" not in checked:
        raise InvalidResponseContract("explicit presentation field mapping required")
    if list_coverage != "complete":
        raise InvalidResponseContract("only explicitly complete list samples supported")
    if not isinstance(samples, dict) or set(samples) != {"list", "metrics", "detail"}:
        raise InvalidResponseContract("exact list, metrics and detail samples required")
    selected_id = _string(selected_id, "selected ID", 200)
    completed = _status_groups(completed_statuses, "completed statuses")
    pending = _status_groups(pending_statuses, "pending statuses")
    if completed & pending:
        raise InvalidResponseContract("completed and pending statuses overlap")

    decoded = {role: _selected(_parse_sample(samples[role]), checked[role]["field"], role)
               for role in ("list", "metrics", "detail")}
    rows = decoded["list"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_ROWS:
        raise InvalidResponseContract("list: expected nonempty bounded JSON array")
    item_names = checked["presentation"]["item"]
    metrics_names = checked["presentation"]["metrics"]
    seen = set()
    counts = {"completed": 0, "pending": 0}
    chosen = None
    for item in rows:
        if not isinstance(item, dict):
            raise InvalidResponseContract("list: row must be JSON object")
        fields = {role: _string(item.get(name), "list " + role,
                                200 if role == "id" else 512)
                  for role, name in item_names.items()}
        if fields["id"] in seen:
            raise InvalidResponseContract("list: duplicate ID")
        seen.add(fields["id"])
        status = fields["status"]
        if status in completed:
            counts["completed"] += 1
        elif status in pending:
            counts["pending"] += 1
        else:
            raise InvalidResponseContract("list: unmapped status value")
        if fields["id"] == selected_id:
            chosen = fields
    if chosen is None:
        raise InvalidResponseContract("selected detail ID not present in complete list")

    metrics = decoded["metrics"]
    if not isinstance(metrics, dict):
        raise InvalidResponseContract("metrics: expected JSON object")
    values = {}
    for role, name in metrics_names.items():
        value = metrics.get(name)
        if type(value) is not int or value < 0 or value > MAX_ROWS:
            raise InvalidResponseContract("metrics: expected nonnegative integer " + role)
        values[role] = value
    if (values["total"] != len(rows) or values["completed"] != counts["completed"]
            or values["pending"] != counts["pending"]
            or values["total"] != values["completed"] + values["pending"]):
        raise InvalidResponseContract("metrics: total/status counts inconsistent with complete list")

    detail = decoded["detail"]
    if not isinstance(detail, dict):
        raise InvalidResponseContract("detail: expected JSON object")
    for role, name in item_names.items():
        if detail.get(name) != chosen[role]:
            raise InvalidResponseContract("detail: selected row mismatch")
    for name in checked["presentation"]["detail_fields"]:
        if name not in detail:
            raise InvalidResponseContract("detail: declared display field absent")
        value = detail[name]
        if not (value is None or type(value) in (str, int, float, bool)):
            raise InvalidResponseContract("detail: display value must be scalar")
        if isinstance(value, str) and len(value) > 1024:
            raise InvalidResponseContract("detail: display text exceeds limit")
        if isinstance(value, float) and not math.isfinite(value):
            raise InvalidResponseContract("detail: nonfinite display number")

    return {
        "schema_version": SCHEMA,
        "status": "SYNTHETIC_SHAPES_MATCH_REVIEW_REQUIRED",
        "execution_performed": False,
        "network_performed": False,
        "generation_allowed": False,
        "customer_runtime_verified": False,
        "list_coverage": "complete",
        "checked_roles": ["list", "metrics", "detail"],
        "sample_rows": len(rows),
    }
