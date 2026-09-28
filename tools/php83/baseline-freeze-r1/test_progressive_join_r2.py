import ast,hashlib,pathlib,types,unittest
import prepare_progressive_join_r2 as p
import run_progressive_join_r2 as r
H=pathlib.Path(__file__).parent
class Rejected(Exception):pass
class Unsettled(Exception):pass
def need(ok,code):
 if not ok:raise Rejected(code)
class QuietAuditTests(unittest.TestCase):
 def test_exact_derivative_and_pins(self):
  self.assertEqual(p.build(),(H/'guest_progressive_join_r2.py').read_text())
  for name,pin in r.PINS.items():self.assertEqual(hashlib.sha256((H/name).read_bytes()).hexdigest(),pin)
 def context(self,fail=False):
  events=[];start={'original':types.SimpleNamespace(size=0)};jstart=types.SimpleNamespace(token="private-token",boot="private-boot")
  def quiet(snapshot):
   events.append('quiet')
   if fail:raise Unsettled()
   return {'status':'QUIET_WINDOW_OBSERVED','samples':9,'quiet_seconds':2,'maximum_seconds':30}
  def fscan(s,patterns,**kw):
   self.assertIs(s,start);events.append('files');return {'counts':[0,0],'status':'COMPLETE_FINITE_FILE_WINDOW','uncovered_tail_bytes':0,'end_offsets':{}}
  def jscan(s,patterns):self.assertIs(s,jstart);events.append('journal');return {'counts':[0,0],'status':'COMPLETE_FINITE_JOURNAL_WINDOW','cutoff_covered':True}
  scope={'Rejected':Rejected,'need':need,'settle':types.SimpleNamespace(wait_quiet=quiet,Unsettled=Unsettled),'files':types.SimpleNamespace(scan_window=fscan,snapshot=lambda _: {},Incomplete=RuntimeError),'journal':types.SimpleNamespace(scan_window=jscan,snapshot=lambda:None,Incomplete=RuntimeError),'legacy':types.SimpleNamespace(logs=lambda:[],logging_preflight=lambda:{}),'overlay':types.SimpleNamespace(audits=lambda:({},{}),source_state=lambda _: {}),'manifest':{'after':{},'modules':{}},'private_before':{},'config_before':{},'source_before':{},'report':{},'failure_stage':'USER_PRIVACY','private_dir':pathlib.Path('/private-fixture'),'private_json':lambda path,data:events.append('save'),'checkpoint':lambda:None,'record_match':lambda *a:events.append('provenance'),'JOURNAL_STATUS':'COMPLETE_FINITE_JOURNAL_WINDOW','codes':{'files':set(),'journal':set()}}
  tree=ast.parse(p.build());accepted=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='accepted');main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');audit=next(n for n in ast.walk(main) if isinstance(n,ast.FunctionDef) and n.name=='audit')
  wrapper=ast.parse('def factory():\n audit_number=0\n return None').body[0];wrapper.body=[wrapper.body[0],audit,ast.Return(value=ast.Name(id='audit',ctx=ast.Load()))]
  exec(compile(ast.fix_missing_locations(ast.Module(body=[accepted,wrapper],type_ignores=[])),'actual-audit','exec'),scope)
  return scope['factory'](),scope,events,start,jstart
 def test_actual_audit_quiet_before_scan_original_start_no_retries(self):
  audit,scope,events,start,jstart=self.context();result=audit([b'a'*16,b'b'*16],start,jstart)
  self.assertEqual([e for e in events if e in ('quiet','files','journal')],['quiet','files','journal','files']);self.assertEqual(scope['report']['last_audit_quiet']['stage'],'USER_PRIVACY');self.assertEqual(result['files']['counts'],[0,0])
 def test_unsettled_never_scans_or_advances_start(self):
  audit,scope,events,start,jstart=self.context(True)
  with self.assertRaisesRegex(Rejected,'QUIET_WINDOW_NOT_ESTABLISHED'):audit([b'a'*16,b'b'*16],start,jstart)
  self.assertNotIn('files',events);self.assertEqual(start['original'].size,0)
 def test_early_load_and_common_end_order(self):
  s=p.build();self.assertLess(s.index("settle=load('baseline_settle_v1'"),s.index('  def audit('));self.assertIn("failure_stage='USER_PRIVACY';report['user_privacy']=audit",s)
  alltext=s[s.index('  def audit_all('):s.index("  report['phase']='invalid-nonce'")];self.assertLess(alltext.index('settle.wait_quiet'),alltext.index('cutoff=files.snapshot'));self.assertIn('files.snapshot(legacy.logs())==cutoff and journal.snapshot()==jcut',alltext);self.assertIn('results=[audit(batch,start,jstart) for batch in batches]',alltext)
 def test_fixed_projection_rejects_secret_fields(self):
  value={'status':'QUIET_WINDOW_OBSERVED','samples':9,'quiet_seconds':2,'maximum_seconds':30,'audit':2,'stage':'USER_PRIVACY'};self.assertEqual(r.audit_quiet_projection(value),value)
  for key,v in [('raw','PRIVATE'),('stage','PRIVATE'),('samples',True),('quiet_seconds',2.0)]:
   item=dict(value);item[key]=v;self.assertRaises(Exception,r.audit_quiet_projection,item)
  failure={'failure_code':'FILES_UNDRAINED_TAIL','failure_stage':'USER_PRIVACY','last_audit_quiet':value};self.assertEqual(r.failure_projection(failure)['failure_stage'],'USER_PRIVACY')
 def test_fresh_state_prior_failed_unit(self):
  self.assertEqual(r.STAGE,'/var/lib/kaltura-baseline-short-progressive-join-r2');self.assertIn('baseline-freeze-2aa0f30b.service',r.REMOTE_GUARD);self.assertIn('assert not os.path.lexists(stage)',r.REMOTE_GUARD)
if __name__=='__main__':unittest.main()
