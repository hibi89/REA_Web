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
from rea.adapter.backend_schema import SCHEMA as API_SCHEMA
from rea.adapter.fable_to_astra import project_fable
from rea.adapter.visual_reference import VisualError, validate_visual
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
    if not isinstance(value, dict) or set(value) not in (set(BINDING_NAMES), {*BINDING_NAMES, 'presentation'}):
        raise BridgeError('binding roles must be list, metrics, detail and optional presentation')
    result = {}
    for role in BINDING_NAMES:
        entry = value[role]
        allowed = ({'path','field'}, {'path','field','path_param'}) if role == 'detail' else ({'path','field'},)
        if not isinstance(entry, dict) or set(entry) not in allowed:
            raise BridgeError(f'{role}: require path, field and optional detail path_param')
        if not _safe_api(entry['path']) or not _valid_field(entry['field']):
            raise BridgeError(f'{role}: invalid path or response field')
        result[role] = {'path': entry['path'], 'field': entry['field']}
    if '{' in result['list']['path'] or '{' in result['metrics']['path']:
        raise BridgeError('list/metrics paths must be parameter-free')
    detail = value['detail']
    param = detail.get('path_param', 'job_id')
    if (not _valid_field(param) or param in ('__proto__','constructor','prototype')
            or result['detail']['path'].count('{' + param + '}') != 1
            or result['detail']['path'].count('{') != 1
            or result['detail']['path'].count('}') != 1):
        raise BridgeError('detail path requires exactly one explicit path parameter')
    if 'path_param' in detail:
        result['detail']['path_param'] = param
    if 'presentation' in value:
        result['presentation'] = _valid_presentation(value['presentation'])
    return result


def _valid_presentation(value: object) -> dict:
    """Owner-declared display fields only. No arbitrary JS/templates/expressions."""
    if not isinstance(value, dict) or set(value) != {'item', 'metrics', 'detail_fields'}:
        raise BridgeError('presentation requires item, metrics, detail_fields')
    expected = {'item': {'id','name','category','status'},
                'metrics': {'total','completed','pending'}}
    result = {}
    for group, keys in expected.items():
        fields = value[group]
        if not isinstance(fields, dict) or set(fields) != keys:
            raise BridgeError('invalid presentation field mapping')
        if any(not _valid_field(v) or v in ('__proto__','constructor','prototype') for v in fields.values()):
            raise BridgeError('unsafe presentation field')
        result[group] = {k:fields[k] for k in sorted(keys)}
    fields = value['detail_fields']
    if (not isinstance(fields, list) or not 1 <= len(fields) <= 12
            or len(set(x for x in fields if isinstance(x,str))) != len(fields)
            or any(not _valid_field(v) or v in ('__proto__','constructor','prototype') for v in fields)):
        raise BridgeError('invalid detail presentation fields')
    result['detail_fields'] = list(fields)
    return result


def _static_schema_review(schema: dict, backend: dict) -> dict:
    """Accept only reviewed static schema hints for the SAME owner ZIP.

    Hints are provenance metadata, not proof of endpoint availability or JSON
    response shapes, and cannot autoapprove an API binding.
    """
    if (not isinstance(schema, dict) or schema.get('schema_version') != API_SCHEMA
            or schema.get('status') != 'REVIEW_REQUIRED'
            or schema.get('generation_allowed') is not False
            or schema.get('execution_performed') is not False
            or schema.get('backend_sha256') != backend['input']['sha256']):
        raise BridgeError('schema review mismatch: backend SHA/status')
    routes = schema.get('routes')
    if not isinstance(routes, list) or len(routes) > 500:
        raise BridgeError('invalid static schema routes')
    declared = set()
    for entry in backend['api']['endpoints']:
        methods = entry.get('methods')
        if (not isinstance(methods, list) or len(methods) > 8
                or any(not isinstance(m,str) or len(m) > 12 for m in methods)
                or not isinstance(entry.get('source'), str)
                or type(entry.get('line')) is not int):
            raise BridgeError('backend endpoint declaration lacks source proof')
        declared.add((entry['path'], tuple(methods), entry['source'], entry['line']))
    models = 0
    for route in routes:
        if not isinstance(route, dict):
            raise BridgeError('invalid schema route')
        methods = route.get('methods')
        if (not isinstance(methods,list) or len(methods)>8
                or any(not isinstance(m,str) or len(m)>12 for m in methods)
                or not isinstance(route.get('source'),str)
                or type(route.get('line')) is not int
                or (route.get('path'),tuple(methods),route['source'],route['line']) not in declared
                or route.get('verification') != 'STATIC_AST_HINT_ONLY'
                or not isinstance(route.get('response'),dict)):
            raise BridgeError('schema route does not match backend declaration')
        response_models = route['response'].get('models',[])
        if not isinstance(response_models,list) or len(response_models)>64:
            raise BridgeError('invalid schema response models')
        models += int(bool(route.get('request_body'))) + len(response_models)
    return {'status':'STATIC_AST_HINT_ONLY_NOT_RUNTIME_VERIFIED',
            'route_hints':len(routes),'model_hints':models,
            'backend_sha256':schema['backend_sha256'],'bindings_autoapproved':False}


