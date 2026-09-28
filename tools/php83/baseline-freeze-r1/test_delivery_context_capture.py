import unittest,json,hashlib
from pathlib import Path
import run_delivery_context_pair as r
import prepare_delivery_context_pair as g
import test_context_capture as base
import delivery_context_pair as pair
class Tests(unittest.TestCase):
 def setUp(self):r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=2001
 def row(self):
  v=base.Tests().row();v.pop('playback_context');v['split_receipt_sha256']=r.PROOF_PIN;v['media_tls_logs_in_every_inventory']=True
  v['delivery_context_pair']={'case':'NATIVE_HTTP_HTTPS_PROFILE_SELECTION_NO_GET','api_calls':2,'selections':[{'requested_protocol':p,'profile_id':i,'selected_expected_profile':True,'source_url_scheme':p} for p,i in [('http',1001),('https',2001)]],'source_urls_enrolled':True,'response_secret_coverage_complete':False,'media_gets':0,'full_acceptance':False};return v
 def parse(self,v):return r.public_rows(json.dumps(v).encode())[0]
 def test_full_public_success_no_old_context_or_url(self):
  row=self.row();self.assertNotIn('playback_context',row);self.assertNotIn('native_url_shape',row);out=self.parse(row);self.assertEqual(out['delivery_context_pair'],row['delivery_context_pair']);self.assertTrue(out['media_tls_logs_in_every_inventory'])
 def test_full_public_missing_drift_and_unknown_private(self):
  for key in ('sources_before','media_privacy','round_privacy','tls_transport','match_provenance','delivery_context_pair','split_receipt_sha256','media_tls_logs_in_every_inventory'):
   v=self.row();v.pop(key)
   with self.assertRaises(Exception):self.parse(v)
  v=self.row();v['delivery_context_pair']['selections'][1]['profile_id']=2002
  with self.assertRaises(Exception):self.parse(v)
  v=self.row();v['private']='SYNTHETIC_SECRET';self.assertNotIn('SYNTHETIC_SECRET',json.dumps(self.parse(v)))
 def test_failure_fixed_reason(self):
  v={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_code':'PROFILE_SELECTION_MISMATCH','failure_stage':'API_ROUND','media_privacy_failure_class':'FINITE_SCAN_INCOMPLETE','media_privacy_failure_code':'COMMON_AUDIT_END_DRIFT'}
  out=self.parse(v);self.assertEqual(out['failure_code'],'PROFILE_SELECTION_MISMATCH');self.assertFalse(out['failure_privacy']['finite_scans_complete_and_zero'])
 def test_receipt_required(self):
  v={'status':'NATIVE_PROFILE_SPLIT_COMMITTED_FINITE_PRIVACY','privacy_passed':True,'full_acceptance':False,'profile_result':{'status':'NATIVE_PROFILE_SPLIT_COMMITTED','original_profile_id':1001,'https_profile_id':2001,'http_preserved':True,'native_model_save_used':True,'full_acceptance':False}}
  self.assertEqual(pair.receipt_id(v),2001)
  for key in ('status','privacy_passed','profile_result'):
   x=dict(v);x.pop(key)
   with self.assertRaises(pair.Rejected):pair.receipt_id(x)
 def test_frozen_generation_and_all_inventory_composition(self):
  h=Path(__file__).parent;self.assertEqual(g.build(),(h/'guest_delivery_context_pair.py').read_text())
  for n,pin in r.PINS.items():self.assertEqual(hashlib.sha256((h/n).read_bytes()).hexdigest(),pin)
  s=g.build();self.assertIn('legacy.logs=lambda:media_logs.extend(lambda:tls_logs.extend(old_logs))',s);self.assertLess(s.index('pair.receipt_id'),s.index('secret=legacy.')) if 'secret=legacy.' in s else None
  self.assertIn("+'/guest_delivery_context_pair.py '+unit+' '+PROOF_PIN",Path(r.__file__).read_text())
if __name__=='__main__':unittest.main()
