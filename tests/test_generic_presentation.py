"""Owner-controlled field mapping for backend responses with non-default names."""
from __future__ import annotations

import copy
import json

import pytest

from rea.adapter.frontend_bridge import BridgeError, make_review, generate_frontend
from tests_static_fixture import FABLE, BACKEND, BINDINGS


CUSTOM = {
    'list':{'path':'/api/jobs','field':'items'},
    'metrics':{'path':'/api/metrics','field':'__root__'},
    'detail':{'path':'/api/jobs/{job_id}','field':'__root__'},
    'presentation': {
        'item': {'id':'ticket','name':'task','category':'department','status':'phase'},
        'metrics': {'total':'all_count','completed':'success_count','pending':'queued_count'},
        'detail_fields': ['ticket','task','department','phase']
    },
}


def test_custom_fields_generate_safe_frontend(tmp_path):
    review = make_review(FABLE,BACKEND,CUSTOM)
    assert review['bindings']['presentation']['item']['name']=='task'
    destination=tmp_path/'my_dashboard'
    generate_frontend(review,destination,owner_confirmed=True)
    js=(destination/'app.js').read_text(encoding='utf8')
    assert 'VIEW.item.name' in js and 'VIEW.metrics[key]' in js
    assert '"task"' in js and '"department"' in js
    assert 'innerHTML' not in js
    assert (destination/'manifest.json').is_file()


def test_custom_path_parameter_supported(tmp_path):
    backend=copy.deepcopy(BACKEND)
    backend['api']['endpoints'][2]['path']='/api/jobs/{ticket_id}'
    bindings=copy.deepcopy(CUSTOM)
    bindings['detail']['path']='/api/jobs/{ticket_id}'
    bindings['detail']['path_param']='ticket_id'
    plan=make_review(FABLE,backend,bindings)
    generate_frontend(plan,tmp_path/'out',owner_confirmed=True)
    js=(tmp_path/'out'/'app.js').read_text(encoding='utf8')
    assert 'path_param' in js and 'ticket_id' in js


@pytest.mark.parametrize('mutate',[
    lambda x: x['presentation']['item'].update(name='<svg/onload=alert(1)>'),
    lambda x: x['presentation']['metrics'].update(total='__proto__'),
    lambda x: x['presentation']['detail_fields'].append('task;alert(1)'),
    lambda x: x['presentation']['detail_fields'].append('task'),
    lambda x: x['presentation'].update(script='alert(1)'),
    lambda x: x['detail'].update(path_param='other'),
    lambda x: x['detail'].update(path_param='constructor'),
])
def test_bad_presentation_is_rejected(mutate):
    bindings=copy.deepcopy(CUSTOM)
    mutate(bindings)
    with pytest.raises(BridgeError):make_review(FABLE,BACKEND,bindings)


def test_old_binding_compatibility():
    assert make_review(FABLE,BACKEND,BINDINGS)['bindings']==BINDINGS