def make_review(fable: dict, backend: dict, bindings: dict | None = None, *,
                visual: dict | None = None, schema: dict | None = None) -> dict:
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
    schema_summary = _static_schema_review(schema, backend) if schema is not None else None
    observed = None
    if visual is not None:
        try:
            observed = validate_visual(visual, expected_origin=reference['source']['site_origin'], allow_loopback=True)
        except VisualError as exc:
            raise BridgeError('visual reference rejected: ' + str(exc)) from exc
    selected = _valid_bindings(bindings) if bindings is not None else None
    if selected is not None:
        for role in BINDING_NAMES:
            binding = selected[role]
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
            'visual_evidence': 'BROWSER_COMPUTED_STYLE_OBSERVED' if observed else 'NOT_CAPTURED_BY_FABLE_STATIC_CONTRACT',
            'style_source': 'REFERENCE_STYLE_GUIDANCE_ORIGINAL_UI' if observed else 'ORIGINAL_REA_NEUTRAL_DEFAULT',
            'layout_similarity_to_reference': 'UNVERIFIED',
            'visual_sha256': observed['sha256'] if observed else None,
            'visual_layout_hint': observed['layout'] if observed else 'unknown',
            'technical_counts': reference['technical_finding_counts'],
        },
        'backend': {'sha256': info['sha256'], 'endpoint_declarations': len(candidates),
                    'runtime_verified': False, 'response_schema_verified': False},
        'bindings': selected,
        'visual_contract': observed,
        'schema_review': schema_summary,
        'unknowns': (['exact_reference_layout_and_assets'] if observed else ['actual_reference_visual_design']) + ['backend_runtime_auth',
                     'backend_response_shape', 'backend_cors_and_hosting'],
    }


HTML = '''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'none'; font-src 'none'; base-uri 'none'; form-action 'none'">
<title>REA WEB | Operations Overview</title><link href="/dashboard/style.css" rel="stylesheet"><script defer src="/dashboard/app.js"></script></head>
<body><div class="shell"><aside class="sidebar"><div class="logo"><span class="glyph">R</span><span>REA WEB<small>OPERATIONS STUDIO</small></span></div><nav aria-label="주 메뉴"><a class="active" href="/dashboard/">● &nbsp; Overview</a><span>WORKSPACE</span><a href="#records">↗ &nbsp; Activity</a><a href="#metrics">▥ &nbsp; Metrics</a></nav><div class="sidebar-foot">LOCAL INTEGRATION<br><strong>Read-only · Same-origin API</strong></div></aside>
<main><header class="top"><div class="breadcrumb">Workspace <span>/</span> Overview</div><div class="connection" id="connection" role="status"><span class="dot"></span><span id="connection-text">CHECKING API</span></div></header><div class="content"><section class="heading"><div><p class="eyebrow">REAL BACKEND · ORIGINAL FRONTEND</p><h1>Operations overview</h1><p class="sub">백엔드 ZIP에서 추출한 API 계약으로 연결하는 독립 제작 대시보드</p></div><span class="chip">Explicit API mapping</span></section>
<section id="metrics" class="metrics" aria-label="주요 지표"><article><label>전체 작업</label><strong id="kpi-total">—</strong><span>All workloads</span></article><article><label>완료 작업</label><strong id="kpi-completed">—</strong><span>Completed jobs</span></article><article><label>대기 작업</label><strong id="kpi-pending">—</strong><span>Pending jobs</span></article></section>
<section class="grid"><section id="records" class="panel records"><div class="panel-title"><div><h2>Activity feed</h2><p>원본 백엔드의 작업 목록을 실시간 조회합니다.</p></div><span id="count" class="tag">0 entries</span></div><label class="search-label">검색 <input id="search" type="search" placeholder="작업명, 번호, 분류 검색" aria-label="작업 검색" autocomplete="off"></label><div class="table-wrap"><table><thead><tr><th>작업</th><th>분류</th><th>상태</th><th>상세</th></tr></thead><tbody id="jobs"></tbody></table></div><p id="empty" class="empty" hidden>검색 결과가 없습니다.</p></section><aside class="panel detail"><div class="panel-title"><div><h2>Job inspector</h2><p>조회할 작업을 선택하십시오.</p></div></div><div id="detail" class="detail-content">왼쪽에서 작업을 선택하면 실제 API 상세 응답을 표시합니다.</div></aside></section>
<p id="error" role="alert" class="error" hidden></p><footer>REA WEB · Independent interface · No reference-site scripts or assets copied · Same-origin read-only GET API</footer>
</div></main></div></body></html>'''

