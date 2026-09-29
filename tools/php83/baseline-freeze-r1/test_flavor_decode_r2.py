import unittest,hashlib
from pathlib import Path
import run_flavor_decode_r1 as r1,run_flavor_decode_r2 as r
H=Path(__file__).parent
class Tests(unittest.TestCase):
 def test_derivation(self):
  self.assertEqual(r.PINS,r1.PINS)
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  self.assertIn('/var/lib/kaltura-baseline-flavor-decode-r2',r.REMOTE_GUARD+r.STAGE);self.assertNotIn('flavor-decode-r1',r.REMOTE_GUARD+r.STAGE)
  self.assertIn('baseline-freeze-bb9fab6d.service',r.REMOTE_GUARD);self.assertIn('now=time.gmtime();assert now.tm_min<30',r.REMOTE_GUARD)
  a=Path('run_flavor_decode_r1.py').read_text().splitlines();b=Path('run_flavor_decode_r2.py').read_text().splitlines()
  self.assertEqual(len([x for x in b if x not in a]),5)
if __name__=='__main__':unittest.main()
