"""Pinned one-flavor-list derivative; no workload repetition or upload."""
import argparse,hashlib
from pathlib import Path
H=Path(__file__).parent
PIN='a3a60d6ad5ddfcadebf13181d757915e41fb4fd65d16c1c08c3f5b4263bf59bb'
def build():
 raw=(H/'guest_https.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='2fa152c361c196c44b799c6fe6676ea17b7058c4c3bbc764f766bfc7243124ac'
 assert hashlib.sha256((H/'short_metadata.py').read_bytes()).hexdigest()==PIN
 s=raw.decode();a=s.index("  report['phase']='untimed-protocol-rehearsal'");b=s.index("  failure_stage='QUIET_SETTLE'",a)
 s=s[:a]+"""  report['phase']='short-flavor-metadata';failure_stage='API_ROUND'
  need(hashlib.sha256((NEW_HERE/'short_metadata.py').read_bytes()).hexdigest()=='a3a60d6ad5ddfcadebf13181d757915e41fb4fd65d16c1c08c3f5b4263bf59bb','METADATA_PIN')
  metadata=load('short_metadata',NEW_HERE/'short_metadata.py')
  try:report['flavor_metadata']=metadata.collect(lambda **form:call(ks=ks,**form))
  except metadata.Rejected as error:
   code=str(error)
   raise Rejected('METADATA_'+code if code in ['API_CALL_FAILED', 'RESPONSE_TYPE', 'TOTAL', 'CARDINALITY', 'ASSET_TYPE', 'ASSET_ID', 'DUPLICATE', 'PARTNER', 'OWNERSHIP', 'STATUS', 'ORIGINAL_TYPE', 'VERSION', 'PARAMS', 'SIZE', 'EXTENSION', 'SOURCE_BINDING'] else 'METADATA_RESPONSE_REJECTED') from None
  report['flavor_metadata']['size_unit']='API_KBytes'
"""+s[b:]
 s=s.replace("  need(report['untimed_round']['functional_round_pass'],'UNTIMED_ROUND_FAILED')\n",'')
 s=s.replace('FIXED_FAILURE_CODES=[',"FIXED_FAILURE_CODES=['METADATA_PIN','METADATA_RESPONSE_REJECTED',")
 s=s.replace('FIXED_FAILURE_CODES=[','FIXED_FAILURE_CODES=['+repr(['METADATA_API_CALL_FAILED', 'METADATA_RESPONSE_TYPE', 'METADATA_TOTAL', 'METADATA_CARDINALITY', 'METADATA_ASSET_TYPE', 'METADATA_ASSET_ID', 'METADATA_DUPLICATE', 'METADATA_PARTNER', 'METADATA_OWNERSHIP', 'METADATA_STATUS', 'METADATA_ORIGINAL_TYPE', 'METADATA_VERSION', 'METADATA_PARAMS', 'METADATA_SIZE', 'METADATA_EXTENSION', 'METADATA_SOURCE_BINDING'])[1:-1]+',')
 return s
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 s=build()
 with Path(a.output).open('x') as f:f.write(s)
 print(hashlib.sha256(s.encode()).hexdigest())
