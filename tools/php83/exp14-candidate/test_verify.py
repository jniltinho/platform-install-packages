import io,importlib.util,unittest,warnings,zipfile
from pathlib import Path
s=importlib.util.spec_from_file_location('v',Path(__file__).with_name('verify.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
class Bytes:
 def __init__(self,b):self.b=b
 def read_bytes(self):return self.b
class Verify(unittest.TestCase):
 def test_duplicate_member(self):
  b=io.BytesIO()
  with warnings.catch_warnings():
   warnings.simplefilter('ignore')
   with zipfile.ZipFile(b,'w') as z:z.writestr('x',b'a');z.writestr('x',b'b')
  with self.assertRaises(ValueError):v.members(b.getvalue())
 def test_bad_zip_identity(self):
  with self.assertRaises(ValueError):v.verify(Bytes(b'bad'),Bytes(b''),Bytes(b''),Bytes(b''))
if __name__=='__main__':unittest.main()
