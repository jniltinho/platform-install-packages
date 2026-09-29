"""Step 2 workload: the reviewed guest_long_ready_r1 base (Sphinx full-content + in-window new-log privacy) with the
phase-B block replaced by flavor_progressive.observe(): flavorasset.getUrl, URL tokens enrolled before use, pinned
HTTPS443 exact 1 MiB Range GETs, SHA256 must equal the natively decoded stored flavor. Read-only; no mutation."""
from pathlib import Path
import hashlib
import prepare_long_ready_r1 as base
import flavor_progressive
H=Path(__file__).parent
BASE_GUEST='75a360064d80409ab8725a5db7e40a88a0cfec7f4c168078bd33ff714529bb0e'
def build():
 assert hashlib.sha256((H/'guest_long_ready_r1.py').read_bytes()).hexdigest()==BASE_GUEST
 s=base.build();assert hashlib.sha256(s.encode()).hexdigest()==BASE_GUEST
 h=lambda n:hashlib.sha256((H/n).read_bytes()).hexdigest()
 a=s.index("  report['phase']='long-ready-phase-b';failure_stage='API_ROUND'\n");b=s.index("  failure_stage='QUIET_SETTLE'\n",a)
 block=("  report['phase']='flavor-progressive-118';failure_stage='API_ROUND'\n"
  "  for name,pin in "+repr({n:h(n) for n in ('flavor_progressive.py','context_urls.py','short_delivery443.py')})+".items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'PROG_PIN')\n"
  "  prog=load('flavor_progressive',NEW_HERE/'flavor_progressive.py');enrollment=load('context_urls',NEW_HERE/'context_urls.py');sd=load('short_delivery443',NEW_HERE/'short_delivery443.py')\n"
  "  def described(stage,value):report.setdefault('progressive_diagnostics',{})[stage]=value\n"
  "  try:report['flavor_progressive']=prog.observe(lambda **form:call(ks=ks,**form),lambda url:enrollment.enroll(url,tracked_tokens),lambda url,headers,limit,status:sd.fetch(lambda u,hh,l:get443.request(tls_ca,u,hh,l),url,headers,limit,status),secret,ks,described,time.monotonic)\n"
  "  except prog.Rejected as error:raise Rejected(str(error)) from None\n")
 s=s[:a]+block+s[b:]
 for x,y in [('\"\"\"FullHD60 phase B: read-only READY/flavor observation of the phase-A entry after finite privacy gates; no upload.\"\"\"',
   '\"\"\"Delivered 1080p60 progressive (flavor 0_j6rfow09) exact-range fetch, SHA256 equal to the decoded stored file; read-only.\"\"\"'),
  ("FIXED_FAILURE_CODES=","FIXED_FAILURE_CODES="+repr(list(flavor_progressive.CODES)+['PROG_PIN'])+'+')]:
  assert s.count(x)==1,x;s=s.replace(x,y)
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 s=build()
 with Path(a.output).open('x') as f:f.write(s)
