"""The release gate must never turn synthetic CI into real approval."""
from __future__ import annotations

from datetime import date
import json

from scripts.rea_sale_gate import GATES, assess, load_record, main, template

SHA = "a" * 40


def verified():
    result = template(SHA)
    for gate in GATES:
        result["checks"][gate] = {
            "status": "VERIFIED", "reviewer": "independent-reviewer",
            "verified_on": date.today().isoformat(),
            "evidence_refs": ["operator-reviewed-evidence-reference"],
        }
    return result


def test_blank_ledger_is_blocked():
    result = assess(template(SHA), SHA)
    assert result["decision"] == "BLOCKED_NOT_APPROVED_FOR_SALE"
    assert len(result["issues"]) == len(GATES)
    assert result["automated_legal_or_human_certification"] is False


def test_every_gate_needs_independent_evidence():
    record = verified()
    assert assess(record, SHA)["decision"] == "READY_FOR_SELLER_FINAL_REVIEW"
    for name in GATES:
        for field, value in (("reviewer", ""), ("verified_on", ""),
                             ("evidence_refs", []), ("status", "PASS")):
            broken = verified()
            broken["checks"][name][field] = value
            assert assess(broken, SHA)["decision"] == "BLOCKED_NOT_APPROVED_FOR_SALE"


def test_mismatched_commit_and_missing_gate_are_blocked():
    assert assess(verified(), "b" * 40)["decision"] == "BLOCKED_NOT_APPROVED_FOR_SALE"
    record = verified()
    del record["checks"][next(iter(GATES))]
    assert assess(record, SHA)["decision"] == "BLOCKED_NOT_APPROVED_FOR_SALE"


def test_cli_init_check_and_nonoverwrite(tmp_path, capsys):
    path = tmp_path / "ledger.json"
    assert main(["--init", str(path), "--source-sha", SHA]) == 0
    assert main(["--init", str(path), "--source-sha", SHA]) == 2
    assert main(["--check", str(path), "--source-sha", SHA]) == 2
    assert "BLOCKED_NOT_APPROVED_FOR_SALE" in capsys.readouterr().out
    path.write_text(json.dumps(verified()), encoding="utf-8")
    assert main(["--check", str(path), "--source-sha", SHA]) == 0
    assert "READY_FOR_SELLER_FINAL_REVIEW" in capsys.readouterr().out


def test_duplicate_json_key_rejected(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"schema_version":"x","schema_version":"y"}', encoding="utf-8")
    try:
        load_record(path)
        assert False, "duplicate keys must fail"
    except ValueError:
        pass


def test_future_date_and_invalid_evidence_rejected():
    record = verified()
    gate = next(iter(GATES))
    record["checks"][gate]["verified_on"] = "2999-01-01"
    assert assess(record, SHA)["decision"] == "BLOCKED_NOT_APPROVED_FOR_SALE"
    record = verified()
    record["checks"][gate]["evidence_refs"] = ["   "]
    assert assess(record, SHA)["decision"] == "BLOCKED_NOT_APPROVED_FOR_SALE"
