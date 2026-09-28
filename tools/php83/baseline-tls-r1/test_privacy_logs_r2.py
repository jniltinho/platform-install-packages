import os,stat,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import privacy_logs_r2 as p
class Tests(unittest.TestCase):
 def test_complete_revalidated_inventory(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);os.chmod(root,0o700)
   for n in p.FILES:(root/n).write_bytes(b'');os.chmod(root/n,0o600)
   real=Path.lstat
   def rootstat(path):
    s=real(path);return type('S',(),{'st_mode':s.st_mode,'st_uid':0,'st_gid':0,'st_nlink':s.st_nlink})()
   with patch.object(p,'DIRECTORY',root),patch.object(Path,'lstat',rootstat):
    self.assertEqual(len(p.extend(lambda:[Path('/old/log')])),3)
    os.chmod(root/'error.log',0o644)
    with self.assertRaises(p.Rejected):p.extend(lambda:[])
    os.chmod(root/'error.log',0o600);(root/'extra').write_bytes(b'')
    with self.assertRaises(p.Rejected):p.extend(lambda:[])
 def test_no_silent_optional_logs(self):
  with patch.object(p,'DIRECTORY',Path('/does-not-exist')):
   with self.assertRaises(FileNotFoundError):p.paths()
if __name__=='__main__':unittest.main()
