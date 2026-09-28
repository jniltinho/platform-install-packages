"""New one-manifest-only guest from frozen selected context observer."""
from pathlib import Path
import hashlib
H=Path(__file__).parent
CODES=['HLS_CONTEXT','HLS_CONTEXT_COVERAGE','HLS_SOURCE_COUNT','HLS_ACCESS_ACTIONS','HLS_SOURCE_GUARD','HLS_REFERENCE_ENROLLMENT','HLS_MANIFEST_REJECTED','HLS_PIN']
def build():
 raw=(H/'guest_context_observer_r2.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='e717197ccbb7cd560230471c3ba8a4abdc58fb813adb772fc82ac01d370f4555';s=raw.decode()
 a=s.index("  try:report['playback_context']=context.observe(");b=s.index("  failure_stage='QUIET_SETTLE'",a)
 pins={n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in ('hls_source_r2.py','hls_first.py','short_delivery443.py','media_get443.py')}
 block="  for name,pin in "+repr(pins)+".items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'HLS_PIN')\n"
 block+='''  first=load('hls_first',NEW_HERE/'hls_first.py')
  import media_get443
  def described(row):report['hls_route']=row
  try:report['playback_context'],report['hls_manifest']=first.observe(lambda **form:call(ks=ks,**form),lambda url:enrollment.enroll(url,tracked_tokens),lambda url,headers,limit:media_get443.request(tls_ca,url,headers,limit),secret,ks,selected_context_asset,described)
  except first.Rejected as error:raise Rejected(str(error) if str(error) in first.CODES else 'HLS_MANIFEST_REJECTED') from None
'''
 s=s[:a]+block+s[b:]
 # Guard source identity before authentication and after the observation.
 anchor='  def serve_source_guard():\n'
 s=s.replace(anchor,anchor+"   f=Path('/opt/kaltura/app/alpha/apps/kaltura/lib/myEntryUtils.class.php');m=f.lstat();need(stat.S_ISREG(m.st_mode) and m.st_uid==0 and m.st_nlink==1 and m.st_size<=512*1024 and hashlib.sha256(f.read_bytes()).hexdigest()=='70ebf2b99fbd5b898f88700b5c696eb1d64258f52bbfeb77bb68f8ef57306089','ROUTE_SOURCE_PIN')\n")
 s=s.replace('FIXED_FAILURE_CODES=[','FIXED_FAILURE_CODES=['+repr(CODES)[1:-1]+',')
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
