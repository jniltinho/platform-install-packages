"""R2 thumbnail workload: prepare_thumbnail.build() with thumbnail_r2.py; r1 guest/receipt stay frozen."""
from pathlib import Path
import hashlib
import prepare_thumbnail as r1
H=Path(__file__).parent
R1_GUEST='6761fc5a0b4aad5f979d52fd1eb49f6c86988f0c82a39ca0c4a4e3abb23bd9b9'
def build():
 assert hashlib.sha256((H/'guest_thumbnail.py').read_bytes()).hexdigest()==R1_GUEST
 s=r1.build();assert hashlib.sha256(s.encode()).hexdigest()==R1_GUEST
 old_pins=repr({n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in r1.MODULES})
 new_pins=repr({n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in ('thumbnail_r2.py','thumbnail_decode.py')})
 for a,b in [(old_pins,new_pins),("thumb=load('thumbnail',NEW_HERE/'thumbnail.py')","thumb=load('thumbnail_r2',NEW_HERE/'thumbnail_r2.py')")]:
  assert s.count(a)==1;s=s.replace(a,b)
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
