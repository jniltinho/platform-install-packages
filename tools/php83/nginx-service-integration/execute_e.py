"""Fresh .83 hookless server meta-package E; normal offline APT only, no starts."""
import argparse,hashlib,importlib.util,io,json,os,re,signal,stat,sys,tarfile
from pathlib import Path
RUN=Path('/var/lib/kaltura-php83-phase-e')
TOOLS=Path('/var/lib/kaltura-php83-pilot/tools')
D3_PIN='a013992d1329df3f072d321cc2aeebe985c4bf3cf000ca5c8c2864d7aa36b99f'
BASELINE='de3df72f0f65e5ab9959f8f5470ff063815301a6174c1c8e090a1415e8432731'
D3_TERMINAL='d1cbc949a3f66752a7551ecd540d36795743893462054462dc45787089765478'
D3_CONTRACT='486d87fbcfc7a4e760d6f10544aaf2469e86f218152af30c76ccd7c10c4a4120'
MACHINE='ad9adac39d0fb440883f0b82c8c45058596b74a6d9e98da2746e4dbdafd3aad8'
ROW={'package':'kaltura-server','version':'18.20.0-1+php83lab1','architecture':'all','previous':None,'sha256':'e53154baff6e5f091a0ee876e558e0469ff38e06f7b4ab5b4207d29573c1b387','local_deb':'/var/lib/kaltura-php83-pilot/packages-phase-d/kaltura-server_18.20.0-1+php83lab1_all.deb'}
PENDING=['full_seed_persistence','effective_authorization','full_application_acceptance']
SUCCESS='LAB_INCREMENTAL_E_META_INSTALLED_SERVICES_UNCHANGED_NGINX_STOPPED_WORKERS_HELD'
class Failure(Exception):pass
def need(ok,code):
 if not ok:raise Failure(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def pin(value):return type(value) is str and re.fullmatch('[a-f0-9]{64}',value) is not None

def validate(c):
 need(type(c) is dict and type(c.get('schema')) is int and c['schema']==1 and c.get('phase')=='E' and c.get('status')=='LAB_INCREMENTAL_AUTHORIZED','CONTRACT')
 need(c.get('package')==ROW and c.get('full_acceptance') is False and c.get('release_authorized') is False and c.get('workers_policy')=='HELD' and c.get('pending')==PENDING,'SCOPE')
 need(c.get('machine_id_sha256')==MACHINE and c.get('baseline_dpkg_sha256')==BASELINE and c.get('d3_terminal_sha256')==D3_TERMINAL,'COHORT')
 for key in ('executor_sha256','snapshot_sha256'):need(pin(c.get(key)),'PIN')
 need(type(c.get('audit_since')) is str and re.fullmatch(r'2026-09-[0-9]{2}T[0-9:]{8}Z',c['audit_since']),'AUDIT_WINDOW')

def hookless(control_raw,data_raw):
 need(len(control_raw)<=65536 and len(data_raw)<=65536,'ARCHIVE_LIMIT')
 with tarfile.open(fileobj=io.BytesIO(control_raw),mode='r:') as archive:
  members=archive.getmembers();need(len(members)==3 and {m.name for m in members}=={'.','./control','./md5sums'},'CONTROL_MEMBERS')
  for member in members:
   need(member.isdir() if member.name=='.' else member.isfile(),'CONTROL_TYPE')
   need(member.uid==0 and member.gid==0 and member.size<=8192,'CONTROL_METADATA')
   if member.name=='./md5sums':need(archive.extractfile(member).read()==b'','EMPTY_MD5SUMS')
  control=archive.extractfile('./control').read().decode()
  fields={line.split(': ',1)[0]:line.split(': ',1)[1] for line in control.splitlines() if ': ' in line and not line.startswith(' ')}
  need(all(fields.get(k)==v for k,v in {'Package':ROW['package'],'Version':ROW['version'],'Architecture':'all'}.items()),'CONTROL_IDENTITY')
 with tarfile.open(fileobj=io.BytesIO(data_raw),mode='r:') as archive:
  members=archive.getmembers();need(len(members)==1 and members[0].name=='.' and members[0].isdir() and members[0].uid==0 and members[0].gid==0,'EMPTY_DATA_ONLY')
 return True

def package(p,f):
 p.trusted_chain(ROW['local_deb']);need(f.digest_file(ROW['local_deb'])==ROW['sha256'],'DEB_PIN')
 hookless(f.bounded(['/usr/bin/dpkg-deb','--ctrl-tarfile',ROW['local_deb']],20),f.bounded(['/usr/bin/dpkg-deb','--fsys-tarfile',ROW['local_deb']],20))

def delta(before,after):
 old={line.split(b'\t')[0]:line for line in before.splitlines()};new={line.split(b'\t')[0]:line for line in after.splitlines()}
 need({key for key in old.keys()|new.keys() if old.get(key)!=new.get(key)}=={b'kaltura-server'},'EXACT_META_DELTA')
 need(new[b'kaltura-server']==b'kaltura-server\t18.20.0-1+php83lab1\tall\tii ','META_CONFIGURED')

def no_nginx(x,f):
 need(not x.nginx_processes(),'NGINX_RUNNING')
 need(f.bounded(['/usr/bin/systemctl','show','kaltura-nginx.service','--property=ActiveState','--value'],10).strip()==b'inactive','NGINX_NOT_STOPPED')

def cohort(c,x,p):
 raw=p.root_read('/var/lib/kaltura-php83-phase-d3/terminal.json');need(sha(raw)==D3_TERMINAL,'D3_TERMINAL');result=json.loads(raw)
 need(result.get('status')=='LAB_INCREMENTAL_D3_INSTALLED_SYNTHETIC_LOGGING_CHECKED_NGINX_STOPPED_WORKERS_HELD' and result.get('worker_hold_preserved') is True and result.get('full_acceptance') is False and len(result.get('checks',{}))==7 and all(v is True for v in result['checks'].values()),'D3_SUCCESS')
 raw=p.root_read('/var/lib/kaltura-php83-phase-d3/contract.json');need(sha(raw)==D3_CONTRACT,'D3_CONTRACT');d3=json.loads(raw);x.validate(d3);need(d3['audit_since']==c['audit_since'],'AUDIT_COHORT')
 raw=p.root_read('/var/lib/kaltura-php83-pilot/proofs/phase-e-snapshot.json');need(sha(raw)==c['snapshot_sha256'],'SNAPSHOT_PIN');snapshot=json.loads(raw)
 need(snapshot.get('status')=='PRE_E_STATE_PRESERVED' and snapshot.get('machine_id_sha256')==MACHINE and snapshot.get('baseline_dpkg_sha256')==BASELINE and snapshot.get('restore_automatically') is False and re.fullmatch('[a-f0-9-]{36}',snapshot.get('snapshot_id','')),'SNAPSHOT')
 return d3

def installed(d3,p,f):
 for path,expected in d3['installed_pins'].items():p.trusted_chain(path);need(f.digest_file(path)==expected,'D3_INSTALLED_DRIFT')

def new_log_identity(p,f):
 # Readonly, private in-memory identities; no file/secret hashes exported.
 result={};count=0
 for root in (Path('/var/lib/kaltura-php83-nginx-log-sink'),Path('/var/lib/kaltura-php83-nginx-access')):
  p.trusted_chain(root,directory=True)
  need((root.stat().st_uid,root.stat().st_gid,stat.S_IMODE(root.stat().st_mode))==(0,0,0o700),'NEW_LOG_ROOT')
  for path in root.rglob('*'):
   count+=1;need(count<=128,'LOG_COUNT');st=path.lstat();need(not path.is_symlink() and not os.listxattr(path),'LOG_METADATA')
   if path.is_dir():need((st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode))==(0,0,0o700),'LOG_DIR');continue
   need(stat.S_ISREG(st.st_mode) and (st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode),st.st_nlink)==(0,0,0o600,1) and st.st_size<=4*1024*1024,'LOG_FILE')
   result[str(path)]=(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,f.digest_file(path))
 return result

