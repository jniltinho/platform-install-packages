"""Decision 7 lab profile creation workload (operator-authorized admin KS, 2026-09-29): guest_long_ready_r1
(Sphinx full-content + in-window new-log privacy) with the phase-B block replaced by lab_profile.setup() under an
admin KS. The partner-102 admin secret is read in-guest only, never exported; it and the admin KS are tracked
(full + 15-char prefix) in every batch audit and added to MEDIA_PRIVACY before first use."""
from pathlib import Path
import hashlib
import prepare_long_ready_r1 as base
import lab_profile
H=Path(__file__).parent
BASE_GUEST='75a360064d80409ab8725a5db7e40a88a0cfec7f4c168078bd33ff714529bb0e'
def build():
 assert hashlib.sha256((H/'guest_long_ready_r1.py').read_bytes()).hexdigest()==BASE_GUEST
 s=base.build();assert hashlib.sha256(s.encode()).hexdigest()==BASE_GUEST
 pin=hashlib.sha256((H/'lab_profile.py').read_bytes()).hexdigest()
 a=s.index("  report['phase']='long-ready-phase-b';failure_stage='API_ROUND'\n");b=s.index("  failure_stage='QUIET_SETTLE'\n",a)
 block=("  report['phase']='lab-profile-decision7';failure_stage='API_ROUND'\n"
  "  need(hashlib.sha256((NEW_HERE/'lab_profile.py').read_bytes()).hexdigest()=="+repr(pin)+",'LAB_PROFILE_PIN')\n"
  "  labp=load('lab_profile',NEW_HERE/'lab_profile.py')\n"
  "  rows=legacy.sql('SELECT admin_secret FROM partner WHERE id=102')\n"
  "  need(len(rows)==1 and len(rows[0])==1,'ADMIN_SECRET_PROVENANCE');admin_secret=rows[0][0]\n"
  "  need(re.fullmatch(r'[A-Za-z0-9_+/=-]{16,4096}',admin_secret) is not None and admin_secret!=secret,'PRIVATE_SECRET_FORMAT')\n"
  "  tracked_tokens.append(admin_secret) # tracked before first use: every later batch audit covers it\n"
  "  admin_ks=call(service='session',action='start',partnerId=102,userId=user,type=2,expiry=600,secret=admin_secret)\n"
  "  need(type(admin_ks) is str and 20<=len(admin_ks)<=8192,'ADMIN_KS');tracked_tokens.append(admin_ks)\n"
  "  admin_patterns=[admin_secret.encode(),admin_secret[:15].encode(),admin_ks.encode(),admin_ks[:15].encode()]\n"
  "  def lab_progress(value):report['lab_profile_progress']=value\n"
  "  try:report['lab_profile']=labp.setup(lambda s,a,**f:call(service=s,action=a,**f),admin_ks,progress=lab_progress)\n"
  "  except labp.Rejected as error:raise Rejected(str(error)) from None\n")
 s=s[:a]+block+s[b:]
 edits=[
  ("  report['media_privacy']=audit([secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()],start,jstart)\n",
   "  report['media_privacy']=audit([secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()]+admin_patterns,start,jstart)\n"),
  ('\"\"\"FullHD60 phase B: read-only READY/flavor observation of the phase-A entry after finite privacy gates; no upload.\"\"\"',
   '\"\"\"Decision 7 lab profile: ONE admin-KS creation of a partner-102 1080p60 flavor params and lab profile; finite privacy gates.\"\"\"'),
  ("FIXED_FAILURE_CODES=","FIXED_FAILURE_CODES="+repr(list(lab_profile.CODES)+['LAB_PROFILE_PIN','ADMIN_SECRET_PROVENANCE','ADMIN_KS'])+'+'),
 ]
 for x,y in edits:
  assert s.count(x)==1,x;s=s.replace(x,y)
 return s
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 s=build()
 with Path(a.output).open('x') as f:f.write(s)
