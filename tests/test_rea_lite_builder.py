from __future__ import annotations

import base64
import hashlib
import json
import re
from pathlib import Path

import pytest
from rea.lite_builder import build
from rea.mvp import DataError, source_sha256


def fixture(tmp_path: Path, content='id,title,category,price\n1,콜드브루,음료,3000\n2,케이크,디저트,4500\n'):
    src = tmp_path / 'catalog.csv'
    src.write_text(content, encoding='utf-8')
    return src


def extract(html):
    payload = re.search(r'<script id="rea-data" type="application/octet-stream">([^<]+)</script>', html).group(1)
    return json.loads(base64.b64decode(payload).decode('utf-8'))


def test_builder_real_pro_parser(tmp_path):
    src = fixture(tmp_path)
    output = tmp_path / 'store.html'
    result = build(src, output, name='My <Store> & shop', theme='inventory', approval='APPROVE', expected_source_sha256=source_sha256(src))
    assert result['status'] == 'CREATED' and result['rows'] == 2
    text = output.read_text(encoding='utf-8')
    assert 'My <Store>' not in text
    data = extract(text)
    assert data['records'][0]['title'] == '콜드브루'
    assert data['name'] == 'My <Store> & shop'
    assert data['theme'] == 'inventory'
    assert 'connect-src \'none\'' in text
    with pytest.raises(FileExistsError):
        build(src, output, name='My Shop', approval='APPROVE')
    assert output.read_text(encoding='utf-8') == text


def test_no_approval_no_files(tmp_path):
    src = fixture(tmp_path)
    with pytest.raises(DataError):
        build(src, tmp_path / 'unapproved.html', name='Test')
    assert not (tmp_path / 'unapproved.html').exists()


def test_changed_source_rejected(tmp_path):
    src = fixture(tmp_path)
    sha = source_sha256(src)
    src.write_text('id,title,category\nB,new,Office\n', encoding='utf-8')
    with pytest.raises(DataError):
        build(src, tmp_path / 'stale.html', name='Test', approval='APPROVE', expected_source_sha256=sha)
    assert not (tmp_path / 'stale.html').exists()


@pytest.mark.parametrize('bad', ['id,title,category\n1,x,g\n1,y,g\n', 'id,title,category\n1,,g\n', 'id,title\n1,x\n', 'id,title,category\n'])
def test_bad_input_never_publishes(tmp_path, bad):
    src = fixture(tmp_path, bad)
    with pytest.raises(DataError):
        build(src, tmp_path / 'bad.html', name='Test', approval='APPROVE')
    assert not (tmp_path / 'bad.html').exists()


def test_explicit_mapping_reuses_real_engine(tmp_path):
    src = fixture(tmp_path, 'key,label,kind,price\n01,Tea,Drink,2000\n')
    out = tmp_path / 'mapped.html'
    build(src, out, name='Mapped', approval='APPROVE', mapping={'id': 'key', 'title': 'label', 'category': 'kind'})
    data = extract(out.read_text(encoding='utf-8'))
    assert data['headers'] == ['id', 'title', 'category', 'price']
    assert data['records'][0] == {'id': '01', 'title': 'Tea', 'category': 'Drink', 'price': '2000'}


def test_mapping_requires_exact_three_fields(tmp_path):
    src = fixture(tmp_path, 'key,label,kind\n01,Tea,Drink\n')
    with pytest.raises(DataError):
        build(src, tmp_path / 'bad.html', name='Bad', approval='APPROVE', mapping={'id': 'key', 'title': 'label'})


def test_json_same_parser(tmp_path):
    src = tmp_path / 'items.json'
    src.write_text(json.dumps([{'id': '1', 'title': 'Desk', 'category': 'Office'}]), encoding='utf-8')
    out = tmp_path / 'office.html'
    build(src, out, name='Office', approval='APPROVE', theme='office')
    assert extract(out.read_text(encoding='utf-8'))['records'][0]['title'] == 'Desk'


def test_theme_and_extension_refusals(tmp_path):
    src = fixture(tmp_path)
    with pytest.raises(DataError):
        build(src, tmp_path / 'bad.html', name='Shop', approval='APPROVE', theme='evil')
    with pytest.raises(DataError):
        build(src, tmp_path / 'bad.txt', name='Shop', approval='APPROVE')
