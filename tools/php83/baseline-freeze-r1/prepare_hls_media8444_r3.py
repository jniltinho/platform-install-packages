"""Whole-batch common-end convergence only, no API/media workload changes."""
from pathlib import Path
import hashlib
H=Path(__file__).parent
def build():
 raw=(H/'guest_hls_media8444_r2.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='f842e0b6aff69ea36d41dae9473876a8ffb5a56c8c9e12415d1104676068176e';s=raw.decode()
 anchor="  convergence=load('convergence',NEW_HERE/'convergence.py')"
 add="\n  need(hashlib.sha256((NEW_HERE/'common_end.py').read_bytes()).hexdigest()=="+repr(hashlib.sha256((H/'common_end.py').read_bytes()).hexdigest())+",'AUDIT_CONVERGENCE_PIN')\n  common_end=load('common_end',NEW_HERE/'common_end.py')"
 assert s.count(anchor)==1;s=s.replace(anchor,anchor+add)
 a=s.index('  def audit_all(');b=s.index("  report['phase']='invalid-nonce'",a)
 s=s[:a]+'''  def audit_all(batches,start,jstart):
   def quiet():
    try:settle.wait_quiet(lambda:(files.snapshot(legacy.logs()),journal.snapshot()))
    except settle.Unsettled:raise Rejected('QUIET_WINDOW_NOT_ESTABLISHED') from None
   def emitted(value):
    rows=report.setdefault('common_end_attempts',[]);need(len(rows)<9,'COMMON_AUDIT_SCHEMA');rows.append(value)
   try:return common_end.run(batches,start,jstart,snapshot=lambda:(files.snapshot(legacy.logs()),journal.snapshot()),quiet=quiet,audit_once=audit_once,emit=emitted)
   except common_end.Rejected as error:raise Rejected(str(error)) from None
'''+s[b:]
 import sys
 sys.path.insert(0,str(H));import common_end
 s=s.replace('FIXED_FAILURE_CODES=[','FIXED_FAILURE_CODES='+repr(list(common_end.CODES))+'+[')
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
