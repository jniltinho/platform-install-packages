"""FullHD60 phase B r3: the reviewed guest_long_ready_r1 with long_ready.py swapped for long_ready_r2.py
(profile-15 entry 0_3h92ab2l, params 118). Read-only; no mutation."""
from pathlib import Path
import hashlib
import prepare_long_ready_r1 as base
H=Path(__file__).parent
BASE_GUEST='75a360064d80409ab8725a5db7e40a88a0cfec7f4c168078bd33ff714529bb0e'
def build():
 assert hashlib.sha256((H/'guest_long_ready_r1.py').read_bytes()).hexdigest()==BASE_GUEST
 s=base.build();assert hashlib.sha256(s.encode()).hexdigest()==BASE_GUEST
 h=lambda n:hashlib.sha256((H/n).read_bytes()).hexdigest()
 for a,b in [("(NEW_HERE/'long_ready.py').read_bytes()).hexdigest()=="+repr(h('long_ready.py')),"(NEW_HERE/'long_ready_r2.py').read_bytes()).hexdigest()=="+repr(h('long_ready_r2.py'))),
  ("longready=load('long_ready',NEW_HERE/'long_ready.py')","longready=load('long_ready_r2',NEW_HERE/'long_ready_r2.py')"),
  ('\"\"\"FullHD60 phase B: read-only READY/flavor observation of the phase-A entry','\"\"\"FullHD60 phase B r3 (profile 15 entry): read-only READY/flavor observation of the phase-A entry')]:
  assert s.count(a)==1,a;s=s.replace(a,b)
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 s=build()
 with Path(a.output).open('x') as f:f.write(s)