CSS = '''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:#162333;background:#f5f7fb;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic",sans-serif}.shell{display:grid;grid-template-columns:248px minmax(0,1fr);min-height:100vh}.sidebar{background:#101d31;color:#e6ebf5;display:flex;flex-direction:column;padding:29px 17px}.logo{display:flex;align-items:center;gap:11px;padding:0 15px 42px;font-size:17px;letter-spacing:.05em;font-weight:850}.logo small{display:block;margin-top:5px;color:#8b9fb9;font-size:9px;letter-spacing:.18em}.glyph{width:34px;height:34px;background:#3678ff;display:grid;place-items:center;border-radius:10px;font-size:20px}.sidebar nav{display:grid;gap:5px}.sidebar nav span{font-size:10px;letter-spacing:.18em;color:#8090ac;margin:25px 15px 11px;font-weight:750}.sidebar nav a{display:block;text-decoration:none;padding:13px 14px;border-radius:10px;color:#b0bfd5;font-size:13px;font-weight:650}.sidebar nav a.active,.sidebar nav a:hover{background:#233753;color:#fff}.sidebar-foot{margin-top:auto;border-top:1px solid #2b405b;padding:23px 13px 5px;color:#89a0be;font-size:10px;letter-spacing:.1em;line-height:2}.sidebar-foot strong{color:#dce5f3;font-size:11px;font-weight:500;letter-spacing:0}main{min-width:0}.top{height:70px;background:#fff;border-bottom:1px solid #e7ebf1;display:flex;align-items:center;justify-content:space-between;padding:0 43px}.breadcrumb{font-size:12px;color:#6f7e93}.breadcrumb span{padding:0 12px;color:#c0ccda}.connection{font-size:11px;font-weight:750;color:#75849b;letter-spacing:.07em}.connection .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#a5b2c3;margin-right:8px}.connection.ready{color:#1f805e}.connection.ready .dot{background:#22a177}.connection.failed{color:#b53b4d}.connection.failed .dot{background:#d94f66}.content{max-width:1510px;margin:auto;padding:39px 43px 32px}.heading{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:30px}.eyebrow{color:#326cf1;font-size:10px;font-weight:850;letter-spacing:.22em;margin:0 0 10px}h1{font-size:35px;letter-spacing:-.055em;margin:0 0 9px;color:#122035}.sub{font-size:13px;color:#718098;margin:0}.chip{border:1px solid #d8e4fb;background:#eff5ff;color:#3166d9;font-size:11px;padding:9px 13px;border-radius:99px;white-space:nowrap}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:17px;margin-bottom:20px}.metrics article,.panel{background:#fff;border:1px solid #e7ecf3;border-radius:15px;box-shadow:0 8px 30px #24375108}.metrics article{padding:24px 27px;min-height:143px}.metrics label{display:block;color:#65748a;font-size:12px;font-weight:650}.metrics strong{display:block;font-size:36px;letter-spacing:-.06em;margin:12px 0 4px;font-weight:800}.metrics span{font-size:11px;color:#8b97a7}.grid{display:grid;grid-template-columns:minmax(0,1.75fr) minmax(260px,1fr);gap:20px}.panel{padding:25px}.panel-title{display:flex;align-items:flex-start;justify-content:space-between;gap:15px;margin-bottom:22px}.panel-title h2{font-size:17px;letter-spacing:-.025em;margin:0 0 5px}.panel-title p{font-size:12px;color:#8693a5;margin:0}.tag{font-size:10px;color:#326ce9;padding:7px 10px;border-radius:6px;background:#eef3ff;white-space:nowrap}.search-label{display:block;font-size:11px;font-weight:700;color:#6d7d91}.search-label input{display:block;width:100%;margin:8px 0 17px;border:1px solid #dce4f0;border-radius:9px;padding:13px 15px;color:#1b2b40;font:inherit;font-size:12px}.search-label input:focus-visible,button:focus-visible{outline:3px solid #8bb6ff}.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:12px}thead{background:#f8fafd;color:#7e8ba1;text-align:left}th,td{padding:15px 10px;border-bottom:1px solid #edf0f5;text-align:left}th{font-size:10px;letter-spacing:.04em}td:first-child{font-weight:700;color:#243753}.status{display:inline-block;border-radius:20px;padding:5px 8px;background:#fff4d7;color:#a36b13;font-size:10px;font-weight:700}.status.done{background:#dcf7e9;color:#138456}button.link{border:0;background:#ecf2ff;color:#285bd7;border-radius:7px;padding:7px 11px;cursor:pointer;font:inherit;font-size:11px;font-weight:700}.detail-content{font-size:13px;color:#6c7b91;line-height:1.9}.detail-row{display:flex;justify-content:space-between;gap:10px;border-bottom:1px solid #edf0f5;padding:10px 0}.detail-row b{color:#1d2f4a;font-size:12px;text-align:right;overflow-wrap:anywhere}.empty,.error{color:#9a4366;font-size:12px}.error{padding:15px;border:1px solid #efc6d1;background:#fff3f6;border-radius:8px;margin-top:18px}footer{margin-top:26px;font-size:11px;color:#99a5b5}@media(max-width:1100px){.grid{grid-template-columns:1fr}.sidebar{width:210px}.shell{grid-template-columns:210px 1fr}}@media(max-width:740px){.shell{display:block}.sidebar{min-height:auto;padding:12px 16px}.logo{padding:0}.sidebar nav,.sidebar-foot{display:none}.top{height:54px;padding:0 20px}.content{padding:26px 17px}.heading{align-items:flex-start}h1{font-size:29px}.metrics{gap:9px}.metrics article{padding:16px 11px;min-height:120px}.metrics strong{font-size:28px}.metrics label{font-size:11px}.panel{padding:17px}}'''

