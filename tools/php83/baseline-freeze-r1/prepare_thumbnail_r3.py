"""R3 thumbnail workload: prepare_thumbnail_r2.build() with thumbnail_r3.py; r1/r2 guests and receipts stay frozen."""
from pathlib import Path
import hashlib
import prepare_thumbnail_r2 as r2
H=Path(__file__).parent
R2_GUEST='b7ba358be2855a27307765ab5b1e9866ddbcd1e50a0390bcc8907a48258c17df'
def build():
 assert hashlib.sha256((H/'guest_thumbnail_r2.py').read_bytes()).hexdigest()==R2_GUEST
 s=r2.build();assert hashlib.sha256(s.encode()).hexdigest()==R2_GUEST
 h=lambda n:hashlib.sha256((H/n).read_bytes()).hexdigest()
 for a,b in [("'thumbnail_r2.py': '%s'"%h('thumbnail_r2.py'),"'thumbnail_r3.py': '%s'"%h('thumbnail_r3.py')),("thumb=load('thumbnail_r2',NEW_HERE/'thumbnail_r2.py')","thumb=load('thumbnail_r3',NEW_HERE/'thumbnail_r3.py')")]:
  assert s.count(a)==1;s=s.replace(a,b)
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
