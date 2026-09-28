"""Lab incremental ES normal-APT phase; pinned D1 and all safety proofs required, no resume."""
import argparse,hashlib,http.client,json,os,re,signal,stat,time,types,uuid
from pathlib import Path
# Frozen lab4 postinst writes its prestart receipts at this canonical path.
RUN=Path('/var/lib/kaltura-php83-phase-d2');RETIRED_RUN=Path('/var/lib/kaltura-php83-phase-d2-incremental');TOOLS=Path('/var/lib/kaltura-php83-pilot/tools')
D1_PIN='98e813f23dbdedf3c1774340d5feddfd685d544cc84719a0e931e976b10a0b8f'
INVENTORY_PIN='d8206a79be4d5eb3e0ee062c7d1302a02c099175537960eb87338e3d75b935aa'
PRESTART_PIN='2c12d4ea7053878473a003d659a4be6a8b1385528aecd241b20580b6bf6ca86d'
ROW={'package':'kaltura-elasticsearch','version':'7.17-1+php83lab6','architecture':'all','previous':None,'sha256':'7959f637addad883be0d51ce54a43aa72ad0f155abdd37ddb68aeb57d582ab53','local_deb':'/var/lib/kaltura-php83-pilot/packages-phase-d/kaltura-elasticsearch_7.17-1+php83lab6_all.deb'}
SUCCESS='LAB_INCREMENTAL_D2_ES_INSTALLED_LOCAL_SEMANTICS_PRIVACY_WORKERS_HELD'
HARDEN=('/etc/elasticsearch/elasticsearch.yml','/etc/elasticsearch/jvm.options','/etc/elasticsearch/log4j2.properties')
ELASTIC='/opt/kaltura/app/configurations/elastic.ini'
INIT_PIN='1dd32a9ce4124b1b02e7522ad4ef8d3ae9e681b675fafd23f3698e383cf8b10f'
SOURCE_PINS={'/opt/kaltura/app/configurations/elastic/mapping/elasticsearch-7/category_mapping.json': '98ec80053876c9f0d51c493033f255849f276b03f8fc8f4bb28039079ffaa82e', '/opt/kaltura/app/configurations/elastic/mapping/elasticsearch-7/entry_mapping.json': 'ce7696504ff3ba5a1d575ac754b0340549270638cc9760cd9a83c67dc2211062', '/opt/kaltura/app/configurations/elastic/mapping/elasticsearch-7/kuser_mapping.json': 'b6e491d433944efa2e55f10d35273a1037da9189b09bd4fffdeac186ce7d6995', '/opt/kaltura/app/configurations/elastic/mapping/elasticsearch-7/search_history_mapping.json': '48143638155b7964864da679665897670ed50c76e56aacb9925624def79e3486', '/opt/kaltura/app/configurations/elastic.ini.template': '4b88b87411e15f2e6cfb945a423cc3297297d890288421abd3eceb72520b73b8', '/opt/kaltura/app/plugins/beacon/config/mapping/elasticsearch-7/beacon_entry_index.json': '86548195523364740edd9dc507c7cfb31d2e54d8336dd5e44e090ebbbc281735', '/opt/kaltura/app/plugins/beacon/config/mapping/elasticsearch-7/beacon_entry_server_node_index.json': '86548195523364740edd9dc507c7cfb31d2e54d8336dd5e44e090ebbbc281735', '/opt/kaltura/app/plugins/beacon/config/mapping/elasticsearch-7/beacon_scheduled_resource_index.json': '5cf22780cda6705a98e9f98a3a046cd49644698045c03c500f4919d270d2f47b', '/opt/kaltura/app/plugins/beacon/config/mapping/elasticsearch-7/beacon_server_node_index.json': 'd119eba2425f8b682768fe6a1ab4fd8f84f3afc59e7e85c8ebcb7038b6b30783'}
class Failure(ValueError):pass
def need(ok,code):
 if not ok:raise Failure(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path,pin):
 path=Path(path)
 for parent in path.parents:
  s=parent.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==0 and not s.st_mode&0o022,'HELPER_PARENT')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 with os.fdopen(fd,'rb') as stream:
  s=os.fstat(stream.fileno());need(stat.S_ISREG(s.st_mode) and s.st_uid==0 and not s.st_mode&0o022,'HELPER_MODE');raw=stream.read(1048577)
 need(sha(raw)==pin,'HELPER_PIN');m=types.ModuleType('pinned_d2_'+path.stem);exec(compile(raw,str(path),'exec'),m.__dict__);return m

PENDING=['full_seed_persistence','effective_authorization','full_application_acceptance']
def incremental_scope(c,phase):
 need(c.get('phase')==phase and c.get('full_acceptance') is False and c.get('pending')==PENDING,'INCREMENTAL_SCOPE')
 need(c.get('workers_policy')=='HELD' and c.get('release_authorized') is False,'INCREMENTAL_SAFETY_SCOPE')

