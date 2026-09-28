"""Fresh .83 lab3 nginx D3 normal offline APT; prepare/review before execution."""
import argparse,hashlib,http.client,itertools,json,os,re,signal,stat,time,uuid
from pathlib import Path
import importlib.util,sys
RUN=Path('/var/lib/kaltura-php83-phase-d3')
TOOLS=Path('/var/lib/kaltura-php83-pilot/tools')
D2_PIN='c5804a9ff6c16ab70e702375113bd851e08985f046d617fafaba22b6b027e99b'
BASELINE='6c73bbed89e4883d5b587a0f99b97e3a8d0edd063a646beda5bafea8c9eab3ab'
D2_TERMINAL='f5446a3b5f167f379d95ee8d8b6218525567e48f513faf19a11d33b855c9efde'
D2_CONTRACT='5eee5e5a095323a377232989e48a3bb3554384157d54a7144b1590c729035a6c'
MACHINE='ad9adac39d0fb440883f0b82c8c45058596b74a6d9e98da2746e4dbdafd3aad8'
PACKAGE={'package':'kaltura-nginx','version':'1.23.0-1+php83lab3','architecture':'amd64','previous':None,'local_deb':'/var/lib/kaltura-php83-pilot/packages-phase-d/kaltura-nginx_1.23.0-1+php83lab3_amd64.deb'}
SERVICES=('apache2','monit','mariadb','elasticsearch')
ABSENT=('/opt/kaltura/nginx','/etc/init.d/kaltura-nginx','/etc/systemd/system/kaltura-nginx.service','/usr/lib/systemd/system/kaltura-nginx.service','/usr/local/lib/kaltura-nginx-lab','/etc/kaltura-nginx-lab','/run/kaltura-php83-nginx-log','/var/lib/kaltura-php83-nginx-log-sink','/var/lib/kaltura-php83-nginx-access','/opt/kaltura/log/nginx','/etc/default/nginx')
PENDING=['full_seed_persistence','effective_authorization','full_application_acceptance']
class Failure(Exception):pass
def need(ok,code):
 if not ok:raise Failure(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def pin(value):return type(value) is str and re.fullmatch('[a-f0-9]{64}',value) is not None

def validate(c):
 need(type(c) is dict and c.get('schema')==1 and type(c['schema']) is int and c.get('phase')=='D3' and c.get('status')=='LAB_INCREMENTAL_AUTHORIZED','CONTRACT')
 need(c.get('full_acceptance') is False and c.get('release_authorized') is False and c.get('workers_policy')=='HELD' and c.get('pending')==PENDING,'SCOPE')
 row=c.get('package',{});need(set(row)==set(PACKAGE)|{'sha256'} and all(row[k]==v for k,v in PACKAGE.items()) and row['sha256']=='c52b28cd2aa081a8254089cb5d32ab72b177975a95f5b23b021600cce375bc19','PACKAGE')
 need(c.get('machine_id_sha256')==MACHINE and c.get('baseline_dpkg_sha256')==BASELINE and c.get('d2_terminal_sha256')==D2_TERMINAL,'COHORT')
 for k in ('executor_sha256','snapshot_sha256'):need(pin(c.get(k)),'PIN')
 need(type(c.get('audit_since')) is str and re.fullmatch(r'2026-09-[0-9]{2}T[0-9:]{8}Z',c['audit_since']),'AUDIT_WINDOW')
 files=c.get('installed_pins');need(type(files) is dict and 8<=len(files)<=128 and all(pin(v) for v in files.values()),'INSTALLED_PINS')
 required={'/opt/kaltura/nginx/sbin/nginx','/etc/init.d/kaltura-nginx','/etc/systemd/system/kaltura-nginx.service','/usr/local/lib/kaltura-nginx-lab/service.py','/usr/local/lib/kaltura-nginx-lab/lab_adapter.py','/usr/local/lib/kaltura-nginx-lab/sanitizer.py','/etc/kaltura-nginx-lab/manifest.json','/opt/kaltura/nginx/conf/kaltura-nginx.conf','/opt/kaltura/nginx/conf/http.conf'}
 need(required<=set(files),'INSTALLED_REQUIRED')
 for p in files:
  need(type(p) is str and '..' not in Path(p).parts and (p in required or p.startswith('/opt/kaltura/nginx/conf/') or p.startswith('/usr/local/lib/kaltura-nginx-lab/')),'INSTALLED_PATH')

def states(f):return {s:f.bounded(['/usr/bin/systemctl','show',s,'--property=ActiveState','--value'],10).decode().strip() for s in SERVICES}
def nginx_processes():
 rows=[]
 for item in Path('/proc').iterdir():
  if not item.name.isdigit():continue
  try:
   executable=os.readlink(item/'exe')
   if (item/'comm').read_bytes().strip()!=b'nginx' and executable.rsplit('/',1)[-1]!='nginx':continue
   need(executable=='/opt/kaltura/nginx/sbin/nginx','UNMANAGED_NGINX')
   raw=(item/'status').read_text();uid=int(re.search(r'^Uid:\s+(\d+)',raw,re.M)[1]);parent=int(re.search(r'^PPid:\s+(\d+)',raw,re.M)[1])
   rows.append((int(item.name),parent,uid))
  except FileNotFoundError:continue
 need(len(rows)<=256,'PROCESS_COUNT');return rows

def snapshot(c,p):
 raw=p.root_read('/var/lib/kaltura-php83-pilot/proofs/phase-d3-snapshot.json');need(sha(raw)==c['snapshot_sha256'],'SNAPSHOT_PIN');s=json.loads(raw)
 need(s.get('status')=='PRE_D3_STATE_PRESERVED' and s.get('machine_id_sha256')==MACHINE and s.get('baseline_dpkg_sha256')==BASELINE and s.get('restore_automatically') is False and re.fullmatch('[a-f0-9-]{36}',s.get('snapshot_id','')),'SNAPSHOT')
def cohort(c,p,m):
 raw=p.root_read('/var/lib/kaltura-php83-phase-d2/terminal.json');need(sha(raw)==D2_TERMINAL,'D2_TERMINAL');t=json.loads(raw)
 need(t.get('status')==m.SUCCESS and t.get('worker_hold_preserved') is True and t.get('full_acceptance') is False and all(t.get('checks',{}).get(k) is True for k in ('package_observation','metadata','input_canaries','es_private_log_capture','generated_secrets')),'D2_SUCCESS')
 raw=p.root_read('/var/lib/kaltura-php83-phase-d2/contract.json');need(sha(raw)==D2_CONTRACT,'D2_CONTRACT');need(json.loads(raw)['audit_since']==c['audit_since'],'AUDIT_COHORT')
 snapshot(c,p)
def package(c,p,f):
 row=c['package'];need(f.digest_file(row['local_deb'])==row['sha256'],'DEB_PIN')
 raw=f.bounded(['/usr/bin/dpkg-deb','--field',row['local_deb'],'Package','Version','Architecture'],20)
 fields=dict(line.split(': ',1) for line in raw.decode().splitlines());need(fields=={'Package':row['package'],'Version':row['version'],'Architecture':row['architecture']},'DEB_IDENTITY')
def delta(before,after):
 old={x.split(b'\t')[0]:x for x in before.splitlines()};new={x.split(b'\t')[0]:x for x in after.splitlines()}
 need({k for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}=={b'kaltura-nginx'},'DPKG_DELTA')
 need(new[b'kaltura-nginx']==b'kaltura-nginx\t1.23.0-1+php83lab3\tamd64\tii ','NGINX_CONFIGURED')

def readiness(c,p,f,old_listeners):
 deadline=time.monotonic()+25
 while True:
  props=dict(line.split('=',1) for line in f.bounded(['/usr/bin/systemctl','show','kaltura-nginx.service','--property=ActiveState,MainPID,KillMode,Restart'],5).decode().splitlines())
  rows=nginx_processes();masters=[x for x in rows if x[2]==0 and x[1]==int(props.get('MainPID','0'))];workers=[x for x in rows if x[2]==7373]
  listeners=p.listeners(f);wanted={'192.168.56.83:88','192.168.56.83:1935'}
  if props.get('ActiveState')=='active' and props.get('KillMode')=='control-group' and props.get('Restart')=='no' and len(masters)==1 and workers and all(x[1]==masters[0][0] for x in workers) and len(masters)+len(workers)==len(rows):
   need({addr for addr,_ in listeners}==old_listeners|wanted,'LISTENER_SET')
   for addr in wanted:need(any(a==addr and '"nginx"' in line for a,line in listeners),'LISTENER_OWNER')
   return {'master_count':1,'worker_count':len(workers),'exact_lab_listeners':True,'supervised':True}
  need(time.monotonic()<deadline,'READINESS_TIMEOUT');time.sleep(.1)

def probe(canary):
 statuses=[]
 for path,expected in (('/nginx_status',200),('/hlsme/'+canary.decode()+'?token='+canary.decode(),404)):
  client=http.client.HTTPConnection('192.168.56.83',88,timeout=3)
  try:
   client.request('GET',path,headers={'Host':'192.168.56.83','Referer':canary.decode(),'User-Agent':canary.decode(),'Cookie':'synthetic='+canary.decode()});response=client.getresponse();body=response.read(65537)
   need(len(body)<=65536 and response.status==expected,'HTTP_PROBE');statuses.append(response.status)
  finally:client.close()
 return statuses

def stopped(p,f,old_listeners):
 f.bounded(['/usr/bin/systemctl','stop','kaltura-nginx.service'],15)
 need(not nginx_processes(),'NGINX_ORPHAN');need({addr for addr,_ in p.listeners(f)}==old_listeners,'STOP_LISTENERS')
 state=f.bounded(['/usr/bin/systemctl','show','kaltura-nginx.service','--property=ActiveState','--value'],5).strip();need(state in (b'inactive',b'failed'),'STOP_STATE')

def private_scans(canaries,synthetic,p,f,d,require_observed=True):
 # Same bounded private-copy pattern as accepted D2; never publish raw values.
 # Continue remaining reachable files after a finding; report incomplete scopes.
 paths=[];total=0;events=0;access=0;issues=0;complete=True
 for root in (Path('/var/lib/kaltura-php83-nginx-log-sink'),Path('/var/lib/kaltura-php83-nginx-access'),Path('/opt/kaltura/log/nginx')):
  if not root.exists():
   if require_observed and root.name!='nginx':issues+=1
   continue
  private=root.name!='nginx'
  try:
   st=root.lstat();need(stat.S_ISDIR(st.st_mode) and not root.is_symlink(),'LOG_ROOT')
  except BaseException:issues+=1;complete=False;continue
  if private and ((st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode))!=(0,0,0o700) or os.listxattr(root)):issues+=1
  entries=list(itertools.islice(root.rglob('*'),257))
  if len(entries)>256:issues+=1;complete=False
  deadline=time.monotonic()+10
  for path in sorted(entries[:256]):
   if time.monotonic()>=deadline:issues+=1;complete=False;break
   if len(paths)>=100 or total>=8*1024*1024:issues+=1;complete=False;break
   try:
    st=path.lstat();need(not stat.S_ISLNK(st.st_mode),'LOG_LINK')
    if stat.S_ISDIR(st.st_mode):
     if private:need((st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode))==(0,0,0o700) and not os.listxattr(path),'LOG_DIRECTORY_METADATA')
     continue
    metadata=(st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode),st.st_nlink)
    if private and (metadata!=(0,0,0o600,1) or os.listxattr(path)):issues+=1
    need(st.st_size<=8*1024*1024-total,'LOG_SIZE');raw=d.read_log(path);total+=len(raw)
   except BaseException:issues+=1;complete=False;continue
   try:d.reject_canaries(raw,canaries+([synthetic] if synthetic else []))
   except BaseException:issues+=1
   # Root0600 copies let the accepted generated-secret collector inspect even
   # failed-start log bytes. They are never exported by this executor.
   target=RUN/('nginx-private-log-'+str(len(paths))+'.log');f.new_private(target,raw);paths.append(str(target))
   try:
    if root.name=='nginx':need(not raw,'UNREVIEWED_NATIVE_LOG')
    elif root.name=='kaltura-php83-nginx-access':
     for line in raw.splitlines():
      need(re.fullmatch(rb'[1-5][0-9]{2} [0-9]{1,20} [0-9]{1,10}\.[0-9]{3} [0-9]{1,20} [0-9]{1,20} (?:GET|POST|HEAD|OPTIONS|OTHER)',line) is not None,'ACCESS_SCHEMA');access+=1
    elif path.name.startswith('events-'):
     for line in raw.splitlines():
      item=json.loads(line);need(set(item)=={'severity','reason','count'} and type(item['count']) is int and item['count']==1 and item['severity'] in ('emerg','alert','crit','err','warning','notice','info','debug') and item['reason'] in ('permission_denied','file_missing','connect_failure','timeout','upstream_failure','invalid_request','unclassified','malformed','truncated','collector_failure','collector_started','collector_stopped','output_limit','access_success','access_redirect','access_client_error','access_server_error','access_informational'),'EVENT_SCHEMA');events+=1
    elif path.name=='terminal.json':
     item=json.loads(raw)
     need(set(item)=={'status','child_reaped'} and type(item['child_reaped']) is bool and item['status'] in ('STOPPED','FAILED','CHILD_EXIT','TIMEOUT'),'WRAPPER_TERMINAL_SCHEMA')
     if require_observed:need(item=={'status':'STOPPED','child_reaped':True},'WRAPPER_TERMINAL')
    else:raise Failure('LOG_FILE_UNKNOWN')
   except BaseException:issues+=1
 if require_observed and (access<1 or events<1):issues+=1
 return paths,{'files':len(paths),'access_events':access,'closed_events':events,'checks_passed':issues==0,'scan_complete':complete,'findings':issues,'synthetic_probe_executed':bool(synthetic),'scope':'BOUNDED_NEW_LOGS_AND_EXISTING_GENERATED_COLLECTOR'}