JS = '''"use strict";
const API = __API_JSON__;
const VIEW = API.presentation || {
  item: {id:'id',name:'name',category:'category',status:'status'},
  metrics: {total:'total',completed:'completed',pending:'pending'},
  detail_fields: ['id','name','category','status','duration_ms']
};
const $ = id => document.getElementById(id);
const safe = value => value == null ? '' : String(value);
const field = (item, name) => Object.prototype.hasOwnProperty.call(item, name) ? item[name] : '';
const node = (tag, value) => {const n=document.createElement(tag); n.textContent=safe(value); return n;};
let cached=[];
function fail(error) {const n=$('error'); n.hidden=false; n.textContent='백엔드 API 연결 실패: '+safe(error.message||error); $('connection').classList.remove('ready'); $('connection').classList.add('failed'); $('connection-text').textContent='API ERROR';}
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
    tr.append(node('td',field(item,VIEW.item.name)||field(item,VIEW.item.id)));
    tr.append(node('td',field(item,VIEW.item.category)));
    const status=document.createElement('td');const badge=node('span',field(item,VIEW.item.status));
    badge.className='status'+(field(item,VIEW.item.status)==='done'?' done':'');status.append(badge);tr.append(status);
    const cell=document.createElement('td');const button=node('button','상세');button.type='button';button.className='link';
    button.addEventListener('click',()=>showDetail(safe(field(item,VIEW.item.id))));cell.append(button);tr.append(cell);target.append(tr);
  }
}
async function showDetail(id) {
  if(!id || id.length>200){fail(new Error('유효하지 않은 작업 ID'));return;}
  const path=API.detail.path.replace('{'+(API.detail.path_param||'job_id')+'}',encodeURIComponent(id));
  try {
    const response=await fetchJson(path);
    const obj=API.detail.field==='__root__'?response:response[API.detail.field];
    if(!obj || typeof obj!=='object' || Array.isArray(obj)) throw new Error('상세 응답 스키마 불일치');
    const box=$('detail');box.replaceChildren();
    for(const key of VIEW.detail_fields){
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
    for(const key of ['total','completed','pending']) $('kpi-'+key).textContent=safe(field(stat,VIEW.metrics[key]));
    render(cached);
    $('connection').classList.add('ready'); $('connection-text').textContent='CONNECTED';
  } catch(error){fail(error);}
}
$('search').addEventListener('input',e=>{const q=e.target.value.toLocaleLowerCase().trim();render(cached.filter(x=>['id','name','category'].some(k=>safe(field(x,VIEW.item[k])).toLocaleLowerCase().includes(q))));});
load();'''


