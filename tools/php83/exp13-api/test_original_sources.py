import importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('osource',Path(__file__).with_name('original-source-identity.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class OriginalSources(unittest.TestCase):
 def test_real_pinned_archive(self):
  values=m.expected('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip');self.assertEqual(len(values),8);self.assertTrue(m.validate(values,values))
 def test_missing(self):
  expected={p:'a'*64 for p in m.PATHS};found=dict(expected);found.pop(m.PATHS[0])
  with self.assertRaises(ValueError):m.validate(found,expected)
 def test_drift(self):
  expected={p:'a'*64 for p in m.PATHS};found=dict(expected);found[m.PATHS[0]]='b'*64
  with self.assertRaises(ValueError):m.validate(found,expected)
 def test_extra(self):
  expected={p:'a'*64 for p in m.PATHS};found={**expected,'unexpected':'b'*64}
  with self.assertRaises(ValueError):m.validate(found,expected)
if __name__=='__main__':unittest.main()