def validate(c):
 incremental_scope(c,'D2')
 need(c.get('schema')==1 and type(c['schema']) is int and c.get('status')=='LAB_INCREMENTAL_AUTHORIZED' and c.get('package')==ROW,'CONTRACT_SCOPE')
 for field in ('executor_sha256','machine_id_sha256','baseline_dpkg_sha256','d1_contract_sha256','d1_terminal_sha256','snapshot_sha256','build_sha256','monit_master_sha256','monit_unit_sha256','recovery_proof_sha256'):
  need(isinstance(c.get(field),str) and re.fullmatch('[0-9a-f]{64}',c[field]),'CONTRACT_PIN')
 need(isinstance(c.get('audit_since'),str) and re.fullmatch(r'2026-09-[0-9]{2}T[0-9:]{8}Z',c['audit_since']),'AUDIT_WINDOW')
def recovery(c,n,p):
 raw=p.root_read(n.PROOFS+'phase-d2-native-logs-recovery.json');need(sha(raw)==c['recovery_proof_sha256'],'RECOVERY_PIN');r=json.loads(raw)
 need(r.get('status')=='COHERENT_PRE_D2_STATE_RESTORED' and r.get('machine_id_sha256')==c['machine_id_sha256'] and r.get('baseline_dpkg_sha256')==c['baseline_dpkg_sha256'] and r.get('resume_failed_run') is False and re.fullmatch('[a-f0-9-]{36}',r.get('preserved_failure_snapshot_id','')) and re.fullmatch('[a-f0-9-]{36}',r.get('restored_snapshot_id','')),'RECOVERY_REQUIRED')
def proofs(c,n,q,p,current):
 recovery(c,n,p)
 raw=p.root_read('/var/lib/kaltura-php83-phase-d1-incremental/contract.json');need(sha(raw)==c['d1_contract_sha256'],'D1_CONTRACT_PIN');d1=json.loads(raw);n.validate(d1);n.seed_gate(d1,p,q)
 need(d1['machine_id_sha256']==c['machine_id_sha256'] and d1['monit_master_sha256']==c['monit_master_sha256'] and d1['monit_unit_sha256']==c['monit_unit_sha256'] and d1['audit_since']==c['audit_since'],'D1_COHORT')
 raw=p.root_read('/var/lib/kaltura-php83-phase-d1-incremental/terminal.json');need(sha(raw)==c['d1_terminal_sha256'],'D1_TERMINAL_PIN');t=json.loads(raw)
 need(t.get('status')==n.SUCCESS and t.get('full_acceptance') is False and t.get('pending')==PENDING and t.get('phase')=='D1' and t.get('workers_policy')=='HELD' and t.get('worker_hold_preserved') is True and t.get('checks')==dict.fromkeys(('package_observation','metadata','input_canaries','generated_secrets'),True),'D1_SUCCESS_REQUIRED')
 original=p.root_read('/var/lib/kaltura-php83-phase-d1-incremental/baseline-dpkg.txt');n.baseline_check(original,p);n.delta(original,current)
 need(sha(current)==c['baseline_dpkg_sha256'] and len([x for x in current.splitlines() if x.startswith(b'kaltura-')])==14,'FOURTEEN_BASELINE')
 raw=p.root_read(n.PROOFS+'phase-d2-snapshot.json');need(sha(raw)==c['snapshot_sha256'],'SNAPSHOT_PIN');snap=json.loads(raw)
 need(snap.get('status')=='PRE_D2_STATE_PRESERVED' and snap.get('machine_id_sha256')==c['machine_id_sha256'] and snap.get('baseline_dpkg_sha256')==c['baseline_dpkg_sha256'] and snap.get('restore_automatically') is False and re.fullmatch('[a-f0-9-]{36}',snap.get('snapshot_id','')),'SNAPSHOT_REQUIRED')
 raw=p.root_read(n.PROOFS+'phase-d2-build.json');need(sha(raw)==c['build_sha256'],'BUILD_PIN');build=json.loads(raw)
 need(build.get('status')=='TWO_BUILDS_CONTROL_ONLY_PASS' and build.get('sha256')==ROW['sha256'] and build.get('changed')==['./control','./postinst'] and build.get('data_archive_byte_identical') is True,'BUILD_SCOPE')

