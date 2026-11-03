"""Synthetic-only, read-only JSON/permission contract tests. No customer assets."""
from __future__ import annotations

import copy
import json

import pytest

from rea.adapter.response_contract import (
    InvalidResponseContract, auth_effect, validate_synthetic_response_contract,
)

BINDINGS = {
    "list": {"path": "/api/jobs", "field": "items"},
    "metrics": {"path": "/api/metrics", "field": "__root__"},
    "detail": {"path": "/api/jobs/{ticket_id}", "field": "__root__", "path_param": "ticket_id"},
    "presentation": {
        "item": {"id": "ticket", "name": "task", "category": "department", "status": "phase"},
        "metrics": {"total": "all_count", "completed": "success_count", "pending": "queued_count"},
        "detail_fields": ["ticket", "task", "department", "phase", "duration_ms"],
    },
}


def sample():
    rows = [
        {"ticket": "A-1", "task": "Synthetic report", "department": "audit", "phase": "done"},
        {"ticket": "B-2", "task": "Synthetic checks", "department": "quality", "phase": "pending"},
    ]
    values = {
        "list": {"items": rows},
        "metrics": {"all_count": 2, "success_count": 1, "queued_count": 1},
        "detail": {**rows[0], "duration_ms": 32},
    }
    return {role: {"status": 200, "content_type": "application/json; charset=utf-8",
                   "body": json.dumps(body, ensure_ascii=False).encode("utf-8")}
            for role, body in values.items()}


def check(samples=None, bindings=None, **kwargs):
    return validate_synthetic_response_contract(
        copy.deepcopy(BINDINGS if bindings is None else bindings),
        sample() if samples is None else samples,
        selected_id=kwargs.pop("selected_id", "A-1"),
        completed_statuses=kwargs.pop("completed_statuses", ["done"]),
        pending_statuses=kwargs.pop("pending_statuses", ["pending"]),
        list_coverage=kwargs.pop("list_coverage", "complete"),
        **kwargs,
    )


def modify(role, update):
    samples = sample()
    parsed = json.loads(samples[role]["body"])
    update(parsed)
    samples[role]["body"] = json.dumps(parsed, ensure_ascii=False).encode("utf-8")
    return samples


def test_complete_synthetic_mapping_is_review_only_and_does_not_expose_values():
    result = check()
    assert result == check()
    assert result["status"] == "SYNTHETIC_SHAPES_MATCH_REVIEW_REQUIRED"
    assert result["sample_rows"] == 2
    assert result["checked_roles"] == ["list", "metrics", "detail"]
    assert result["customer_runtime_verified"] is False
    assert result["generation_allowed"] is False
    assert result["execution_performed"] is False and result["network_performed"] is False
    serialized = json.dumps(result)
    assert "A-1" not in serialized and "Synthetic" not in serialized


def test_owner_mapping_does_not_use_default_names():
    assert check()["sample_rows"] == 2
    default = copy.deepcopy(BINDINGS)
    default.pop("presentation")
    with pytest.raises(InvalidResponseContract, match="explicit presentation"):
        check(bindings=default)


@pytest.mark.parametrize("role,status,effect", [
    ("list", 200, "READ_OK"), ("metrics", 200, "READ_OK"),
    ("detail", 200, "READ_OK"),
    ("list", 401, "CLEAR_PROTECTED_VIEW"), ("metrics", 403, "CLEAR_PROTECTED_VIEW"),
    ("list", 403, "CLEAR_PROTECTED_VIEW"), ("detail", 401, "CLEAR_PROTECTED_VIEW"),
    ("detail", 403, "DETAIL_ONLY_ERROR"), ("detail", 404, "DETAIL_ONLY_ERROR"),
    ("detail", 500, "DETAIL_ONLY_ERROR"), ("metrics", 503, "GLOBAL_API_ERROR"),
])
def test_authorization_effect_matrix(role, status, effect):
    assert auth_effect(role, status) == effect


@pytest.mark.parametrize("role,status", [
    ("unknown", 200), ("list", True), ("detail", 99), ("metrics", 600)
])
def test_invalid_authorization_policy_input_rejected(role, status):
    with pytest.raises(InvalidResponseContract, match="invalid role"):
        auth_effect(role, status)


@pytest.mark.parametrize("key", ["list", "metrics", "detail"])
@pytest.mark.parametrize("code", [401, 403, 500])
def test_non200_sample_is_not_accepted_even_for_detail_error(key, code):
    samples = sample()
    samples[key]["status"] = code
    with pytest.raises(InvalidResponseContract, match="not 200"):
        check(samples)


