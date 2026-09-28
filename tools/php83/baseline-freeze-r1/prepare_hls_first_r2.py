"""Closed manifest failure diagnostics only; same transport/parser/request count."""
from pathlib import Path
import hashlib
H=Path(__file__).parent
def build():
 raw=(H/'guest_hls_first.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='453af48e64cd98f36e8302dc5970cebe07229b2fe0257c1db4bbe21f1fc95d16';s=raw.decode()
 s=s.replace('hls_first.py','hls_first_r2.py').replace(hashlib.sha256((H/'hls_first.py').read_bytes()).hexdigest(),hashlib.sha256((H/'hls_first_r2.py').read_bytes()).hexdigest())
 anchor="  first=load('hls_first',NEW_HERE/'hls_first_r2.py')"
 s=s.replace(anchor,"  need(hashlib.sha256((NEW_HERE/'manifest_diagnostic.py').read_bytes()).hexdigest()=="+repr(hashlib.sha256((H/'manifest_diagnostic.py').read_bytes()).hexdigest())+",'HLS_PIN')\n"+anchor)
 s=s.replace("  def described(row):report['hls_route']=row", "  def described(row):report['hls_route']=row\n  def diagnosed(row):report['hls_diagnostic']=row")
 s=s.replace('selected_context_asset,described)','selected_context_asset,described,diagnosed)')
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