def harden(h,i,f):
 # Exactly three native files; durable intent before the first chmod. No content/owner changes.
 observed={}
 for path in HARDEN:
  raw,identity,mode=h.checked(path,{0o660},i.PINS[path]);observed[path]={'sha256':sha(raw),'identity':identity,'before_mode':mode}
 f.new_private(RUN/'native-mode-intent.json',json.dumps(observed).encode())
 for path,row in observed.items():
  h.trusted_parents(path);fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
  try:
   s=os.fstat(fd);need((s.st_dev,s.st_ino)==tuple(row['identity']) and (s.st_uid,s.st_gid,s.st_nlink,stat.S_IMODE(s.st_mode))==(0,112,1,0o660) and not os.listxattr(fd),'NATIVE_MODE_DRIFT')
   need(sha(os.read(fd,1048577))==row['sha256'],'NATIVE_CONTENT_DRIFT');os.fchmod(fd,0o640);os.fsync(fd)
  finally:os.close(fd)
  h.checked(path,{0o640},row['sha256']);h.syncdir(Path(path).parent)
 f.new_private(RUN/'native-mode-complete.json',b'{"status":"THREE_NATIVE_CONFIGS_0640_BYTES_OWNERS_UNCHANGED"}')
def package_delta(before,after):
 old={x.split(b'\t')[0]:x for x in before.splitlines()};new={x.split(b'\t')[0]:x for x in after.splitlines()}
 need({k for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}=={b'kaltura-elasticsearch'} and new[b'kaltura-elasticsearch']==b'kaltura-elasticsearch\t7.17-1+php83lab6\tall\tii ','EXACT_ONE_ES_DELTA')
def get(path):
 need(path.startswith('/') and not any(x in path for x in ('\r','\n','#')),'HTTP_PATH');conn=http.client.HTTPConnection('127.0.0.1',9200,timeout=10)
 try:
  conn.request('GET',path,headers={'Accept':'application/json'});response=conn.getresponse();raw=response.read(8*1024*1024+1)
  need(response.status==200 and len(raw)<=8*1024*1024,'ES_HTTP');return json.loads(raw)
 finally:conn.close()
def expected_indices(month):
 need(re.fullmatch(r'2026_[0-9]{2}',month) is not None,'MONTH')
 return {'kaltura_'+k:'/opt/kaltura/app/configurations/elastic/mapping/elasticsearch-7/'+k+'_mapping.json' for k in ('entry','category','kuser','search_history')}|{k+'_'+month:'/opt/kaltura/app/plugins/beacon/config/mapping/elasticsearch-7/'+k+'.json' for k in ('beacon_entry_index','beacon_entry_server_node_index','beacon_scheduled_resource_index','beacon_server_node_index')}
def subset(want,got):
 if isinstance(want,dict):return isinstance(got,dict) and all(k in got and subset(v,got[k]) for k,v in want.items())
 if isinstance(want,list):return isinstance(got,list) and len(want)==len(got) and all(subset(x,y) for x,y in zip(want,got))
 return type(want) is type(got) and want==got

def canonical_mapping(index,value):
 # Only exact pinned-source paths observed in native ES 7.17.29 serialization.
 value=json.loads(json.dumps(value))
 if index in ('kaltura_entry','kaltura_category','kaltura_kuser','kaltura_search_history'):
  value.setdefault('_source',{'enabled':True})
  if value.get('dynamic') is False:value['dynamic']='false'
 fields={'kaltura_kuser':('picture','enabled')}
 if index.startswith('beacon_scheduled_resource_index_'):fields[index]=('raw_data','index')
 if index in fields:
  field,key=fields[index];node=value.get('properties',{}).get(field,{})
  if node.get(key)=='false':node[key]=False
 return value

def flatten(value,prefix=''):
 out={}
 if isinstance(value,dict):
  for key,child in value.items():out.update(flatten(child,prefix+('.' if prefix else '')+key))
 else:out[prefix]=[str(x) for x in value] if isinstance(value,list) else (str(value).lower() if isinstance(value,bool) else str(value))
 return out

