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
 def test_body_only_no_media(self):
  code=Path(m.__file__).read_text();self.assertNotIn('uploadtoken',code);self.assertNotIn('print(ks',code);self.assertNotIn('print(secret',code)
if __name__=='__main__':unittest.main()
