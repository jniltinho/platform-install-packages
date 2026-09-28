"""Reference descriptors before unchanged origin rejection, no nested requests."""
from pathlib import Path
import hashlib
H=Path(__file__).parent
def build():
 raw=(H/'guest_hls_first_r2.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='357d463c14164a5a9647d34582820bed773d703d48e3e6a5f0496722bd17e231';s=raw.decode()
 s=s.replace('hls_first_r2.py','hls_first_r3.py').replace(hashlib.sha256((H/'hls_first_r2.py').read_bytes()).hexdigest(),hashlib.sha256((H/'hls_first_r3.py').read_bytes()).hexdigest())
 anchor="  first=load('hls_first',NEW_HERE/'hls_first_r3.py')"
 s=s.replace(anchor,"  need(hashlib.sha256((NEW_HERE/'nested_descriptor.py').read_bytes()).hexdigest()=="+repr(hashlib.sha256((H/'nested_descriptor.py').read_bytes()).hexdigest())+",'HLS_PIN')\n"+anchor)
 s=s.replace("  def diagnosed(row):report['hls_diagnostic']=row","  def diagnosed(row):report['hls_diagnostic']=row\n  def nested(row):report['hls_nested']=row")
 s=s.replace('selected_context_asset,described,diagnosed)','selected_context_asset,described,diagnosed,nested)')
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