def semantics(month,p):
 root=get('/');need(root.get('cluster_name')=='kaltura' and root.get('version',{}).get('number')=='7.17.29','ES_IDENTITY')
 aliases=get('/_aliases');wanted=expected_indices(month);need(set(aliases)==set(wanted),'EXACT_EIGHT_INDICES')
 targets={}
 for index,row in aliases.items():
  for alias in row.get('aliases',{}):targets.setdefault(alias,set()).add(index)
 expected={'search_history_index':{'kaltura_search_history'},'search_history_search':{'kaltura_search_history'}}
 for prefix in ('beacon_entry_index','beacon_entry_server_node_index','beacon_scheduled_resource_index','beacon_server_node_index'):
  for alias in (prefix,prefix+'_search'):expected[alias]={prefix+'_'+month}
 expected['beaconindex']={k for k in wanted if k.startswith('beacon_')};need(targets==expected,'EXACT_ALIAS_MEMBERSHIP')
 for index,path in wanted.items():
  raw=p.root_read(path);need(sha(raw)==SOURCE_PINS[path],'MAPPING_SOURCE_PIN');source=json.loads(raw)
  need(get('/'+index+'/_count').get('count')==0,'FRESH_INDEX_NONEMPTY')
  mapping=get('/'+index+'/_mapping');need(set(mapping)=={index} and subset(canonical_mapping(index,source['mappings']),canonical_mapping(index,mapping[index]['mappings'])),'MAPPING_SEMANTICS')
  actual=get('/'+index+'/_settings?flat_settings=true')[index]['settings'];expect={}
  for key,value in flatten(source['settings']).items():expect[key if key.startswith('index.') else 'index.'+key]=value
  expect['index.number_of_replicas']='0';need(all(actual.get(k)==v for k,v in expect.items()),'INDEX_SETTINGS')
 health=get('/_cluster/health');need(health.get('status')=='green' and health.get('number_of_nodes')==1 and health.get('active_primary_shards',0)>0,'CLUSTER_HEALTH')
 nodes=get('/_nodes/settings,jvm,plugins');need(len(nodes.get('nodes',{}))==1,'ONE_NODE');node=next(iter(nodes['nodes'].values()))
 need(node.get('jvm',{}).get('mem',{}).get('heap_max_in_bytes')==1073741824,'HEAP_1G')
 need(any(x.get('name')=='analysis-icu' and x.get('version')=='7.17.29' for x in node.get('plugins',[])),'ICU_LOADED')
 settings=node.get('settings',{});need(settings.get('network',{}).get('host')=='127.0.0.1' and str(settings.get('ingest',{}).get('geoip',{}).get('downloader',{}).get('enabled')).lower()=='false','OFFLINE_LOOPBACK_EFFECTIVE')
 return {'indices':8,'aliases':len(expected),'mapping_source_pins':True,'green':True,'icu_loaded':True,'heap_bytes':1073741824,'geoip_downloader':False}

def cache_inputs(p,a):
 for name in ('kLocalMemCacheConf','kRemoteMemCacheConf'):
  path='/opt/kaltura/app/configurations/'+name+'.ini';values=a.ini(p.root_read(path))
  need(values.get(('','host')) in ('127.0.0.1','localhost') and values.get(('','port'))=='11211','LOCAL_CACHE_ENDPOINT')
  for (section,key),value in values.items():
   need((section=='' and key in ('host','port')) or (section=='write_address_list' and key.isdecimal() and value in ('127.0.0.1','localhost')),'CACHE_EXTRA_ENDPOINT')
  overlay=Path('/opt/kaltura/app/configurations/hosts')/name
  need(not os.path.lexists(overlay) or (p.trusted_chain(overlay,directory=True) is None and not list(overlay.iterdir())),'CACHE_HOST_OVERRIDE')
 overlay=Path('/opt/kaltura/app/configurations/hosts/elastic');need(not os.path.lexists(overlay) or (p.trusted_chain(overlay,directory=True) is None and not list(overlay.iterdir())),'ES_HOST_OVERRIDE')

def app_probe(p,f):
 root=Path('/opt/kaltura/app/alpha/web');p.trusted_chain(root,directory=True);nonce=uuid.uuid4().hex;path=root/('pilot83-es-'+nonce+'.php')
 source=('''<?php ini_set('display_errors','0'); header('Content-Type: application/json'); try { require '/opt/kaltura/app/api_v3/bootstrap.php'; $ok=true; foreach(['kLocalMemCacheConf','kRemoteMemCacheConf'] as $name){$m=kConf::getMap($name); $ok=$ok && in_array($m['host']??null,['127.0.0.1','localhost'],true) && (string)($m['port']??'')==='11211'; foreach(($m['write_address_list']??[]) as $v){$ok=$ok && in_array($v,['127.0.0.1','localhost'],true);}} echo json_encode(['nonce'=>'NONCE','version'=>PHP_VERSION_ID,'sapi'=>PHP_SAPI,'elastic_host'=>kConf::get('elasticHost','elastic',null),'elastic_port'=>(string)kConf::get('elasticPort','elastic',null),'elastic_version'=>(string)kConf::get('elasticVersion','elastic',null),'cache_local'=>$ok]); } catch(Throwable $e){http_response_code(500);echo '{"status":"PROBE_FAILED"}';}''').replace('NONCE',nonce).encode()
 f.new_private(path,source,0o644);owned=path.lstat()
 try:
  obj=json.loads(p.curl(f,'http://192.168.56.83/'+path.name));need(obj=={'nonce':nonce,'version':80306,'sapi':'apache2handler','elastic_host':'127.0.0.1','elastic_port':'9200','elastic_version':'7','cache_local':True},'FRESH_NATIVE_CONFIG');return {'native_effective_es_and_local_cache':True,'response_sha256':sha(json.dumps(obj,sort_keys=True).encode())}
 finally:
  now=path.lstat();need((now.st_dev,now.st_ino,now.st_uid,stat.S_IMODE(now.st_mode))==(owned.st_dev,owned.st_ino,0,0o644) and f.digest_file(path)==sha(source),'PROBE_OWNERSHIP');path.unlink();f.sync_dir(root)

