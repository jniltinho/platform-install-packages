import json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
import profile_envelope as e
PRE={'status':'PRIVATE_ROW_BACKUP_PREPARED','profile_id':1001,'mutation_performed':False,'full_acceptance':False}
POST={'status':'NATIVE_PROFILE_SPLIT_COMMITTED','original_profile_id':1001,'https_profile_id':2000,'http_preserved':True,'native_model_save_used':True,'selection_runtime_verified':False,'external_cache_rollback_available':False,'full_acceptance':False}
def child(row):return {'exit':0,'failure':None,'stdout_private':json.dumps(row).encode(),'stderr_private':b''}
class Tests(unittest.TestCase):
 def test_native_failure_closed(self):
  row={'status':'FAILED_CLOSED','failure_stage':'NATIVE_TRANSACTION','failure_code':'ORIGINAL_STATE','recovery_required':True,'full_acceptance':False};value=child(row);value['exit']=2
  with self.assertRaises(e.NativeRejected) as got:e.projection(value,'apply')
  self.assertEqual(got.exception.code,'ORIGINAL_STATE')
  value['stdout_private']=json.dumps(dict(row,failure_code='SECRET_VALUE')).encode()
  with self.assertRaises(e.Rejected) as got:e.projection(value,'apply')
  self.assertEqual(str(got.exception),'NATIVE_RESULT_SCHEMA')
 def test_projection(self):self.assertEqual(e.projection(child(PRE),'prepare'),PRE);self.assertEqual(e.projection(child(POST),'apply'),POST)
 def test_prepare_bool_identity(self):
  for key in ('mutation_performed','full_acceptance'):
   with self.assertRaises(e.Rejected):e.projection(child(dict(PRE,**{key:0})),'prepare')
 def test_schema(self):
  for row in [dict(POST,extra='secret'),dict(POST,https_profile_id=True),dict(POST,full_acceptance=True)]:
   with self.assertRaises(e.Rejected):e.projection(child(row),'apply')
 def test_output_leak(self):
  r=child(PRE);r['stderr_private']=b'syntheticSECRET12345'
  with self.assertRaises(e.Rejected):e.private_outputs_clean(r,[b'syntheticSECRET12345'])
 def fixture(self,phasefail=None,auditfail=False):
  c=Mock();c.patterns.return_value=[b'a'*16,b'b'*16];c.snapshot.return_value='original-boundary';c.invoke.side_effect=[child(PRE),child(POST)]
  if phasefail:c.invoke.side_effect=[child(PRE),RuntimeError('private exception')]
  if auditfail:c.audit.side_effect=RuntimeError('private audit')
  return c
 def run_case(self,c):
  with tempfile.TemporaryDirectory() as t:
   with patch.object(e,'STATE',Path(t)/'state'),patch.object(e,'fsync_backup'),patch.object(e.stat,'S_IMODE',return_value=0o700):
    # Pure lifecycle doubles root stat; no guest/action execution.
    with patch.object(Path,'lstat',return_value=type('S',(),{'st_uid':0,'st_gid':0,'st_mode':0o40700})()):return e.execute(c)
 def test_prepare_audit_failure_never_apply(self):
  c=self.fixture(auditfail=True);r=self.run_case(c);self.assertFalse(r['apply_attempted']);self.assertEqual(c.invoke.call_count,1);self.assertFalse(r['privacy_passed'])
 def test_apply_failure_reuses_boundary(self):
  c=self.fixture(phasefail=True);r=self.run_case(c);self.assertTrue(r['apply_attempted']);self.assertFalse(r['privacy_passed']);self.assertTrue(r['failure_privacy_passed']);self.assertTrue(all(x.args[0]=='original-boundary' for x in c.audit.call_args_list))
 def test_success(self):
  c=self.fixture();r=self.run_case(c);self.assertTrue(r['privacy_passed']);self.assertFalse(r['full_acceptance']);self.assertEqual(c.invoke.call_count,2)
if __name__=='__main__':unittest.main()
