"""Trusted synthetic packaged ZIP: real Chromium checks emitted CSS and dashboard.

The ZIP is assembled from *self-authored* FastAPI only. Chromium receives
in-page synthetic API responses, not network HTTP; CSP is inspected as text,
not enforced in this harness. No customer code or external URL is executed.
"""
from __future__ import annotations

import json
import os
import re
import zipfile

from playwright.sync_api import expect, sync_playwright

from rea.adapter.backend_zip import inspect_backend_zip
from rea.adapter.frontend_bridge import generate_frontend, make_review
from rea.adapter.project_bundle import build_synthetic_project
from rea.adapter.visual_reference import sanitize_observation
from test_project_bundle import trusted_bundle_input
from tests_static_fixture import FABLE, BINDINGS


def test_styled_trusted_zip_renders_kpi_and_reference_colors_in_chromium(tmp_path):
    backend_zip, _, reconciliation, sha = trusted_bundle_input(tmp_path)
    backend = inspect_backend_zip(backend_zip)
    origin = make_review(FABLE, backend, BINDINGS)['reference']['origin']
    visual = sanitize_observation({
        'origin': origin, 'layout': 'sidebar',
        'viewport': {'width': 1365, 'height': 900},
        'colors': {'canvas': '#f3f5f7', 'surface': '#ffffff', 'ink': '#132233',
                   'navigation': '#223355', 'accent': '#bb4064'},
        'components': {'navigation': 1, 'buttons': 2, 'tables': 1, 'forms': 0,
                       'inputs': 1, 'card_like': 3},
        'evidence': {'navigation_visible': True, 'panel_visible': True,
                     'button_visible': True},
    }, allow_loopback=True)
    frontend = tmp_path / 'generated'
    generate_frontend(make_review(FABLE, backend, BINDINGS, visual=visual),
                      frontend, owner_confirmed=True)
    output = tmp_path / 'trusted_synthetic.zip'
    build_synthetic_project(backend_zip, frontend, reconciliation, output,
                            expected_backend_sha256=sha,
                            developer_authorized_synthetic=True)

    with zipfile.ZipFile(output) as archive:
        contents = {name: archive.read(name) for name in
                    ('dashboard/index.html', 'dashboard/style.css',
                     'dashboard/app.js', 'dashboard/manifest.json')}
    manifest = json.loads(contents['dashboard/manifest.json'])
    assert manifest['visual_contract']['sha256'] == visual['sha256']
    assert manifest['reference']['layout_similarity_to_reference'] == 'UNVERIFIED'
    # Test the exact ZIP CSS and JS in a controlled document. This sandbox
    # forbids all browser navigation; do not claim network or CSP enforcement.
    original_html = contents['dashboard/index.html'].decode('utf-8')
    assert "default-src 'none'" in original_html
    assert "connect-src 'self'" in original_html
    markup = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', '', original_html)
    markup = markup.replace('<link href="/dashboard/style.css" rel="stylesheet">', '')
    markup = markup.replace('<script defer src="/dashboard/app.js"></script>', '')
    errors, requests = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.environ.get('REA_CHROMIUM_PATH') or None,
            args=['--no-sandbox'],
        )
        try:
            page = browser.new_page(viewport={'width': 1365, 'height': 900})
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.set_content(markup)
            page.add_style_tag(content=contents['dashboard/style.css'].decode('utf-8'))
            page.add_script_tag(content="""
window.fetch = async (path, options) => {
  if (!path.startsWith('/api/')) throw Error('Unexpected test path');
  window.syntheticCalls ??= [];
  window.syntheticCalls.push({path, method:options?.method||'GET'});
  const payload = path === '/api/jobs'
    ? {items:[{id:'X1',name:'Synthetic row',category:'audit',status:'done'},
              {id:'X2',name:'Pending check',category:'quality',status:'pending'}]}
    : path === '/api/metrics'
      ? {total:2,completed:1,pending:1}
      : {id:'X2',name:'Pending check',category:'quality',status:'pending'};
  return new Response(JSON.stringify(payload), {status:200,
    headers:{'Content-Type':'application/json'}});
};
""")
            page.add_script_tag(content=contents['dashboard/app.js'].decode('utf-8'))
            expect(page.locator('#connection-text')).to_have_text('CONNECTED')
            expect(page.locator('#kpi-total')).to_have_text('2')
            expect(page.locator('#kpi-completed')).to_have_text('1')
            expect(page.locator('#jobs tr')).to_have_count(2)
            assert page.locator('.sidebar').evaluate(
                'el => getComputedStyle(el).backgroundColor') == 'rgb(34, 51, 85)'
            assert page.locator('.glyph').evaluate(
                'el => getComputedStyle(el).backgroundColor') == 'rgb(187, 64, 100)'
            page.locator('#search').fill('pending')
            expect(page.locator('#jobs tr')).to_have_count(1)
            page.get_by_role('button', name='상세').click()
            expect(page.locator('#detail')).to_contain_text('X2')
            assert not errors, errors
            requests = page.evaluate('window.syntheticCalls')
            assert requests and all(x['method'] == 'GET' for x in requests)
            assert len([x for x in requests if x['path'] == '/api/metrics']) == 1
        finally:
            browser.close()
