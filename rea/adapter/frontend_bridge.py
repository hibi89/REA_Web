"""Reference evidence + reviewed backend contract -> independent dashboard frontend.

Never imports/runs owner ZIP code, fetches a reference URL, copies remote assets,
or infers a backend response schema from FastAPI decorator declarations.
Only emits a frontend after explicit endpoint/shape mapping confirmation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile

from rea.adapter.backend_zip import SCHEMA as BACKEND_SCHEMA
from rea.adapter.fable_to_astra import project_fable
from rea.safe_publish import publish_directory

SCHEMA = 'rea.frontend_bridge.v0.1'
BINDING_NAMES = ('list', 'metrics', 'detail')
FIELD_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]{0,63}$')
API_RE = re.compile(r'^/api(?:/[A-Za-z0-9_.{}-]+)+$')
SHA_RE = re.compile(r'^[a-f0-9]{64}$')
MAX_INPUT = 2 * 1024 * 1024


class BridgeError(ValueError):
    """Unsafe or unapproved contract input."""


def _safe_api(path: object) -> bool:
    return isinstance(path, str) and len(path) <= 200 and bool(API_RE.fullmatch(path)) and '..' not in path


def _valid_field(name: object) -> bool:
    return isinstance(name, str) and bool(FIELD_RE.fullmatch(name))


def _valid_bindings(value: object) -> dict:
    """Field names and response shapes are EXPLICIT owner input, never inferred."""
    if not isinstance(value, dict) or set(value) != set(BINDING_NAMES):
        raise BridgeError('binding roles must be list, metrics and detail')
    result = {}
    for role in BINDING_NAMES:
        entry = value[role]
        if not isinstance(entry, dict) or set(entry) != {'path', 'field'}:
            raise BridgeError(f'{role}: require path and response field')
        if not _safe_api(entry['path']) or not _valid_field(entry['field']):
            raise BridgeError(f'{role}: invalid path or response field')
        result[role] = {'path': entry['path'], 'field': entry['field']}
    if '{' in result['list']['path'] or '{' in result['metrics']['path']:
        raise BridgeError('list/metrics paths must be parameter-free')
    if result['detail']['path'].count('{job_id}') != 1 or result['detail']['path'].count('{') != 1:
        raise BridgeError('detail path requires exactly one {job_id}')
    return result


def make_review(fable: dict, backend: dict, bindings: dict | None = None) -> dict:
    """Join independent, untrusted declarations without approving runtime claims."""
    if not isinstance(fable, dict) or not isinstance(backend, dict):
        raise BridgeError('Fable result and backend contract must be JSON objects')
    try:
        reference = project_fable(fable)
    except (TypeError, ValueError) as exc:
        raise BridgeError('invalid Fable report') from exc
    if (backend.get('schema_version') != BACKEND_SCHEMA
            or backend.get('status') != 'REVIEW_REQUIRED'
            or backend.get('generation_allowed') is not False
            or backend.get('execution_performed') is not False):
        raise BridgeError('untrusted or unsupported backend contract status')
    info = backend.get('input')
    if not isinstance(info, dict) or not isinstance(info.get('sha256'), str) or not SHA_RE.fullmatch(info['sha256']):
        raise BridgeError('missing backend SHA256')
    api = backend.get('api')
    if not isinstance(api, dict) or not isinstance(api.get('endpoints'), list) or len(api['endpoints']) > 500:
        raise BridgeError('invalid endpoint declarations')
    candidates = set()
    for endpoint in api['endpoints']:
        if not isinstance(endpoint, dict) or not _safe_api(endpoint.get('path')):
            raise BridgeError('unsafe endpoint path')
        methods = endpoint.get('methods')
        if not isinstance(methods, list) or len(methods) > 8:
            raise BridgeError('invalid HTTP verbs')
        if ('GET' in methods and endpoint.get('verification') == 'STATIC_DECLARATION_ONLY'
                and endpoint.get('mount') in ('app_declaration', 'local_router_mount_declaration')):
            candidates.add(endpoint['path'])
    selected = _valid_bindings(bindings) if bindings is not None else None
    if selected is not None:
        for role, binding in selected.items():
            if binding['path'] not in candidates:
                raise BridgeError(f'{role}: GET declaration not found or router mount unverified')
    return {
        'schema_version': SCHEMA,
        'status': 'OWNER_REVIEW_REQUIRED',
        'generation_allowed': False,
        'reference': {
            'origin': reference['source']['site_origin'],
            'source_sha256': reference['source']['sha256'],
            'mode': reference['source']['scan_mode'],
            'visual_evidence': 'NOT_CAPTURED_BY_FABLE_STATIC_CONTRACT',
            'style_source': 'ORIGINAL_REA_NEUTRAL_DEFAULT',
            'layout_similarity_to_reference': 'UNVERIFIED',
            'technical_counts': reference['technical_finding_counts'],
        },
        'backend': {'sha256': info['sha256'], 'endpoint_declarations': len(candidates),
                    'runtime_verified': False, 'response_schema_verified': False},
        'bindings': selected,
        'unknowns': ['actual_reference_visual_design', 'backend_runtime_auth',
                     'backend_response_shape', 'backend_cors_and_hosting'],
    }


HTML = '''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'none'; font-src 'none'; base-uri 'none'; form-action 'none'">
<title>REA WEB | Operations Overview</title><link href="/dashboard/style.css" rel="stylesheet"><script defer src="/dashboard/app.js"></script></head>
<body><div class="shell"><aside class="sidebar"><div class="logo"><span class="glyph">R</span><span>REA WEB<small>OPERATIONS STUDIO</small></span></div><nav aria-label="주 메뉴"><a class="active" href="/dashboard/">● &nbsp; Overview</a><span>WORKSPACE</span><a href="#records">↗ &nbsp; Activity</a><a href="#metrics">▥ &nbsp; Metrics</a></nav><div class="sidebar-foot">LOCAL INTEGRATION<br><strong>Read-only · API connected</strong></div></aside>
<main><header class="top"><div class="breadcrumb">Workspace <span>/</span> Overview</div><div class="connection"><span class="dot"></span> LOCAL API</div></header><div class="content"><section class="heading"><div><p class="eyebrow">REAL BACKEND · ORIGINAL FRONTEND</p><h1>Operations overview</h1><p class="sub">백엔드 ZIP에서 추출한 API 계약으로 연결하는 독립 제작 대시보드</p></div><span class="chip">Synthetic demo</span></section>
<section id="metrics" class="metrics" aria-label="주요 지표"><article><label>전체 작업</label><strong id="kpi-total">—</strong><span>All workloads</span></article><article><label>완료 작업</label><strong id="kpi-completed">—</strong><span>Completed jobs</span></article><article><label>대기 작업</label><strong id="kpi-pending">—</strong><span>Pending jobs</span></article></section>
<section class="grid"><section id="records" class="panel records"><div class="panel-title"><div><h2>Activity feed</h2><p>원본 백엔드의 작업 목록을 실시간 조회합니다.</p></div><span id="count" class="tag">0 entries</span></div><label class="search-label">검색 <input id="search" type="search" placeholder="작업명, 번호, 분류 검색" aria-label="작업 검색" autocomplete="off"></label><div class="table-wrap"><table><thead><tr><th>작업</th><th>분류</th><th>상태</th><th>상세</th></tr></thead><tbody id="jobs"></tbody></table></div><p id="empty" class="empty" hidden>검색 결과가 없습니다.</p></section><aside class="panel detail"><div class="panel-title"><div><h2>Job inspector</h2><p>조회할 작업을 선택하십시오.</p></div></div><div id="detail" class="detail-content">왼쪽에서 작업을 선택하면 실제 API 상세 응답을 표시합니다.</div></aside></section>
<p id="error" role="alert" class="error" hidden></p><footer>REA WEB · Independent interface · No reference-site scripts or assets copied · Same-origin read-only GET API</footer>
</div></main></div></body></html>'''

CSS = '''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:#162333;background:#f5f7fb;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic",sans-serif}.shell{display:grid;grid-template-columns:248px minmax(0,1fr);min-height:100vh}.sidebar{background:#101d31;color:#e6ebf5;display:flex;flex-direction:column;padding:29px 17px}.logo{display:flex;align-items:center;gap:11px;padding:0 15px 42px;font-size:17px;letter-spacing:.05em;font-weight:850}.logo small{display:block;margin-top:5px;color:#8b9fb9;font-size:9px;letter-spacing:.18em}.glyph{width:34px;height:34px;background:#3678ff;display:grid;place-items:center;border-radius:10px;font-size:20px}.sidebar nav{display:grid;gap:5px}.sidebar nav span{font-size:10px;letter-spacing:.18em;color:#8090ac;margin:25px 15px 11px;font-weight:750}.sidebar nav a{display:block;text-decoration:none;padding:13px 14px;border-radius:10px;color:#b0bfd5;font-size:13px;font-weight:650}.sidebar nav a.active,.sidebar nav a:hover{background:#233753;color:#fff}.sidebar-foot{margin-top:auto;border-top:1px solid #2b405b;padding:23px 13px 5px;color:#89a0be;font-size:10px;letter-spacing:.1em;line-height:2}.sidebar-foot strong{color:#dce5f3;font-size:11px;font-weight:500;letter-spacing:0}main{min-width:0}.top{height:70px;background:#fff;border-bottom:1px solid #e7ebf1;display:flex;align-items:center;justify-content:space-between;padding:0 43px}.breadcrumb{font-size:12px;color:#6f7e93}.breadcrumb span{padding:0 12px;color:#c0ccda}.connection{font-size:11px;font-weight:750;color:#1f805e;letter-spacing:.07em}.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#22a177;margin-right:8px}.content{max-width:1510px;margin:auto;padding:39px 43px 32px}.heading{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:30px}.eyebrow{color:#326cf1;font-size:10px;font-weight:850;letter-spacing:.22em;margin:0 0 10px}h1{font-size:35px;letter-spacing:-.055em;margin:0 0 9px;color:#122035}.sub{font-size:13px;color:#718098;margin:0}.chip{border:1px solid #d8e4fb;background:#eff5ff;color:#3166d9;font-size:11px;padding:9px 13px;border-radius:99px;white-space:nowrap}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:17px;margin-bottom:20px}.metrics article,.panel{background:#fff;border:1px solid #e7ecf3;border-radius:15px;box-shadow:0 8px 30px #24375108}.metrics article{padding:24px 27px;min-height:143px}.metrics label{display:block;color:#65748a;font-size:12px;font-weight:650}.metrics strong{display:block;font-size:36px;letter-spacing:-.06em;margin:12px 0 4px;font-weight:800}.metrics span{font-size:11px;color:#8b97a7}.grid{display:grid;grid-template-columns:minmax(0,1.75fr) minmax(260px,1fr);gap:20px}.panel{padding:25px}.panel-title{display:flex;align-items:flex-start;justify-content:space-between;gap:15px;margin-bottom:22px}.panel-title h2{font-size:17px;letter-spacing:-.025em;margin:0 0 5px}.panel-title p{font-size:12px;color:#8693a5;margin:0}.tag{font-size:10px;color:#326ce9;padding:7px 10px;border-radius:6px;background:#eef3ff;white-space:nowrap}.search-label{display:block;font-size:11px;font-weight:700;color:#6d7d91}.search-label input{display:block;width:100%;margin:8px 0 17px;border:1px solid #dce4f0;border-radius:9px;padding:13px 15px;color:#1b2b40;font:inherit;font-size:12px}.search-label input:focus-visible,button:focus-visible{outline:3px solid #8bb6ff}.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:12px}thead{background:#f8fafd;color:#7e8ba1;text-align:left}th,td{padding:15px 10px;border-bottom:1px solid #edf0f5;text-align:left}th{font-size:10px;letter-spacing:.04em}td:first-child{font-weight:700;color:#243753}.status{display:inline-block;border-radius:20px;padding:5px 8px;background:#fff4d7;color:#a36b13;font-size:10px;font-weight:700}.status.done{background:#dcf7e9;color:#138456}button.link{border:0;background:#ecf2ff;color:#285bd7;border-radius:7px;padding:7px 11px;cursor:pointer;font:inherit;font-size:11px;font-weight:700}.detail-content{font-size:13px;color:#6c7b91;line-height:1.9}.detail-row{display:flex;justify-content:space-between;gap:10px;border-bottom:1px solid #edf0f5;padding:10px 0}.detail-row b{color:#1d2f4a;font-size:12px;text-align:right;overflow-wrap:anywhere}.empty,.error{color:#9a4366;font-size:12px}.error{padding:15px;border:1px solid #efc6d1;background:#fff3f6;border-radius:8px;margin-top:18px}footer{margin-top:26px;font-size:11px;color:#99a5b5}@media(max-width:1100px){.grid{grid-template-columns:1fr}.sidebar{width:210px}.shell{grid-template-columns:210px 1fr}}@media(max-width:740px){.shell{display:block}.sidebar{min-height:auto;padding:12px 16px}.logo{padding:0}.sidebar nav,.sidebar-foot{display:none}.top{height:54px;padding:0 20px}.content{padding:26px 17px}.heading{align-items:flex-start}h1{font-size:29px}.metrics{gap:9px}.metrics article{padding:16px 11px;min-height:120px}.metrics strong{font-size:28px}.metrics label{font-size:11px}.panel{padding:17px}}'''

JS = '''"use strict";
const API = __API_JSON__;
const $ = id => document.getElementById(id);
const safe = value => value == null ? '' : String(value);
const field = (item, name) => Object.prototype.hasOwnProperty.call(item, name) ? item[name] : '';
const node = (tag, value) => {const n=document.createElement(tag); n.textContent=safe(value); return n;};
let cached=[];
function fail(error) {const n=$('error'); n.hidden=false; n.textContent='백엔드 API 연결 실패: '+safe(error.message||error);}
async function fetchJson(path) {
  const response = await fetch(path, {credentials:'same-origin',cache:'no-store',headers:{Accept:'application/json'}});
  if (!response.ok) throw new Error('HTTP '+response.status+' / '+path);
  return response.json();
}
function render(items) {
  const target=$('jobs'); target.replaceChildren();
  $('count').textContent=items.length+' entries'; $('empty').hidden=items.length!==0;
  for(const item of items){
    const tr=document.createElement('tr');
    tr.append(node('td',field(item,'name')||field(item,'id')));
    tr.append(node('td',field(item,'category')));
    const status=document.createElement('td');const badge=node('span',field(item,'status'));
    badge.className='status'+(field(item,'status')==='done'?' done':'');status.append(badge);tr.append(status);
    const cell=document.createElement('td');const button=node('button','상세');button.type='button';button.className='link';
    button.addEventListener('click',()=>showDetail(safe(field(item,'id'))));cell.append(button);tr.append(cell);target.append(tr);
  }
}
async function showDetail(id) {
  if(!id || id.length>200){fail(new Error('유효하지 않은 작업 ID'));return;}
  const path=API.detail.path.replace('{job_id}',encodeURIComponent(id));
  try {
    const response=await fetchJson(path);
    const obj=API.detail.field==='__root__'?response:response[API.detail.field];
    if(!obj || typeof obj!=='object' || Array.isArray(obj)) throw new Error('상세 응답 스키마 불일치');
    const box=$('detail');box.replaceChildren();
    for(const key of ['id','name','category','status','duration_ms']){
      const row=document.createElement('div');row.className='detail-row';row.append(node('span',key));row.append(node('b',field(obj,key)));box.append(row);
    }
  } catch(error) {fail(error);}
}
async function load(){
  try {
    const [jobs,metrics]=await Promise.all([fetchJson(API.list.path),fetchJson(API.metrics.path)]);
    const arr=API.list.field==='__root__'?jobs:jobs[API.list.field];
    const stat=API.metrics.field==='__root__'?metrics:metrics[API.metrics.field];
    if(!Array.isArray(arr) || arr.length>10000 || arr.some(x=>!x||typeof x!=='object'||Array.isArray(x))) throw new Error('목록 응답 스키마 불일치');
    if(!stat || typeof stat!=='object'||Array.isArray(stat)) throw new Error('지표 응답 스키마 불일치');
    cached=arr;
    for(const key of ['total','completed','pending']) $('kpi-'+key).textContent=safe(field(stat,key));
    render(cached);
  } catch(error){fail(error);}
}
$('search').addEventListener('input',e=>{const q=e.target.value.toLocaleLowerCase().trim();render(cached.filter(x=>['id','name','category'].some(k=>safe(field(x,k)).toLocaleLowerCase().includes(q))));});
load();'''


def _js_config(bindings: dict) -> str:
    result = json.dumps(bindings, separators=(',', ':'), ensure_ascii=True)
    # The config is embedded in a separate JS file, never in a SCRIPT tag.
    return result


def generate_frontend(review: dict, destination: Path, *, owner_confirmed: bool = False) -> dict:
    """Publish source-only same-origin frontend; no backend ZIP extraction/execution."""
    if not isinstance(review, dict) or review.get('schema_version') != SCHEMA or review.get('status') != 'OWNER_REVIEW_REQUIRED':
        raise BridgeError('unsupported review format')
    binding = _valid_bindings(review.get('bindings'))
    if not owner_confirmed:
        raise BridgeError('explicit owner_confirmed required to generate frontend')
    # Defense against edited review files: no claim of runtime or actual design proof.
    if review.get('generation_allowed') is not False or review.get('backend', {}).get('runtime_verified') is not False:
        raise BridgeError('untrusted review approval state')
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('output path exists')
    destination.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        'schema_version': SCHEMA, 'status': 'FRONTEND_SOURCE_GENERATED_NOT_RUNTIME_VERIFIED',
        'owner_bindings_confirmed': True, 'backend_modified': False,
        'reference': review['reference'], 'backend': review['backend'],
        'bindings': binding, 'frontend_path': '/dashboard/',
        'limitations': ['backend_not_bundled', 'serve_on_same_origin_under_/dashboard',
                        'response_schema_must_be_runtime_verified', 'design_not_observed_from_reference'],
    }
    with tempfile.TemporaryDirectory(prefix='.rea-bridge-', dir=destination.parent) as temp:
        stage = Path(temp) / 'dashboard'
        stage.mkdir()
        (stage / 'index.html').write_text(HTML+'\n', encoding='utf-8')
        (stage / 'style.css').write_text(CSS+'\n', encoding='utf-8')
        (stage / 'app.js').write_text(JS.replace('__API_JSON__', _js_config(binding))+'\n', encoding='utf-8')
        (stage / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
        (stage / 'README_KO.md').write_text(
            '# REA generated frontend (NOT a runnable backend)\n\n'
            '원본 백엔드 ZIP을 실행하거나 수정하지 않았습니다. 현재 결과는 프론트엔드 소스입니다.\n'
            '신뢰할 수 있는 FastAPI 앱에서 `app.mount("/dashboard", StaticFiles(directory=THIS_FOLDER, html=True))`로 제공하세요.\n'
            '반드시 동일 origin에서 /api/* 경로를 제공해야 합니다. 실제 API 응답 형식과 인증은 실행 검증 전까지 미확인입니다.\n'
            '테스트용 임시 합성 백엔드 외 원본의 실행·배포·권한 변경에는 별도 승인이 필요합니다.\n', encoding='utf-8')
        publish_directory(stage, destination)
    return manifest


def _read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_INPUT:
        raise BridgeError('input must be a regular JSON file <= 2 MiB')
    return json.loads(path.read_text(encoding='utf-8'))


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description='REA Fable + backend ZIP contract review and approved original frontend')
    parser.add_argument('--fable', required=True, type=Path)
    parser.add_argument('--backend', required=True, type=Path)
    parser.add_argument('--bindings', type=Path, help='explicit owner response-field and GET path mappings')
    parser.add_argument('--out', type=Path, help='NEW frontend source directory')
    parser.add_argument('--owner-confirmed', action='store_true')
    args=parser.parse_args(argv)
    try:
        if args.owner_confirmed and (args.bindings is None or args.out is None):
            raise BridgeError('approved output requires --bindings and --out')
        if args.out is not None and not args.owner_confirmed:
            raise BridgeError('preview mode cannot write frontend without owner confirmation')
        plan=make_review(_read_json(args.fable), _read_json(args.backend),
                         _read_json(args.bindings) if args.bindings is not None else None)
        if args.out is None:
            print(json.dumps(plan, indent=2, ensure_ascii=False))
        else:
            result=generate_frontend(plan,args.out,owner_confirmed=args.owner_confirmed)
            print(json.dumps(result,indent=2,ensure_ascii=False))
        return 0
    except (BridgeError,OSError,ValueError) as exc:
        print('REA bridge refused: '+str(exc),file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
