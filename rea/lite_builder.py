"""Offline single-HTML REA Lite builder. Requires the REAL rea.mvp parser.

No network/server/EXE; seller confirms one exact data source before release.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import tempfile
from pathlib import Path

from rea.mvp import DataError, REQUIRED, map_owner_fields, parse_input, source_sha256
from rea.safe_publish import publish_archive

THEMES = frozenset({'cafe', 'inventory', 'office'})
_TEMPLATE = Path(__file__).resolve().parent / 'lite_assets' / 'template.html'


def build(source: Path, output: Path, *, name: str, theme: str = 'cafe',
          approval: str = '', mapping: dict[str, str] | None = None,
          expected_source_sha256: str | None = None) -> dict:
    """Create NEW offline HTML from a consented, hash-pinned owner source.

    No silent mapping, overwrites, customer-data logging, external access or storage.
    """
    if approval != 'APPROVE':
        raise DataError('Owner must explicitly confirm APPROVE for this build')
    if theme not in THEMES:
        raise DataError('Unsupported theme')
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100 or '\x00' in name:
        raise DataError('Name must have 1-100 characters')
    source = Path(source)
    output = Path(output)
    if output.suffix.lower() != '.html':
        raise DataError('Output must be a new .html file')
    if output.exists() or output.is_symlink():
        raise FileExistsError(f'Output already exists: {output}')
    before = source_sha256(source)
    if expected_source_sha256 is not None and expected_source_sha256 != before:
        raise DataError('Source hash does not match owner approval')
    if mapping is None:
        headers, records = parse_input(source)
    else:
        headers, records = parse_input(source, require_semantics=False)
        headers, records = map_owner_fields(headers, records, mapping)
    if not set(REQUIRED).issubset(headers):
        raise DataError('Missing canonical fields')
    data = {'version': 1, 'name': name.strip(), 'theme': theme,
            'headers': headers, 'records': records,
            'sourceSha256': before}
    encoded = base64.b64encode(json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).decode('ascii')
    template = _TEMPLATE.read_text(encoding='utf-8')
    if template.count('REPLACE_WITH_DATA_BASE64') != 1:
        raise RuntimeError('Lite template data anchor missing or ambiguous')
    html = template.replace('REPLACE_WITH_DATA_BASE64', encoded)
    if source_sha256(source) != before:
        raise DataError('Source changed during Lite build')
    output.parent.mkdir(parents=True, exist_ok=True)
    # Stage fully on the destination filesystem, then publish without overwrite.
    # The existing Pro publish_archive primitive accepts any completed file:
    # Windows rename and POSIX hard-link both refuse pre-existing destinations.
    descriptor, stage_name = tempfile.mkstemp(prefix=".rea-lite-staging-", suffix=".html", dir=output.parent)
    stage = Path(stage_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(html)
            handle.flush()
            os.fsync(handle.fileno())
        publish_archive(stage, output)
    finally:
        stage.unlink(missing_ok=True)
    return {'status': 'CREATED', 'output': str(output), 'rows': len(records),
            'theme': theme, 'sha256': before, 'mappingApproved': mapping is not None}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='REA Lite seller-side offline HTML builder')
    parser.add_argument('--source', type=Path, required=True, help='Owner-authorized CSV/JSON')
    parser.add_argument('--out', type=Path, required=True, help='NEW HTML path (no overwrite)')
    parser.add_argument('--name', required=True)
    parser.add_argument('--theme', choices=sorted(THEMES), default='cafe')
    parser.add_argument('--approval', required=True, help='Must be literal APPROVE')
    parser.add_argument('--source-sha256', help='Exact hash approved after preview')
    parser.add_argument('--mapping-file', type=Path, help='Owner-confirmed id/title/category mapping JSON')
    args = parser.parse_args(argv)
    try:
        mapping = None
        if args.mapping_file:
            if args.mapping_file.is_symlink() or not args.mapping_file.is_file() or args.mapping_file.stat().st_size > 4096:
                raise DataError('Invalid mapping file')
            mapping = json.loads(args.mapping_file.read_text(encoding='utf-8'))
        result = build(args.source, args.out, name=args.name, theme=args.theme,
                       approval=args.approval, mapping=mapping,
                       expected_source_sha256=args.source_sha256)
    except (OSError, ValueError, FileExistsError) as exc:
        parser.exit(2, f'REA_LITE_BUILD_REFUSED: {exc}\n')
    # Only non-sensitive metadata; output path may reveal user directories, omitted here.
    print(json.dumps({k: v for k, v in result.items() if k != 'output'}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
