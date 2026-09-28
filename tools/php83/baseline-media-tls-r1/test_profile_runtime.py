import ast,hashlib,unittest
from pathlib import Path
import profile_runtime as r
class Tests(unittest.TestCase):
 def test_helper_pins(self):
  for name,pin in r.LOCAL_PINS.items():self.assertEqual(hashlib.sha256((r.HERE/name).read_bytes()).hexdigest(),pin)
 def test_snapshot_pin(self):
  p=r.HERE.parents[2]/'doc/php83/evidence/baseline-media-tls-r1/pre-change-snapshot.json';self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),r.SNAPSHOT_PIN)
 def test_payload_pin(self):
  p=r.HERE.parent/'baseline-freeze-r1/delivery_profile_split.php';self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),r.PAYLOAD_PIN)
 def test_bad_unit(self):
  with self.assertRaises(r.Rejected):r.Context('anything')
 def test_no_api_calls(self):
  source=Path(r.__file__).read_text();self.assertNotIn('PostTransport(',source);self.assertNotIn("action='start'",source)
if __name__=='__main__':unittest.main()