def sources(p):
 for path,pin in SOURCE_PINS.items():need(sha(p.root_read(path))==pin,'SOURCE_PIN')
def package(p,f):
 path=Path(ROW['local_deb']);f.safe_parents(path);s=path.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==0 and s.st_nlink==1 and not s.st_mode&0o022 and f.digest_file(path)==ROW['sha256'],'PACKAGE_PIN')
 fields=dict(x.split(': ',1) for x in f.bounded(['/usr/bin/dpkg-deb','-f',str(path),'Package','Version','Architecture'],30).decode().splitlines());need(fields=={k.capitalize():ROW[k] for k in ('package','version','architecture')},'PACKAGE_IDENTITY')
def memory_gate(f):
 props=dict(line.split('=',1) for line in f.bounded(['/usr/bin/systemctl','show','elasticsearch','--property=Slice,MemoryMax,MemoryHigh,MemorySwapMax'],20).decode().splitlines())
 need(props=={'Slice':'system.slice','MemoryMax':'infinity','MemoryHigh':'infinity','MemorySwapMax':'infinity'},'UNIT_MEMORY_LIMIT')
 mounts=[line.split() for line in Path('/proc/self/mountinfo').read_text().splitlines() if ' - cgroup2 ' in line]
 need(len(mounts)==1 and mounts[0][3:5]==['/','/sys/fs/cgroup'],'CGROUP_ROOT_MOUNT')
 for name in ('memory.max','memory.high'):
  need(Path('/sys/fs/cgroup/system.slice',name).read_text().strip()=='max','SLICE_MEMORY_LIMIT')
def fresh_run(h):
 need(RUN==h.RUN,'PRESTART_RUN_CONTRACT')
 # Neither successful nor failed prior attempts are resumable; dangling links count.
 need(not any(os.path.lexists(path) for path in (RUN,RETIRED_RUN,Path('/usr/sbin/policy-rc.d'))),'NO_RESUME_OR_POLICY')

def guard(c,n,q,p,s,b,f,d,a,i,h):
 validate(c);baseline=f.bounded(b.DPKG,30);proofs(c,n,q,p,baseline) # Incremental authorization and exact D1 safety success before any RUN/mutation.
 fresh_run(h);h.fresh_logs();info=i.inventory()
 need(info.get('status')=='READONLY_D2_INVENTORY_MATCHED_NOT_START_APPROVAL' and c['machine_id_sha256']==i.MACHINE,'LAB_INVENTORY')
 need(all(not row['present'] for row in info['fresh_kaltura_roots'].values()),'FRESH_KALTURA_ROOTS_ABSENT')
 need(int(info['memory_kib']['MemAvailable'])>=4*1024*1024,'MEMORY_HEADROOM')
 # Conservative root-cgroup unlimited admission only; unknown nested limits block.
 memory_gate(f)
 for path in HARDEN:need(info['files'][path]['mode']=='0660' and info['files'][path]['uid']==0 and info['files'][path]['gid']==112,'NATIVE_MODE_BASELINE')
 for unit in ('apt-daily.timer','apt-daily-upgrade.timer','apt-daily.service','apt-daily-upgrade.service','unattended-upgrades.service'):
  need(f.bounded(['/usr/bin/systemctl','show','--property=ActiveState','--value',unit],20).strip()==b'inactive','APT_CONCURRENCY')
 need(not f.bounded(['/usr/bin/dpkg','--audit'],30).strip() and b.states(f)=={'apache2':'active','monit':'active','mariadb':'active'},'BASELINE_SERVICES')
 n.source_current(q,p);p.canonical_config(b,a);identity=n.held(p);n.monit(c,p,f,True);q.log_modes(after=True);sources(p);cache_inputs(p,a);package(p,f)
 need(f.digest_file(s.FUNCTIONS)==s.NEW_FUNCTIONS,'SHARED_FUNCTIONS');d.service_identity();d.auth_check();d.logging_guard();q.synchronous_file_health(b,d)
 _,_,canaries=d.private_inputs();n.generated(a,c,True,['/var/lib/kaltura-php83-phase-d1-incremental/apt-private.log'])
 need(not os.path.lexists('/opt/kaltura/app/configurations/elastic/populate/kaltura-php83-lab.ini'),'FRESH_POPULATE_CONFIG')
 return baseline,canaries,p.private_inventory(),p.configs(s,b),identity,q.bindings(p,f),p.root_read(ELASTIC)
