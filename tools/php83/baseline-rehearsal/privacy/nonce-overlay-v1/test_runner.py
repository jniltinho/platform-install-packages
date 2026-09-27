import importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('nonce_run',Path(__file__).with_name('run.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_private_field_nested_rejected(self):
  for key in ['secret','password','ks','token','canary','nonce','user_id']:
   with self.assertRaises(ValueError):m.check_public([{'safe':[{key:'private'}]}])
 def test_partial_complete_receipts_preserved(self):
  self.assertEqual(m.public_rows(b'{"user_attempted":true}\n{"truncated":',partial=True),[{'user_attempted':True}])
 def test_partial_secret_not_exported(self):
  with self.assertRaises(ValueError):m.public_rows(b'{"ks":"private"}\n',partial=True)
 def test_user_checkpoint_before_send(self):
  code=Path(__file__).with_name('guest.py').read_text();self.assertIn("report['user_attempted']=True;checkpoint()",code)
 def test_safe_receipt(self):m.check_public({'status':'INCOMPLETE','counts':[0,0],'auth':False})
 def test_destination_and_cleanup(self):
  code=Path(m.__file__).read_text()
  for s in ['baseline74','IPAddressDeny=any','IPAddressAllow=192.168.56.74/32','RuntimeMaxSec=360','systemctl stop','Stage pin failed']:self.assertIn(s,code)
 def test_pending_reject_before_ssh(self):
  code=Path(m.__file__).read_text();self.assertLess(code.index("if 'PENDING_REVIEW'"),code.index("stage=run("))
 def test_only_fixed_dependencies(self):
  self.assertEqual(len(m.FILES),8);self.assertEqual(len(m.FILES),len(set(m.FILES)))
if __name__=='__main__':unittest.main()
