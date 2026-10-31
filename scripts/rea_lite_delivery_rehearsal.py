"""Three isolated synthetic REA Lite seller-delivery rehearsals.

Runs the real rea.mvp parser and Lite builder. Timings are machine-only;
never call these measurements human delivery times or customer acceptance.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import platform
import re
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter_ns

from rea.lite_builder import build
from rea.mvp import parse_input, preview_schema, source_sha256

_EMBEDDED_DATA = re.compile(r'<script id="rea-data" type="application/octet-stream">([A-Za-z0-9+/=]+)</script>')
_CASES = (
    {
        'case': 'cafe_canonical_csv',
        'theme': 'cafe',
        'extension': '.csv',
        'source': 'id,title,category,price\nC01,Cold Brew,Drink,4000\nC02,Tea,Drink,3000\n',
        'mapping': None,
    },
    {
        'case': 'inventory_flat_json',
        'theme': 'inventory',
        'extension': '.json',
        'source': '[{"id":"I01","title":"Desk","category":"Furniture","qty":"3"},'
                  '{"id":"I02","title":"Chair","category":"Furniture","qty":"8"}]',
        'mapping': None,
    },
    {
        'case': 'office_owner_mapping_csv',
        'theme': 'office',
        'extension': '.csv',
        'source': 'stock_code,item_name,group_name,note\nO01,Notebook,Stationery,Blue\nO02,Pen,Stationery,Black\n',
        'mapping': {'id': 'stock_code', 'title': 'item_name', 'category': 'group_name'},
    },
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_rehearsal() -> dict:
    """Produce a privacy-safe receipt for three synthetic delivery paths."""
    cases = []
    with TemporaryDirectory(prefix='rea-lite-rehearsal-') as directory:
        workspace = Path(directory)
        for scenario in _CASES:
            started = perf_counter_ns()
            identifier = scenario['case']
            source = workspace / (identifier + scenario['extension'])
            source.write_text(scenario['source'], encoding='utf-8', newline='')
            mapping = scenario['mapping']
            headers, rows = parse_input(source, require_semantics=mapping is None)
            preview = preview_schema(headers, rows)
            if preview['row_count'] != 2 or preview['review_status'] != 'UNAPPROVED':
                raise AssertionError(f'{identifier}: invalid Pro preview gate')
            digest = source_sha256(source)
            destination = workspace / (identifier + '.html')
            response = build(source, destination, name='Synthetic REA Lite QA',
                             theme=scenario['theme'], approval='APPROVE',
                             mapping=mapping, expected_source_sha256=digest)
            raw = destination.read_bytes()
            text = raw.decode('utf-8')
            matched = _EMBEDDED_DATA.search(text)
            if matched is None:
                raise AssertionError(f'{identifier}: embedded dataset missing')
            payload = json.loads(base64.b64decode(matched.group(1), validate=True))
            if (payload['theme'] != scenario['theme'] or len(payload['records']) != 2
                    or payload['sourceSha256'] != digest or response['rows'] != 2
                    or not {'id', 'title', 'category'}.issubset(payload['headers'])
                    or "connect-src 'none'" not in text):
                raise AssertionError(f'{identifier}: payload/security contract mismatch')
            if mapping is not None and payload['records'][0]['id'] != 'O01':
                raise AssertionError(f'{identifier}: owner mapping not applied')
            try:
                build(source, destination, name='Overwrite refused',
                      theme=scenario['theme'], approval='APPROVE',
                      mapping=mapping, expected_source_sha256=digest)
            except FileExistsError:
                pass
            else:
                raise AssertionError(f'{identifier}: output was overwritable')
            if _sha256(destination.read_bytes()) != _sha256(raw):
                raise AssertionError(f'{identifier}: output changed after refusal')
            elapsed_ms = round((perf_counter_ns() - started) / 1_000_000, 3)
            cases.append({
                'scenario': identifier, 'theme': scenario['theme'],
                'source_type': scenario['extension'][1:],
                'rows': 2, 'preview_unapproved': True,
                'explicit_approval_test': True,
                'owner_mapping_test': mapping is not None,
                'no_overwrite_test': True,
                'source_sha256': digest, 'html_sha256': _sha256(raw),
                'html_bytes': len(raw), 'machine_elapsed_ms': elapsed_ms,
                'status': 'PASS',
            })
    return {
        'schema': 'rea.lite.synthetic_rehearsal.v1',
        'status': 'THREE_SYNTHETIC_MACHINE_REHEARSALS_PASS',
        'real_customer_data_used': False,
        'human_delivery_time_measured': False,
        'human_windows_acceptance': 'NOT_RUN',
        'commercial_approval': 'NOT_GRANTED',
        'platform': platform.system(), 'python': platform.python_version(),
        'case_count': len(cases), 'cases': cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Three synthetic-only REA Lite delivery rehearsals')
    parser.add_argument('--receipt', type=Path, help='NEW JSON receipt file; refuses overwrite')
    args = parser.parse_args(argv)
    if args.receipt and (args.receipt.exists() or args.receipt.is_symlink()):
        parser.error('Receipt already exists; refusing overwrite')
    receipt = run_rehearsal()
    payload = json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + '\n'
    if args.receipt:
        try:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            with args.receipt.open('x', encoding='utf-8') as handle:
                handle.write(payload)
        except FileExistsError:
            parser.error('Receipt created by another process; refusing overwrite')
    print(payload, end='')
    return 0


if __name__ == '__main__':
    sys.exit(main())
