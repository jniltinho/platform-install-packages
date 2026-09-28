"""Produce reviewed one-round derivative from frozen V2 observer; no execution."""
import argparse,hashlib
from pathlib import Path
H=Path(__file__).parent;raw=(H/'guest_v2.py').read_bytes();assert hashlib.sha256(raw).hexdigest()=='6eaaf54dd2365eb8093952631234fed1711badd607976c0e6b39115f0a6994f8'
s=raw.decode().replace('media_window=None','media_window=None;tracked_tokens=[]')
s=s.replace("def checkpoint():print(json.dumps(report,sort_keys=True),flush=True)","def checkpoint():print(json.dumps(report if report.get('phase')=='done' or report.get('status')=='FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION' else {'status':'INCOMPLETE'},sort_keys=True),flush=True)")
a="  sys.path.insert(0,str(HERE.parents[1]))"
pins={n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in ('protocol_v2.py','rehearsal.py')}
s=s.replace(a,"  for name,pin in "+repr(pins)+".items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'REHEARSAL_PIN')\n  sys.path.insert(0,str(NEW_HERE))\n"+a)
a="  source=Path('/home/vagrant/privacy-media-overlay-v3/short360.mp4')"
s=s.replace(a,"  rehearsal=load('baseline_rehearsal_v2',NEW_HERE/'rehearsal.py')\n"+a)
anchor="  report['phase']='invalid-nonce';"
fn="""  def audit_all(batches,start,jstart):
   cutoff=files.snapshot(legacy.logs());jcut=journal.snapshot()
   expected_offsets={p:m.size for p,m in cutoff.items()}
   results=[audit(batch,start,jstart) for batch in batches]
   need(files.snapshot(legacy.logs())==cutoff and journal.snapshot()==jcut,'COMMON_AUDIT_END_DRIFT')
   need(all(r['files']['end_offsets']==expected_offsets for r in results),'COMMON_AUDIT_END_DRIFT')
   return {'common_end_verified':True,'pattern_count':sum(map(len,batches)),'batches':results}
"""
s=s.replace(anchor,fn+anchor)
a="  report['media_privacy']=audit([secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()],start,jstart)"
block="""  report['phase']='untimed-protocol-rehearsal'
  tracked=rehearsal.TrackedTransport(legacy.PostTransport(legacy.Origin('192.168.56.74','http',80)),tracked_tokens)
  credentials=rehearsal.protocol.Credentials(partner,user,secret)
  report['untimed_round']=rehearsal.validate_round(rehearsal.protocol.run_round(tracked,credentials,report['fixture']))
  report['round_token_count']=len(tracked_tokens)
"""+a+"""
  report['round_privacy']=audit_all(rehearsal.patterns(secret,ks,tracked_tokens),start,jstart)
  need(report['untimed_round']['functional_round_pass'],'UNTIMED_ROUND_FAILED')"""
s=s.replace(a,block)
a="   try:report['media_failure_privacy']=audit([v for v in [secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()] if v],*media_window)"
s=s.replace(a,"   try:\n    if tracked_tokens:report['media_failure_privacy_batches']=audit_all(rehearsal.patterns(secret,ks,tracked_tokens),*media_window)\n    else:report['media_failure_privacy']=audit([v for v in [secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()] if v],*media_window)")
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
with Path(a.output).open('x') as f:f.write(s)
print(hashlib.sha256(s.encode()).hexdigest())
