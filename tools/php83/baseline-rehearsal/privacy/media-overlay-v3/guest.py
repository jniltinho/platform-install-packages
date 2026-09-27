"""Approved lab74 synthetic upload/READY/source delivery after finite privacy gates."""
from urllib.parse import urlsplit
import ast,hashlib,importlib.util,json,os,stat,re,secrets,socket,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
EXPECTED_OVERLAY_MANIFEST='cf16bc5c49acbe5863934ba737c72e2b65878c84048389354e79163afeca0cb8'
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
def bind_tenant(value,partner):
 need(type(value) is dict,'OWNED_OBJECT_SHAPE')
 actual=value.get('partnerId')
 need(type(actual) in {int,str} and str(actual)==str(partner),'OWNED_PARTNER_BINDING')
def bind_entry(value,partner,entry_id=None):
 bind_tenant(value,partner)
 need(type(value.get('id')) is str and (entry_id is None or value['id']==entry_id),'OWNED_ENTRY_BINDING')
def bind_asset(value,partner,entry_id):
 bind_tenant(value,partner)
 need(type(value.get('entryId')) is str and value['entryId']==entry_id,'OWNED_ASSET_ENTRY_BINDING')
def allowed_codes(module):
 return {n.value for n in ast.walk(ast.parse(Path(module.__file__).read_bytes())) if isinstance(n,ast.Constant) and type(n.value) is str and re.fullmatch('[A-Z_]+',n.value)}
def scanner_code(error,allowed):
 code=str(error);return code if code in allowed else 'UNKNOWN_SCANNER_CODE'
