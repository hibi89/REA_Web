import hashlib, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
from rea.lite_builder import build_lite
from rea.mvp import DataError
BASE='식별자,이름,분류,비고\nA-01,콜드브루,커피,진한 맛\nA-02,딸기우유,음료,시원함\n'
class LiteBuilder(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.src=self.root/'raw.csv';self.src.write_text(BASE,encoding='utf-8');self.out=self.root/'catalog.html';self.kw=dict(mapping={'id':'식별자','title':'이름','category':'분류'},expected_sha256=hashlib.sha256(self.src.read_bytes()).hexdigest(),confirmation='APPROVE')
 def build(self,**changes):return build_lite(self.src,self.out,**{**self.kw,**changes})
 def test_actual_html_generated_plain_data_serverless(self):
  r=self.build();s=self.out.read_text(encoding='utf-8');self.assertEqual(r['rows'],2);self.assertIn('콜드브루',s);self.assertIn('script-src',s);self.assertIn("connect-src 'none'",s)
  self.assertFalse(r['customer_sale_approved']);self.assertFalse(r['server_required']);self.assertFalse(r['remote_upload'])
 def test_themes(self):
  for theme in ('cafe','inventory','office'):
   with self.subTest(theme=theme):
    f=self.root/(theme+'.html');r=build_lite(self.src,f,**{**self.kw,'theme':theme});self.assertEqual(r['theme'],theme);self.assertIn('data-theme="'+theme+'"',f.read_text(encoding='utf-8'))
 def test_duplicate_source_id_rejected(self):
  self.src.write_text(BASE+'A-01,중복,커피,테스트\n',encoding='utf-8');self.kw['expected_sha256']=hashlib.sha256(self.src.read_bytes()).hexdigest()
  with self.assertRaises(DataError):self.build();self.assertFalse(self.out.exists())
 def test_old_sha_rejected(self):
  self.src.write_text(BASE+'A-03,새로운 메뉴,커피,테스트\n',encoding='utf-8')
  with self.assertRaises(DataError):self.build();self.assertFalse(self.out.exists())
 def test_owner_explicit_confirmation(self):
  with self.assertRaises(DataError):self.build(confirmation='CONFIRM');self.assertFalse(self.out.exists())
 def test_missing_mapping(self):
  with self.assertRaises((DataError,KeyError)):self.build(mapping={'id':'식별자','title':'이름','category':'이름'});self.assertFalse(self.out.exists())
 def test_never_overwrite_existing(self):
  self.out.write_text('KEEP',encoding='utf-8');self.assertRaises(FileExistsError,self.build);self.assertEqual(self.out.read_text(encoding='utf-8'),'KEEP')
 def test_html_raw_tag_script_safely_encoded(self):
  self.src.write_text('식별자,이름,분류,비고\nA-01,"</script><img src=x onerror=alert(1)>",음료,자연어\n',encoding='utf-8')
  self.kw['expected_sha256']=hashlib.sha256(self.src.read_bytes()).hexdigest();self.build()
  html=self.out.read_text(encoding='utf-8');self.assertNotIn('</script><img',html);self.assertIn('\\u003c/script\\u003e',html)
 def test_injection_in_title_escaped(self):
  self.build(name='<script>alert(1)</script>');x=self.out.read_text(encoding='utf-8');self.assertNotIn('<title><script>',x);self.assertIn('&lt;script&gt;',x)
 def test_source_and_output_unchanged_on_failure(self):
  b=self.src.read_bytes();self.out.write_text('untouched',encoding='utf-8');self.assertRaises(FileExistsError,self.build);self.assertEqual(self.src.read_bytes(),b);self.assertEqual(self.out.read_text(encoding='utf-8'),'untouched')
 def test_symlink_parent_rejected(self):
  target=self.root/'target';target.mkdir();link=self.root/'shortcut'
  try:link.symlink_to(target, target_is_directory=True)
  except OSError:self.skipTest('links unsupported')
  with self.assertRaises(DataError):build_lite(self.src,link/'app.html',**self.kw)
 def test_absolute_paths_only(self):
  with self.assertRaises(DataError):build_lite(self.src,Path('relative.html'),**self.kw)
 def test_no_extra_unapproved_source_columns(self):
  self.build();self.assertIn('"비고"',self.out.read_text(encoding='utf-8'))
 def test_bad_theme_rejected(self):
  with self.assertRaises(DataError):self.build(theme='remote');self.assertFalse(self.out.exists())
 def test_js_prototype_pollution_header_refused(self):
  self.src.write_text('식별자,이름,분류,__proto__\nA01,상품,분류,evil\n',encoding='utf8')
  self.kw['expected_sha256']=hashlib.sha256(self.src.read_bytes()).hexdigest()
  with self.assertRaises(DataError):self.build()
  self.assertFalse(self.out.exists())
 def test_missing_output_parent_rejected(self):
  self.out=self.root/'does-not-exist'/'no.html'
  with self.assertRaises(DataError):self.build()
 def test_owner_csv_no_sensitive_data_in_receipt(self):
  result=self.build()
  self.assertNotIn('콜드브루',json.dumps(result,ensure_ascii=False))
 def test_original_source_header_mapping_is_embedded_for_customer_csv_updates(self):
  self.build()
  contents=self.out.read_text(encoding='utf-8')
  self.assertIn('"source_headers":["식별자","이름","분류","비고"]',contents)
  self.assertIn('"owner_mapping":{"id":"식별자","title":"이름","category":"분류"}',contents)
 def test_cli_prints_metadata_not_source_content(self):
  cmd=[sys.executable,'-m','rea.lite_builder','--source',str(self.src),'--out',str(self.out),'--source-sha256',self.kw['expected_sha256'],'--id-field','식별자','--title-field','이름','--category-field','분류','--confirm','APPROVE']
  p=subprocess.run(cmd,encoding='utf-8',capture_output=True,cwd=Path(__file__).parents[1]);self.assertEqual(p.returncode,0,p.stderr);self.assertNotIn('콜드브루',p.stdout);self.assertFalse(json.loads(p.stdout)['customer_sale_approved'])
if __name__=='__main__':unittest.main()
