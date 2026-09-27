import importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('apply',Path(__file__).with_name('apply.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_reviewed_payload(self):
  p=m.payload();self.assertEqual(len(p['pin']),64);self.assertEqual(len(p['blobs']),9)
 def test_native_guard(self):
  for text in ['192.168.56.74','192.168.56.20','kaltura-php74-baseline','not root.exists()','0o444','0o555','0o600','INCOMPLETE_TIMEOUT_MANUAL_RECOVERY_NO_AUTH']:
   self.assertIn(text,m.GUEST)
 def test_no_auth(self):
  self.assertNotIn('session.start',m.GUEST);self.assertNotIn('curl',m.GUEST)
if __name__=='__main__':unittest.main()
