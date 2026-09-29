"""FullHD60 phase B workload: guest_thumbnail_r5 (Sphinx full-content privacy) plus privacy_new_logs (logs created
in-window scanned from offset 0) with the thumbnail block replaced by long_ready.observe() and a read-only
file_sync binding of the stored original to the fixture SHA256. No upload, no mutation."""
from pathlib import Path
import hashlib
import prepare_thumbnail_r5 as r5
import long_ready,privacy_new_logs
H=Path(__file__).parent
R5_GUEST='6a3bc5c0551102a9c4cff75c1cf3d5e6fc2ae4a67b0b4fe424188af2925a1b24'
LONG_SHA='611e3644fb56fc1f12ddccd1d889258d249e36a4eca445451c16d13f5c5f5b07'
def build():
 assert hashlib.sha256((H/'guest_thumbnail_r5.py').read_bytes()).hexdigest()==R5_GUEST
 s=r5.build();assert hashlib.sha256(s.encode()).hexdigest()==R5_GUEST
 h=lambda n:hashlib.sha256((H/n).read_bytes()).hexdigest()
 a=s.index("  report['phase']='thumbnail';failure_stage='API_ROUND'\n");b=s.index("  failure_stage='QUIET_SETTLE'\n",a)
 block=("  report['phase']='long-ready-phase-b';failure_stage='API_ROUND'\n"
  "  need(hashlib.sha256((NEW_HERE/'long_ready.py').read_bytes()).hexdigest()=="+repr(h('long_ready.py'))+",'LONG_READY_PIN')\n"
  "  longready=load('long_ready',NEW_HERE/'long_ready.py')\n"
  "  try:report['long_ready']=longready.observe(lambda s,a,**f:call(service=s,action=a,**f),ks)\n"
  "  except longready.Rejected as error:raise Rejected(str(error)) from None\n"
  "  original=next(r for r in report['long_ready']['flavors'] if r['isOriginal']);need(type(original['version']) is int,'LONG_READY_FLAVORS')\n"
  "  rows=legacy.sql(\"SELECT id,partner_id,object_id,version,file_root,file_path,status FROM file_sync WHERE object_type=4 AND object_sub_type=1 AND file_type=1 AND status=2 AND partner_id=102 AND object_id='\"+original['id']+\"' AND version='\"+str(original['version'])+\"' LIMIT 2\")\n"
  "  candidates=[]\n"
  "  for row in rows:\n"
  "   try:candidates.append(legacy.owned_storage(row,102,original['id'],str(original['version'])))\n"
  "   except legacy.Failed:continue\n"
  "  need(len(candidates)==1,'LOCAL_SOURCE_BINDING')\n"
  "  report['long_ready']['stored_original_sha256_match']=legacy.checksum(candidates[0][0])=="+repr(LONG_SHA)+"\n"
  "  need(report['long_ready']['stored_original_sha256_match'],'STORED_SOURCE_BYTES')\n")
 s=s[:a]+block+s[b:]
 edits=[
  ("  legacy.logs=lambda:sphinx.exclude(",
   "  need(hashlib.sha256((NEW_HERE/'privacy_new_logs.py').read_bytes()).hexdigest()=="+repr(h('privacy_new_logs.py'))+",'NEW_LOG_PIN')\n"
   "  newlogs=load('privacy_new_logs',NEW_HERE/'privacy_new_logs.py')\n"
   "  legacy.logs=lambda:sphinx.exclude("),
  ('\"\"\"Read-only existing lab74 media observation after finite privacy gates; no upload.\"\"\"',
   '\"\"\"FullHD60 phase B: read-only READY/flavor observation of the phase-A entry after finite privacy gates; no upload.\"\"\"'),
  ("FIXED_FAILURE_CODES=","FIXED_FAILURE_CODES="+repr(list(long_ready.CODES+privacy_new_logs.CODES)+['LONG_READY_PIN','NEW_LOG_PIN'])+'+'),
 ]
 for x,y in edits:
  assert s.count(x)==1,x;s=s.replace(x,y)
 old="lambda:files.scan_window(start,patterns,inventory=legacy.logs)"
 assert s.count(old)==2;s=s.replace(old,"lambda:newlogs.scan(files,start,patterns,legacy.logs)")
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 s=build()
 with Path(a.output).open('x') as f:f.write(s)
