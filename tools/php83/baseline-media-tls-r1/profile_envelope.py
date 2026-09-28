"""Local native profile split lifecycle with mandatory finite privacy windows.
Context is supplied by the separately pinned runtime binding, not user input.
No API/KS operations. Failed/incomplete privacy is never mutation success.
"""
import json,os,stat
from pathlib import Path
STATE=Path('/var/lib/kaltura-baseline-delivery-split-r1')
class Rejected(ValueError):pass
class NativeRejected(Rejected):
 def __init__(self,stage,code):self.stage=stage;self.code=code;super().__init__('NATIVE_FAILED_CLOSED')
NATIVE_CODES=frozenset('ROW_ID ROW_CARDINALITY ROW_TYPE ROW_CAP ORIGINAL_STATE STATE_METADATA BACKUP_CAP EXCLUSIVE_FILE PRIVATE_WRITE BACKUP_METADATA BACKUP_SCHEMA COMPETING_DEFAULT PARTNER_OVERRIDE DELTA_SCHEMA NATIVE_TIMESTAMP UNEXPECTED_MODEL_DELTA MODE TRANSACTION_ACTIVE BACKUP_DRIFT MODEL_TYPE NEW_SAVE NEW_ID ORIGINAL_SAVE NESTED_TRANSACTION TARGET DB_IDENTITY NATIVE_LIFECYCLE_FAILURE'.split())
ENVELOPE_CODES=frozenset('BACKUP_METADATA NATIVE_PROCESS_FAILED NATIVE_RESULT_SCHEMA NATIVE_OUTPUT_SHAPE PRIVATE_MARKER_IN_CHILD_OUTPUT STATE_OCCUPIED PATTERN_SCHEMA STATE_METADATA'.split())
def need(ok,code):
 if not ok:raise Rejected(code)
def fsync_backup():
 fd=os.open(STATE/'before.json',os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 try:
  s=os.fstat(fd);need(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and 0<s.st_size<=65536 and not os.listxattr(fd),'BACKUP_METADATA');os.fsync(fd)
 finally:os.close(fd)
 directory=os.open(STATE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(directory)
 finally:os.close(directory)
def projection(result,phase):
 need(result['failure'] is None and not result['stderr_private'],'NATIVE_PROCESS_FAILED')
 try:
  def pairs(rows):
   out={}
   for k,v in rows:
    if k in out:raise ValueError()
    out[k]=v
   return out
  r=json.loads(result['stdout_private'],object_pairs_hook=pairs)
 except Exception:raise Rejected('NATIVE_RESULT_SCHEMA') from None
 if type(r) is dict and r.get('status')=='FAILED_CLOSED':
  need(set(r)=={'status','failure_stage','failure_code','recovery_required','full_acceptance'} and result['exit']==2 and r['failure_stage'] in ('TARGET','BOOTSTRAP','DB_IDENTITY','NATIVE_TRANSACTION') and r['failure_code'] in NATIVE_CODES and r['recovery_required'] is True and r['full_acceptance'] is False,'NATIVE_RESULT_SCHEMA')
  raise NativeRejected(r['failure_stage'],r['failure_code'])
 need(result['exit']==0,'NATIVE_PROCESS_FAILED')
 if phase=='prepare':
  need(r=={'status':'PRIVATE_ROW_BACKUP_PREPARED','profile_id':1001,'mutation_performed':False,'full_acceptance':False} and type(r['profile_id']) is int and r['mutation_performed'] is False and r['full_acceptance'] is False,'NATIVE_RESULT_SCHEMA')
 else:
  expected={'status','original_profile_id','https_profile_id','http_preserved','native_model_save_used','selection_runtime_verified','external_cache_rollback_available','full_acceptance'}
  need(type(r) is dict and set(r)==expected and r['status']=='NATIVE_PROFILE_SPLIT_COMMITTED' and type(r['original_profile_id']) is int and r['original_profile_id']==1001 and type(r['https_profile_id']) is int and r['https_profile_id']>0 and r['https_profile_id']!=1001 and r['http_preserved'] is True and r['native_model_save_used'] is True and r['selection_runtime_verified'] is False and r['external_cache_rollback_available'] is False and r['full_acceptance'] is False,'NATIVE_RESULT_SCHEMA')
 return r
def private_outputs_clean(result,patterns):
 need(all(type(result[k]) is bytes and len(result[k])<=65536 for k in ('stdout_private','stderr_private')),'NATIVE_OUTPUT_SHAPE')
 need(not any(p in result[k] for p in patterns for k in ('stdout_private','stderr_private')),'PRIVATE_MARKER_IN_CHILD_OUTPUT')
def execute(context):
 """context.guard includes target/snapshot/source/runtime/TLS/config invariants."""
 context.guard();need(not os.path.lexists(STATE),'STATE_OCCUPIED')
 # Boundary precedes credential reads and ALL bootstrap execution.
 boundary=context.snapshot();patterns=context.patterns();need(type(patterns) is list and 2<=len(patterns)<=16 and all(type(p) is bytes and 15<=len(p)<=4096 for p in patterns),'PATTERN_SCHEMA')
 STATE.mkdir(mode=0o700);s=STATE.lstat();need(s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o700,'STATE_METADATA')
 report={'status':'PROFILE_MUTATION_FAILED_OR_INCOMPLETE','prepare_completed':False,'apply_attempted':False,'privacy_passed':False,'full_acceptance':False,'secret_coverage':'native_default_DB_and_authorized_root_DB_only','automatic_rollback':False}
 phase='PREPARE'
 try:
  before=context.invoke('prepare');private_outputs_clean(before,patterns);projection(before,'prepare');fsync_backup();phase='PREPARE_PRIVACY';context.audit(boundary,patterns);phase='PREPARE_GUARD';context.guard();report['prepare_completed']=True
  report['apply_attempted']=True;phase='APPLY'
  after=context.invoke('apply');private_outputs_clean(after,patterns);result=projection(after,'apply')
  phase='APPLY_PRIVACY';context.audit(boundary,patterns);phase='APPLY_GUARD';context.guard()
  report.update(status='NATIVE_PROFILE_SPLIT_COMMITTED_FINITE_PRIVACY',privacy_passed=True,profile_result=result)
 except BaseException as error:
  report['failure_phase']=phase
  report['failure_code']=str(error) if isinstance(error,Rejected) and str(error) in ENVELOPE_CODES else 'ENVELOPE_OR_GUARD_FAILURE'
  if isinstance(error,NativeRejected):report.update(failure_code='NATIVE_FAILED_CLOSED',native_failure_stage=error.stage,native_failure_code=error.code)
  # The native phase may have committed or created an intent. Never retry/apply
  # automatically and never replace the original pre-prepare boundary.
  report['recovery_required']=True
  try:context.audit(boundary,patterns);context.guard();report['failure_privacy_passed']=True
  except BaseException:report['failure_privacy_passed']=False
 return report
