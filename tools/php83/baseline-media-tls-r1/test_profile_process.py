import subprocess,unittest
from unittest.mock import patch
import profile_process as p
class Tests(unittest.TestCase):
 def child(self,script):
  original=subprocess.Popen
  def start(*args,**kwargs):kwargs['cwd']='/';return original(*args,**kwargs)
  with patch.object(p.subprocess,'Popen',side_effect=start):return p._execute(['/bin/sh','-c',script])
 def test_success(self):
  r=self.child('printf public');self.assertEqual(r['exit'],0);self.assertEqual(r['stdout_private'],b'public');self.assertIsNone(r['failure'])
 def test_failure_private(self):
  r=self.child('printf synthetic >&2;exit 2');self.assertEqual(r['exit'],2);self.assertEqual(r['stderr_private'],b'synthetic')
 def test_bounded_output(self):
  with patch.object(p,'CAP',32):r=self.child('while :; do printf 1234567890; done')
  self.assertEqual(r['failure'],'PROCESS_OUTPUT_LIMIT');self.assertLessEqual(len(r['stdout_private']),32)
 def test_phase(self):
  with self.assertRaises(p.Rejected):p.invoke(None,'delete','','')
if __name__=='__main__':unittest.main()
