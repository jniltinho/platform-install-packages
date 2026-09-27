"""Fresh synthetic lab74 nonce then USER only after finite privacy gates; no media writes."""
import hashlib,importlib.util,json,os,re,secrets,socket,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
EXPECTED_OVERLAY_MANIFEST='66253ff6864b228914962a04ec912b422d4425e0744a8e62f7ecd6fc15b84224'
JOURNAL_STATUS="COMPLETE_FINITE_JOURNAL_WINDOW"
class Rejected(RuntimeError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def network_policy(raw):
 values={}
 for line in raw.splitlines():
  key,value=line.split('=',1);need(key not in values,'DUPLICATE_NETWORK_PROPERTY');values[key]=value
 need(values.get('NoNewPrivileges')=='yes','NETWORK_POLICY')
 need(set(values.get('IPAddressDeny','').split())=={'0.0.0.0/0','::/0'},'NETWORK_POLICY')
 need(set(values.get('IPAddressAllow','').split())=={'127.0.0.0/8','::1/128','192.168.56.74/32'},'NETWORK_POLICY')
def accepted(a,b):
 for row in [a,b]:
  need(type(row) is dict and type(row.get('counts')) is list and len(row['counts'])>=2,'SCAN_RESULT')
  need(all(type(v) is int and v==0 for v in row['counts']),'PRIVATE_MARKER_LOGGED')
 need(a.get('status')=='COMPLETE_FINITE_FILE_WINDOW' and type(a.get('uncovered_tail_bytes')) is int and a['uncovered_tail_bytes']==0,'FILE_WINDOW_INCOMPLETE')
 # Journal status is checked by its authoritative scanner; completion flag is supplied by adapter below.
 need(b.get('complete') is True,'JOURNAL_WINDOW_INCOMPLETE')
 return True
def main(unit):
 report={'status':'INCOMPLETE','phase':'preflight','baseline_label':'PUBLISHED_PHP74_WITH_APPROVED_PRIVACY_OVERLAY','benchmark_executed':False,'user_attempted':False,'upload_attempted':False,'universal_privacy':False}
 def checkpoint():print(json.dumps(report,sort_keys=True),flush=True)
 try:
  need(os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline','LAB_IDENTITY')
  rows=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10));ips={a.get('local') for x in rows for a in x.get('addr_info',[])}
  need('192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}),'LAB_IP')
  need(re.fullmatch('privacy-nonce-[0-9a-f]{8}',unit) is not None,'UNIT')
  policy=subprocess.check_output(['systemctl','show',unit+'.service','-p','IPAddressDeny','-p','IPAddressAllow','-p','NoNewPrivileges'],timeout=10).decode()
  network_policy(policy)
  legacy=load('nonce_legacy',HERE.parents[1]/'untimed_driver.py')
  files=load('nonce_files',HERE.parent/'append-window-v1/scan.py')
  journal=load('nonce_journal',HERE.parent/'journal-window-v1/scan.py')
  overlay_root=Path('/home/vagrant/privacy-application-overlay-v3')
  raw=(overlay_root/'manifest.json').read_bytes()
  need(hashlib.sha256(raw).hexdigest()==EXPECTED_OVERLAY_MANIFEST,'OVERLAY_MANIFEST')
  manifest=json.loads(raw)
  for n,h in manifest['files'].items():need(hashlib.sha256((overlay_root/n).read_bytes()).hexdigest()==h,'OVERLAY_STAGE')
  overlay=load('nonce_overlay',overlay_root/'guest.py')
  private_before=legacy.logging_preflight();config_before=overlay.audits()[1]
  source_before=overlay.source_state(manifest['after']);report['sources_before']=source_before
  for p,h in manifest['modules'].items():need(overlay.digest(p)==h,'RUNTIME_PIN')
  report['phase']='web-provider'
  provider=legacy.probe(secrets.token_hex(16));provider.pop('nonce',None)
  report['provider']=provider;report['provider_probe_removed']=True;checkpoint()
  state=Path('/root/kaltura-sanity.rc').read_text();match=re.fullmatch(r'PARTNER_ID=([1-9][0-9]*)\s*',state)
  need(match is not None,'SYNTHETIC_PARTNER_STATE');partner=int(match[1])
  # No credential read until wrong-secret logging gate succeeds.
  user='privacy-'+secrets.token_hex(16);canary='invalid-'+secrets.token_hex(24)+'-secret-marker'
  def call(**params):return legacy.PostTransport(legacy.Origin('192.168.56.74','http',80)).request(dict(format=1,**params)).value
  def audit(patterns,start,jstart):
   f=files.scan_window(start,patterns,inventory=legacy.logs)
   j=journal.scan_window(jstart,patterns)
   need(j.get('status')==JOURNAL_STATUS and j.get('cutoff_covered') is True,'JOURNAL_STATUS');j['complete']=True
   # Recheck the same file window after journal drain, without hiding any earlier hit.
   report['last_privacy_observation']={'files':f,'journal':j};checkpoint()
   accepted(f,j)
   f_after=files.scan_window(start,patterns,inventory=legacy.logs)
   report['last_privacy_observation']['files_after_journal']=f_after
   need(f_after['end_offsets']==f['end_offsets'],'FILE_TAIL_DURING_JOURNAL')
   f=f_after
   need(len(f.get('counts',[]))==len(patterns) and len(j.get('counts',[]))==len(patterns),'PATTERN_COUNT')
   accepted(f,j)
   need(legacy.logging_preflight()==private_before and overlay.audits()[1]==config_before,'CONFIG_DRIFT')
   need(overlay.source_state(manifest['after'])==source_before,'SOURCE_DRIFT')
   for p,h in manifest['modules'].items():need(overlay.digest(p)==h,'RUNTIME_PIN')
   return {'files':f,'journal':j,'scope':'finite phase only; no history or future-write claim'}
  report['phase']='invalid-nonce';start=files.snapshot(legacy.logs());jstart=journal.snapshot()
  value=call(service='session',action='start',partnerId=partner,userId=user,type=0,expiry=60,secret=canary)
  need(type(value) is dict and value.get('objectType')=='KalturaAPIException' and value.get('code')=='START_SESSION_ERROR','WRONG_SECRET_CONTROL')
  report['invalid_nonce']=audit([canary.encode(),canary[:15].encode()],start,jstart)
  report['wrong_secret_rejected']=True;checkpoint()
  report['phase']='synthetic-user'
  rows=legacy.sql('SELECT id,admin_email,secret FROM partner WHERE id='+str(partner))
  need(len(rows)==1 and len(rows[0])==3 and rows[0][0]==str(partner) and rows[0][1]=='sanity@kaltura.local','SYNTHETIC_PARTNER_PROVENANCE')
  secret=rows[0][2];need(re.fullmatch(r'[A-Za-z0-9_+/=-]{16,4096}',secret) is not None,'PRIVATE_SECRET_FORMAT')
  start=files.snapshot(legacy.logs());jstart=journal.snapshot();report['user_attempted']=True;checkpoint()
  ks=call(service='session',action='start',partnerId=partner,userId=user,type=0,expiry=120,secret=secret)
  need(type(ks) is str and 20<=len(ks)<=8192,'USER_KS')
  denied=call(service='session',action='start',partnerId=partner,userId=user,type=2,expiry=60,secret=secret)
  need(type(denied) is dict and denied.get('objectType')=='KalturaAPIException' and denied.get('code')=='START_SESSION_ERROR','ADMIN_ESCALATION_CONTROL')
  report['user_privacy']=audit([secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()],start,jstart)
  report['sources_after']=overlay.source_state(manifest['after'])
  report['user_session_accepted']=True;report['admin_escalation_rejected']=True
  report['status']='SYNTHETIC_USER_FINITE_PRIVACY_GATE_PASSED';report['phase']='done'
 except Exception as error:
  # Only bounded fixed codes; no repr/value/credential or arbitrary backend error text.
  code=str(error);report['failure_code']=code if isinstance(error,Rejected) and re.fullmatch('[A-Z_]{1,64}',code) else type(error).__name__
  report['status']='FAILED_OR_INCOMPLETE_NO_MEDIA'
 checkpoint();return 0 if report['status']=='SYNTHETIC_USER_FINITE_PRIVACY_GATE_PASSED' else 2
if __name__=='__main__':sys.exit(main(sys.argv[1]))
