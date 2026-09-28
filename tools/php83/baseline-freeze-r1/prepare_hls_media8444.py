"""Versioned two-GET derivative; historical context and HLS guests unchanged."""
from pathlib import Path
import hashlib
H=Path(__file__).parent
MODULES=['hls_context_proof.py','hls_media8444.py','hls_nested8444.py','hls_playlist_bridge.py','hls_response.py','hls_source_r2.py','short_delivery443.py','manifest_diagnostic.py','nested_descriptor.py','media_get443.py','media_get8444.py']
SOURCE_PINS={'alpha/lib/model/DeliveryProfileVodPackagerHls.php':'664b7d41cc60728c329ae3eb38409c02e5d83a54a0be12d02416af8dfd2e6241','alpha/lib/model/DeliveryProfileVod.php':'e9058bbd6cc16aa79a928ddf91ef80e819481f43404ed7d3fddb35ec4b310494','alpha/apps/kaltura/lib/myEntryUtils.class.php':'70ebf2b99fbd5b898f88700b5c696eb1d64258f52bbfeb77bb68f8ef57306089'}
def build():
 raw=(H/'guest_delivery_context_pair_r2.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='dd887c2097eb5d017f79773dc352575602fc1fff738bc73c502a6ad1a4dacbb8';s=raw.decode()
 old="  pair=load('delivery_context_pair',NEW_HERE/'delivery_context_pair_r2.py')"
 add='  for name,pin in '+repr({n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in MODULES})+":need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'HLS_PIN')\n"
 add+="  pair=load('hls_context_proof',NEW_HERE/'hls_context_proof.py')\n  hls=load('hls_media8444',NEW_HERE/'hls_media8444.py')\n  get443=load('media_get443',NEW_HERE/'media_get443.py');get8444=load('media_get8444',NEW_HERE/'media_get8444.py')\n"
 add+='  def hls_source_guard():\n   for name,pin in '+repr(SOURCE_PINS)+".items():\n    f=Path('/opt/kaltura/app')/name;m=f.lstat();need(stat.S_ISREG(m.st_mode) and m.st_uid==0 and m.st_nlink==1 and m.st_size<=512*1024 and not m.st_mode&0o002 and hashlib.sha256(f.read_bytes()).hexdigest()==pin,'HLS_SOURCE_PIN')\n  hls_source_guard()"
 assert s.count(old)==1;s=s.replace(old,add)
 start=s.index("  try:report['delivery_context_pair']");end=s.index("  failure_stage='QUIET_SETTLE'",start)
 s=s[:start]+"  def described(stage,value):report.setdefault('hls_diagnostics',{})[stage]=value\n  try:\n   report['playback_context'],report['hls_media']=hls.observe(lambda **form:call(ks=ks,**form),lambda url:enrollment.enroll(url,tracked_tokens),lambda url,headers,limit:get443.request(tls_ca,url,headers,limit),lambda url,headers,limit:get8444.request(tls_ca,url,headers,limit),secret,ks,selected_context_asset,expected_https_id,described)\n  except hls.Rejected as error:raise Rejected(str(error) if str(error) in hls.CODES else 'HLS_MEDIA_REJECTED') from None\n"+s[end:]
 s=s.replace('  direct_source_guard()\n','  hls_source_guard()\n  direct_source_guard()\n')
 import sys
 sys.path.insert(0,str(H));import hls_media8444
 s=s.replace('FIXED_FAILURE_CODES=[','FIXED_FAILURE_CODES='+repr(['HLS_PIN','HLS_SOURCE_PIN',*hls_media8444.CODES])+ '+[')
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
