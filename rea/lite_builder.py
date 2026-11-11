"""REA Lite: owner-approved, local-only single HTML creator using the real Pro parser.

Customer file data is embedded in plaintext HTML. Never use sensitive data without owner permission.
No external requests, Python runtime, server or local database is required for the customer.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import stat
from pathlib import Path

from rea.mvp import DataError, REQUIRED, map_owner_fields, parse_input, source_sha256

TEMPLATE = Path(__file__).resolve().parent / 'lite_assets' / 'template.html'
THEMES = ('cafe', 'inventory', 'office')
MAX_OUTPUT_BYTES = 16 * 1024 * 1024
HASH = re.compile(r'[a-f0-9]{64}\Z')


def _render_rows(columns: list[str], rows: list[dict[str, str]], theme: str, name: str,
                 source_headers: list[str], mapping: dict[str, str]) -> str:
    if theme not in THEMES or not name.strip() or len(name.strip()) > 100 or '\x00' in name:
        raise DataError('Invalid Lite theme or app title')
    document = TEMPLATE.read_text(encoding='utf-8')
    if (document.count('__REA_DATA_JSON__') != 1 or document.count('__REA_APP_NAME__') != 2
            or document.count('__REA_THEME__') != 1):
        raise RuntimeError('Lite template markers have changed')
    if any(field in ('__proto__', 'prototype', 'constructor') for field in columns):
        raise DataError('Reserved browser field name in local source')
    if any(field in ('__proto__', 'prototype', 'constructor') for field in source_headers):
        raise DataError('Reserved source field name')
    payload = {'contract': 'REA_LITE_V1', 'fields': columns, 'rows': rows,
               'source_headers': source_headers, 'owner_mapping': mapping,
               'theme': theme, 'title': name.strip(), 'source_approval': 'OWNER_APPROVED_LOCAL_BUILD_ONLY'}
    # Escape HTML raw-text/script terminators and JS-sensitive chars; JSON stays strict.
    safe_json = json.dumps(payload, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    for original, escaped in (('&', r'\u0026'), ('<', r'\u003c'), ('>', r'\u003e'),
                              ('\u2028', r'\u2028'), ('\u2029', r'\u2029')):
        safe_json = safe_json.replace(original, escaped)
    return (document.replace('__REA_APP_NAME__', html.escape(name.strip(), quote=True))
                    .replace('__REA_THEME__', theme)
                    .replace('__REA_DATA_JSON__', safe_json))


def build_lite(source: Path, output: Path, *, mapping: dict[str, str],
               expected_sha256: str, confirmation: str, name: str = 'REA Lite',
               theme: str = 'office') -> dict:
    """Consume exactly one owner-pinned input, write a fresh local HTML, never overwrite."""
    source, output = Path(source), Path(output)
    if confirmation != 'APPROVE' or not isinstance(expected_sha256, str) or HASH.fullmatch(expected_sha256) is None:
        raise DataError('Source approval and exact preview SHA256 required')
    if not source.is_absolute() or not output.is_absolute() or output.suffix.lower() != '.html':
        raise DataError('Use absolute source and new local .html output paths')
    if output.exists() or output.is_symlink() or output == source:
        raise FileExistsError('Output must be new; overwrite refused')
    if not output.parent.is_dir() or output.parent.is_symlink():
        raise DataError('Output parent must exist locally and must not be a link')
    for node in (output.parent, *output.parent.parents):
        if node.is_symlink() or getattr(node.lstat(), 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400):
            raise DataError('Linked output path is prohibited')
    before = source_sha256(source)
    if before != expected_sha256:
        raise DataError('Source SHA changed since owner preview')
    headers, records = parse_input(source, require_semantics=False)
    fields, rows = map_owner_fields(headers, records, mapping)
    if source_sha256(source) != before:
        raise DataError('Input changed while parsing')
    generated = _render_rows(fields, rows, theme, name, headers, mapping)
    encoded = generated.encode('utf-8')
    if len(encoded) > MAX_OUTPUT_BYTES:
        raise DataError('Generated HTML exceeds bound')
    # Recheck before creating any file; refuse the remaining race if it happens.
    if source_sha256(source) != before:
        raise DataError('Source changed before creating HTML')
    created = False
    try:
        with output.open('xb') as target:
            created = True
            target.write(encoded)
        if source_sha256(source) != before:
            raise DataError('Input changed after generation')
        if output.stat().st_size != len(encoded) or hashlib.sha256(output.read_bytes()).digest() != hashlib.sha256(encoded).digest():
            raise DataError('Generated HTML integrity failure')
    except Exception:
        if created:
            output.unlink(missing_ok=True)
        raise
    return {'contract': 'REA_LITE_BUILD_RECEIPT_V1', 'status': 'LOCAL_HTML_BUILT_NOT_RELEASE_APPROVED',
            'source_sha256': before, 'html_sha256': hashlib.sha256(encoded).hexdigest(),
            'rows': len(rows), 'fields': fields, 'theme': theme, 'customer_sale_approved': False,
            'windows_buyer_accepted': False, 'remote_upload': False, 'server_required': False,
            'original_source_modified': False}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Build one owner-reviewed offline REA Lite HTML')
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--id-field', required=True)
    parser.add_argument('--title-field', required=True)
    parser.add_argument('--category-field', required=True)
    parser.add_argument('--confirm', required=True)
    parser.add_argument('--theme', choices=THEMES, default='office')
    parser.add_argument('--name', default='REA Lite')
    a = parser.parse_args(argv)
    try:
        result = build_lite(a.source, a.out, mapping=dict(id=a.id_field, title=a.title_field,
            category=a.category_field), expected_sha256=a.source_sha256, confirmation=a.confirm,
            theme=a.theme, name=a.name)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, DataError, FileExistsError, ValueError):
        print('REA_LITE_BUILD_BLOCKED')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
