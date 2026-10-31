"""Independent synthetic-only seller delivery rehearsal gate."""
from __future__ import annotations

import json
import pytest
from scripts.rea_lite_delivery_rehearsal import main, run_rehearsal


def test_three_real_parser_delivery_flows():
    receipt = run_rehearsal()
    assert receipt['status'] == 'THREE_SYNTHETIC_MACHINE_REHEARSALS_PASS'
    assert receipt['case_count'] == 3
    assert [entry['source_type'] for entry in receipt['cases']] == ['csv', 'json', 'csv']
    assert [entry['theme'] for entry in receipt['cases']] == ['cafe', 'inventory', 'office']
    assert [entry['owner_mapping_test'] for entry in receipt['cases']] == [False, False, True]
    assert all(entry['status'] == 'PASS' and entry['no_overwrite_test'] for entry in receipt['cases'])
    assert all(entry['html_bytes'] > 1000 and entry['machine_elapsed_ms'] >= 0 for entry in receipt['cases'])
    assert receipt['human_delivery_time_measured'] is False
    assert receipt['human_windows_acceptance'] == 'NOT_RUN'
    assert receipt['commercial_approval'] == 'NOT_GRANTED'


def test_receipt_written_once_no_override(tmp_path):
    target = tmp_path / 'new' / 'receipt.json'
    assert main(['--receipt', str(target)]) == 0
    payload = json.loads(target.read_text(encoding='utf-8'))
    assert payload['case_count'] == 3
    assert all(len(entry['html_sha256']) == 64 for entry in payload['cases'])
    old_bytes = target.read_bytes()
    with pytest.raises(SystemExit) as exc:
        main(['--receipt', str(target)])
    assert exc.value.code == 2
    assert target.read_bytes() == old_bytes


def test_rehearsal_receipt_excludes_raw_customer_data():
    receipt = run_rehearsal()
    serialized = json.dumps(receipt)
    assert 'Cold Brew' not in serialized
    assert 'Notebook' not in serialized
    assert 'source_path' not in serialized
    assert 'real_customer_data_used' in serialized
