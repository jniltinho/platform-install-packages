import unittest,ast,hashlib,json,copy,types
from pathlib import Path
import common_end as c,prepare_hls_media8444_r3 as g,run_hls_media8444_r3 as r
import test_hls_media8444 as base
import test_common_end as fixtures
H=Path(__file__).parent
class Tests(unittest.TestCase):
 def setUp(self):r.PROOF_PIN='a'*64;r.EXPECTED_HTTPS_ID=1004
 def test_actual_integrated_audit_all_same_starts_no_workload_repeat(self):
  source=g.build();tree=ast.parse(source);node=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='audit_all')
  sequence=iter([fixtures.snap(),fixtures.snap(4),fixtures.snap(4),fixtures.snap(4)]);current=[None];calls=[];start,jstart=object(),object();workloads=[];report={}
  def files_snapshot(_):current[0]=next(sequence);return current[0][0]
  def audit_once(batch,s,j):self.assertIs(s,start);self.assertIs(j,jstart);calls.append(batch);return fixtures.result(3 if len(calls)==1 else 4)
  def need(ok,code):
   if not ok:raise ValueError(code)
  ns={'common_end':c,'files':types.SimpleNamespace(snapshot=files_snapshot),'journal':types.SimpleNamespace(snapshot=lambda:current[0][1]),'legacy':types.SimpleNamespace(logs=lambda:[]),'settle':types.SimpleNamespace(wait_quiet=lambda callback:None,Unsettled=RuntimeError),'audit_once':audit_once,'report':report,'need':need,'Rejected':ValueError}
  exec(compile(ast.Module(body=[node],type_ignores=[]),'actual_guest_audit_all','exec'),ns)
  workloads.append('one_context_and_two_gets');value=ns['audit_all']([[b'a',b'b']],start,jstart)
  self.assertEqual(len(workloads),1);self.assertEqual(len(calls),2);self.assertTrue(value['common_end_verified']);self.assertEqual([v['classification'] for v in report['common_end_attempts']],['APPEND_ONLY','STABLE'])
 def row(self):
  b=base.Tests();b.setUp();row=b.row();row['common_end_attempts']=[{'attempt':1,'classification':'STABLE','file_appends':0,'journal_advanced':False,'offset_batches_changed':0}];return row
 def test_full_public_success_and_failures(self):
  row=self.row();self.assertEqual(r.public_rows(json.dumps(row).encode())[0]['common_end_attempts'],row['common_end_attempts'])
  for key in ('common_end_attempts','round_privacy','media_tls_logs_in_every_inventory','hls_media'):
   bad=self.row();bad.pop(key);self.assertRaises(Exception,r.public_rows,json.dumps(bad).encode())
  bad=self.row();bad['common_end_attempts'][0]['classification']='APPEND_ONLY';self.assertRaises(Exception,r.public_rows,json.dumps(bad).encode())
 def test_failed_drift_is_not_privacy_pass(self):
  row={'status':'FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','failure_code':'COMMON_AUDIT_CONVERGENCE_EXHAUSTED','failure_stage':'BATCH_PRIVACY','common_end_attempts':[{'attempt':3,'classification':'APPEND_ONLY','file_appends':1,'journal_advanced':False,'offset_batches_changed':1}],'private':'SECRET'}
  out=r.public_rows(json.dumps(row).encode())[0];self.assertNotIn('SECRET',json.dumps(out));self.assertNotIn('round_privacy',out)
 def test_workload_unchanged(self):
  old=(H/'guest_hls_media8444_r2.py').read_text();new=g.build()
  a=old[old.index("  report['phase']='invalid-nonce'"):];b=new[new.index("  report['phase']='invalid-nonce'"):];self.assertEqual(a,b)
 def test_regeneration_pins_boundaries(self):
  self.assertEqual(g.build(),(H/'guest_hls_media8444_r3.py').read_text())
  for n,p in r.PINS.items():self.assertEqual(hashlib.sha256((H/n).read_bytes()).hexdigest(),p)
  self.assertIn('baseline-freeze-2329cd95.service',r.REMOTE_GUARD);self.assertEqual(r.STAGE,'/var/lib/kaltura-baseline-hls-media8444-r3')
if __name__=='__main__':unittest.main()
