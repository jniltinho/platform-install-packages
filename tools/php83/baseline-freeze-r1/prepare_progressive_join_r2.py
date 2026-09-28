"""Quiet before every finite audit; original starts and common ends remain mandatory."""
import argparse,hashlib
from pathlib import Path
H=Path(__file__).parent
def build():
 raw=(H/'guest_progressive_join.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='1c379e18dbf569b2717242fcd4c6dbbad9151eb0f56dbb7983cd2bace395a09b'
 s=raw.decode();block="  need(hashlib.sha256((NEW_HERE/'settle.py').read_bytes()).hexdigest()=='2b1382fc7ff4163240d9c6e3342738ce90ab8537df9ea9999497a44e24d84764','SETTLE_PIN')\n  settle=load('baseline_settle_v1',NEW_HERE/'settle.py')\n"
 assert s.count(block)==1;s=s.replace(block,'')
 anchor="  content=load('direct_content',NEW_HERE/'direct_content.py');provenance=load('privacy_provenance',NEW_HERE/'privacy_provenance.py')\n";assert s.count(anchor)==1;s=s.replace(anchor,anchor+block)
 anchor="   f=scan('files','files_initial',lambda:files.scan_window(start,patterns,inventory=legacy.logs))"
 added="""   try:quiet=settle.wait_quiet(lambda:(files.snapshot(legacy.logs()),journal.snapshot()))
   except settle.Unsettled:raise Rejected('QUIET_WINDOW_NOT_ESTABLISHED') from None
   item=dict(quiet,audit=number,stage=failure_stage)
   private_json(private_dir/('quiet-'+str(number)+'.json'),item)
   report['last_audit_quiet']=item
"""
 assert s.count(anchor)==1;s=s.replace(anchor,added+anchor)
 anchor="  def audit_all(batches,start,jstart):\n   cutoff=files.snapshot(legacy.logs());jcut=journal.snapshot()"
 replacement="""  def audit_all(batches,start,jstart):
   try:settle.wait_quiet(lambda:(files.snapshot(legacy.logs()),journal.snapshot()))
   except settle.Unsettled:raise Rejected('QUIET_WINDOW_NOT_ESTABLISHED') from None
   cutoff=files.snapshot(legacy.logs());jcut=journal.snapshot()"""
 assert s.count(anchor)==1;s=s.replace(anchor,replacement)
 s=s.replace("report['invalid_nonce']=audit(","failure_stage='INVALID_NONCE_PRIVACY';report['invalid_nonce']=audit(").replace("report['user_privacy']=audit(","failure_stage='USER_PRIVACY';report['user_privacy']=audit(")
 return s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();s=build()
 with Path(a.output).open('x') as f:f.write(s)
 print(hashlib.sha256(s.encode()).hexdigest())