def ini_delta(before,after):
 expected=before
 for old,new in ((b'@ELASTIC_PORT@',b'9200'),(b'@ELASTIC_HOST@',b'127.0.0.1'),(b'@BEACONS_ELASTIC_HOST@',b'127.0.0.1'),(b'@BEACONS_ELASTIC_PORT@',b'9200'),(b'@CURL_TIMEOUT_IN_SEC@',b'10')):expected=expected.replace(old,new)
 if not re.search(rb'^elasticVersion',expected,re.M):expected=re.sub(rb'^(elasticPort = .*)$',rb'\1\nelasticVersion = 7',expected,count=1,flags=re.M)
 need(after==expected,'ELASTIC_INI_DELTA')
def contain(f):
 failures=[]
 for unit in ('monit','apache2','elasticsearch'):
  try:
   try:f.bounded(['/usr/bin/systemctl','stop',unit],60)
   except BaseException:
    if unit!='elasticsearch':raise
    f.bounded(['/usr/bin/systemctl','kill','--kill-whom=all','--signal=KILL','elasticsearch'],20)
   need(f.bounded(['/usr/bin/systemctl','show','--property=ActiveState','--value',unit],20).strip() in (b'inactive',b'failed'),'CONTAINMENT_STATE')
  except BaseException:failures.append(unit)
 need(not failures,'CONTAINMENT_FAILED')
def log_copies(f,d,canaries):
 # Native daemon logs are untrusted input. Copy bounded regular files into root600
 # evidence so the existing full generated-secret scanner can inspect them.
 out=[];total=0
 for root in (Path('/var/log/elasticsearch'),Path('/opt/kaltura/log/elasticsearch'),Path('/var/lib/kaltura-php83-elasticsearch-logs')):
  if not root.exists():continue
  need(not root.is_symlink() and root.is_dir(),'LOG_ROOT')
  for path in sorted(root.iterdir()):
   need(len(out)<64,'LOG_COUNT');fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
   with os.fdopen(fd,'rb') as stream:
    st=os.fstat(stream.fileno());need(stat.S_ISREG(st.st_mode) and st.st_nlink==1,'LOG_FILE');raw=stream.read(32*1024*1024+1)
   total+=len(raw);need(len(raw)<=32*1024*1024 and total<=128*1024*1024,'LOG_BUDGET')
   target=RUN/('es-private-log-'+str(len(out))+'.log');f.new_private(target,raw);out.append(str(target));d.reject_canaries(raw,canaries)
 return out

