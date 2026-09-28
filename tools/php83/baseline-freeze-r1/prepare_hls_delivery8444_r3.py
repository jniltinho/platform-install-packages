"""Versioned optional source-proven timed-ID3 stream, never arbitrary OTHER."""
from pathlib import Path
import hashlib
H=Path(__file__).parent
MODULES=['decode_diagnostic_r3.py','hls_decode_r3.py','hls_delivery8444_r3.py']
def build():
 raw=(H/'guest_hls_delivery8444_r2.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='e00d85dd59c3014325b18f214b5ee27d098194a6392db6aa44725b1ba8d024cc';s=raw.decode()
 old="  hls=load('hls_delivery8444_r2',NEW_HERE/'hls_delivery8444_r2.py')"
 new='  for name,pin in '+repr({n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in MODULES})+".items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'HLS_PIN')\n  hls=load('hls_delivery8444_r3',NEW_HERE/'hls_delivery8444_r3.py')"
 assert s.count(old)==1;return s.replace(old,new)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