def guard(c,m,n,q,p,s,b,f,d,a):
 validate(c);need(sha(p.root_read(Path(__file__).resolve()))==c['executor_sha256'],'EXECUTOR_PIN')
 import socket
 need(os.geteuid()==0 and os.getegid()==0 and socket.gethostname()=='kaltura-php83-lab','LAB_IDENTITY');need(sha(p.root_read('/etc/machine-id'))==MACHINE,'MACHINE')
 ips={v.get('local') for row in json.loads(f.bounded(['/usr/sbin/ip','-j','-4','addr'],10)) for v in row.get('addr_info',[])}
 need('192.168.56.83' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.74'}),'LAB_IP')
 need(not os.path.lexists(RUN) and not os.path.lexists('/usr/sbin/policy-rc.d'),'NO_RESUME')
 for path in ABSENT:need(not os.path.lexists(path),'FRESH_PATH')
 need(not nginx_processes(),'NGINX_PRESENT');identity=n.held(p);cohort(c,p,m)
 baseline=f.bounded(b.DPKG,20);need(sha(baseline)==BASELINE,'BASELINE');need(not f.bounded(['/usr/bin/dpkg','--audit'],20).strip(),'DPKG_AUDIT')
 need(states(f)==dict.fromkeys(SERVICES,'active'),'BASELINE_SERVICES')
 for unit in ('apt-daily.timer','apt-daily-upgrade.timer','apt-daily.service','apt-daily-upgrade.service','unattended-upgrades.service'):
  need(f.bounded(['/usr/bin/systemctl','show',unit,'--property=ActiveState','--value'],10).strip()==b'inactive','APT_CONCURRENCY')
 package(c,p,f);n.source_current(q,p);configs=p.configs(s,b);private=p.private_inventory();_,_,canaries=d.private_inputs()
 n.generated(a,c,True,['/var/lib/kaltura-php83-phase-d1-incremental/apt-private.log','/var/lib/kaltura-php83-phase-d2/apt-private.log'])
 listeners={addr for addr,_ in p.listeners(f)};need(not any(addr.rsplit(':',1)[-1] in ('88','1935') for addr in listeners),'PORT_OCCUPIED')
 return baseline,list(canaries),configs,private,identity,listeners

def execute(c,m,n,q,p,s,b,f,d,a):
 baseline,canaries,configs,private,identity,listeners=guard(c,m,n,q,p,s,b,f,d,a)
 cursor=d.cursor();d.scan_logs(canaries,cursor)
 f.safe_parents(RUN);RUN.mkdir(mode=0o700);os.chmod(RUN,0o700);f.sync_dir(RUN.parent);f.RUN=RUN;b.RUN=RUN
 status='FAILED_REQUIRES_OPERATOR_RECOVERY';attempted=False;contained=False;checks={};handlers={};synthetic=b'';copies=[]
 try:
  def interrupted(sig,frame):raise Failure('INTERRUPTED')
  for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGHUP):handlers[sig]=signal.signal(sig,interrupted)
  for sub in ('archives','apt-lists'):(RUN/sub).mkdir(mode=0o700)
  f.new_private(RUN/'contract.json',json.dumps(c).encode());f.new_private(RUN/'baseline-dpkg.txt',baseline)
  f.new_private(RUN/'services-before.json',json.dumps(states(f)).encode());f.new_private(RUN/'archives.json',json.dumps(f.populate_archives([c['package']])).encode())
  args=b.apt_args();paths=[c['package']['local_deb']]
  simulation=f.bounded(args[:1]+['--simulate']+args[1:]+paths,90);d.reject_canaries(simulation,canaries);f.new_private(RUN/'simulation.log',simulation)
  need(f.parse_solver(simulation)==[('kaltura-nginx','1.23.0-1+php83lab3','amd64',None)],'ONE_PACKAGE_SOLVER')
  need(f.bounded(b.DPKG,20)==baseline and p.configs(s,b)==configs and states(f)==dict.fromkeys(SERVICES,'active'),'PRE_INTENT_DRIFT')
  cohort(c,p,m);package(c,p,f);n.held(p,identity);p.preserve_private(private)
  for path in ABSENT:need(not os.path.lexists(path),'PRE_INTENT_PATH')
  need(f.digest_file(RUN/'archives'/f.archive_name(c['package']))==c['package']['sha256'],'CACHE_PIN')
  f.new_private(RUN/'attempted.json',b'{"normal_apt":true,"resume_supported":false,"workers_policy":"HELD"}');attempted=True
  with open(RUN/'apt-private.log','xb',opener=lambda path,flags:os.open(path,flags,0o600)) as output:
   try:f.bounded(args[:1]+['--yes']+args[1:]+paths,180,output)
   finally:output.flush();os.fsync(output.fileno())
  after=f.bounded(b.DPKG,20);delta(baseline,after);need(not f.bounded(['/usr/bin/dpkg','--audit'],20).strip(),'POST_DPKG_AUDIT')
  for path,pin_value in c['installed_pins'].items():
   p.trusted_chain(path);need(Path(path).stat().st_size<=64*1024*1024 and f.digest_file(path)==pin_value,'INSTALLED_PIN')
  n.held(p,identity);need(p.configs(s,b)==configs,'PRIVATE_CONFIG_DRIFT');p.preserve_private(private)
  runtime=readiness(c,p,f,listeners);synthetic=('SYNTHETIC_D3_'+uuid.uuid4().hex).encode();statuses=probe(synthetic);runtime['http_statuses']=statuses;f.new_private(RUN/'runtime.json',json.dumps(runtime).encode())
  status='D3_INSTALLED_BOUNDED_SYNTHETIC_PROBE_PENDING_FINAL_CHECKS'
 finally:
  with f.signals_blocked():
   try:
    if os.path.lexists('/etc/systemd/system/kaltura-nginx.service') or nginx_processes():stopped(p,f,listeners)
    else:need({addr for addr,_ in p.listeners(f)}==listeners,'FAILURE_LISTENERS')
    contained=True;checks['nginx_stopped']=True
   except BaseException:checks['nginx_stopped']=False;status='FAILED_REQUIRES_OPERATOR_RECOVERY'
   def record_package():
    after=f.bounded(b.DPKG,20);f.new_private(RUN/'after-dpkg.txt',after)
    if status!='FAILED_REQUIRES_OPERATOR_RECOVERY':delta(baseline,after)
   def record_services():
    after=states(f);f.new_private(RUN/'services-after.json',json.dumps(after).encode());need(after==dict.fromkeys(SERVICES,'active'),'SERVICES_CHANGED')
   def scan_new():
    extra,report=private_scans(canaries,synthetic,p,f,d,require_observed=status!='FAILED_REQUIRES_OPERATOR_RECOVERY');copies.extend(extra);f.new_private(RUN/'nginx-log-scan.json',json.dumps(report).encode());need(report['checks_passed'] and report['scan_complete'],'NEW_LOG_AUDIT')
   def generated():
    extras=['/var/lib/kaltura-php83-phase-d1-incremental/apt-private.log','/var/lib/kaltura-php83-phase-d2/apt-private.log']+copies
    if (RUN/'apt-private.log').exists():extras.append(str(RUN/'apt-private.log'))
    report=n.generated(a,c,True,extras);f.new_private(RUN/'generated-audit.json',json.dumps(report).encode())
   actions=(('package_observation',record_package),('baseline_services_preserved',record_services),('hold_and_metadata',lambda:(n.held(p,identity),p.preserve_private(private),need(p.configs(s,b)==configs,'CONFIG_DRIFT'))),('input_canaries',lambda:d.scan_logs(canaries+([synthetic] if synthetic else []),cursor,RUN/'apt-private.log' if (RUN/'apt-private.log').exists() else None)),('new_synthetic_logging',scan_new),('generated_secrets',generated))
   for name,action in actions:
    try:action();checks[name]=True
    except BaseException:checks[name]=False;status='FAILED_REQUIRES_OPERATOR_RECOVERY'
   if status!='FAILED_REQUIRES_OPERATOR_RECOVERY' and all(checks.values()):status='LAB_INCREMENTAL_D3_INSTALLED_SYNTHETIC_LOGGING_CHECKED_NGINX_STOPPED_WORKERS_HELD'
   terminal={'status':status,'checks':checks,'normal_apt_attempted':attempted,'failure_contained':contained,'worker_hold_preserved':checks.get('hold_and_metadata',False),'resume_supported':False,'full_acceptance':False,'full_application_acceptance':False,'phase':'D3','workers_policy':'HELD','pending':PENDING,'privacy_scope':'BOUNDED_SYNTHETIC_AND_EXISTING_COLLECTORS_NOT_FULL_AUTHENTICATED_TRAFFIC'}
   try:f.new_private(RUN/'terminal.json',json.dumps(terminal).encode())
   finally:
    for sig,old in handlers.items():signal.signal(sig,old)
 need(status.startswith('LAB_INCREMENTAL_D3_'),'D3_FAILED');return terminal

