"""R4 thumbnail workload: prepare_thumbnail_r3.build() with thumbnail_r4.py; r1-r3 guests and receipts stay frozen."""
from pathlib import Path
import hashlib
import prepare_thumbnail_r3 as r3
H=Path(__file__).parent
R3_GUEST='07c761a2358cf77c8a32e5c56ba0468ee32a135412e9391f6c8476ad78871236'
def build():
 assert hashlib.sha256((H/'guest_thumbnail_r3.py').read_bytes()).hexdigest()==R3_GUEST
 s=r3.build();assert hashlib.sha256(s.encode()).hexdigest()==R3_GUEST
 h=lambda n:hashlib.sha256((H/n).read_bytes()).hexdigest()
 for a,b in [("'thumbnail_r3.py': '%s'"%h('thumbnail_r3.py'),"'thumbnail_r4.py': '%s'"%h('thumbnail_r4.py')),("thumb=load('thumbnail_r3',NEW_HERE/'thumbnail_r3.py')","thumb=load('thumbnail_r4',NEW_HERE/'thumbnail_r4.py')")]:
  assert s.count(a)==1;s=s.replace(a,b)
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 s=build()
 with Path(a.output).open('x') as f:f.write(s)
