"""FullHD60 phase A workload: guest_thumbnail_r5 (Sphinx full-content privacy, frozen audits) with the thumbnail
block replaced by long_upload.upload(). Existing short-entry observation and all privacy audits are retained."""
from pathlib import Path
import hashlib
import prepare_thumbnail_r5 as r5
import long_upload
H=Path(__file__).parent
R5_GUEST='6a3bc5c0551102a9c4cff75c1cf3d5e6fc2ae4a67b0b4fe424188af2925a1b24'
CA='5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef'
def build():
 assert hashlib.sha256((H/'guest_thumbnail_r5.py').read_bytes()).hexdigest()==R5_GUEST
 s=r5.build();assert hashlib.sha256(s.encode()).hexdigest()==R5_GUEST
 pin=hashlib.sha256((H/'long_upload.py').read_bytes()).hexdigest()
 a=s.index("  report['phase']='thumbnail';failure_stage='API_ROUND'\n");b=s.index("  failure_stage='QUIET_SETTLE'\n",a)
 block=("  report['phase']='long-upload-phase-a';failure_stage='API_ROUND'\n"
  "  need(hashlib.sha256((NEW_HERE/'long_upload.py').read_bytes()).hexdigest()=="+repr(pin)+",'LONG_PIN')\n"
  "  longup=load('long_upload',NEW_HERE/'long_upload.py')\n"
  "  def long_progress(value):report['long_upload_progress']=value\n"
  "  try:\n"
  "   long_data=longup.read_source();boundary='baseline-long-'+secrets.token_hex(12)\n"
  "   report['long_upload']=longup.upload(lambda s,a,**f:call(service=s,action=a,**f),lambda params,content:legacy.deadline._bounded(longup._part_worker,(('192.168.56.74','https',8443),tls_ca,"+repr(CA)+",params,content,boundary),limit=1024*1024,deadline=30),ks,long_data,boundary,progress=long_progress)\n"
  "  except longup.Rejected as error:raise Rejected(str(error)) from None\n")
 s=s[:a]+block+s[b:]
 doc='"""Read-only existing lab74 media observation after finite privacy gates; no upload."""'
 assert s.count(doc)==1;s=s.replace(doc,'"""FullHD60 phase A: existing lab74 media observation plus ONE chunked upload mutation (new entry); finite privacy gates."""')
 old="FIXED_FAILURE_CODES="
 assert s.count(old)==1;s=s.replace(old,old+repr(list(long_upload.CODES)+['LONG_PIN'])+'+')
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 s=build()
 with Path(a.output).open('x') as f:f.write(s)