def private_json(path,data):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as out:json.dump(data,out);out.flush();os.fsync(out.fileno())
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
 media_window=None
 def checkpoint():print(json.dumps(report,sort_keys=True),flush=True)
 try:
  need(os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline','LAB_IDENTITY')
  rows=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10));ips={a.get('local') for x in rows for a in x.get('addr_info',[])}
  need('192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}),'LAB_IP')
  need(re.fullmatch('privacy-media-[0-9a-f]{8}',unit) is not None,'UNIT')
  policy=subprocess.check_output(['systemctl','show',unit+'.service','-p','IPAddressDeny','-p','IPAddressAllow','-p','NoNewPrivileges'],timeout=10).decode()
  network_policy(policy)
  sys.path.insert(0,str(HERE.parents[1]))
  legacy=__import__('untimed_driver') # Importable by multiprocessing spawn children.
  files=load('nonce_files',HERE.parent/'append-window-v1/scan.py')
  journal=load('nonce_journal',HERE.parent/'journal-window-v1/scan.py')
  overlay_root=Path('/home/vagrant/privacy-application-overlay-v4')
  raw=(overlay_root/'manifest.json').read_bytes()
  need(hashlib.sha256(raw).hexdigest()==EXPECTED_OVERLAY_MANIFEST,'OVERLAY_MANIFEST')
  manifest=json.loads(raw)
  for n,h in manifest['files'].items():need(hashlib.sha256((overlay_root/n).read_bytes()).hexdigest()==h,'OVERLAY_STAGE')
  overlay=load('nonce_overlay',overlay_root/'guest.py')
  parent=Path('/root/kaltura-baseline-private');info=parent.lstat()
  need(stat.S_ISDIR(info.st_mode) and info.st_uid==0 and not info.st_mode&0o077,'PRIVATE_DIAGNOSTIC_PARENT')
  private_dir=parent/unit;private_dir.mkdir(mode=0o700)
  audit_number=0;codes={'files':allowed_codes(files),'journal':allowed_codes(journal)}
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
   nonlocal audit_number
   audit_number+=1;number=audit_number
   private_json(private_dir/('boundary-'+str(number)+'.json'),{'file_marks':{p:vars(mark) for p,mark in start.items()},'journal':{'token':jstart.token,'boot':jstart.boot}})
   def scan(which,phase,operation):
    module=files if which=='files' else journal
    report['privacy_phase']=phase;checkpoint()
    try:return operation()
    except module.Incomplete as error:
     code=scanner_code(error,codes[which]);report.setdefault('privacy_errors',[]).append({'phase':phase,'code':code,'audit':number})
     try:after={p:vars(mark) for p,mark in files.snapshot(legacy.logs()).items()}
     except Exception:after=None
     private_json(private_dir/('failure-'+str(number)+'-'+phase+'.json'),{'phase':phase,'code':code,'current_file_marks':after})
     raise Rejected(which.upper()+'_'+code) from None
   f=scan('files','files_initial',lambda:files.scan_window(start,patterns,inventory=legacy.logs))
   j=scan('journal','journal',lambda:journal.scan_window(jstart,patterns))
   need(j.get('status')==JOURNAL_STATUS and j.get('cutoff_covered') is True,'JOURNAL_STATUS');j['complete']=True
   # Recheck the same file window after journal drain, without hiding any earlier hit.
   report['last_privacy_observation']={'files':f,'journal':j};checkpoint()
   accepted(f,j)
   f_after=scan('files','files_after_journal',lambda:files.scan_window(start,patterns,inventory=legacy.logs))
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
  ks=call(service='session',action='start',partnerId=partner,userId=user,type=0,expiry=1200,secret=secret)
  need(type(ks) is str and 20<=len(ks)<=8192,'USER_KS')
  denied=call(service='session',action='start',partnerId=partner,userId=user,type=2,expiry=60,secret=secret)
  need(type(denied) is dict and denied.get('objectType')=='KalturaAPIException' and denied.get('code')=='START_SESSION_ERROR','ADMIN_ESCALATION_CONTROL')
  report['user_privacy']=audit([secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()],start,jstart)
  report['user_session_accepted']=True;report['admin_escalation_rejected']=True;checkpoint()
  source=Path('/home/vagrant/privacy-media-overlay-v3/short360.mp4');raw=source.read_bytes()
  need(len(raw)<=2*1024*1024 and hashlib.sha256(raw).hexdigest()==legacy.SOURCE_PIN,'MEDIA_SOURCE_PIN')
  report['source_sha256']=legacy.SOURCE_PIN
  start=files.snapshot(legacy.logs());jstart=journal.snapshot()
  def value(service,action,**params):return legacy.api_value(call(service=service,action=action,**params))
  media_window=(start,jstart)
  report['phase']='upload';report['upload_attempted']=True;checkpoint()
  token=value('uploadtoken','add',ks=ks);token_id=token.get('id') if type(token) is dict else None
  need(type(token_id) is str and re.fullmatch('[A-Za-z0-9_-]{1,128}',token_id) is not None,'UPLOAD_TOKEN')
  reply=legacy.deadline._bounded(legacy._upload_worker,({'service':'uploadtoken','action':'upload','format':1,'ks':ks,'uploadTokenId':token_id,'resume':0,'finalChunk':1,'resumeAt':-1},raw,secrets.token_hex(16)),limit=1024*1024,deadline=30)
  legacy.api_value(legacy.strict_json(reply))
  tag='privacy-media-'+secrets.token_hex(16)
  entry=value('media','add',ks=ks,**{'entry:objectType':'KalturaMediaEntry','entry:name':tag+'-short360','entry:tags':tag,'entry:referenceId':tag,'entry:mediaType':1})
  bind_entry(entry,partner)
  entry_id=legacy.media_projection(entry)['id'];report['owned_entry_id']=entry_id;checkpoint()
  attached=value('media','addContent',ks=ks,entryId=entry_id,**{'resource:objectType':'KalturaUploadedFileTokenResource','resource:token':token_id});bind_entry(attached,partner,entry_id)
  report['phase']='ready-poll';until=time.monotonic()+600;polls=0;checkpoint()
  while True:
   entry=value('media','get',ks=ks,entryId=entry_id,version=-1);polls+=1
   bind_entry(entry,partner,entry_id)
   if str(entry.get('status'))=='2':break
   need(time.monotonic()<until and str(entry.get('status')) not in ['-1','-2','3'],'READY_NOT_REACHED')
   time.sleep(2)
  report['ready_poll_count']=polls;report['media_projection']=legacy.media_projection(entry);report['phase']='source-binding';checkpoint()
  assets=value('flavorasset','getByEntryId',ks=ks,entryId=entry_id)
  need(type(assets) is list and all(type(a) is dict for a in assets),'ASSET_LIST')
  originals=[a for a in assets if type(a.get('isOriginal')) in {bool,int,str} and a.get('isOriginal') in [True,1,'1']];need(len(originals)==1,'ORIGINAL_ASSET_COUNT')
  asset=originals[0];bind_asset(asset,partner,entry_id);asset_id=asset.get('id');version=str(asset.get('version'))
  need(type(asset_id) is str and legacy.ID.fullmatch(asset_id) is not None and version.isdigit(),'ASSET_VERSION')
  rows=legacy.sql("SELECT id,partner_id,object_id,version,file_root,file_path,status FROM file_sync WHERE object_type=4 AND object_sub_type=1 AND file_type=1 AND status=2 AND partner_id="+str(partner)+" AND object_id='"+asset_id+"' AND version='"+version+"'")
  candidates=[]
  for row in rows:
   try:candidates.append(legacy.owned_storage(row,partner,asset_id,version))
   except legacy.Failed:continue
  need(len(candidates)==1,'LOCAL_SOURCE_BINDING');stored,sync_id=candidates[0]
  need(legacy.checksum(stored)==legacy.SOURCE_PIN,'STORED_SOURCE_BYTES')
  report.update(original_asset_id=asset_id,asset_version=version,file_sync_id=sync_id,stored_source_sha256=legacy.SOURCE_PIN)
  listing=value('media','list',ks=ks,**{'filter:objectType':'KalturaMediaEntryFilter','filter:idEqual':entry_id,'filter:orderBy':'+createdAt','pager:objectType':'KalturaFilterPager','pager:pageSize':1,'pager:pageIndex':1})
  need(type(listing) is dict and type(listing.get('objects')) is list and len(listing['objects'])==1 and str(listing.get('totalCount'))=='1','OWNED_LIST')
  need(legacy.typed_equal(legacy.media_projection(listing['objects'][0]),report['media_projection']),'LIST_IDENTITY')
  report['owned_list_passed']=True;report['phase']='source-http-delivery';checkpoint()
  url=value('flavorasset','getUrl',ks=ks,id=asset_id)
  need(type(url) is str,'PLAYBACK_URL_SHAPE')
  legacy.Origin('192.168.56.74','http',80).validate(url)
  need(not urlsplit(url).query and '/ks/' not in url.lower() and secret not in url and ks not in url,'PLAYBACK_URL_PRIVACY')
  delivered=legacy.deadline.get(legacy.Origin('192.168.56.74','http',80),url,limit=2*1024*1024,deadline=30)
  need(hashlib.sha256(delivered).hexdigest()==legacy.SOURCE_PIN,'HTTP_SOURCE_BYTES')
  report['http_source_delivery_sha256']=legacy.SOURCE_PIN
  report['media_privacy']=audit([secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()],start,jstart)
  need(legacy.checksum(stored)==legacy.SOURCE_PIN and legacy.checksum(source)==legacy.SOURCE_PIN,'SOURCE_AFTER')
  report['sources_after']=overlay.source_state(manifest['after']);report['status']='SYNTHETIC_MEDIA_READY_AND_SOURCE_DELIVERY_OBSERVED';report['phase']='done'

 except Exception as error:
  # Only bounded fixed codes; no repr/value/credential or arbitrary backend error text.
  code=str(error);report['failure_code']=code if (isinstance(error,Rejected) or type(error).__name__=='Failed') and re.fullmatch('[A-Z0-9_]{1,100}',code) else type(error).__name__
  report['status']='FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION'
  if media_window is not None:
   try:report['media_failure_privacy']=audit([secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()],*media_window)
   except Exception as scan_error:report['media_privacy_failure_class']=type(scan_error).__name__
 checkpoint();return 0 if report['status']=='SYNTHETIC_MEDIA_READY_AND_SOURCE_DELIVERY_OBSERVED' else 2
if __name__=='__main__':sys.exit(main(sys.argv[1]))
