"""Read-only existing lab74 media observation after finite privacy gates; no upload."""
from urllib.parse import urlsplit
import ast,hashlib,importlib.util,json,os,stat,re,secrets,socket,subprocess,sys,time
from pathlib import Path
NEW_HERE=Path(__file__).resolve().parent
HERE=Path('/home/vagrant/privacy-media-overlay-v3/tools/php83/baseline-rehearsal/privacy/media-overlay-v3')
EXPECTED_OVERLAY_MANIFEST='cf16bc5c49acbe5863934ba737c72e2b65878c84048389354e79163afeca0cb8'
JOURNAL_STATUS="COMPLETE_FINITE_JOURNAL_WINDOW"
FIXED_FAILURE_CODES=['TLS_LOG_ADAPTER_PIN','TLS_CA_PIN','ADMIN_ESCALATION_CONTROL', 'CLI_VERSION', 'COMMON_AUDIT_END_DRIFT', 'CONFIG_DRIFT', 'DEPENDENCY_PIN', 'DUPLICATE_NETWORK_PROPERTY', 'ENTRY_DB_BINDING', 'EXACT_PRIOR_PARTNER', 'FILES_BOOT_CHANGED', 'FILES_BYTE_LIMIT', 'FILES_COMPLETE_FINITE_FILE_WINDOW', 'FILES_COMPLETE_FINITE_JOURNAL_WINDOW', 'FILES_CURSOR_CONTINUITY', 'FILES_DEADLINE', 'FILES_DUPLICATE_JSON_FIELD', 'FILES_EMPTY_JOURNAL', 'FILES_END_CURSOR_MISSING', 'FILES_IDENTITY_CHANGED', 'FILES_INVALID_JSON', 'FILES_INVENTORY', 'FILES_INVENTORY_CHANGED', 'FILES_JOURNAL_PROCESS', 'FILES_JOURNAL_STDERR', 'FILES_JOURNAL_TIMEOUT', 'FILES_LATEST_IDENTITY', 'FILES_LIMITS', 'FILES_OBSERVED_CURSOR_MISSING', 'FILES_OBSERVED_TAIL_MISSING', 'FILES_PATTERNS', 'FILES_RECORD_IDENTITY', 'FILES_RECORD_LIMIT', 'FILES_REWRITTEN', 'FILES_SCAN_FAILED', 'FILES_SHORT_READ', 'FILES_SNAPSHOT_FAILED', 'FILES_START', 'FILES_START_CURSOR_MISSING', 'FILES_SYMLINK', 'FILES_TAIL_REGRESSED', 'FILES_TRUNCATED', 'FILES_UNDRAINED_JOURNAL_TAIL', 'FILES_UNDRAINED_TAIL', 'FILES_UNSAFE_FILE', 'FILES_UNSAFE_PATH', 'FILES_UNSUPPORTED_FIELD', 'FILES__BOOT_ID', 'FILES___CURSOR', 'FILE_TAIL_DURING_JOURNAL', 'FILE_WINDOW_INCOMPLETE', 'JOURNAL_BOOT_CHANGED', 'JOURNAL_BYTE_LIMIT', 'JOURNAL_COMPLETE_FINITE_FILE_WINDOW', 'JOURNAL_COMPLETE_FINITE_JOURNAL_WINDOW', 'JOURNAL_CURSOR_CONTINUITY', 'JOURNAL_DEADLINE', 'JOURNAL_DUPLICATE_JSON_FIELD', 'JOURNAL_EMPTY_JOURNAL', 'JOURNAL_END_CURSOR_MISSING', 'JOURNAL_IDENTITY_CHANGED', 'JOURNAL_INVALID_JSON', 'JOURNAL_INVENTORY', 'JOURNAL_INVENTORY_CHANGED', 'JOURNAL_JOURNAL_PROCESS', 'JOURNAL_JOURNAL_STDERR', 'JOURNAL_JOURNAL_TIMEOUT', 'JOURNAL_LATEST_IDENTITY', 'JOURNAL_LIMITS', 'JOURNAL_OBSERVED_CURSOR_MISSING', 'JOURNAL_OBSERVED_TAIL_MISSING', 'JOURNAL_PATTERNS', 'JOURNAL_RECORD_IDENTITY', 'JOURNAL_RECORD_LIMIT', 'JOURNAL_REWRITTEN', 'JOURNAL_SCAN_FAILED', 'JOURNAL_SHORT_READ', 'JOURNAL_SNAPSHOT_FAILED', 'JOURNAL_START', 'JOURNAL_START_CURSOR_MISSING', 'JOURNAL_STATUS', 'JOURNAL_SYMLINK', 'JOURNAL_TAIL_REGRESSED', 'JOURNAL_TRUNCATED', 'JOURNAL_UNDRAINED_JOURNAL_TAIL', 'JOURNAL_UNDRAINED_TAIL', 'JOURNAL_UNSAFE_FILE', 'JOURNAL_UNSAFE_PATH', 'JOURNAL_UNSUPPORTED_FIELD', 'JOURNAL_WINDOW_INCOMPLETE', 'JOURNAL__BOOT_ID', 'JOURNAL___CURSOR', 'LAB_IDENTITY', 'LAB_IP', 'LIST_IDENTITY', 'LOCAL_SOURCE_BINDING', 'MEDIA_SOURCE_PIN', 'NETWORK_POLICY', 'OBSERVATION_PIN', 'OBSERVED_PROFILE_SELECTION', 'ORIGINAL_ASSET_COUNT', 'OVERLAY_MANIFEST', 'OVERLAY_STAGE', 'OWNED_ASSET_ENTRY_BINDING', 'OWNED_ENTRY_BINDING', 'OWNED_LIST', 'OWNED_OBJECT_SHAPE', 'OWNED_PARTNER_BINDING', 'PATTERN_COUNT', 'PRIOR_ASSET_IDENTITY', 'PRIVATE_DIAGNOSTIC_PARENT', 'PRIVATE_MARKER_LOGGED', 'PRIVATE_SECRET_FORMAT', 'QUIET_WINDOW_NOT_ESTABLISHED', 'REHEARSAL_PIN', 'RUNTIME_PIN', 'SCAN_RESULT', 'SETTLE_PIN', 'SOURCE_AFTER', 'SOURCE_DRIFT', 'STORED_SOURCE_BYTES', 'SYNTHETIC_PARTNER_PROVENANCE', 'SYNTHETIC_PARTNER_STATE', 'UNIT', 'UNTIMED_ROUND_FAILED', 'USER_KS', 'VERSION_PROJECTION', 'WRONG_SECRET_CONTROL']
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
 media_window=None;tracked_tokens=[];failure_stage='PREFLIGHT'
 def checkpoint():print(json.dumps(report if report.get('phase')=='done' or report.get('status')=='FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION' else {'status':'INCOMPLETE'},sort_keys=True),flush=True)
 try:
  need(os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline','LAB_IDENTITY')
  rows=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10));ips={a.get('local') for x in rows for a in x.get('addr_info',[])}
  need('192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}),'LAB_IP')
  need(re.fullmatch('baseline-freeze-[0-9a-f]{8}',unit) is not None,'UNIT')
  policy=subprocess.check_output(['systemctl','show',unit+'.service','-p','IPAddressDeny','-p','IPAddressAllow','-p','NoNewPrivileges'],timeout=10).decode()
  network_policy(policy)
  stage=Path('/home/vagrant/privacy-media-overlay-v3')
  frozen={'tools/php83/baseline-api/protocol.py': '4587eab6222c2cacc381b6ef100dc557f1afb814250dcc5ba92b3b2ee7eeca34', 'tools/php83/baseline-api/transport.py': '5a5896f22aeef0a8baf0ba3869b2cbfebcd655b94ab5671dc13580d1035edf20', 'tools/php83/baseline-protocol/deadline_transport.py': '330c7aedaa57c439af579b9fa9f262c1062bbd66014d3e4c0adbe9b8a6c1dbe2', 'tools/php83/baseline-protocol/guarded_http.py': '4cc44f15645ced42e1e156586a79a2795d38f929c6f812eb695e427ee7e47b59', 'tools/php83/baseline-rehearsal/privacy/append-window-v1/scan.py': '43189edbe0cfb9f4a0654b7b8425f8f4a876bf270a309f96309142a0ec5b34fc', 'tools/php83/baseline-rehearsal/privacy/journal-window-v1/scan.py': 'a390e2464c3df47b36ed0b2e19607887b908351d3e7245439e392646239ba5e8', 'tools/php83/baseline-rehearsal/privacy/media-overlay-v3/guest.py': '716786236935d53bbe513275b4cac71b4f9b42b67cf1615d50031d76789b6810', 'tools/php83/baseline-rehearsal/untimed_driver.py': 'b461835902bde19d3ec3ca555a88dac640176aa7318315d9cb4bee3d29df14b5'}
  for name,pin in frozen.items():
   p=stage/name;st=p.lstat();need(stat.S_ISREG(st.st_mode) and st.st_uid==0 and not st.st_mode&0o222 and hashlib.sha256(p.read_bytes()).hexdigest()==pin,'DEPENDENCY_PIN')
  obsraw=(NEW_HERE/'observation_v2.py').read_bytes();need(hashlib.sha256(obsraw).hexdigest()=='ec32386df1c745f5754ece19f3127f6da85415e644c8556e6c07666b2ea1abc5','OBSERVATION_PIN')
  obs=load('baseline_observation',NEW_HERE/'observation_v2.py')
  for name,pin in {'protocol_v2.py': '147d74b0a04779fd0819ebe210d8a1a6aea4af8fbc773683a278e540ce70d4b8', 'rehearsal.py': 'ccf78ba0b1d3c94f05f63fd2d87c351953022c149c0e75392b5c86be2c02bb70'}.items():need(hashlib.sha256((NEW_HERE/name).read_bytes()).hexdigest()==pin,'REHEARSAL_PIN')
  sys.path.insert(0,str(NEW_HERE))
  sys.path.insert(0,str(HERE.parents[1]))
  legacy=__import__('untimed_driver') # Importable by multiprocessing spawn children.
  need(hashlib.sha256((NEW_HERE/'privacy_logs_r2.py').read_bytes()).hexdigest()=='d67eb65900c3134c91efaf94b18ba482b59261c81b0084de0cea3bcd37d5246c','TLS_LOG_ADAPTER_PIN')
  tls_logs=load('baseline_tls_logs_r2',NEW_HERE/'privacy_logs_r2.py')
  old_logs=legacy.logs
  legacy.logs=lambda:tls_logs.extend(old_logs)
  legacy.logs() # Mandatory metadata inventory before any credential request/read.
  tls_ca=legacy.read_file(Path('/var/lib/kaltura-baseline-tls-r2/ca.crt'),16384,private=True)
  need(hashlib.sha256(tls_ca).hexdigest()=='5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef','TLS_CA_PIN')

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
  report['apache_runtime_current']='UNVERIFIED_NO_WEB_FILE_PROBE'
  report['cli_version']=subprocess.check_output(['/usr/bin/php','-n','-r','echo PHP_VERSION;'],timeout=10).decode()
  need(re.fullmatch(r'7\.4\.[0-9]+',report['cli_version']) is not None,'CLI_VERSION')
  state=Path('/root/kaltura-sanity.rc').read_text();match=re.fullmatch(r'PARTNER_ID=([1-9][0-9]*)\s*',state)
  need(match is not None,'SYNTHETIC_PARTNER_STATE');partner=int(match[1])
  # No credential read until wrong-secret logging gate succeeds.
  user='privacy-'+secrets.token_hex(16);canary='invalid-'+secrets.token_hex(24)+'-secret-marker'
  def call(**params):return legacy.PostTransport(legacy.Origin('192.168.56.74','https',8443),tls_ca,'5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef').request(dict(format=1,**params)).value
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
  def audit_all(batches,start,jstart):
   cutoff=files.snapshot(legacy.logs());jcut=journal.snapshot()
   expected_offsets={p:m.size for p,m in cutoff.items()}
   results=[audit(batch,start,jstart) for batch in batches]
   need(files.snapshot(legacy.logs())==cutoff and journal.snapshot()==jcut,'COMMON_AUDIT_END_DRIFT')
   need(all(r['files']['end_offsets']==expected_offsets for r in results),'COMMON_AUDIT_END_DRIFT')
   return {'common_end_verified':True,'pattern_count':sum(map(len,batches)),'batches':results}
  report['phase']='invalid-nonce';start=files.snapshot(legacy.logs());jstart=journal.snapshot()
  value=call(service='session',action='start',partnerId=partner,userId=user,type=0,expiry=60,secret=canary)
  need(type(value) is dict and value.get('objectType')=='KalturaAPIException' and value.get('code')=='START_SESSION_ERROR','WRONG_SECRET_CONTROL')
  report['invalid_nonce']=audit([canary.encode(),canary[:15].encode()],start,jstart)
  report['wrong_secret_rejected']=True;checkpoint()
  report['phase']='synthetic-user'
  rows=legacy.sql('SELECT id,admin_email,secret FROM partner WHERE id='+str(partner))
  need(len(rows)==1 and len(rows[0])==3 and rows[0][0]==str(partner) and rows[0][1]=='sanity@kaltura.local','SYNTHETIC_PARTNER_PROVENANCE')
  need(partner==102,'EXACT_PRIOR_PARTNER')
  secret=rows[0][2];need(re.fullmatch(r'[A-Za-z0-9_+/=-]{16,4096}',secret) is not None,'PRIVATE_SECRET_FORMAT')
  start=files.snapshot(legacy.logs());jstart=journal.snapshot();report['user_attempted']=True;checkpoint()
  media_window=(start,jstart);ks=''
  ks=call(service='session',action='start',partnerId=partner,userId=user,type=0,expiry=1200,secret=secret)
  need(type(ks) is str and 20<=len(ks)<=8192,'USER_KS')
  denied=call(service='session',action='start',partnerId=partner,userId=user,type=2,expiry=60,secret=secret)
  need(type(denied) is dict and denied.get('objectType')=='KalturaAPIException' and denied.get('code')=='START_SESSION_ERROR','ADMIN_ESCALATION_CONTROL')
  report['user_privacy']=audit([secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()],start,jstart)
  report['user_session_accepted']=True;report['admin_escalation_rejected']=True;checkpoint()
  rehearsal=load('baseline_rehearsal_v2',NEW_HERE/'rehearsal.py')
  need(hashlib.sha256((NEW_HERE/'settle.py').read_bytes()).hexdigest()=='2b1382fc7ff4163240d9c6e3342738ce90ab8537df9ea9999497a44e24d84764','SETTLE_PIN')
  settle=load('baseline_settle_v1',NEW_HERE/'settle.py')
  source=Path('/home/vagrant/privacy-media-overlay-v3/short360.mp4');raw=source.read_bytes()
  need(len(raw)<=2*1024*1024 and hashlib.sha256(raw).hexdigest()==legacy.SOURCE_PIN,'MEDIA_SOURCE_PIN')
  report['source_sha256']=legacy.SOURCE_PIN
  start=files.snapshot(legacy.logs());jstart=journal.snapshot()
  def value(service,action,**params):return legacy.api_value(call(service=service,action=action,**params))
  media_window=(start,jstart)
  report['phase']='existing-entry-observation';entry_id=obs.ENTRY
  entry=value('media','get',ks=ks,entryId=entry_id,version=-1);bind_entry(entry,partner,entry_id)
  report['media_projection']=obs.projection(entry)
  assets=value('flavorasset','getByEntryId',ks=ks,entryId=entry_id)
  report['actual_assets']=obs.assets_projection(assets)
  originals=[a for a in assets if type(a.get('isOriginal')) in {bool,int,str} and a.get('isOriginal') in [True,1,'1']];need(len(originals)==1,'ORIGINAL_ASSET_COUNT')
  asset=originals[0];bind_asset(asset,partner,entry_id);asset_id=asset.get('id');version=str(asset.get('version'))
  need(asset_id=='0_ewuu0o46' and version=='2','PRIOR_ASSET_IDENTITY')
  rows=legacy.sql("SELECT id,partner_id,object_id,version,file_root,file_path,status FROM file_sync WHERE object_type=4 AND object_sub_type=1 AND file_type=1 AND status=2 AND partner_id="+str(partner)+" AND object_id='"+asset_id+"' AND version='"+version+"' LIMIT 2")
  candidates=[]
  for row in rows:
   try:candidates.append(legacy.owned_storage(row,partner,asset_id,version))
   except legacy.Failed:continue
  need(len(candidates)==1,'LOCAL_SOURCE_BINDING');stored,sync_id=candidates[0]
  need(sync_id==315 and legacy.checksum(stored)==legacy.SOURCE_PIN,'STORED_SOURCE_BYTES')
  report.update(original_asset_id=asset_id,asset_version=version,file_sync_id=sync_id,stored_source_sha256=legacy.SOURCE_PIN)
  listing=value('media','list',ks=ks,**{'filter:objectType':'KalturaMediaEntryFilter','filter:idEqual':entry_id,'filter:orderBy':'+createdAt','pager:objectType':'KalturaFilterPager','pager:pageSize':1,'pager:pageIndex':1})
  need(type(listing) is dict and type(listing.get('objects')) is list and len(listing['objects'])==1 and str(listing.get('totalCount'))=='1','OWNED_LIST')
  need(legacy.typed_equal(legacy.media_projection(listing['objects'][0]),report['media_projection']),'LIST_IDENTITY')
  report['list_total_count']=listing['totalCount']
  rows=legacy.sql("SELECT id,partner_id,COALESCE(data,''),conversion_profile_id FROM entry WHERE id='0_wzmt2sfy' AND partner_id=102 LIMIT 2")
  need(len(rows)==1 and len(rows[0])==4 and rows[0][:2]==['0_wzmt2sfy','102'],'ENTRY_DB_BINDING')
  concrete=obs.entry_version(rows[0][2]);selected=rows[0][3]
  need(selected=='14','OBSERVED_PROFILE_SELECTION')
  report['version_observations']=[]
  for version in [-1,0]+([concrete] if concrete is not None and concrete not in (-1,0) else []):
   reply=call(service='media',action='get',ks=ks,entryId=entry_id,version=version)
   if type(reply) is dict and reply.get('objectType')=='KalturaAPIException':
    report['version_observations'].append({'requested':version,'outcome':'API_REJECTED'})
   else:
    need(obs.typed_equal(obs.projection(reply),report['media_projection']),'VERSION_PROJECTION')
    report['version_observations'].append({'requested':version,'outcome':'TYPED_PROJECTION_MATCH'})
  positive=concrete is not None and any(r['requested']==concrete and r['outcome']=='TYPED_PROJECTION_MATCH' for r in report['version_observations'])
  report['fixture']=obs.fixture(entry,listing,concrete)
  report['entry_version_status']='OBSERVED_FROM_ENTRY_DATA' if concrete is not None else 'UNRESOLVED'
  profile_reply=call(service='conversionprofile',action='get',ks=ks,id=int(selected)) if re.fullmatch('[1-9][0-9]*',selected) else None
  report['profile']=obs.profile(profile_reply,selected)
  report['phase']='untimed-protocol-rehearsal';failure_stage='API_ROUND'
  tracked=rehearsal.TrackedTransport(legacy.PostTransport(legacy.Origin('192.168.56.74','https',8443),tls_ca,'5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef'),tracked_tokens)
  credentials=rehearsal.protocol.Credentials(partner,user,secret)
  report['untimed_round']=rehearsal.validate_round(rehearsal.protocol.run_round(tracked,credentials,report['fixture']))
  report['round_token_count']=len(tracked_tokens)
  failure_stage='QUIET_SETTLE'
  try:report['quiet_window']=settle.wait_quiet(lambda:(files.snapshot(legacy.logs()),journal.snapshot()))
  except settle.Unsettled:raise Rejected('QUIET_WINDOW_NOT_ESTABLISHED') from None
  failure_stage='MEDIA_PRIVACY'
  report['media_privacy']=audit([secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()],start,jstart)
  failure_stage='BATCH_PRIVACY'
  report['round_privacy']=audit_all(rehearsal.patterns(secret,ks,tracked_tokens),start,jstart)
  need(report['untimed_round']['functional_round_pass'],'UNTIMED_ROUND_FAILED')
  failure_stage='POSTCHECK'
  need(legacy.checksum(stored)==legacy.SOURCE_PIN and legacy.checksum(source)==legacy.SOURCE_PIN,'SOURCE_AFTER')
  report['sources_after']=overlay.source_state(manifest['after']);report['overlay_manifest_sha256']=EXPECTED_OVERLAY_MANIFEST;report['runtime_pins_verified']=True;report['tls_transport']={'scheme':'https','port':8443,'ca_sha256':'5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef','tls_logs_in_every_inventory':True};report['status']='EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE';report['phase']='done'

 except Exception as error:
  # Only bounded fixed codes; no repr/value/credential or arbitrary backend error text.
  report['failure_stage']=failure_stage;report['failure_code']=str(error) if type(error) is Rejected and str(error) in FIXED_FAILURE_CODES else 'UNEXPECTED_OR_DEPENDENCY_FAILURE'
  report['status']='FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION'
  if media_window is not None:
   try:
    if tracked_tokens:report['media_failure_privacy_batches']=audit_all(rehearsal.patterns(secret,ks,tracked_tokens),*media_window)
    else:report['media_failure_privacy']=audit([v for v in [secret.encode(),secret[:15].encode(),ks.encode(),ks[:15].encode()] if v],*media_window)
   except Exception as scan_error:report['media_privacy_failure_class']='FINITE_SCAN_INCOMPLETE'
 checkpoint();return 0 if report['status']=='EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE' else 2
if __name__=='__main__':sys.exit(main(sys.argv[1]))
