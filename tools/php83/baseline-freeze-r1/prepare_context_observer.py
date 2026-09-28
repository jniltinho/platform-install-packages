"""One no-GET playback context; source response remains private."""
from pathlib import Path
import hashlib
H=Path(__file__).parent
CODES=['CONTEXT_CALL','CONTEXT_TYPE','URL_ENROLLMENT_INCOMPLETE','RESPONSE_COVERAGE_INCOMPLETE','SOURCE_TYPE','SOURCE_FIELDS','CONTEXT_ARRAY','CONTEXT_PIN']
def build():
 raw=(H/'guest_serve_progressive_r3.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='e65c2b9026f74da55e499d870e506757c0f51d79c0072e18e93e05fb40a05037'
 s=raw.decode();a=s.index("  report['phase']='native-route-observation'");b=s.index("  failure_stage='QUIET_SETTLE'",a)
 pins={n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in ('playback_context_r3.py','context_urls.py')}
 block="  report['phase']='playback-context-no-get';failure_stage='API_ROUND'\n  for name,pin in "+repr(pins)+".items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'CONTEXT_PIN')\n"
 block+='''  context=load('playback_context_r3',NEW_HERE/'playback_context_r3.py')
  enrollment=load('context_urls',NEW_HERE/'context_urls.py')
  try:report['playback_context']=context.observe(lambda **form:call(ks=ks,**form),lambda url:enrollment.enroll(url,tracked_tokens))
  except context.Rejected as error:raise Rejected(str(error) if str(error) in '''+repr(CODES)+''' else 'CONTEXT_TYPE') from None
'''
 s=s[:a]+block+s[b:];s=s.replace('FIXED_FAILURE_CODES=[','FIXED_FAILURE_CODES=['+repr(CODES)[1:-1]+',')
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
