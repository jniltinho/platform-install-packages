import unittest,json,hashlib,copy
from pathlib import Path
import run_delivery_context_pair_r2 as r
import prepare_delivery_context_pair_r2 as g
import delivery_context_pair_r2 as pair
import test_delivery_context_capture as base
H=Path(__file__).parent
RECEIPT=H.parents[2]/'doc/php83/evidence/baseline-media-tls-r1/profile-recovery-native-r1.json'
class Tests(unittest.TestCase):
 def setUp(self):r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
 def row(self):
  v=base.Tests().row();v['delivery_context_pair']['selections'][1]['profile_id']=1004;v['split_receipt_sha256']=r.PROOF_PIN;return v
 def test_full_public_success_reconciliation_not_commit(self):
  out=r.public_rows(json.dumps(self.row()).encode())[0];self.assertEqual(out['split_proof_kind'],'READ_ONLY_STORED_SPLIT_RECONCILIATION');self.assertFalse(out['prior_mutation_attempt_success']);self.assertTrue(out['recovery_adjudication_required']);self.assertNotIn('native_url_shape',out)
 def test_full_public_missing_or_drift_rejected(self):
  for k in ('round_privacy','split_receipt_sha256','media_tls_logs_in_every_inventory','delivery_context_pair','sources_after'):
   v=self.row();v.pop(k)
   with self.assertRaises(Exception):r.public_rows(json.dumps(v).encode())
  v=self.row();v['delivery_context_pair']['selections'][1]['profile_id']=2001
  with self.assertRaises(Exception):r.public_rows(json.dumps(v).encode())
 def test_actual_closed_receipt_identity(self):
  value=json.loads(RECEIPT.read_text());self.assertEqual(pair.receipt_id(value),1004)
 def test_failed_partial_duplicate_or_forged_commit_rejected(self):
  v=json.loads(RECEIPT.read_text())
  for path,value in [(('guest_exit',),2),(('unit_inactive',),False),(('observation','privacy_passed'),False),(('observation','recovery_required'),False),(('observation','observation','original_relation'),'OTHER_DRIFT'),(('observation','observation','matching_https_clone_ids'),[1004,1005]),(('observation','observation','candidate_rows'),2),(('observation','observation','unexpected_candidate_rows'),1),(('pins','delivery_profile_recovery.py'),'0'*64)]:
   w=copy.deepcopy(v);d=w
   for k in path[:-1]:d=d[k]
   d[path[-1]]=value
   with self.assertRaises(pair.Rejected):pair.receipt_id(w)
  with self.assertRaises(pair.Rejected):pair.receipt_id({'status':'NATIVE_PROFILE_SPLIT_COMMITTED_FINITE_PRIVACY'})
 def test_generation_pins_and_prior_inactive(self):
  self.assertEqual(g.build(),(H/'guest_delivery_context_pair_r2.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  self.assertIn('baseline-profile-91c456f4.service',r.REMOTE_GUARD);self.assertEqual(r.STAGE,'/var/lib/kaltura-baseline-delivery-context-pair-r2')
if __name__=='__main__':unittest.main()
