"""R5 thumbnail workload: prepare_thumbnail_r4.build() plus privacy_sphinx_binlog (full-content scan of the
Sphinx RT binlog directory instead of append windows). thumbnail_r4.py is reused unchanged; r1-r4 frozen."""
from pathlib import Path
import hashlib
import prepare_thumbnail_r4 as r4
import privacy_sphinx_binlog
H=Path(__file__).parent
R4_GUEST='4482e7fac847264b5b238fb9a44c7ed14619715feb81445e12fb685019a09f97'
def build():
 assert hashlib.sha256((H/'guest_thumbnail_r4.py').read_bytes()).hexdigest()==R4_GUEST
 s=r4.build();assert hashlib.sha256(s.encode()).hexdigest()==R4_GUEST
 pin=hashlib.sha256((H/'privacy_sphinx_binlog.py').read_bytes()).hexdigest()
 edits=[
  ("  legacy.logs=lambda:media_logs.extend(lambda:tls_logs.extend(old_logs))\n",
   "  need(hashlib.sha256((NEW_HERE/'privacy_sphinx_binlog.py').read_bytes()).hexdigest()=="+repr(pin)+",'SPHINX_BINLOG_PIN')\n"
   "  sphinx=load('privacy_sphinx_binlog',NEW_HERE/'privacy_sphinx_binlog.py')\n"
   "  legacy.logs=lambda:sphinx.exclude(lambda:media_logs.extend(lambda:tls_logs.extend(old_logs)))\n"),
  ("   accepted(f,j)\n   need(legacy.logging_preflight()",
   "   accepted(f,j)\n"
   "   try:sb=sphinx.scan(list(patterns))\n"
   "   except sphinx.Rejected as error:raise Rejected(str(error)) from None\n"
   "   rows=report.setdefault('sphinx_binlog_audits',[]);need(len(rows)<128,'PROVENANCE_LIMIT');rows.append(dict(sb,audit=number))\n"
   "   need(not any(sb['counts']),'PRIVATE_MARKER_LOGGED')\n"
   "   need(legacy.logging_preflight()"),
  ("FIXED_FAILURE_CODES=","FIXED_FAILURE_CODES="+repr(list(privacy_sphinx_binlog.CODES))+"+"),
 ]
 for a,b in edits:
  assert s.count(a)==1,a;s=s.replace(a,b)
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 s=build()
 with Path(a.output).open('x') as f:f.write(s)
