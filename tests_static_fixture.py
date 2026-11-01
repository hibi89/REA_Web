"""Single trusted synthetic schema fixture, no customer data."""
FABLE = {
  'schema_version':'1.0','target':{'input_url':'https://example.org/'},
  'scanned_at':'2026-11-01T00:00:00+00:00','scan_mode':'static',
  'frontend':[],'backend_inferred':[],'infra':[],
  'api':{'endpoints':[],'candidates':[],'chart_candidates':[]},'charts':[],'warnings':[],
}
BACKEND = {
  'schema_version':'rea.backend_contract.v0.1','status':'REVIEW_REQUIRED',
  'generation_allowed':False,'execution_performed':False,'input':{'sha256':'f'*64},
  'api':{'endpoints':[
     {'path':path,'methods':['GET'],'verification':'STATIC_DECLARATION_ONLY','mount':'app_declaration'}
     for path in ('/api/jobs','/api/metrics','/api/jobs/{job_id}')
  ]},
}
BINDINGS={'list':{'path':'/api/jobs','field':'items'},
          'metrics':{'path':'/api/metrics','field':'__root__'},
          'detail':{'path':'/api/jobs/{job_id}','field':'__root__'}}
