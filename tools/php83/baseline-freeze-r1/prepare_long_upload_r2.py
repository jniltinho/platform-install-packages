"""FullHD60 phase A r2 on the Decision 7 lab profile (15): guest_long_ready_r1 (Sphinx full-content + in-window
new-log privacy) with the phase-B block replaced by long_upload_r2.upload(). Phase A r1's batch audit failed on
new worker logs; this base scans them from offset 0."""
from pathlib import Path
import hashlib
import prepare_long_ready_r1 as base
import long_upload_r2
H=Path(__file__).parent
BASE_GUEST='75a360064d80409ab8725a5db7e40a88a0cfec7f4c168078bd33ff714529bb0e'
CA='5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef'
def build():
 assert hashlib.sha256((H/'guest_long_ready_r1.py').read_bytes()).hexdigest()==BASE_GUEST
 s=base.build();assert hashlib.sha256(s.encode()).hexdigest()==BASE_GUEST
 pin=hashlib.sha256((H/'long_upload_r2.py').read_bytes()).hexdigest()
 a=s.index("  report['phase']='long-ready-phase-b';failure_stage='API_ROUND'\n");b=s.index("  failure_stage='QUIET_SETTLE'\n",a)
 block=("  report['phase']='long-upload-phase-a-r2';failure_stage='API_ROUND'\n"
  "  need(hashlib.sha256((NEW_HERE/'long_upload_r2.py').read_bytes()).hexdigest()=="+repr(pin)+",'LONG_PIN')\n"
  "  longup=load('long_upload_r2',NEW_HERE/'long_upload_r2.py')\n"
  "  def long_progress(value):report['long_upload_progress']=value\n"
  "  try:\n"
  "   long_data=longup.read_source();boundary='baseline-long-'+secrets.token_hex(12)\n"
  "   report['long_upload']=longup.upload(lambda s,a,**f:call(service=s,action=a,**f),lambda params,content:legacy.deadline._bounded(longup._part_worker,(('192.168.56.74','https',8443),tls_ca,"+repr(CA)+",params,content,boundary),limit=1024*1024,deadline=30),ks,long_data,boundary,progress=long_progress)\n"
  "  except longup.Rejected as error:raise Rejected(str(error)) from None\n")
 s=s[:a]+block+s[b:]
 edits=[('\"\"\"FullHD60 phase B: read-only READY/flavor observation of the phase-A entry after finite privacy gates; no upload.\"\"\"',
   '\"\"\"FullHD60 phase A r2: ONE chunked upload mutation on lab profile 15 (new entry); finite privacy gates.\"\"\"'),
  ("FIXED_FAILURE_CODES=","FIXED_FAILURE_CODES="+repr(list(long_upload_r2.CODES)+['LONG_PIN'])+'+')]
 for x,y in edits:
  assert s.count(x)==1,x;s=s.replace(x,y)
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 s=build()
 with Path(a.output).open('x') as f:f.write(s)
