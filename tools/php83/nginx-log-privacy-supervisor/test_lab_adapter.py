import hashlib,importlib.util,json,os,shutil,tempfile,unittest
from pathlib import Path
import lab_adapter as a

class Tests(unittest.TestCase):
 def fixture(self,base,body):
  for name in ('config','socket','sink'):(base/name).mkdir(mode=0o700)
  binary=base/'child';binary.write_text('#!/usr/bin/python3\n'+body);binary.chmod(0o700)
  config=base/'config/nginx.conf';config.write_text('fixture');config.chmod(0o600)
  sanitizer=base/'sanitizer.py';shutil.copyfile(Path(__file__).resolve().parents[1]/'nginx-log-privacy/sanitizer.py',sanitizer);sanitizer.chmod(0o600)
  sp=importlib.util.spec_from_file_location('fixture_sanitizer',sanitizer);module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
  pins=tuple((str(p),hashlib.sha256(p.read_bytes()).hexdigest()) for p in (binary,config,sanitizer))
  return a.Spec(str(binary),str(config),str(config.parent),str(base/'socket'),str(base/'sink'),pins,seconds=2,fixture_roots=(str(base),)),module
 def test_burst_and_partial(self):
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp);s,m=self.fixture(base,"import os\nfor _ in range(2000):os.write(2,b'2026/01/01 12:00:00 [error] 1#1: SYNTHETIC_CANARY\\n')\nos.write(2,b'SYNTHETIC_PARTIAL')\n")
   report=a.run(s,m);events=b''.join(p.read_bytes() for p in sorted((base/'sink').glob('events-*')))
   self.assertEqual(report['status'],'CHILD_EXIT');self.assertEqual(len(events.splitlines()),2001);self.assertNotIn(b'SYNTHETIC',events);self.assertTrue(report['child_reaped'])
 def test_unsafe_parent(self):
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp);s,m=self.fixture(base,'pass\n');(base/'config').chmod(0o770)
   self.assertEqual(a.run(s,m)['status'],'FAILED');self.assertFalse((base/'socket/syslog').exists())
 def test_no_inferred_fixture_policy(self):
  if os.geteuid()==0:self.skipTest('nonroot assertion')
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp);s,m=self.fixture(base,'pass\n');s=a.dataclasses.replace(s,fixture_roots=())
   self.assertEqual(a.run(s,m)['status'],'FAILED')
 def test_separate_and_private(self):
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp);s,m=self.fixture(base,"import os\nos.write(2,b'safe\\n')\n");r=a.run(s,m)
   self.assertEqual(r['status'],'CHILD_EXIT');self.assertEqual((base/'socket/syslog').stat().st_mode&0o777,0o600)
   self.assertTrue(all(p.stat().st_mode&0o777==0o600 for p in (base/'sink').iterdir()));self.assertFalse(list((base/'config').glob('events-*')))
 def test_socket_loss_cleanup(self):
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp);s,m=self.fixture(base,"import os,time\nos.unlink("+repr(str(base/'socket/syslog'))+");time.sleep(20)\n")
   r=a.run(s,m);self.assertEqual(r['status'],'FAILED');self.assertTrue(r['child_reaped'])
if __name__=='__main__':unittest.main()
