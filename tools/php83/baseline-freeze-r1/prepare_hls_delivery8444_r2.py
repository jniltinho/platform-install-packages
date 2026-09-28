"""Retain exact decoder predicates; add closed facts before metadata rejection."""
from pathlib import Path
import hashlib
H=Path(__file__).parent
MODULES=['hls_decode_r2.py','hls_delivery8444_r2.py','decode_diagnostic.py']
def build():
 raw=(H/'guest_hls_delivery8444.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='6ad49706944501fb9bc0784c611e362788d0aa683cbfc941f0ee2d734e969d13';s=raw.decode()
 old="  hls=load('hls_delivery8444',NEW_HERE/'hls_delivery8444.py')"
 new='  for name,pin in '+repr({n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in MODULES})+".items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'HLS_PIN')\n  hls=load('hls_delivery8444_r2',NEW_HERE/'hls_delivery8444_r2.py')"
 assert s.count(old)==1;return s.replace(old,new)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
