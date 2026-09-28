import json,pathlib,stat,tempfile,types,unittest
from unittest import mock
import diagnose_untimed as d
class DiagnosticTests(unittest.TestCase):
 def test_boundaries_not_read_failure_only_fixedcode(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=pathlib.Path(tmp)/'unit';root.mkdir(mode=0o700)
   (root/'boundary-1.json').write_text('INVALID JSON PRIVATE_CURSOR');(root/'boundary-1.json').chmod(0o600)
   (root/'failure-2-journal.json').write_text(json.dumps({'phase':'journal','code':'BYTE_LIMIT','current_file_marks':{'SYNTHETIC_PRIVATE':'DO_NOT_EXPORT'}}));(root/'failure-2-journal.json').chmod(0o600)
   original=pathlib.Path.lstat
   def metadata(p):
    s=original(p);return types.SimpleNamespace(st_mode=s.st_mode,st_uid=0,st_nlink=s.st_nlink,st_size=s.st_size,st_dev=s.st_dev,st_ino=s.st_ino)
   with mock.patch.object(d,'ROOT',root),mock.patch.object(d.os,'geteuid',return_value=0),mock.patch.object(d.socket,'gethostname',return_value='kaltura-php74-baseline'),mock.patch.object(pathlib.Path,'lstat',metadata),mock.patch('builtins.print') as output:
    self.assertEqual(d.main(),0);value=output.call_args[0][0];self.assertNotIn('SYNTHETIC_PRIVATE',value);self.assertNotIn('PRIVATE_CURSOR',value);self.assertNotIn('DO_NOT_EXPORT',value);self.assertIn('BYTE_LIMIT',value)
 def test_wrong_host_rejected(self):
  with mock.patch.object(d.socket,'gethostname',return_value='kaltura-php83'),mock.patch('builtins.print') as output:
   self.assertEqual(d.main(),2);self.assertNotIn('root/',output.call_args[0][0])
if __name__=='__main__':unittest.main()
