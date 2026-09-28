"""Read-only recovery observation; never retries or relabels the failed mutation."""
import hashlib,importlib.util,json,os,signal,stat,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
RUNTIME_PIN='625a2fac3538ed7b7d4114d130c40101e3a20dbe855184515446b50f3c33e64f'
OBSERVER_PIN='ecf663ca573c2c1c887d37c5aab29571c2c38dea93ed6c17de2f317b9cf37a82'
TRANSPORT_PIN='9735aad64f31a3329de5844f9061da9f18f12e1b34787971d9ee360872443776'
class Rejected(ValueError):pass
def need(ok):
 if not ok:raise Rejected('RECOVERY_ENVELOPE_REJECTED')
def frozen(path,pin):
 s=path.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and s.st_nlink==1 and not s.st_mode&0o222 and s.st_size<=1048576 and not os.listxattr(path));need(hashlib.sha256(path.read_bytes()).hexdigest()==pin)
def projection(result):
 need(result['failure'] is None and result['exit']==0 and result['stderr_private']==b'')
 def pairs(items):
  d={}
  for k,v in items:need(k not in d);d[k]=v
  return d
 r=json.loads(result['stdout_private'],object_pairs_hook=pairs)
 fixed={'status':'READ_ONLY_SPLIT_RECOVERY_OBSERVED','original_profile_id':1001,'candidate_scope':'GLOBAL_TYPE61_DEFAULTS_ONLY','sql_select_count':3,'db_identity_verified':True,'private_before_compared':True,'transaction_rollback_proven':False,'cache_state_verified':False,'recovery_performed':False,'retry_authorized':False,'full_acceptance':False}
 need(type(r) is dict and set(r)==set(fixed)|{'original_relation','candidate_rows','matching_https_clone_ids','unexpected_candidate_rows'})
 need(all(type(r[k]) is type(v) and r[k]==v for k,v in fixed.items()))
 need(r['original_relation'] in ('EXACT_BACKUP','EXPECTED_HTTP_DELTA','OTHER_DRIFT'))
 need(type(r['candidate_rows']) is int and 0<=r['candidate_rows']<=2 and type(r['unexpected_candidate_rows']) is int and 0<=r['unexpected_candidate_rows']<=r['candidate_rows'])
 ids=r['matching_https_clone_ids'];need(type(ids) is list and len(ids)<=2 and all(type(v) is int and 0<v<=9999999999 and v!=1001 for v in ids) and len(set(ids))==len(ids) and len(ids)+r['unexpected_candidate_rows']==r['candidate_rows'])
 return r
def observe(context,invoke):
 report={'status':'READ_ONLY_RECOVERY_FAILED_OR_INCOMPLETE','privacy_passed':False,'recovery_required':True,'recovery_performed':False,'retry_authorized':False,'full_acceptance':False,'secret_coverage':'native_default_DB_and_authorized_root_DB_only'}
 boundary=None;patterns=None;phase='GUARD'
 try:
  context.guard();phase='BOUNDARY';boundary=context.snapshot();phase='PATTERNS';patterns=context.patterns()
  need(type(patterns) is list and 2<=len(patterns)<=16 and all(type(v) is bytes and 15<=len(v)<=4096 for v in patterns))
  phase='OBSERVATION';result=invoke();context.modules['profile_envelope.py'].private_outputs_clean(result,patterns);observed=projection(result)
  phase='PRIVACY';context.audit(boundary,patterns);phase='POST_GUARD';context.guard()
  report.update(status='READ_ONLY_RECOVERY_OBSERVED_FINITE_PRIVACY',privacy_passed=True,observation=observed)
 except BaseException:
  report['failure_phase']=phase
  report['failure_privacy_passed']=False
  if boundary is not None and patterns is not None:
   try:context.audit(boundary,patterns);context.guard();report['failure_privacy_passed']=True
   except BaseException:pass
 return report
def main():
 frozen(HERE/'profile_runtime.py',RUNTIME_PIN)
 spec=importlib.util.spec_from_file_location('recovery_runtime_base',HERE/'profile_runtime.py');r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
 need(len(sys.argv)==2);context=r.Context(sys.argv[1])
 def invoke():
  for p in (HERE,*HERE.parents):
   s=p.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==0 and not s.st_mode&0o022 and not os.listxattr(p))
  frozen(HERE/'delivery_profile_recovery.py',OBSERVER_PIN);frozen(HERE/'profile_socket.py',TRANSPORT_PIN)
  return context.process._execute(['/usr/bin/python3','-B',str(HERE/'delivery_profile_recovery.py')])
 result=observe(context,invoke);result['finite_audits_completed']=context.audit_count;print(json.dumps(result,sort_keys=True));return 0 if result['status']=='READ_ONLY_RECOVERY_OBSERVED_FINITE_PRIVACY' else 2
if __name__=='__main__':
 def interrupted(*args):raise Rejected('INTERRUPTED')
 signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
 try:code=main()
 except Exception:print(json.dumps({'status':'READ_ONLY_RECOVERY_FAILED_CLOSED','recovery_required':True,'retry_authorized':False,'full_acceptance':False}));code=2
 raise SystemExit(code)
