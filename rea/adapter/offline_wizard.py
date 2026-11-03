"""Human-reviewed offline GET binding wizard; no ZIP execution or network."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile

from rea.adapter.backend_schema import UnsafeSchema
from rea.adapter.backend_zip import UnsafeBackendZip
from rea.adapter.frontend_bridge import BridgeError, _read_json
from rea.adapter.offline_compose import compose


def _choose(role: str, paths: list[str]) -> str:
    if not paths:
        raise BridgeError(role + ': no eligible declared GET path')
    print('\n' + role.upper() + ' — choose an owner-approved GET path:')
    for index, path in enumerate(paths, 1):
        print(f'  {index}. {path}')
    value = input(role + ' path number: ').strip()
    if not value.isascii() or not value.isdecimal():
        raise BridgeError(role + ': enter a displayed path number')
    index = int(value)
    if not 1 <= index <= len(paths):
        raise BridgeError(role + ': path number out of range')
    return paths[index - 1]


def _field(role: str) -> str:
    value = input(role + ' response field (exact key or __root__): ').strip()
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,63}', value):
        raise BridgeError(role + ': invalid response field')
    return value


def run(backend_zip: Path, fable: Path, destination: Path, *,
        visual: Path | None = None, presentation: Path | None = None,
        source_authorized: bool = False, paginated_list: bool = False) -> dict:
    if not source_authorized:
        raise BridgeError('--owner-authorized-source required before ZIP read')
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('output path already exists; choose a NEW directory')

    preview = compose(backend_zip, fable, visual=visual, source_authorized=True)
    paths = preview['candidate_get_paths']
    print('Read-only preview: source rights, response semantics and runtime NOT verified.')
    print('ZIP SHA256: ' + preview['backend_sha256'])
    print('Unresolved declarations: ' + str(preview['unresolved_backend_declarations']))
    print('All response fields are explicit operator input, never inferred.')

    plain = [p for p in paths if '{' not in p and '}' not in p]
    detail_routes = [
        p for p in paths if len(re.findall(r'\{[A-Za-z_][A-Za-z0-9_]*\}', p)) == 1
        and p.count('{') == 1 and p.count('}') == 1
    ]
    bindings = {
        'list': {'path': _choose('list', plain), 'field': _field('list')},
        'metrics': {'path': _choose('metrics', plain), 'field': _field('metrics')},
    }
    if paginated_list:
        print('Owner-approved pagination parameters (NOT inferred from source):')
        total_field = _field('total count')
        limit_param = _field('limit query parameter')
        offset_param = _field('offset query parameter')
        page_size_text = input('page size, 1..100: ').strip()
        if not page_size_text.isascii() or not page_size_text.isdecimal():
            raise BridgeError('page size must be integer 1..100')
        bindings['list']['pagination'] = {
            'total_field': total_field, 'limit_param': limit_param,
            'offset_param': offset_param, 'page_size': int(page_size_text),
        }
    detail_path = _choose('detail', detail_routes)
    parameter = re.findall(r'\{([A-Za-z_][A-Za-z0-9_]*)\}', detail_path)[0]
    bindings['detail'] = {'path': detail_path, 'field': _field('detail'),
                          'path_param': parameter}
    if presentation is not None:
        bindings['presentation'] = _read_json(presentation)

    print('\nReview exact owner-selected mapping:')
    print(json.dumps(bindings, ensure_ascii=False, sort_keys=True, indent=2))
    print('NEW frontend-only output directory: ' + str(destination))
    if input('Type APPROVE exactly to generate frontend SOURCE ONLY: ').strip() != 'APPROVE':
        raise BridgeError('explicit APPROVE declined; no output generated')

    # Reuse existing static inspectors, safe no-overwrite publisher and original
    # generator. Reject the ZIP if bytes differ from the reviewed preview.
    with tempfile.TemporaryDirectory(prefix='rea-mapping-') as temp:
        selected = Path(temp) / 'bindings.json'
        selected.write_text(json.dumps(bindings, ensure_ascii=False), encoding='utf-8')
        result = compose(
            backend_zip, fable, bindings=selected, visual=visual,
            destination=destination, source_authorized=True,
            owner_confirmed=True, expected_backend_sha256=preview['backend_sha256'])
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Offline reviewed GET binding wizard')
    parser.add_argument('--backend-zip', type=Path, required=True)
    parser.add_argument('--fable', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--visual', type=Path)
    parser.add_argument('--paginated-list', action='store_true',
                        help='prompt for explicit total/limit/offset/page_size mapping')
    parser.add_argument('--presentation', type=Path,
                        help='optional owner-provided display field map JSON')
    parser.add_argument('--owner-authorized-source', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = run(args.backend_zip, args.fable, args.out, visual=args.visual,
                     presentation=args.presentation,
                     source_authorized=args.owner_authorized_source,
                     paginated_list=args.paginated_list)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    except (BridgeError, UnsafeBackendZip, UnsafeSchema, OSError,
            ValueError, EOFError, KeyboardInterrupt) as exc:
        print('REA offline wizard refused: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
