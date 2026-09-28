"""Finite whole-batch privacy convergence; never owns a workload or moves starts."""
import time
class Rejected(ValueError):pass
CODES=('COMMON_AUDIT_SCHEMA','COMMON_AUDIT_POSITIVE','COMMON_AUDIT_UNSAFE_DRIFT','COMMON_AUDIT_CONVERGENCE_EXHAUSTED','COMMON_AUDIT_DEADLINE')
def need(ok,code):
 if not ok:raise Rejected(code)
def marks(value):
 need(type(value) is dict and 0<len(value)<=512,'COMMON_AUDIT_SCHEMA')
 for p,m in value.items():
  need(type(p) is str and all(type(getattr(m,k,None)) is int and getattr(m,k)>=0 for k in ('device','inode','size','mtime_ns')),'COMMON_AUDIT_SCHEMA')
 return value
def transition(before,after):
 a,ja=before;b,jb=after;marks(a);marks(b)
 need(set(a)==set(b),'COMMON_AUDIT_UNSAFE_DRIFT')
 appended=0
 for p,m in a.items():
  n=b[p]
  need((m.device,m.inode)==(n.device,n.inode) and n.size>=m.size,'COMMON_AUDIT_UNSAFE_DRIFT')
  need(n.mtime_ns>=m.mtime_ns and (n.size!=m.size or n.mtime_ns==m.mtime_ns),'COMMON_AUDIT_UNSAFE_DRIFT')
  appended+=n.size>m.size
 need(type(ja.boot) is str and ja.boot==jb.boot and type(ja.token) is str and type(jb.token) is str and bool(ja.token) and bool(jb.token),'COMMON_AUDIT_UNSAFE_DRIFT')
 return appended,ja.token!=jb.token

def zero(result,count):
 need(type(result) is dict and type(result.get('files')) is dict and type(result.get('journal')) is dict,'COMMON_AUDIT_SCHEMA')
 f,j=result['files'],result['journal']
 for part in (f,j):
  counts=part.get('counts');need(type(counts) is list and len(counts)==count and all(type(x) is int and x>=0 for x in counts),'COMMON_AUDIT_SCHEMA')
  need(not any(counts),'COMMON_AUDIT_POSITIVE')
 need(f.get('status')=='COMPLETE_FINITE_FILE_WINDOW' and type(f.get('uncovered_tail_bytes')) is int and f['uncovered_tail_bytes']==0 and type(f.get('end_offsets')) is dict,'COMMON_AUDIT_SCHEMA')
 need(j.get('status')=='COMPLETE_FINITE_JOURNAL_WINDOW' and j.get('complete') is True and j.get('cutoff_covered') is True,'COMMON_AUDIT_SCHEMA')
 return f['end_offsets']
def validate_diagnostic(v):
 need(type(v) is dict and set(v)=={'attempt','classification','file_appends','journal_advanced','offset_batches_changed'},'COMMON_AUDIT_SCHEMA')
 need(type(v['attempt']) is int and 1<=v['attempt']<=3 and v['classification'] in ('STABLE','APPEND_ONLY','UNSAFE'),'COMMON_AUDIT_SCHEMA')
 need(type(v['file_appends']) is int and 0<=v['file_appends']<=512 and type(v['journal_advanced']) is bool and type(v['offset_batches_changed']) is int and 0<=v['offset_batches_changed']<=3,'COMMON_AUDIT_SCHEMA');return dict(v)
def run(batches,start,jstart,*,snapshot,quiet,audit_once,emit,clock=time.monotonic):
 need(type(batches) is list and 1<=len(batches)<=3 and all(type(b) is list and 2<=len(b)<=32 for b in batches),'COMMON_AUDIT_SCHEMA')
 deadline=clock()+700;previous=None
 for attempt in range(1,4):
  need(clock()+30+65*len(batches)<=deadline,'COMMON_AUDIT_DEADLINE')
  quiet();cut=snapshot()
  if previous is not None:transition(previous,cut)
  expected={p:m.size for p,m in marks(cut[0]).items()};results=[]
  for batch in batches:
   need(clock()+65<=deadline,'COMMON_AUDIT_DEADLINE')
   # No nested retries here. The full original window, including every pattern,
   # is scanned again; any scanner/positive/config failure escapes immediately.
   result=audit_once(batch,start,jstart);offsets=zero(result,len(batch))
   need(set(offsets)==set(expected) and all(type(v) is int and v>=0 for v in offsets.values()),'COMMON_AUDIT_SCHEMA')
   results.append(result)
  end=snapshot();changed=sum(r['files']['end_offsets']!=expected for r in results)
  try:appends,journal_advanced=transition(cut,end)
  except Rejected:
   emit(validate_diagnostic({'attempt':attempt,'classification':'UNSAFE','file_appends':0,'journal_advanced':False,'offset_batches_changed':changed}));raise
  need(all(expected[p]<=r['files']['end_offsets'][p]<=end[0][p].size for r in results for p in expected),'COMMON_AUDIT_UNSAFE_DRIFT')
  need(clock()<=deadline,'COMMON_AUDIT_DEADLINE')
  stable=cut==end and changed==0
  emit(validate_diagnostic({'attempt':attempt,'classification':'STABLE' if stable else 'APPEND_ONLY','file_appends':appends,'journal_advanced':journal_advanced,'offset_batches_changed':changed}))
  if stable:return {'common_end_verified':True,'pattern_count':sum(map(len,batches)),'batches':results}
  # An offset mismatch with no observed append/advance is not proven append-only.
  need(appends>0 or journal_advanced,'COMMON_AUDIT_UNSAFE_DRIFT')
  previous=end
 raise Rejected('COMMON_AUDIT_CONVERGENCE_EXHAUSTED')
