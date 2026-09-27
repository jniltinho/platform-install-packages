import importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('nonce_guest',Path(__file__).with_name('guest.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_zero_requires_exact_types(self):
  for counts in [[False,0],[0.0,0],['0',0],[0,1],[]]:
   with self.assertRaises(m.Rejected):m.accepted({'counts':counts},{'counts':[0,0]})
 def test_complete_finite_pair(self):
  self.assertTrue(m.accepted({'counts':[0,0],'status':'COMPLETE_FINITE_FILE_WINDOW','uncovered_tail_bytes':0},{'counts':[0,0],'complete':True}))
 def test_missing_journal(self):
  with self.assertRaises(m.Rejected):m.accepted({'counts':[0,0],'status':'COMPLETE_FINITE_FILE_WINDOW','uncovered_tail_bytes':0},{'counts':[0,0],'complete':1})
 def test_tail_rejected(self):
  with self.assertRaises(m.Rejected):m.accepted({'counts':[0,0],'status':'COMPLETE_FINITE_FILE_WINDOW','uncovered_tail_bytes':1},{'counts':[0,0],'complete':True})
 def test_secret_read_after_gate(self):
  code=Path(m.__file__).read_text();self.assertLess(code.index("report['invalid_nonce']=audit"),code.index("rows=legacy.sql"))
 def test_exact_network_policy(self):
  good='NoNewPrivileges=yes\nIPAddressDeny=0.0.0.0/0 ::/0\nIPAddressAllow=127.0.0.0/8 ::1/128 192.168.56.74/32'
  m.network_policy(good)
  for bad in [good+' 192.168.56.20/32',good.replace('IPAddressDeny','Unrelated'),good.replace('NoNewPrivileges=yes','NoNewPrivileges=no')]:
   with self.assertRaises(m.Rejected):m.network_policy(bad)
 def test_overlay_verified_before_exec(self):
  code=Path(m.__file__).read_text();self.assertLess(code.index("hashlib.sha256(raw)"),code.index("overlay=load('nonce_overlay'"))
 def test_spawn_importable_module(self):
  code=Path(m.__file__).read_text();self.assertIn("legacy=__import__('untimed_driver')",code);self.assertNotIn("load('nonce_legacy'",code)
 def test_owned_entry_rejects_cross_binding(self):
  m.bind_entry({'id':'0_abcdefgh','partnerId':'101'},101,'0_abcdefgh')
  for bad in [{'id':'0_wrongabc','partnerId':101},{'id':'0_abcdefgh','partnerId':102},{'id':'0_abcdefgh','partnerId':True},{'id':'0_abcdefgh','partnerId':101.0}]:
   with self.assertRaises(m.Rejected):m.bind_entry(bad,101,'0_abcdefgh')
 def test_asset_entry_and_tenant_binding(self):
  m.bind_asset({'entryId':'0_abcdefgh','partnerId':101},101,'0_abcdefgh')
  for bad in [{'entryId':'0_wrongabc','partnerId':101},{'entryId':'0_abcdefgh','partnerId':102},{'entryId':True,'partnerId':101}]:
   with self.assertRaises(m.Rejected):m.bind_asset(bad,101,'0_abcdefgh')
 def test_each_media_stage_binds(self):
  code=Path(m.__file__).read_text()
  for guard in ['bind_entry(entry,partner)','bind_entry(attached,partner,entry_id)','bind_entry(entry,partner,entry_id)','bind_asset(asset,partner,entry_id)']:self.assertIn(guard,code)
 def test_diagnostic_code_allowlist(self):
  self.assertEqual(m.scanner_code(RuntimeError('TRUNCATED'),{'TRUNCATED'}),'TRUNCATED')
  self.assertEqual(m.scanner_code(RuntimeError('PRIVATE_VALUE'),{'TRUNCATED'}),'UNKNOWN_SCANNER_CODE')
 def test_private_metadata_no_patterns(self):
  code=Path(m.__file__).read_text()
  self.assertIn("'file_marks':{p:vars(mark)",code);self.assertIn("'current_file_marks':after",code)
  self.assertNotIn("'patterns':patterns",code);self.assertNotIn("'ks':ks}",code)
 def test_private_file_exclusive(self):
  import tempfile,json
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'metadata';m.private_json(p,{'phase':'files'})
   self.assertEqual(p.stat().st_mode&0o777,0o600)
   with self.assertRaises(FileExistsError):m.private_json(p,{})
 def test_media_scope(self):
  code=Path(m.__file__).read_text()
  for required in ['MEDIA_SOURCE_PIN','STORED_SOURCE_BYTES','HTTP_SOURCE_BYTES',"not urlsplit(url).query",'media_failure_privacy',"report['upload_attempted']=True;checkpoint()",'version.isdigit()','time.monotonic()+600']:self.assertIn(required,code)
  self.assertNotIn('version)>0',code);self.assertNotIn("value('media','delete'",code)
 def test_body_only_no_secret_prints(self):
  code=Path(m.__file__).read_text();self.assertIn('uploadtoken',code);self.assertNotIn('print(ks',code);self.assertNotIn('print(secret',code)
if __name__=='__main__':unittest.main()
