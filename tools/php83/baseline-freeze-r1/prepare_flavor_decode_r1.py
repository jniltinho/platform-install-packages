"""Stored 1080p60 flavor decode workload: the reviewed guest_long_ready_r1 base (Sphinx full-content + in-window
new-log privacy) with the phase-B block replaced by: API binding of flavor 0_j6rfow09 (entry 0_3h92ab2l, params 118,
READY), file_sync binding of its stored file under /opt/kaltura/web/content, stable read, SHA256 and a pinned full
local decode (flavor_decode.py). Read-only; exports metadata, size and hash only."""
from pathlib import Path
import hashlib
import prepare_long_ready_r1 as base
import flavor_decode
H=Path(__file__).parent
BASE_GUEST='75a360064d80409ab8725a5db7e40a88a0cfec7f4c168078bd33ff714529bb0e'
FLAVOR='0_j6rfow09';ENTRY='0_3h92ab2l'
def build():
 assert hashlib.sha256((H/'guest_long_ready_r1.py').read_bytes()).hexdigest()==BASE_GUEST
 s=base.build();assert hashlib.sha256(s.encode()).hexdigest()==BASE_GUEST
 pin=hashlib.sha256((H/'flavor_decode.py').read_bytes()).hexdigest()
 a=s.index("  report['phase']='long-ready-phase-b';failure_stage='API_ROUND'\n");b=s.index("  failure_stage='QUIET_SETTLE'\n",a)
 block=("  report['phase']='flavor-decode-118';failure_stage='API_ROUND'\n"
  "  need(hashlib.sha256((NEW_HERE/'flavor_decode.py').read_bytes()).hexdigest()=="+repr(pin)+",'FLAVOR_DECODE_PIN')\n"
  "  fdec=load('flavor_decode',NEW_HERE/'flavor_decode.py')\n"
  "  fa=call(service='flavorasset',action='get',ks=ks,id="+repr(FLAVOR)+")\n"
  "  need(type(fa) is dict and fa.get('objectType')=='KalturaFlavorAsset' and fa.get('id')=="+repr(FLAVOR)+" and fa.get('entryId')=="+repr(ENTRY)+" and str(fa.get('partnerId'))=='102' and str(fa.get('flavorParamsId'))=='118' and str(fa.get('status'))=='2' and re.fullmatch('[1-9][0-9]{0,5}',str(fa.get('version'))) is not None,'FLAVOR_ASSET_BINDING')\n"
  "  fversion=str(fa.get('version'))\n"
  "  rows=legacy.sql(\"SELECT id,partner_id,object_id,version,file_root,file_path,status FROM file_sync WHERE object_type=4 AND object_sub_type=1 AND file_type=1 AND status=2 AND partner_id=102 AND object_id='"+FLAVOR+"' AND version='\"+fversion+\"' LIMIT 2\")\n"
  "  candidates=[]\n"
  "  for row in rows:\n"
  "   try:candidates.append(legacy.owned_storage(row,102,"+repr(FLAVOR)+",fversion))\n"
  "   except legacy.Failed:continue\n"
  "  need(len(candidates)==1,'LOCAL_SOURCE_BINDING');stored_flavor=candidates[0][0]\n"
  "  ffd=os.open(stored_flavor,os.O_RDONLY|os.O_NOFOLLOW)\n"
  "  with os.fdopen(ffd,'rb') as ff:\n"
  "   before=os.fstat(ff.fileno());need(stat.S_ISREG(before.st_mode) and 0<before.st_size<=fdec.MAX_BYTES,'FLAVOR_DECODE_INPUT');flavor_bytes=ff.read(before.st_size+1)\n"
  "   after=os.fstat(ff.fileno());need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns) and len(flavor_bytes)==before.st_size,'FLAVOR_DECODE_INPUT')\n"
  "  try:decoded=fdec.decode(flavor_bytes)\n"
  "  except fdec.Rejected as error:raise Rejected(str(error)) from None\n"
  "  report['flavor_decode']={'flavor_id':"+repr(FLAVOR)+",'entry_id':"+repr(ENTRY)+",'flavor_params_id':118,'flavor_version':int(fversion),'stored_bytes':len(flavor_bytes),'stored_sha256':hashlib.sha256(flavor_bytes).hexdigest(),'decode':decoded}\n")
 s=s[:a]+block+s[b:]
 for x,y in [('\"\"\"FullHD60 phase B: read-only READY/flavor observation of the phase-A entry after finite privacy gates; no upload.\"\"\"',
   '\"\"\"Stored 1080p60 flavor (params 118) full local decode after finite privacy gates; read-only, no upload.\"\"\"'),
  ("FIXED_FAILURE_CODES=","FIXED_FAILURE_CODES="+repr(list(flavor_decode.CODES)+['FLAVOR_DECODE_PIN','FLAVOR_ASSET_BINDING'])+'+')]:
  assert s.count(x)==1,x;s=s.replace(x,y)
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 s=build()
 with Path(a.output).open('x') as f:f.write(s)