def extras(p):
 result=['/var/lib/kaltura-php83-phase-d1-incremental/apt-private.log','/var/lib/kaltura-php83-phase-d2/apt-private.log','/var/lib/kaltura-php83-phase-d3/apt-private.log']
 paths=list(Path('/var/lib/kaltura-php83-phase-d3').glob('nginx-private-log-*.log'));need(len(paths)<=100,'D3_LOG_COUNT')
 for path in paths:p.root_read(path);result.append(str(path))
 return result

def guard(c,x,n,q,p,s,b,f,d,a):
 validate(c);need(sha(p.root_read(Path(__file__).resolve()))==c['executor_sha256'],'EXECUTOR_PIN')
 import socket
 need(os.geteuid()==0 and os.getegid()==0 and socket.gethostname()=='kaltura-php83-lab','LAB_IDENTITY');need(sha(p.root_read('/etc/machine-id'))==MACHINE,'MACHINE')
 ips={v.get('local') for row in json.loads(f.bounded(['/usr/sbin/ip','-j','-4','addr'],10)) for v in row.get('addr_info',[])}
 need('192.168.56.83' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.74'}),'LAB_IP')
 need(not os.path.lexists(RUN) and not os.path.lexists('/usr/sbin/policy-rc.d'),'NO_RESUME')
 d3=cohort(c,x,p);identity=n.held(p);no_nginx(x,f);installed(d3,p,f)
 baseline=f.bounded(b.DPKG,20);need(sha(baseline)==BASELINE,'BASELINE');old=p.root_read('/var/lib/kaltura-php83-phase-d3/baseline-dpkg.txt');need(sha(old)==x.BASELINE,'PRE_D3_PIN');x.delta(old,baseline)
 need(not f.bounded(['/usr/bin/dpkg','--audit'],20).strip(),'DPKG_AUDIT');need(x.states(f)==dict.fromkeys(x.SERVICES,'active'),'BASELINE_SERVICES')
 for unit in ('apt-daily.timer','apt-daily-upgrade.timer','apt-daily.service','apt-daily-upgrade.service','unattended-upgrades.service'):
  need(f.bounded(['/usr/bin/systemctl','show',unit,'--property=ActiveState','--value'],10).strip()==b'inactive','APT_CONCURRENCY')
 package(p,f);n.source_current(q,p);configs=p.configs(s,b);private=p.private_inventory();logs=new_log_identity(p,f);_,_,canaries=d.private_inputs();n.generated(a,c,True,extras(p))
 listeners={addr for addr,_ in p.listeners(f)};need(not any(addr.rsplit(':',1)[-1] in ('88','1935') for addr in listeners),'NGINX_LISTENERS')
 return d3,baseline,list(canaries),configs,private,logs,identity,listeners

def execute(c,x,n,q,p,s,b,f,d,a):
 d3,baseline,canaries,configs,private,logs,identity,listeners=guard(c,x,n,q,p,s,b,f,d,a)
 cursor=d.cursor();d.scan_logs(canaries,cursor);f.safe_parents(RUN);RUN.mkdir(mode=0o700);os.chmod(RUN,0o700);f.sync_dir(RUN.parent);f.RUN=RUN;b.RUN=RUN
 status='FAILED_REQUIRES_OPERATOR_RECOVERY';attempted=False;checks={};handlers={}
 def invariants():
  n.held(p,identity);no_nginx(x,f);installed(d3,p,f);p.preserve_private(private)
  need(p.configs(s,b)==configs and new_log_identity(p,f)==logs,'PRIVATE_DRIFT')
  need(x.states(f)==dict.fromkeys(x.SERVICES,'active') and {addr for addr,_ in p.listeners(f)}==listeners,'SERVICES_LISTENERS_CHANGED')
 try:
  def interrupted(sig,frame):raise Failure('INTERRUPTED')
  for sig in (signal.SIGTERM,signal.SIGINT,signal.SIGHUP):handlers[sig]=signal.signal(sig,interrupted)
  for name in ('archives','apt-lists'):(RUN/name).mkdir(mode=0o700)
  f.new_private(RUN/'contract.json',json.dumps(c).encode());f.new_private(RUN/'baseline-dpkg.txt',baseline);f.new_private(RUN/'services-before.json',json.dumps(x.states(f)).encode())
  f.new_private(RUN/'archives.json',json.dumps(f.populate_archives([ROW])).encode());args=b.apt_args();paths=[ROW['local_deb']]
  simulation=f.bounded(args[:1]+['--simulate']+args[1:]+paths,90);d.reject_canaries(simulation,canaries);f.new_private(RUN/'simulation.log',simulation)
  need(f.parse_solver(simulation)==[('kaltura-server','18.20.0-1+php83lab1','all',None)],'ONE_PACKAGE_SOLVER')
  need(f.bounded(b.DPKG,20)==baseline,'PRE_INTENT_DPKG');cohort(c,x,p);package(p,f);invariants();need(f.digest_file(RUN/'archives'/f.archive_name(ROW))==ROW['sha256'],'CACHE_PIN')
  f.new_private(RUN/'attempted.json',b'{"normal_apt":true,"resume_supported":false,"service_actions":false,"workers_policy":"HELD"}');attempted=True
  with open(RUN/'apt-private.log','xb',opener=lambda path,flags:os.open(path,flags,0o600)) as output:
   try:f.bounded(args[:1]+['--yes']+args[1:]+paths,90,output)
   finally:output.flush();os.fsync(output.fileno())
  after=f.bounded(b.DPKG,20);delta(baseline,after);need(not f.bounded(['/usr/bin/dpkg','--audit'],20).strip(),'POST_DPKG_AUDIT');invariants();status=SUCCESS
 finally:
  with f.signals_blocked():
   def record_package():
    after=f.bounded(b.DPKG,20);f.new_private(RUN/'after-dpkg.txt',after)
    if status==SUCCESS:delta(baseline,after)
   def generated():
    paths=extras(p)+([str(RUN/'apt-private.log')] if (RUN/'apt-private.log').exists() else []);report=n.generated(a,c,True,paths);f.new_private(RUN/'generated-audit.json',json.dumps(report).encode())
   for name,action in (('package_observation',record_package),('unchanged_runtime_and_privacy_metadata',invariants),('input_canaries',lambda:d.scan_logs(canaries,cursor,RUN/'apt-private.log' if (RUN/'apt-private.log').exists() else None)),('generated_secrets',generated)):
    try:action();checks[name]=True
    except BaseException:checks[name]=False;status='FAILED_REQUIRES_OPERATOR_RECOVERY'
   try:f.new_private(RUN/'services-after.json',json.dumps(x.states(f)).encode())
   except BaseException:status='FAILED_REQUIRES_OPERATOR_RECOVERY'
   terminal={'status':status,'checks':checks,'normal_apt_attempted':attempted,'service_actions':False,'worker_hold_preserved':checks.get('unchanged_runtime_and_privacy_metadata',False),'resume_supported':False,'full_acceptance':False,'full_application_acceptance':False,'phase':'E','workers_policy':'HELD','pending':PENDING}
   try:f.new_private(RUN/'terminal.json',json.dumps(terminal).encode())
   finally:
    for sig,old in handlers.items():signal.signal(sig,old)
 need(status==SUCCESS,'E_FAILED');return terminal

def load_d3():
 path=TOOLS/'execute-nginx-d3-r1.py'
 for p in (path,*path.parents):
  st=p.lstat();need(st.st_uid==0 and not st.st_mode&0o022 and not stat.S_ISLNK(st.st_mode),'HELPER_TRUST')
 raw=path.read_bytes();need(len(raw)<=1024*1024 and sha(raw)==D3_PIN,'HELPER_PIN')
 spec=importlib.util.spec_from_loader('pinned_d3',loader=None);module=importlib.util.module_from_spec(spec);module.__file__=str(path);sys.modules['pinned_d3']=module;exec(compile(raw,str(path),'exec'),module.__dict__);return module

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 for name in ('contract','contract-sha256','execute-contract'):parser.add_argument('--'+name,required=True)
 parser.add_argument('--check',action='store_true');args=parser.parse_args()
 try:
  need(pin(args.contract_sha256) and args.contract_sha256==args.execute_contract,'EXPLICIT_CONTRACT')
  x=load_d3();m=x.load_d2();n=m.load(TOOLS/'application-phase-d1-incremental.py',m.D1_PIN);q=n.load_c();p=q.load_b()
  raw=p.root_read(args.contract);need(sha(raw)==args.contract_sha256,'CONTRACT_PIN');c=json.loads(raw);validate(c)
  s=p.load('application-services.py',p.UPGRADE_PIN);b=s.load_base();f=b.load_helper('fresh-install.py',b.FRESH_PIN);d=b.load_helper('database-bootstrap.py',q.DB_PIN);a=p.load('generated-secret-audit-r2.py',q.AUDIT_R2_PIN)
  if args.check:guard(c,x,n,q,p,s,b,f,d,a);print(json.dumps({'status':'E_READONLY_GUARD_PASS','apt_executed':False,'full_acceptance':False}));return 0
  print(json.dumps(execute(c,x,n,q,p,s,b,f,d,a)));return 0
 except BaseException as exc:
  code=exc.args[0] if type(exc) is Failure and exc.args and type(exc.args[0]) is str and re.fullmatch('[A-Z_]{1,64}',exc.args[0]) else 'UNEXPECTED_FAILURE'
  print(json.dumps({'status':'BLOCKED_OR_FAILED','failure_code':code,'phase':'E','full_acceptance':False,'resume_supported':False,'workers_policy':'HELD'}));return 78
if __name__=='__main__':raise SystemExit(main())