def execute(c,n,q,p,s,b,f,d,a,i,h):
 baseline,canaries,private,configs,identity,old_listeners,elastic_before=guard(c,n,q,p,s,b,f,d,a,i,h)
 cursor=d.cursor();d.scan_logs(canaries,cursor);f.safe_parents(RUN);RUN.mkdir(mode=0o700);os.chmod(RUN,0o700);f.sync_dir(RUN.parent);f.RUN=RUN;b.RUN=RUN
 status='FAILED_REQUIRES_OPERATOR_RECOVERY';handlers={};attempted=False;contained=False;checks={};copies=[]
 try:
  def interrupted(signum,frame):raise Failure('INTERRUPTED')
  for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGHUP):handlers[sig]=signal.signal(sig,interrupted)
  for sub in ('archives','apt-lists'):(RUN/sub).mkdir(mode=0o700)
  f.new_private(RUN/'contract.json',json.dumps(c).encode());f.new_private(RUN/'baseline-dpkg.txt',baseline);f.new_private(RUN/'archives.json',json.dumps(f.populate_archives([ROW])).encode())
  args=b.apt_args();paths=[ROW['local_deb']];simulation=f.bounded(args[:1]+['--simulate']+args[1:]+paths,180);f.new_private(RUN/'simulation.log',simulation);d.reject_canaries(simulation,canaries)
  need(f.parse_solver(simulation)==[(ROW['package'],ROW['version'],ROW['architecture'],None)],'ONE_PACKAGE_SOLVER')
  need(f.bounded(b.DPKG,30)==baseline and p.configs(s,b)==configs and p.root_read(ELASTIC)==elastic_before,'PRE_APT_DRIFT');proofs(c,n,q,p,baseline);sources(p);cache_inputs(p,a);package(p,f);n.held(p,identity);fresh=i.inventory();need(int(fresh['memory_kib']['MemAvailable'])>=4*1024*1024,'MEMORY_HEADROOM');memory_gate(f)
  need(f.digest_file(RUN/'archives'/f.archive_name(ROW))==ROW['sha256'],'CACHE_PIN')
  h.stopped();harden(h,i,f);month=f.bounded(['/usr/bin/date','+%Y_%m'],20).decode().strip();expected_indices(month)
  f.new_private(RUN/'attempted.json',b'{"normal_apt":true,"resume_supported":false}');attempted=True
  with open(RUN/'apt-private.log','xb',opener=lambda path,flags:os.open(path,flags,0o600)) as log:
   try:f.bounded(args[:1]+['--yes']+args[1:]+paths,900,log)
   finally:log.flush();os.fsync(log.fileno())
  after=f.bounded(b.DPKG,30);package_delta(baseline,after);need(not f.bounded(['/usr/bin/dpkg','--audit'],30).strip(),'DPKG_AUDIT')
  need(f.bounded(['/usr/bin/date','+%Y_%m'],20).decode().strip()==month,'MONTH_ROLLOVER')
  need(p.configs(s,b)==configs,'PRIVATE_CONFIG_CHANGED');ini_delta(elastic_before,p.root_read(ELASTIC));n.source_current(q,p);n.held(p,identity);q.log_modes(after=True);n.monit(c,p,f,True);p.preserve_private(private);sources(p);cache_inputs(p,a);q.synchronous_file_health(b,d)
  h.checked(h.CONFIG,{0o640},h.AFTER_PIN);h.checked(h.HEAP,{0o640},sha(b'-Xms1g\n-Xmx1g\n'))
  for path,pin in h.NATIVE.items():h.checked(path,{0o640},pin)
  receipt=json.loads(p.root_read(RUN/'prestart-mode-complete.json'));need(receipt.get('status')=='EXACT_PRIVATE_ES_PRESTART_CONFIG_READY' and receipt.get('config_sha256')==h.AFTER_PIN and receipt.get('daemon_logs')=='/var/lib/kaltura-php83-elasticsearch-logs' and receipt.get('daemon_logs_mode')=='0700','PRESTART_RECEIPT');h.private_logs(0o700)
  need(sha(p.root_read('/etc/init.d/kaltura-elastic-populate'))==INIT_PIN and not os.path.lexists('/opt/kaltura/log/populate_elastic.pid'),'POPULATE_HELD')
  need(f.bounded(['/usr/bin/systemctl','show','elasticsearch','--property=ActiveState','--value'],20).strip()==b'active','ES_ACTIVE')
  observed=p.listeners(f);need({addr for addr,_ in observed}==old_listeners|{'127.0.0.1:9200','127.0.0.1:9300'},'EXACT_LOCAL_LISTENERS')
  for port in (9200,9300):need(any(addr=='127.0.0.1:'+str(port) and '"java"' in line for addr,line in observed),'JAVA_LOCAL_LISTENER')
  semantic=semantics(month,p);effective=app_probe(p,f)
  old_monit=p.monit
  try:p.monit=lambda c,f,after=False:n.monit(c,p,f,True);runtime=p.readiness(c,b,f,old_listeners|{'127.0.0.1:9200','127.0.0.1:9300'})
  finally:p.monit=old_monit
  f.new_private(RUN/'runtime.json',json.dumps({'es':semantic,'native':runtime,'effective_config':effective}).encode());status=SUCCESS
 finally:
  with f.signals_blocked():
   if status!=SUCCESS:
    try:contain(f);contained=True
    except BaseException:contained=False
   def generated():
    raw=n.generated(a,c,True,['/var/lib/kaltura-php83-phase-d1-incremental/apt-private.log']+([str(RUN/'apt-private.log')] if (RUN/'apt-private.log').exists() else [])+copies)
    f.new_private(RUN/'generated-audit.json',json.dumps(raw).encode())
   for name,fn in (
    ('package_observation',lambda:f.new_private(RUN/'after-dpkg.txt',f.bounded(b.DPKG,30))),
    ('metadata',lambda:(n.held(p,identity),p.preserve_private(private),q.log_modes(after=True),h.private_logs(0o700))),
    ('input_canaries',lambda:d.scan_logs(canaries,cursor,RUN/'apt-private.log' if (RUN/'apt-private.log').exists() else None)),
    ('es_private_log_capture',lambda:copies.extend(log_copies(f,d,canaries))),
    ('generated_secrets',generated)):
    try:fn();checks[name]=True
    except BaseException:checks[name]=False;status='FAILED_REQUIRES_OPERATOR_RECOVERY'
   if status!=SUCCESS and not contained:
    try:contain(f);contained=True
    except BaseException:contained=False
   terminal={'status':status,'checks':checks,'normal_apt_attempted':attempted,'worker_hold_preserved':checks.get('metadata',False),'failure_contained':contained,'resume_supported':False,'full_application_acceptance':False,'full_acceptance':False,'pending':PENDING,'phase':'D2','workers_policy':'HELD'}
   try:f.new_private(RUN/'terminal.json',json.dumps(terminal).encode())
   finally:
    for sig,handler in handlers.items():signal.signal(sig,handler)
 need(status==SUCCESS,'D2_FAILED');return terminal

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 for name in ('contract','contract-sha256','execute-contract'):parser.add_argument('--'+name,required=True)
 args=parser.parse_args()
 try:
  need(args.contract_sha256==args.execute_contract,'EXPLICIT_CONTRACT');n=load(TOOLS/'application-phase-d1-incremental.py',D1_PIN);q=n.load_c();p=q.load_b();raw=p.root_read(args.contract);need(sha(raw)==args.contract_sha256,'CONTRACT_PIN');c=json.loads(raw);validate(c);need(sha(p.root_read(Path(__file__).resolve()))==c['executor_sha256'],'EXECUTOR_PIN')
  s=p.load('application-services.py',p.UPGRADE_PIN);b=s.load_base();f=b.load_helper('fresh-install.py',b.FRESH_PIN);d=b.load_helper('database-bootstrap.py',q.DB_PIN);a=p.load('generated-secret-audit-r2.py',q.AUDIT_R2_PIN);i=load(TOOLS/'phase-d2-preinventory-r3.py',INVENTORY_PIN);h=load(TOOLS/'elastic-prestart-private-logs-r2.py',PRESTART_PIN)
  print(json.dumps(execute(c,n,q,p,s,b,f,d,a,i,h)));return 0
 except BaseException as exc:
  code=exc.args[0] if type(exc) is Failure and exc.args and exc.args[0] in FAILURE_CODES else 'UNEXPECTED_FAILURE'
  line=0;tb=exc.__traceback__
  while tb:
   if tb.tb_frame.f_code.co_filename==__file__:line=tb.tb_lineno
   tb=tb.tb_next
  print(json.dumps({'status':'BLOCKED_OR_FAILED','failure_code':code,'source_line':line,'resume_supported':False,'full_application_acceptance':False,'full_acceptance':False,'pending':PENDING,'phase':'D2','workers_policy':'HELD'}));return 78
