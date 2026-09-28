"""New thumbnail workload; frozen HLS envelope retained, no HLS requests repeated."""
from pathlib import Path
import hashlib
H=Path(__file__).parent
MODULES=['thumbnail.py','thumbnail_decode.py']
SOURCE_PINS={'api_v3/services/ThumbAssetService.php':'f6f10cae05c4fc6eef2931b1fba651c8451448384bdbeaf21104983afd32679f','alpha/lib/model/thumbAsset.php':'478e479282058b84e1f7c1368d5d94d9fb1f00f5c558052496690587b253d24b','api_v3/lib/types/conversionProfile/KalturaThumbAsset.php':'ab2ce68922da90c23a4aece918a15871f2ad0eb84ab57c3adc0dcb7294013c59'}
def build():
 raw=(H/'guest_hls_delivery8444_r3.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='0ab983cf74d994d5e1d3333e4c109a8b918d98ac8ad7c6cc7e21862dbabf8840';s=raw.decode()
 old="  hls=load('hls_delivery8444_r3',NEW_HERE/'hls_delivery8444_r3.py')"
 new='  for name,pin in '+repr({n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in MODULES})+".items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'THUMB_PIN')\n  thumb=load('thumbnail',NEW_HERE/'thumbnail.py')\n  thumbdecode=load('thumbnail_decode',NEW_HERE/'thumbnail_decode.py')\n  def thumb_source_guard():\n   for name,pin in "+repr(SOURCE_PINS)+".items():need(legacy.checksum(Path('/opt/kaltura/app')/name)==pin,'THUMB_SOURCE_PIN')\n  thumb_source_guard()"
 assert s.count(old)==1;s=s.replace(old,new)
 a=s.index("  report['phase']='playback-context-no-get'");b=s.index("  failure_stage='QUIET_SETTLE'",a)
 s=s[:a]+'''  report['phase']='thumbnail';failure_stage='API_ROUND'
  enrollment=load('context_urls',NEW_HERE/'context_urls.py')
  def described(stage,value):report.setdefault('thumbnail_diagnostics',{})[stage]=value
  try:
   report['thumbnail']=thumb.observe(lambda **form:call(ks=ks,**form),lambda url:enrollment.enroll(url,tracked_tokens),lambda url,headers,limit:get443.request(tls_ca,url,headers,limit),thumbdecode.decode,secret,ks,described)
  except (thumb.Rejected,thumbdecode.Rejected) as error:raise Rejected(str(error) if str(error) in thumb.CODES+thumbdecode.CODES else 'THUMB_RESPONSE') from None
'''+s[b:]
 s=s.replace("  failure_stage='POSTCHECK'","  failure_stage='POSTCHECK'\n  thumb_source_guard()")
 import thumbnail,thumbnail_decode
 s=s.replace('FIXED_FAILURE_CODES=', 'FIXED_FAILURE_CODES='+repr(list(thumbnail.CODES+thumbnail_decode.CODES)+['THUMB_PIN','THUMB_SOURCE_PIN'])+'+',1)
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