def load_d2():
 path=TOOLS/'application-phase-d2-private-logs-r3.py'
 for p in (path,*path.parents):
  st=p.lstat();need(st.st_uid==0 and not st.st_mode&0o022 and not stat.S_ISLNK(st.st_mode),'HELPER_TRUST')
 raw=path.read_bytes();need(len(raw)<=1024*1024 and sha(raw)==D2_PIN,'HELPER_PIN')
 spec=importlib.util.spec_from_loader('pinned_d2',loader=None);module=importlib.util.module_from_spec(spec);module.__file__=str(path);sys.modules['pinned_d2']=module;exec(compile(raw,str(path),'exec'),module.__dict__);return module

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 for name in ('contract','contract-sha256','execute-contract'):parser.add_argument('--'+name,required=True)
 parser.add_argument('--check',action='store_true')
 args=parser.parse_args()
 try:
  need(pin(args.contract_sha256) and args.contract_sha256==args.execute_contract,'EXPLICIT_CONTRACT')
  m=load_d2();n=m.load(TOOLS/'application-phase-d1-incremental.py',m.D1_PIN);q=n.load_c();p=q.load_b()
  raw=p.root_read(args.contract);need(sha(raw)==args.contract_sha256,'CONTRACT_PIN');c=json.loads(raw);validate(c)
  s=p.load('application-services.py',p.UPGRADE_PIN);b=s.load_base();f=b.load_helper('fresh-install.py',b.FRESH_PIN);d=b.load_helper('database-bootstrap.py',q.DB_PIN);a=p.load('generated-secret-audit-r2.py',q.AUDIT_R2_PIN)
  if args.check:
   guard(c,m,n,q,p,s,b,f,d,a);print(json.dumps({'status':'D3_READONLY_GUARD_PASS','apt_executed':False,'full_acceptance':False}));return 0
  print(json.dumps(execute(c,m,n,q,p,s,b,f,d,a)));return 0
 except BaseException as exc:
  code=exc.args[0] if type(exc) is Failure and exc.args and type(exc.args[0]) is str and re.fullmatch('[A-Z_]{1,64}',exc.args[0]) else 'UNEXPECTED_FAILURE'
  print(json.dumps({'status':'BLOCKED_OR_FAILED','failure_code':code,'phase':'D3','full_acceptance':False,'resume_supported':False,'workers_policy':'HELD'}));return 78
if __name__=='__main__':raise SystemExit(main())
