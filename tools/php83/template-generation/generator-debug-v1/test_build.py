import importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('b',Path(__file__).with_name('build.py'));b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
class DebugTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.raw=b.prior.read_archive(*b.prior.ARCHIVES['original'])[b.TARGET]
 def test_pin(self):self.assertEqual(b.prior.sha(self.raw),b.PIN)
 def test_three_only(self):
  changed=b.transform(self.raw);self.assertEqual(changed.count(b.NEW),3);self.assertEqual(changed.replace(b.NEW,b.OLD),self.raw)
 def test_byte_delta(self):self.assertEqual(len(b.transform(self.raw))-len(self.raw),18)
 def test_line_preservation(self):self.assertEqual(b.transform(self.raw).count(b'\n'),self.raw.count(b'\n'))
 def test_reject_drift(self):
  with self.assertRaises(ValueError):b.transform(self.raw+b' ')
 def test_reject_reapplication(self):
  with self.assertRaises(ValueError):b.transform(b.transform(self.raw))
 def test_missing(self):
  with self.assertRaises(ValueError):b.transform(self.raw.replace(b.OLD,b'false',1))
if __name__=='__main__':unittest.main()
