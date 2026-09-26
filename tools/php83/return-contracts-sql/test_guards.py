import hashlib,json,pathlib,tempfile,unittest
from unittest.mock import patch
import prepare,verify,observe
class Guards(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name);self.addCleanup(self.tmp.cleanup)
 def fixture(self):
  (self.root/'a').write_bytes(b'known');d={'files':{'a':prepare.sha(b'known')}};(self.root/'manifest.json').write_text(json.dumps(d));return prepare.sha((self.root/'manifest.json').read_bytes())
 def test_verify(self):pin=self.fixture();self.assertEqual(verify.verify(self.root,pin)['files'],{'a':prepare.sha(b'known')})
 def test_manifest_drift(self):self.fixture();self.assertRaises(ValueError,verify.verify,self.root,'0'*64)
 def test_file_drift(self):pin=self.fixture();(self.root/'a').write_text('changed');self.assertRaises(ValueError,verify.verify,self.root,pin)
 def test_extra_file(self):pin=self.fixture();(self.root/'extra').write_text('x');self.assertRaises(ValueError,verify.verify,self.root,pin)
 def test_missing_file(self):pin=self.fixture();(self.root/'a').unlink();self.assertRaises(ValueError,verify.verify,self.root,pin)
 def test_symlink(self):pin=self.fixture();(self.root/'link').symlink_to(self.root/'a');self.assertRaises(ValueError,verify.verify,self.root,pin)
 def test_nested_manifest_not_ignored(self):pin=self.fixture();(self.root/'nested').mkdir();(self.root/'nested/manifest.json').write_text('x');self.assertRaises(ValueError,verify.verify,self.root,pin)
 def test_empty_files(self):raw=json.dumps({'files':{}}).encode();(self.root/'manifest.json').write_bytes(raw);self.assertRaises(ValueError,verify.verify,self.root,prepare.sha(raw))
 def test_prepare_badzip(self):z=self.root/'bad.zip';z.write_bytes(b'x');self.assertRaises(ValueError,prepare.prepare,z,self.root/'out')
 def test_prepare_existing(self):self.assertRaises(ValueError,prepare.prepare,'not-opened',self.root)
 def test_self_rehashed_manifest_refused(self):
  self.fixture()
  with patch.object(prepare,'prepare',return_value={'files':{'not-authorized':'0'*64}}):self.assertRaises(ValueError,observe.validate,self.root,'unused')
 def test_atomic(self):out=self.root/'report';observe.atomic(out,{'a':1});self.assertEqual(json.loads(out.read_text()),{'a':1});self.assertEqual(len(list(self.root.iterdir())),1)
 def test_diagnostic_channel(self):s=(prepare.HERE/'probe.php').read_text();self.assertIn('return false;',s);self.assertNotIn('return true;',s)
 def test_no_scalar_coercion(self):s=(prepare.HERE/'probe.php').read_text();self.assertFalse(any(x in s for x in ['(int)','(bool)','(string)','intval(','boolval(']))
 def test_only_four_seams(self):
  import re
  self.assertEqual(re.findall(r'class (\w+)',(prepare.HERE/'seams.php').read_text()),['KalturaLog','KalturaMonitorClient','kQueryCache','kApiCache'])
 def test_datadir_before_ddl(self):s=(prepare.HERE/'probe.php').read_text();self.assertLess(s.index('SELECT @@datadir'),s.index('CREATE DATABASE'))
 def test_native_control_full_classes(self):s=(prepare.HERE/'probe.php').read_text();self.assertIn("['PDO','PropelPDO','KalturaPDO','DebugPDO']",s);self.assertIn("get_class($s)",s)
 def test_exact_unit_cleanup(self):s=(prepare.HERE/'observe.py').read_text();self.assertIn("remote('sudo -n systemctl stop '+db['unit'])",s);self.assertNotIn('pkill',s)
if __name__=='__main__':unittest.main()