FAILURE_CODES=('RECOVERY_PIN','RECOVERY_REQUIRED','PRESTART_RUN_CONTRACT','APT_CONCURRENCY', 'AUDIT_WINDOW', 'BASELINE_SERVICES', 'BUILD_PIN', 'BUILD_SCOPE', 'CACHE_EXTRA_ENDPOINT', 'CACHE_HOST_OVERRIDE', 'CACHE_PIN', 'CGROUP_ROOT_MOUNT', 'CLUSTER_HEALTH', 'CONTAINMENT_FAILED', 'CONTAINMENT_STATE', 'CONTRACT_PIN', 'CONTRACT_SCOPE', 'D1_COHORT', 'D1_CONTRACT_PIN', 'D1_SUCCESS_REQUIRED', 'D1_TERMINAL_PIN', 'D2_FAILED', 'DPKG_AUDIT', 'ELASTIC_INI_DELTA', 'ES_ACTIVE', 'ES_HOST_OVERRIDE', 'ES_HTTP', 'ES_IDENTITY', 'EXACT_ALIAS_MEMBERSHIP', 'EXACT_EIGHT_INDICES', 'EXACT_LOCAL_LISTENERS', 'EXACT_ONE_ES_DELTA', 'EXECUTOR_PIN', 'EXPLICIT_CONTRACT', 'FOURTEEN_BASELINE', 'FRESH_INDEX_NONEMPTY', 'FRESH_KALTURA_ROOTS_ABSENT', 'FRESH_NATIVE_CONFIG', 'FRESH_POPULATE_CONFIG', 'HEAP_1G', 'HELPER_MODE', 'HELPER_PARENT', 'HELPER_PIN', 'HTTP_PATH', 'ICU_LOADED', 'INDEX_SETTINGS', 'INTERRUPTED', 'JAVA_LOCAL_LISTENER', 'LAB_INVENTORY', 'LOCAL_CACHE_ENDPOINT', 'LOG_BUDGET', 'LOG_COUNT', 'LOG_FILE', 'LOG_ROOT', 'MAPPING_SEMANTICS', 'MAPPING_SOURCE_PIN', 'MEMORY_HEADROOM', 'MONTH', 'MONTH_ROLLOVER', 'NATIVE_CONTENT_DRIFT', 'NATIVE_MODE_BASELINE', 'NATIVE_MODE_DRIFT', 'NO_RESUME_OR_POLICY', 'OFFLINE_LOOPBACK_EFFECTIVE', 'ONE_NODE', 'ONE_PACKAGE_SOLVER', 'PACKAGE_IDENTITY', 'PACKAGE_PIN', 'POPULATE_HELD', 'PRESTART_RECEIPT', 'PRE_APT_DRIFT', 'PRIVATE_CONFIG_CHANGED', 'PROBE_OWNERSHIP', 'SHARED_FUNCTIONS', 'SLICE_MEMORY_LIMIT', 'SNAPSHOT_PIN', 'SNAPSHOT_REQUIRED', 'SOURCE_PIN', 'UNIT_MEMORY_LIMIT')
if __name__=='__main__':raise SystemExit(main())
