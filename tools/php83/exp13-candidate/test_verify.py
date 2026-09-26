import importlib.util
import io
from pathlib import Path
import unittest
import warnings
import zipfile
s=importlib.util.spec_from_file_location('verifier',Path(__file__).with_name('verify.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
class Bytes:
 def __init__(self,data):self.data=data
 def read_bytes(self):return self.data
class Verification(unittest.TestCase):
 def test_duplicate_zip(self):
  b=io.BytesIO()
  with warnings.catch_warnings():
   warnings.simplefilter('ignore')
   with zipfile.ZipFile(b,'w') as z:z.writestr('x',b'a');z.writestr('x',b'b')
  with self.assertRaises(ValueError):v.members(b.getvalue())
 def test_original_badpin(self):
  with self.assertRaises(ValueError):v.verify(Bytes(b'bad'),Bytes(b''),Bytes(b''),Bytes(b''))
 def test_actual_artifacts(self):
  root=v.ROOT.parent/'platform-install-packages-php83-artifacts'
  p=root/'exp13/Rigel-18.20.0-php83-experimental.exp13.zip';q=root/'exp13-repeat/Rigel-18.20.0-php83-experimental.exp13.zip'
  r=v.verify(Path('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip'),root/'exp12/Rigel-18.20.0-php83-experimental.exp12.zip',p,q)
  self.assertIs(r['application_acceptance'],False);self.assertEqual(r['delta_modified'],12);self.assertEqual(r['delta_added'],1)
 def test_repeat_corruption(self):
  root=v.ROOT.parent/'platform-install-packages-php83-artifacts';p=root/'exp13/Rigel-18.20.0-php83-experimental.exp13.zip'
  with self.assertRaises(ValueError):v.verify(Path('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip'),root/'exp12/Rigel-18.20.0-php83-experimental.exp12.zip',p,Bytes(b'corrupt'))
if __name__=='__main__':unittest.main()
