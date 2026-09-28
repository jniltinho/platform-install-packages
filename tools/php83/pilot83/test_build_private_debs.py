import importlib.util,pathlib,tempfile,unittest,os
from unittest import mock
p=pathlib.Path(__file__).with_name('build-private-debs.py');s=importlib.util.spec_from_file_location('builder',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class BuildGuards(unittest.TestCase):
 def test_requires_fakeroot(self):
  with mock.patch.dict(os.environ,{},clear=True),self.assertRaises(ValueError):m.build(pathlib.Path('/unused'),None,None)
 def test_outside(self):
  with self.assertRaises(ValueError):m.regular(pathlib.Path('/other/file'),pathlib.Path('/owned'))
 def test_symlink_target(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);f=root/'target';f.symlink_to('/etc/passwd')
   with self.assertRaises(ValueError):m.regular(f,root)
 def test_symlink_parent(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);(root/'parent').symlink_to('/tmp')
   with self.assertRaises(ValueError):m.regular(root/'parent'/'new',root,True)
 def test_added_collision(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);f=root/'x';f.write_bytes(b'old')
   with self.assertRaises(ValueError):m.regular(f,root,True)
 def test_missing_replace(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.regular(pathlib.Path(d)/'x',pathlib.Path(d))
 def test_write_preserves_metadata(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);f=root/'x';f.write_bytes(b'old');f.chmod(0o664)
   with mock.patch.object(m.os,'chown') as c:m.write_delta(f,root,b'new');c.assert_called_once_with(f,os.getuid(),os.getgid())
   self.assertEqual(f.read_bytes(),b'new');self.assertEqual(f.stat().st_mode&0o777,0o664)
 def test_empty_checksum_has_no_blank_line(self):
  self.assertEqual(m.checksum_bytes([]),b'')
  self.assertEqual(m.checksum_bytes(['abc  file']),b'abc  file\n')
if __name__=='__main__':unittest.main()
