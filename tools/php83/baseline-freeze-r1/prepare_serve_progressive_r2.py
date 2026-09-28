"""Complete-zero append conflict convergence; no workload retry."""
from pathlib import Path
import hashlib
H=Path(__file__).parent
CODES=['AUDIT_CONVERGENCE_DEADLINE','AUDIT_CONVERGENCE_EXHAUSTED','AUDIT_CONVERGENCE_PIN']
def build():
 raw=(H/'guest_serve_progressive.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='317688ac736a9a2a8567edc7d779e989b9ac9e7765a0ccd64ac74bead3a954c2';s=raw.decode()
 anchor="  def audit(patterns,start,jstart):\n"
 s=s.replace(anchor,"  need(hashlib.sha256((NEW_HERE/'convergence.py').read_bytes()).hexdigest()=="+repr(hashlib.sha256((H/'convergence.py').read_bytes()).hexdigest())+",'AUDIT_CONVERGENCE_PIN')\n  convergence=load('convergence',NEW_HERE/'convergence.py')\n  def audit_once(patterns,start,jstart):\n",1)
 # Preserve a file match immediately even if journal collection would fail later.
 anchor="   j=scan('journal','journal',lambda:journal.scan_window(jstart,patterns))"
 s=s.replace(anchor,"   if any(f.get('counts',[])):\n    record_match('files_and_journal',patterns,f,{'counts':[0]*len(patterns)},number)\n    raise Rejected('PRIVATE_MARKER_LOGGED')\n"+anchor)
 a="   need(f_after['end_offsets']==f['end_offsets'],'FILE_TAIL_DURING_JOURNAL')\n   f=f_after"
 s=s.replace(a,"   record_match('files_after_journal',patterns,f_after,j,number)\n   accepted(f_after,j)\n   need(f_after['end_offsets']==f['end_offsets'],'FILE_TAIL_DURING_JOURNAL')\n   f=f_after")
 s=s.replace("   need(j.get('status')==JOURNAL_STATUS", "   if any(j.get('counts',[])):\n    record_match('files_and_journal',patterns,f,j,number)\n    raise Rejected('PRIVATE_MARKER_LOGGED')\n   need(j.get('status')==JOURNAL_STATUS")
 # Avoid duplicate private filename, already recorded above.
 s=s.replace("   record_match('files_after_journal',patterns,f,j,number)\n   accepted(f,j)","   accepted(f,j)")
 anchor='  def audit_all(batches,start,jstart):'
 s=s.replace(anchor,"  def audit(patterns,start,jstart):\n   try:return convergence.run(lambda:audit_once(patterns,start,jstart),Rejected)\n   except convergence.Exhausted as error:raise Rejected(str(error)) from None\n"+anchor)
 s=s.replace('FIXED_FAILURE_CODES=[','FIXED_FAILURE_CODES=['+repr(CODES)[1:-1]+',')
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
