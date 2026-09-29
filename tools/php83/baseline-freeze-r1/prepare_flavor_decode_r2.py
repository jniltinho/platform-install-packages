"""Stored 1080p60 flavor decode workload r2: identical to prepare_flavor_decode_r1 except the API binding uses the
already-proven flavorasset.getByEntryId (phase B runs) and selects exactly flavor 0_j6rfow09, instead of
flavorasset.get, which failed FLAVOR_ASSET_BINDING natively under the user KS (cause not diagnosed; entitlement
filtering on assetPeer is the leading hypothesis). All other checks, SQL binding, stable read and decode unchanged."""
from pathlib import Path
import hashlib
import prepare_flavor_decode_r1 as r1
H=Path(__file__).parent
R1_GUEST='3252b37a54a3e3e154c51f9de86f650124ce3c829c5081f608ab1000a9947d89'
def build():
 assert hashlib.sha256((H/'guest_flavor_decode_r1.py').read_bytes()).hexdigest()==R1_GUEST
 s=r1.build();assert hashlib.sha256(s.encode()).hexdigest()==R1_GUEST
 old="  fa=call(service='flavorasset',action='get',ks=ks,id='0_j6rfow09')\n"
 new=("  listed=call(service='flavorasset',action='getByEntryId',ks=ks,entryId='0_3h92ab2l')\n"
  "  need(type(listed) is list and 1<=len(listed)<=32 and all(type(x) is dict for x in listed),'FLAVOR_ASSET_BINDING')\n"
  "  matches=[x for x in listed if x.get('id')=='0_j6rfow09'];need(len(matches)==1,'FLAVOR_ASSET_BINDING');fa=matches[0]\n")
 assert s.count(old)==1;s=s.replace(old,new)
 d1='\"\"\"Stored 1080p60 flavor (params 118) full local decode after finite privacy gates; read-only, no upload.\"\"\"'
 assert s.count(d1)==1;s=s.replace(d1,'\"\"\"Stored 1080p60 flavor (params 118) full local decode (r2: getByEntryId binding) after finite privacy gates; read-only, no upload.\"\"\"')
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 s=build()
 with Path(a.output).open('x') as f:f.write(s)
