import importlib.util,unittest,tempfile,json,stat
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile,ZipInfo
s=importlib.util.spec_from_file_location('build',Path(__file__).with_name('build.py'));b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
class BuildTests(unittest.TestCase):
 def test_exact_transform(self):
  raw=b'prefix '+b.OLD+b' suffix\n'
  with patch.object(b,'PIN',b.sha(raw)):self.assertEqual(b.transform(raw),b'prefix '+b.NEW+b' suffix\n')
 def test_wrong_pin(self):
  with self.assertRaises(ValueError):b.transform(b.OLD)
 def test_ambiguous(self):
  raw=b.OLD+b.OLD
  with patch.object(b,'PIN',b.sha(raw)):
   with self.assertRaises(ValueError):b.transform(raw)
 def test_missing(self):
  raw=b'no target'
  with patch.object(b,'PIN',b.sha(raw)):
   with self.assertRaises(ValueError):b.transform(raw)
 def archive(self,name='safe.php',mode=stat.S_IFREG|0o644):
  d=tempfile.TemporaryDirectory();self.addCleanup(d.cleanup);p=Path(d.name)/'fixture.zip'
  with ZipFile(p,'w') as z:
   i=ZipInfo('server-Rigel-18.20.0/'+name);i.external_attr=mode<<16;z.writestr(i,b'fixture')
  return p
 def test_archive_positive(self):
  p=self.archive()
  with patch.object(b,'FILES',['safe.php']):self.assertEqual(b.read_archive(p,b.sha(p.read_bytes())),{'safe.php':b'fixture'})
 def test_archive_wrong_pin(self):
  with self.assertRaises(ValueError):b.read_archive(self.archive(),'0'*64)
 def test_archive_symlink(self):
  p=self.archive(mode=stat.S_IFLNK|0o777)
  with patch.object(b,'FILES',['safe.php']):
   with self.assertRaises(ValueError):b.read_archive(p,b.sha(p.read_bytes()))
 def test_archive_parent(self):
  p=self.archive('../escape.php')
  with patch.object(b,'FILES',['../escape.php']):
   with self.assertRaises(ValueError):b.read_archive(p,b.sha(p.read_bytes()))
 def test_missing_input(self):
  p=self.archive()
  with self.assertRaises(ValueError):b.read_archive(p,b.sha(p.read_bytes()))
 def test_closure_has_no_capture(self):self.assertNotIn(b'use (',b.NEW);self.assertNotIn(b'$this',b.NEW)
if __name__=='__main__':unittest.main()
