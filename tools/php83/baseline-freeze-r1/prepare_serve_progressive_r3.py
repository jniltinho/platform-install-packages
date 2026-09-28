"""Only source-supported forceproxy=true pair and fixed failure-audit code."""
from pathlib import Path
import hashlib
H=Path(__file__).parent
SOURCE='/opt/kaltura/app/alpha/lib/model/DeliveryProfileAkamaiHttp.php'
SOURCE_PIN='116ebbe16200e83e16e008f3aea610b7e9ae2a012704f7796068926e447ad2b9'
def build():
 raw=(H/'guest_serve_progressive_r2.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='09e5ddba62d5ae9815724028afc25d017e865eaf1be09fe05a833b07842fae9e';s=raw.decode()
 old=hashlib.sha256((H/'serve_flavor_guard.py').read_bytes()).hexdigest();new=hashlib.sha256((H/'serve_flavor_guard_r2.py').read_bytes()).hexdigest()
 s=s.replace('serve_flavor_guard.py','serve_flavor_guard_r2.py').replace(old,new)
 anchor='  def serve_source_guard():\n'
 s=s.replace(anchor,anchor+'   f=Path('+repr(SOURCE)+');m=f.lstat();need(stat.S_ISREG(m.st_mode) and m.st_uid==0 and m.st_nlink==1 and m.st_size<=512*1024 and hashlib.sha256(f.read_bytes()).hexdigest()=='+repr(SOURCE_PIN)+",'ROUTE_SOURCE_PIN')\n")
 s=s.replace("   except Exception as scan_error:report['media_privacy_failure_class']='FINITE_SCAN_INCOMPLETE'", "   except Exception as scan_error:\n    report['media_privacy_failure_class']='FINITE_SCAN_INCOMPLETE'\n    report['media_privacy_failure_code']=str(scan_error) if type(scan_error) is Rejected and str(scan_error) in FIXED_FAILURE_CODES else 'UNEXPECTED_OR_DEPENDENCY_FAILURE'")
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
