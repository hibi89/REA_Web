"""Reproducible SYNTHETIC package, source identity, no-execution and hard failures."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

from rea.adapter.backend_zip import inspect_backend_zip
from rea.adapter.backend_schema import inspect_backend_schema
from rea.adapter.frontend_bridge import make_review, generate_frontend
from rea.adapter.project_bundle import build_synthetic_project, UnsafeProjectBundle
from rea.adapter.runtime_contract import reconcile
from tests_static_fixture import FABLE, BINDINGS

SOURCE = '''from fastapi import FastAPI, HTTPException
app=FastAPI()
JOBS=[{"id":"X1","name":"Synthetic task","category":"audit","status":"done"},
      {"id":"X2","name":"Pending check","category":"quality","status":"pending"}]
@app.get('/api/jobs')
def jobs(): return {"items":JOBS}
@app.get('/api/metrics')
def metrics(): return {"total":2,"completed":1,"pending":1}
@app.get('/api/jobs/{job_id}')
def detail(job_id:str):
 for job in JOBS:
  if job['id']==job_id:return job
 raise HTTPException(status_code=404)
'''


def trusted_bundle_input(tmp_path, source=SOURCE, extra=None):
    archive = tmp_path / 'owner_synthetic.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('app.py', source)
        z.writestr('requirements.txt', 'fastapi>=0.110,<1\nuvicorn>=0.27,<1\n')
        for name, data in (extra or {}).items():
            z.writestr(name, data)
    contract = inspect_backend_zip(archive)
    schema = inspect_backend_schema(archive)
    from fastapi import FastAPI
    trusted = FastAPI()
    @trusted.get('/api/jobs')
    def jobs(): return {'items': []}
    @trusted.get('/api/metrics')
    def metrics(): return {'total':2,'completed':1,'pending':1}
    @trusted.get('/api/jobs/{job_id}')
    def detail(job_id:str): return {'id':job_id}
    reconciliation = reconcile(contract, schema, trusted.openapi())
    assert reconciliation['status'] == 'DECLARATIONS_MATCH_REVIEW_REQUIRED', reconciliation['issues']
    review = make_review(FABLE, contract, BINDINGS)
    frontend = tmp_path / 'generated_frontend'
    generate_frontend(review, frontend, owner_confirmed=True)
    return archive, frontend, reconciliation, contract['input']['sha256']


def package(tmp_path, *, source=SOURCE, extra=None):
    archive, frontend, reconciliation, sha = trusted_bundle_input(tmp_path, source, extra)
    output = tmp_path / 'bundle.zip'
    result = build_synthetic_project(archive, frontend, reconciliation, output,
                                    expected_backend_sha256=sha, developer_authorized_synthetic=True)
    return output, result


def test_bundle_deterministic_and_all_hashes(tmp_path):
    archive, front, reconciliation, sha = trusted_bundle_input(tmp_path)
    one=tmp_path/'one.zip'; two=tmp_path/'two.zip'
    x=build_synthetic_project(archive,front,reconciliation,one,expected_backend_sha256=sha,developer_authorized_synthetic=True)
    y=build_synthetic_project(archive,front,reconciliation,two,expected_backend_sha256=sha,developer_authorized_synthetic=True)
    assert one.read_bytes()==two.read_bytes()
    assert x['archive_sha256']==y['archive_sha256']==hashlib.sha256(one.read_bytes()).hexdigest()
    with zipfile.ZipFile(one) as z:
        assert z.testzip() is None
        hashes=json.loads(z.read('SHA256SUMS.json'))
        manifest=json.loads(z.read('MANIFEST.json'))
        assert manifest['trusted_synthetic_only'] is True
        assert manifest['runtime_origin_attested'] is False
        assert manifest['behavior_verified_by_bundle_generator'] is False
        assert manifest['original_backend_zip_sha256']==sha
        assert manifest['file_count']==len(z.namelist())
        assert all(hashlib.sha256(z.read(name)).hexdigest()==digest for name,digest in hashes.items())
        assert all(not name.startswith('/') and '..' not in name for name in z.namelist())
        assert 'backend/app.py' in z.namelist() and 'dashboard/app.js' in z.namelist()
        assert 'runtime_entry.py' in z.namelist()


def test_bundle_does_not_execute_owner_python(tmp_path):
    marker=tmp_path/'SHOULD_NOT_EXIST'
    source=SOURCE+f'\nopen({str(marker)!r},"w").write("danger")\n'
    package(tmp_path,source=source)
    assert not marker.exists()


def test_refuse_missing_developer_authorization(tmp_path):
    z,front,r,sha=trusted_bundle_input(tmp_path)
    with pytest.raises(UnsafeProjectBundle, match='authorization'):
        build_synthetic_project(z,front,r,tmp_path/'new.zip',expected_backend_sha256=sha)
    assert not (tmp_path/'new.zip').exists()


def test_refuse_bad_backend_sha(tmp_path):
    z,front,r,sha=trusted_bundle_input(tmp_path)
    with pytest.raises(UnsafeProjectBundle, match='review mismatch|SHA'):
        build_synthetic_project(z,front,r,tmp_path/'new.zip',expected_backend_sha256='0'*64,developer_authorized_synthetic=True)


def test_refuse_unreviewed_declared_runtime(tmp_path):
    z,front,r,sha=trusted_bundle_input(tmp_path)
    r['status']='MISMATCH'
    with pytest.raises(UnsafeProjectBundle):
        build_synthetic_project(z,front,r,tmp_path/'new.zip',expected_backend_sha256=sha,developer_authorized_synthetic=True)


def test_refuse_falsely_attested_runtime(tmp_path):
    z,front,r,sha=trusted_bundle_input(tmp_path)
    r['runtime_origin_attested']=True
    with pytest.raises(UnsafeProjectBundle):
        build_synthetic_project(z,front,r,tmp_path/'new.zip',expected_backend_sha256=sha,developer_authorized_synthetic=True)


def test_refuse_missing_get_binding_confirmation(tmp_path):
    z,front,r,sha=trusted_bundle_input(tmp_path)
    r['matched_declarations']=[e for e in r['matched_declarations'] if e['path']!='/api/metrics']
    with pytest.raises(UnsafeProjectBundle,match='binding'):
        build_synthetic_project(z,front,r,tmp_path/'new.zip',expected_backend_sha256=sha,developer_authorized_synthetic=True)


def test_refuse_unsafe_archive_extras(tmp_path):
    z,front,r,sha=trusted_bundle_input(tmp_path,extra={'.env':'API_TOKEN=never-copy'})
    with pytest.raises(UnsafeProjectBundle,match='only permits'):
        build_synthetic_project(z,front,r,tmp_path/'new.zip',expected_backend_sha256=sha,developer_authorized_synthetic=True)


def test_refuse_symlink_frontend_entry(tmp_path):
    z,front,r,sha=trusted_bundle_input(tmp_path)
    p=front/'app.js'; tmp=tmp_path/'real_js'; p.rename(tmp)
    p.symlink_to(tmp)
    with pytest.raises(UnsafeProjectBundle,match='nonregular'):
        build_synthetic_project(z,front,r,tmp_path/'new.zip',expected_backend_sha256=sha,developer_authorized_synthetic=True)


def test_refuse_tampered_frontend_manifest(tmp_path):
    z,front,r,sha=trusted_bundle_input(tmp_path)
    manifest=front/'manifest.json'; d=json.loads(manifest.read_text(encoding='utf-8'))
    d['backend']['sha256']='0'*64
    manifest.write_text(json.dumps(d),encoding='utf-8')
    with pytest.raises(UnsafeProjectBundle,match='SHA mismatch'):
        build_synthetic_project(z,front,r,tmp_path/'new.zip',expected_backend_sha256=sha,developer_authorized_synthetic=True)



@pytest.mark.parametrize('filename,extra,error', [
    ('app.js', b'\\n// unexpected executable change\\n', 'JavaScript'),
    ('index.html', b'\\n<!-- injected page content -->\\n', 'HTML'),
    ('style.css', b'\\n@import url(https://untrusted.example/);\\n', 'neutral frontend CSS'),
])
def test_reject_mutated_generated_frontend_source_before_packaging(tmp_path, filename, extra, error):
    """Generated assets are trust inputs, not authorized by editable manifest flags."""
    z, front, review, sha = trusted_bundle_input(tmp_path)
    changed = front / filename
    changed.write_bytes(changed.read_bytes() + extra)
    output = tmp_path / 'refused.zip'
    with pytest.raises(UnsafeProjectBundle, match=error):
        build_synthetic_project(z, front, review, output,
                                expected_backend_sha256=sha,
                                developer_authorized_synthetic=True)
    assert not output.exists()


def test_reject_manifest_only_binding_remap_without_regenerated_javascript(tmp_path):
    z, front, review, sha = trusted_bundle_input(tmp_path)
    path = front / 'manifest.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    data['bindings']['list']['path'] = '/api/metrics'
    path.write_text(json.dumps(data), encoding='utf-8')
    output = tmp_path / 'refused.zip'
    with pytest.raises(UnsafeProjectBundle, match='JavaScript'):
        build_synthetic_project(z, front, review, output,
                                expected_backend_sha256=sha,
                                developer_authorized_synthetic=True)
    assert not output.exists()


def test_no_overwrite(tmp_path):
    z,front,r,sha=trusted_bundle_input(tmp_path)
    out=tmp_path/'new.zip'; out.write_bytes(b'KEEP')
    with pytest.raises(FileExistsError):
        build_synthetic_project(z,front,r,out,expected_backend_sha256=sha,developer_authorized_synthetic=True)
    assert out.read_bytes()==b'KEEP'


def test_clean_extract_and_cli_integrity_guard(tmp_path):
    out,_=package(tmp_path)
    extraction=tmp_path/'unpacked'; extraction.mkdir()
    with zipfile.ZipFile(out) as archive:
        archive.extractall(extraction)
    checked=subprocess.run([sys.executable,'runtime_entry.py','--check'],cwd=extraction,text=True,capture_output=True)
    assert checked.returncode==0,checked.stderr
    assert 'SOURCE_HASH' in checked.stdout
    app=extraction/'backend/app.py'; app.write_text(app.read_text(encoding='utf-8')+'\n#touched',encoding='utf-8')
    checked=subprocess.run([sys.executable,'runtime_entry.py','--check'],cwd=extraction,text=True,capture_output=True)
    assert checked.returncode==2 and 'REFUSED' in checked.stderr


def test_tampered_frontend_asset_rejected_by_manual_launcher(tmp_path):
    out,_=package(tmp_path)
    extraction=tmp_path/'clean';extraction.mkdir()
    with zipfile.ZipFile(out) as archive:archive.extractall(extraction)
    js=extraction/'dashboard/app.js'
    js.write_bytes(js.read_bytes()+b'\n//broken')
    checked=subprocess.run([sys.executable,'runtime_entry.py','--check'],cwd=extraction,text=True,capture_output=True)
    assert checked.returncode==2 and 'package content changed' in checked.stderr


def test_cli_no_auto_execution(tmp_path):
    z,front,r,sha=trusted_bundle_input(tmp_path)
    review=tmp_path/'review.json'; review.write_text(json.dumps(r),encoding='utf-8')
    out=tmp_path/'out.zip'
    cmd=[sys.executable,'-m','rea.adapter.project_bundle','--backend-zip',str(z),'--frontend',str(front),'--runtime-review',str(review),'--expected-sha256',sha,'--out',str(out)]
    missing=subprocess.run(cmd,text=True,capture_output=True)
    assert missing.returncode==2 and not out.exists()
    accepted=subprocess.run(cmd+['--developer-authorized-synthetic'],text=True,capture_output=True)
    assert accepted.returncode==0,accepted.stderr
    again=subprocess.run(cmd+['--developer-authorized-synthetic'],text=True,capture_output=True)
    assert again.returncode==2 and out.exists()
