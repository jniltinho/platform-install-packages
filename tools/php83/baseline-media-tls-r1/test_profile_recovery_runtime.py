import copy,hashlib,json,unittest
from pathlib import Path
from types import SimpleNamespace
import profile_recovery_runtime as r
import profile_envelope as e
GOOD={'status':'READ_ONLY_SPLIT_RECOVERY_OBSERVED','original_profile_id':1001,'original_relation':'EXPECTED_HTTP_DELTA','candidate_rows':1,'matching_https_clone_ids':[1234],'unexpected_candidate_rows':0,'candidate_scope':'GLOBAL_TYPE61_DEFAULTS_ONLY','sql_select_count':3,'db_identity_verified':True,'private_before_compared':True,'transaction_rollback_proven':False,'cache_state_verified':False,'recovery_performed':False,'retry_authorized':False,'full_acceptance':False}
def output(v=GOOD):return dict(exit=0,failure=None,stderr_private=b'',stdout_private=json.dumps(v).encode())
class Context:
 def __init__(self):self.modules={'profile_envelope.py':e};self.events=[];self.boundary=object();self.audit_count=0
 def guard(self):self.events.append('guard')
 def snapshot(self):self.events.append('snapshot');return self.boundary
 def patterns(self):self.events.append('patterns');return [b'syntheticPattern123',b'anotherPattern456']
 def audit(self,b,p):
  if b is not self.boundary:raise AssertionError('boundary')
  self.events.append('audit');self.audit_count+=1
class Tests(unittest.TestCase):
 def test_pins(self):
  for p,h in [(r.HERE/'profile_runtime.py',r.RUNTIME_PIN),(r.HERE.parent/'baseline-freeze-r1/delivery_profile_recovery.py',r.OBSERVER_PIN),(r.HERE.parent/'baseline-freeze-r1/profile_socket.py',r.TRANSPORT_PIN)]:self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),h)
 def test_success_is_not_recovery(self):
  c=Context();v=r.observe(c,lambda:output());self.assertTrue(v['privacy_passed']);self.assertTrue(v['recovery_required']);self.assertFalse(v['retry_authorized']);self.assertFalse(v['recovery_performed']);self.assertEqual(c.events,['guard','snapshot','patterns','audit','guard'])
 def test_projection_negatives(self):
  for k,v in [('full_acceptance',True),('cache_state_verified',True),('db_identity_verified',1),('original_profile_id',True),('matching_https_clone_ids',[1234,1234]),('candidate_rows',True),('candidate_scope','ALL'),('original_relation','COMMITTED'),('extra','raw')]:
   bad=copy.deepcopy(GOOD);bad[k]=v
   with self.assertRaises(r.Rejected):r.projection(output(bad))
 def test_ambiguous_is_observed_not_fixed(self):
  bad=copy.deepcopy(GOOD);bad.update(original_relation='OTHER_DRIFT',matching_https_clone_ids=[],unexpected_candidate_rows=1)
  v=r.observe(Context(),lambda:output(bad));self.assertEqual(v['observation']['original_relation'],'OTHER_DRIFT');self.assertTrue(v['recovery_required'])
 def test_failure_audits_same_start(self):
  c=Context();v=r.observe(c,lambda:dict(exit=2,failure=None,stderr_private=b'',stdout_private=b'{}'));self.assertTrue(v['failure_privacy_passed']);self.assertFalse(v['privacy_passed']);self.assertEqual(c.events.count('snapshot'),1);self.assertEqual(c.audit_count,1)
 def test_private_output_rejects(self):
  v=r.observe(Context(),lambda:dict(exit=0,failure=None,stderr_private=b'',stdout_private=b'syntheticPattern123'));self.assertFalse(v['privacy_passed']);self.assertTrue(v['failure_privacy_passed']);self.assertNotIn('syntheticPattern123',json.dumps(v))
 def test_privacy_failure_never_observation_success(self):
  c=Context()
  def fail(*args):raise ValueError()
  c.audit=fail;v=r.observe(c,lambda:output());self.assertFalse(v['privacy_passed']);self.assertFalse(v['failure_privacy_passed']);self.assertNotIn('observation',v)
if __name__=='__main__':unittest.main()
