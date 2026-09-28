"""One source-supported transcoded HLS context; no GET/repeated workload."""
from pathlib import Path
import hashlib
H=Path(__file__).parent
CODES=['SELECTED_ASSET','SELECTED_SIZE','SELECTED_TAGS']
def build():
 raw=(H/'guest_context_observer.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='32c4e5027839ba176c11d16850c8d48a815928f43a5c3f9023813021747df363';s=raw.decode()
 old=hashlib.sha256((H/'playback_context_r3.py').read_bytes()).hexdigest();s=s.replace('playback_context_r3.py','playback_context_r4.py').replace(old,hashlib.sha256((H/'playback_context_r4.py').read_bytes()).hexdigest())
 anchor="  try:report['playback_context']=context.observe("
 pins={n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in ('context_selected.py','short_metadata.py')}
 s=s.replace(anchor,"  for name,pin in "+repr(pins)+".items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'CONTEXT_PIN')\n  selection=load('context_selected',NEW_HERE/'context_selected.py')\n  try:selected_context_asset=selection.select(assets)\n  except selection.Rejected as error:raise Rejected(str(error) if str(error) in ('SELECTED_ASSET','SELECTED_TAGS') else 'SELECTED_ASSET') from None\n"+anchor)
 s=s.replace('lambda url:enrollment.enroll(url,tracked_tokens))','lambda url:enrollment.enroll(url,tracked_tokens),selected_context_asset)')
 s=s.replace("'CONTEXT_ARRAY', 'CONTEXT_PIN'] else", "'CONTEXT_ARRAY', 'CONTEXT_PIN', 'SELECTED_ASSET','SELECTED_SIZE','SELECTED_TAGS'] else")
 s=s.replace('FIXED_FAILURE_CODES=[','FIXED_FAILURE_CODES=['+repr(CODES)[1:-1]+',')
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