@pytest.mark.parametrize("mutation", [
    lambda x: x["items"][0].pop("ticket"),
    lambda x: x["items"][0].update(task=None),
    lambda x: x["items"][0].update(phase="unknown"),
    lambda x: x["items"].append(copy.deepcopy(x["items"][0])),
    lambda x: x.update(items={"not": "an array"}),
    lambda x: x["items"].append("not-an-object"),
])
def test_wrong_list_shapes_refused(mutation):
    with pytest.raises(InvalidResponseContract):
        check(modify("list", mutation))


@pytest.mark.parametrize("mutation", [
    lambda x: x.pop("all_count"),
    lambda x: x.update(all_count=3),
    lambda x: x.update(success_count=True),
    lambda x: x.update(queued_count=-1),
    lambda x: x.update(success_count=0),
    lambda x: x.update(all_count=2.0),
])
def test_wrong_metrics_shapes_and_semantics_refused(mutation):
    with pytest.raises(InvalidResponseContract):
        check(modify("metrics", mutation))


@pytest.mark.parametrize("mutation", [
    lambda x: x.pop("duration_ms"),
    lambda x: x.update(ticket="B-2"),
    lambda x: x.update(task="Not the selected item"),
    lambda x: x.update(duration_ms={"nested": "not scalar"}),
])
def test_wrong_detail_shape_or_identity_refused(mutation):
    with pytest.raises(InvalidResponseContract):
        check(modify("detail", mutation))


def test_selected_row_must_exist_and_owner_status_semantics_must_be_explicit():
    with pytest.raises(InvalidResponseContract, match="selected detail ID"):
        check(selected_id="does-not-exist")
    with pytest.raises(InvalidResponseContract, match="overlap"):
        check(completed_statuses=["done"], pending_statuses=["pending", "done"])
    with pytest.raises(InvalidResponseContract, match="only explicitly complete"):
        check(list_coverage="paginated")


@pytest.mark.parametrize("role", ["list", "metrics", "detail"])
def test_unauthorized_secret_fields_anywhere_are_refused(role):
    def mutate(x):
        x["nested"] = {"user": {"refresh_token": "NEVER_ECHO_THIS_VALUE"}}
    with pytest.raises(InvalidResponseContract, match="credential field") as err:
        check(modify(role, mutate))
    assert "NEVER_ECHO_THIS_VALUE" not in str(err.value)


def test_duplicate_json_key_and_nonstandard_number_are_refused():
    samples = sample()
    samples["metrics"]["body"] = b'{"all_count":2,"all_count":2,"success_count":1,"queued_count":1}'
    with pytest.raises(InvalidResponseContract):
        check(samples)
    samples = sample()
    samples["metrics"]["body"] = b'{"all_count":NaN,"success_count":1,"queued_count":1}'
    with pytest.raises(InvalidResponseContract):
        check(samples)


@pytest.mark.parametrize("invalid_body", [b"{bad-json", b"[]", b"", b'{"x":{}', b"\xff"])
def test_malformed_json_or_wrong_root_is_refused(invalid_body):
    samples = sample()
    samples["metrics"]["body"] = invalid_body
    with pytest.raises(InvalidResponseContract):
        check(samples)


def test_mime_body_cap_nested_depth_and_untrusted_status_are_refused():
    examples = sample()
    examples["list"]["content_type"] = "text/html"
    with pytest.raises(InvalidResponseContract, match="not JSON"):
        check(examples)
    examples = sample()
    examples["list"]["body"] = b" " * (1024 * 1024 + 1)
    with pytest.raises(InvalidResponseContract, match="1 MiB"):
        check(examples)
    examples = sample()
    nested = {"child": {}}
    for _ in range(12):
        nested = {"child": nested}
    examples["detail"]["body"] = json.dumps(nested).encode()
    with pytest.raises(InvalidResponseContract, match="structure exceeds"):
        check(examples)
    examples = sample()
    examples["detail"]["status"] = True
    with pytest.raises(InvalidResponseContract, match="not 200"):
        check(examples)


def test_invalid_owner_paths_are_refused_without_running_anything():
    bad = copy.deepcopy(BINDINGS)
    bad["list"]["path"] = "https://external.example/api/jobs"
    with pytest.raises(InvalidResponseContract, match="invalid owner"):
        check(bindings=bad)
    bad = copy.deepcopy(BINDINGS)
    bad["detail"]["path_param"] = "__proto__"
    with pytest.raises(InvalidResponseContract, match="invalid owner"):
        check(bindings=bad)


def test_samples_exactly_three_get_roles_only():
    missing = sample()
    missing.pop("detail")
    with pytest.raises(InvalidResponseContract, match="exact list"):
        check(missing)
    injected = sample()
    injected["write"] = {"status": 200, "content_type": "application/json", "body": b"{}"}
    with pytest.raises(InvalidResponseContract, match="exact list"):
        check(injected)
