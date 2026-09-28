import hashlib,pathlib,unittest
import serve_flavor_guard_r2 as g
import prepare_serve_progressive_r3 as p
import run_serve_progressive_r3 as r
H=pathlib.Path(__file__).parent
BASE='https://192.168.56.74/p/102/sp/10200/serveFlavor/entryId/0_wzmt2sfy/v/2/flavorId/0_ewuu0o46/fileName/owned.mp4'
def check(url):return g.check(url,expected_filename='owned.mp4',secret='s'*48,ks='k'*80)
class Tests(unittest.TestCase):
 def test_exact_optional_pair(self):
  self.assertEqual(check(BASE),BASE);self.assertEqual(check(BASE+'/forceproxy/true/name/a.mp4'),BASE+'/forceproxy/true/name/a.mp4')
 def test_reject_other_values(self):
  for v in ['false','1','0','TRUE','%74rue','true/forceproxy/true','true/unknown/value']:
   with self.assertRaises(g.Rejected):check(BASE+'/forceproxy/'+v)
 def test_credentials_still_first(self):
  with self.assertRaisesRegex(g.Rejected,'CREDENTIAL'):check(BASE+'/forceproxy/'+'k'*15)
 def test_exact_derivative_pins(self):
  self.assertEqual(p.build(),(H/'guest_serve_progressive_r3.py').read_text())
  for n,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),pin)
  self.assertEqual(p.build().count('  serve_source_guard()'),2);self.assertIn(p.SOURCE_PIN,p.build())
 def test_fixed_failed_scan_projection(self):
  row={'failure_code':'SOURCE_ROUTE_UNKNOWN_KEY','failure_stage':'API_ROUND','media_privacy_failure_class':'FINITE_SCAN_INCOMPLETE','media_privacy_failure_code':'COMMON_AUDIT_END_DRIFT'}
  self.assertEqual(r.failure_projection(row)['failure_privacy']['code'],'COMMON_AUDIT_END_DRIFT')
  for k in ['media_privacy_failure_class','media_privacy_failure_code']:
   bad=dict(row);bad[k]='SYNTHETIC_SECRET';self.assertRaises(Exception,r.failure_projection,bad)
 def test_fresh_state(self):self.assertEqual(r.STAGE,'/var/lib/kaltura-baseline-serve-progressive-r3');self.assertIn('baseline-freeze-1919daa8.service',r.REMOTE_GUARD)
if __name__=='__main__':unittest.main()
