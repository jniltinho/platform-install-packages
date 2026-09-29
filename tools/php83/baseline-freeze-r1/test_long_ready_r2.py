import unittest,hashlib,time
from pathlib import Path
from unittest.mock import patch
import run_long_ready_r1 as r1,run_long_ready_r2 as r
H=Path(__file__).parent
class Tests(unittest.TestCase):
 def test_derivation(self):
  self.assertEqual(r.PINS,r1.PINS)
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  self.assertIn('/var/lib/kaltura-baseline-long-ready-r2',r.REMOTE_GUARD+r.STAGE);self.assertNotIn('long-ready-r1',r.REMOTE_GUARD+r.STAGE)
  for u in ('56fbc341','068f5a98'):self.assertIn('baseline-freeze-'+u+'.service',r.REMOTE_GUARD)
 def test_clock_window_guard(self):
  guard=[l for l in r.REMOTE_GUARD.splitlines() if l.startswith('now=time.gmtime()')][0]
  def ok(h,m):
   with patch.object(time,'gmtime',return_value=time.struct_time((2026,9,29,h,m,0,0,272,0))):
    try:exec('import time\n'+guard,{});return True
    except AssertionError:return False
  self.assertEqual([ok(2,0),ok(2,29),ok(2,30),ok(2,50),ok(0,10),ok(0,20),ok(23,5)],[True,True,False,False,False,True,False])
if __name__=='__main__':unittest.main()
