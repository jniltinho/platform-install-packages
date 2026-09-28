"""No-GET context-selected stored-profile observation."""
from pathlib import Path
import hashlib
H=Path(__file__).parent
def build():
 raw=(H/'guest_context_observer_r2.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='e717197ccbb7cd560230471c3ba8a4abdc58fb813adb772fc82ac01d370f4555';s=raw.decode()
 anchor='  def serve_source_guard():\n'
 s=s.replace(anchor,anchor+"   f=Path('/opt/kaltura/app/alpha/lib/model/om/BaseDeliveryProfilePeer.php');m=f.lstat();need(stat.S_ISREG(m.st_mode) and m.st_uid==0 and m.st_nlink==1 and m.st_size<=512*1024 and hashlib.sha256(f.read_bytes()).hexdigest()=='9805a9bf1c4d0fe721ff90673ec848b9732722f8e5f6df8e3a4bf44d928f75e0','ROUTE_SOURCE_PIN')\n")
 anchor="  try:report['playback_context']=context.observe("
 s=s.replace(anchor,"  captured_context=[]\n  def captured_call(**form):\n   response=call(ks=ks,**form);captured_context.append(response);return response\n"+anchor)
 s=s.replace('context.observe(lambda **form:call(ks=ks,**form),','context.observe(captured_call,')
 anchor="  failure_stage='QUIET_SETTLE'"
 extra="  need(hashlib.sha256((NEW_HERE/'delivery_profile_observation.py').read_bytes()).hexdigest()=="+repr(hashlib.sha256((H/'delivery_profile_observation.py').read_bytes()).hexdigest())+",'CONTEXT_PIN')\n  profile_observer=load('delivery_profile_observation',NEW_HERE/'delivery_profile_observation.py')\n  try:\n   need(len(captured_context)==1,'DELIVERY_PROFILE_OBSERVATION')\n   observed_profile=profile_observer.selected(captured_context[0])\n   report['delivery_profile']=profile_observer.parse(legacy.sql(profile_observer.query(observed_profile)),observed_profile)\n  except profile_observer.Rejected:raise Rejected('DELIVERY_PROFILE_OBSERVATION') from None\n  del captured_context\n"
 s=s.replace(anchor,extra+anchor,1).replace('FIXED_FAILURE_CODES=[',"FIXED_FAILURE_CODES=['DELIVERY_PROFILE_OBSERVATION',")
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 with Path(a.output).open('x') as f:f.write(build())
