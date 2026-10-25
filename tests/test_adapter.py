"""Deterministic synthetic negative/positive tests for Fable/Astra boundary."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import pytest
from rea.adapter.fable_to_astra import InvalidFable, project_fable, verify_astra

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "samples/fable_record_redacted.json").read_text(encoding="utf-8"))


def case():
    return copy.deepcopy(DATA)


def test_inferred_never_observed():
    r = project_fable(case())
    assert [o["certainty"] for o in r["astra_observation_bundle"]["observations"]] == ["inferred", "inferred"]
    assert [o["feature"] for o in r["astra_observation_bundle"]["observations"]] == ["navigation", "filter"]


def test_approval_gate():
    r = project_fable(case())
    assert r["status"] == "REVIEW_REQUIRED" and not r["generation_allowed"]
    assert not r["implementation_ready"] and r["approved_semantic_bindings"] == []
    assert r["db_api_mapping_status"] == "not_started"


def test_query_fragment_path_not_serialized():
    d = case()
    d["target"]["input_url"] = "https://example.org/personal/SECRET_PATH?access_token=SECRET_TOKEN#SECRET_FRAG"
    data = json.dumps(project_fable(d))
    assert all(x not in data for x in ("SECRET_TOKEN", "SECRET_PATH", "SECRET_FRAG"))


def test_technical_inference_only_counts():
    r = project_fable(case())
    assert list(r["technical_finding_counts"].values()) == [1, 1, 1, 1]
    assert "/api/items" not in json.dumps(r)


@pytest.mark.parametrize("mode", ["static", "runtime"])
def test_no_interactions_without_record(mode):
    d = case()
    d["scan_mode"] = mode
    d.pop("record")
    assert project_fable(d)["astra_observation_bundle"] is None


def test_no_markers_no_bundle():
    d = case()
    d["record"]["interactions"] = []
    assert project_fable(d)["astra_observation_bundle"] is None


@pytest.mark.parametrize("path,value", [
    (("schema_version",), "2.0"),
    (("target",), None),
    (("api", "endpoints"), "garbage"),
    (("charts",), {}),
    (("scanned_at",), "2026-10-25T12:00:00"),
    (("target", "input_url"), "file:///etc/passwd"),
    (("target", "input_url"), "https://user:secret@example.org/"),
    (("scan_mode",), "admin"),
    (("record", "allowed_origins"), ["https://out-of-scope.example.org"]),
])
def test_invalid_inputs(path, value):
    d = case()
    owner = d
    for component in path[:-1]:
        owner = owner[component]
    owner[path[-1]] = value
    with pytest.raises(InvalidFable):
        project_fable(d)


@pytest.mark.parametrize("source_ref", ["../private", ".env", "x?token=abc"])
def test_bad_source_ref(source_ref):
    with pytest.raises(InvalidFable):
        project_fable(case(), source_ref=source_ref)


def test_selector_never_emitted():
    d = case()
    d["record"]["interactions"][0]["selector"] = "[secret=LEAK_THIS]"
    assert "LEAK_THIS" not in json.dumps(project_fable(d))


def test_bad_marker_ignored():
    d = case()
    d["record"]["interactions"][0]["type"] = "submit"
    r = project_fable(d)
    assert (r["record_markers_accepted"], r["record_markers_ignored"]) == (1, 1)


def test_duplicate_marker_ignored():
    d = case()
    d["record"]["interactions"].append(copy.deepcopy(d["record"]["interactions"][0]))
    r = project_fable(d)
    assert (r["record_markers_accepted"], r["record_markers_ignored"]) == (2, 1)


def test_marker_limit():
    d = case()
    d["record"]["interactions"] *= 101
    with pytest.raises(InvalidFable):
        project_fable(d)


def test_unique_evidence_linkage():
    bundle = project_fable(case())["astra_observation_bundle"]
    assert len({e["id"] for e in bundle["evidence"]}) == 2
    assert [e["id"] for e in bundle["evidence"]] == [o["evidence_ids"][0] for o in bundle["observations"]]


def test_deterministic():
    assert project_fable(case()) == project_fable(case())


def test_preview_cli():
    p = subprocess.run([sys.executable, "-m", "rea.adapter.fable_to_astra",
                       "samples/fable_record_redacted.json", "--preview-only"],
                       cwd=ROOT, text=True, capture_output=True)
    assert p.returncode == 0, p.stderr
    r = json.loads(p.stdout)
    assert r["astra_contract_validation"] == "NOT_RUN" and r["astra_functional_spec_draft"] is None


def test_actual_astra_schema_and_unresolved():
    pytest.importorskip("astra_contracts.observation")
    r = verify_astra(project_fable(case()))
    assert r["astra_contract_validation"] == "VALIDATED"
    spec = r["astra_functional_spec_draft"]
    assert not spec["candidate_features"] and len(spec["unresolved"]) == 2
    assert spec["db_api_mapping_status"] == "not_started" and not spec["implementation_ready"]


def test_actual_astra_static():
    pytest.importorskip("astra_contracts.observation")
    d = case()
    d["scan_mode"] = "static"
    d.pop("record")
    r = verify_astra(project_fable(d))
    assert r["astra_contract_validation"] == "NO_UI_OBSERVATIONS" and r["astra_functional_spec_draft"] is None