def _reference_css(visual: dict | None) -> str:
    """Author an original stylesheet from bounded observed palette/layout hints."""
    if visual is None:
        return ''
    colors = visual['colors']
    css = ['/* Sanitized reference computed-style hints; original REA layout. */']
    rules = {
        'canvas': 'body', 'surface': '.metrics article,.panel,.top',
        'ink': 'body,h1', 'navigation': '.sidebar', 'accent': '.glyph',
    }
    properties = {
        'canvas': 'background-color', 'surface': 'background-color',
        'ink': 'color', 'navigation': 'background-color', 'accent': 'background-color',
    }
    for key in ('canvas','surface','ink','navigation','accent'):
        if colors.get(key):
            css.append(f'{rules[key]}{{{properties[key]}:{colors[key]};}}')
    accent = colors.get('accent')
    if accent:
        css.append(f'.eyebrow,.tag{{color:{accent};}}')
        css.append(f'button.link{{color:{accent};}}')
    if visual['layout'] == 'topbar':
        css.append('.shell{display:block}.sidebar{display:flex;flex-direction:row;align-items:center;min-height:0;padding:13px 28px;gap:24px}.logo{padding:0;white-space:nowrap}.sidebar nav{display:flex;gap:12px;align-items:center}.sidebar nav a{padding:10px 13px}.sidebar nav span,.sidebar-foot{display:none}@media(max-width:740px){.sidebar{display:flex;flex-wrap:wrap}.sidebar nav{display:flex;overflow-x:auto;width:100%}.sidebar nav a{white-space:nowrap}}')
    return '\n'.join(css) + '\n'


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
    visual = review.get('visual_contract')
    if visual is not None:
        ref = review.get('reference', {})
        try:
            visual = validate_visual(visual, expected_origin=ref.get('origin'), allow_loopback=True)
        except VisualError as exc:
            raise BridgeError('invalid stored visual evidence') from exc
        if (ref.get('visual_sha256') != visual['sha256'] or
                ref.get('style_source') != 'REFERENCE_STYLE_GUIDANCE_ORIGINAL_UI' or
                ref.get('visual_evidence') != 'BROWSER_COMPUTED_STYLE_OBSERVED'):
            raise BridgeError('visual provenance mismatch')
    else:
        if review.get('reference', {}).get('style_source') != 'ORIGINAL_REA_NEUTRAL_DEFAULT':
            raise BridgeError('missing visual evidence')
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('output path exists')
    destination.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        'schema_version': SCHEMA, 'status': 'FRONTEND_SOURCE_GENERATED_NOT_RUNTIME_VERIFIED',
        'owner_bindings_confirmed': True, 'backend_modified': False,
        'reference': review['reference'], 'backend': review['backend'],
        'bindings': binding, 'schema_review': review.get('schema_review'), 'frontend_path': '/dashboard/',
        'limitations': ['backend_not_bundled', 'serve_on_same_origin_under_/dashboard',
                        'response_schema_must_be_runtime_verified',
                        'reference_visual_hints_not_pixel_replication' if visual else 'design_not_observed_from_reference'],
    }
    with tempfile.TemporaryDirectory(prefix='.rea-bridge-', dir=destination.parent) as temp:
        stage = Path(temp) / 'dashboard'
        stage.mkdir()
        (stage / 'index.html').write_text(HTML+'\n', encoding='utf-8')
        (stage / 'style.css').write_text(CSS+'\n'+_reference_css(visual), encoding='utf-8')
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
    parser.add_argument('--visual', type=Path, help='separately captured, origin-matched computed-style reference JSON')
    parser.add_argument('--schema', type=Path, help='read-only FastAPI AST model/route hints for same backend SHA')
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
                         _read_json(args.bindings) if args.bindings is not None else None,
                         visual=_read_json(args.visual) if args.visual is not None else None,
                         schema=_read_json(args.schema) if args.schema is not None else None)
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
