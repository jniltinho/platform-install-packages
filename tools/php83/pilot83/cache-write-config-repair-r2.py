"""One-shot .83 public cache placeholder repair; no service/package/database writes."""
import argparse,grp,hashlib,json,os,pwd,re,socket,stat,types
from pathlib import Path
RUN=Path('/var/lib/kaltura-php83-cache-write-repair-r1')
TARGET=Path('/opt/kaltura/app/configurations/kRemoteMemCacheConf.ini')
TEMP=TARGET.with_name('.pilot83-cache-write-r1.ini')
TOOLS=Path('/var/lib/kaltura-php83-pilot/tools')
D1_RUN=Path('/var/lib/kaltura-php83-phase-d1-incremental')
SNAPSHOT=Path('/var/lib/kaltura-php83-pilot/proofs/cache-write-repair-r1-snapshot.json')
D1_PIN='98e813f23dbdedf3c1774340d5feddfd685d544cc84719a0e931e976b10a0b8f'
MACHINE='ad9adac39d0fb440883f0b82c8c45058596b74a6d9e98da2746e4dbdafd3aad8'
BEFORE='77b21c0ddf8e9987a014c0283639458b8da46d2df010438ec62ab92433d63980'
AFTER='238c2f883b8ec0a09d15b4bf5676bc8b593c6ddce467a3ae9820bcdf34948ee8'
TOKEN=b'@MEMACHED_HOSTNAME_FOR_WRITE@'
SUCCESS='LAB_CACHE_WRITE_PLACEHOLDER_REPAIRED_WORKERS_HELD'
def need(ok,code):
 if not ok:raise ValueError(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parents(path):
 for p in Path(path).parents:
  s=p.lstat();known=(p==Path('/opt/kaltura/app/configurations') and (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(0,0,0o775))
  if known:need(set(grp.getgrgid(0).gr_mem)<={'root'} and all(x.pw_name=='root' for x in pwd.getpwall() if x.pw_gid==0),'ROOT_GROUP')
  need(stat.S_ISDIR(s.st_mode) and s.st_uid==0 and (not s.st_mode&0o022 or known) and not os.listxattr(p,follow_symlinks=False),'PARENT_TRUST')
def read(path,pin=None,exact=False):
 path=Path(path);parents(path);fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 with os.fdopen(fd,'rb') as stream:
  s=os.fstat(stream.fileno());need(stat.S_ISREG(s.st_mode) and s.st_uid==0 and s.st_nlink==1 and not s.st_mode&0o022 and not os.listxattr(stream.fileno()),'FILE_TRUST')
  if exact:need((s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(0,0,0o644),'CONFIG_METADATA')
  raw=stream.read(1048577);t=os.fstat(stream.fileno())
  need(len(raw)<=1048576 and identity(s)==identity(t),'READ_CHANGED')
 need(pin is None or sha(raw)==pin,'FILE_PIN');return raw,s
def identity(s):return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def sync(path):
 fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
def private(path,raw):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
 sync(path.parent)
def transform(raw):
 need(len(raw)==341 and sha(raw)==BEFORE and raw.count(TOKEN)==1,'PREIMAGE')
 out=raw.replace(TOKEN,b'127.0.0.1');need(sha(out)==AFTER,'POSTIMAGE');return out
def load():
 raw,_=read(TOOLS/'application-phase-d1-incremental.py',D1_PIN)
 n=types.ModuleType('pinned_d1');exec(compile(raw,'pinned_d1','exec'),n.__dict__);return n
def validate(c):
 need(c.get('schema')==1 and type(c['schema']) is int and c.get('status')=='LAB_CACHE_WRITE_REPAIR_AUTHORIZED','CONTRACT')
 need(c.get('machine_id_sha256')==MACHINE and c.get('full_acceptance') is False and c.get('release_authorized') is False,'SCOPE')
 for key in ('executor_sha256','snapshot_sha256','baseline_dpkg_sha256','d1_contract_sha256','d1_terminal_sha256'):
  need(isinstance(c.get(key),str) and re.fullmatch('[a-f0-9]{64}',c[key]),'CONTRACT_PIN')
def stopped(b,f):need(b.states(f)=={'apache2':'inactive','monit':'inactive','mariadb':'active'},'SERVICES')
def fresh():
 for p in (RUN,TEMP,Path('/var/lib/kaltura-php83-phase-d2'),Path('/var/lib/kaltura-php83-phase-d2-incremental'),Path('/usr/sbin/policy-rc.d')):need(not os.path.lexists(p),'NO_RESUME')
def apply(c,n,q,p,s,b,f,d,a):
 validate(c);need(os.geteuid()==os.getegid()==0 and socket.gethostname()=='kaltura-php83-lab','HOST')
 need(sha(read('/etc/machine-id')[0])==MACHINE,'MACHINE')
 ips={v.get('local') for x in json.loads(f.bounded(['/usr/sbin/ip','-j','-4','addr'],20)) for v in x.get('addr_info',[])}
 need('192.168.56.83' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.74'}),'IP')
 fresh();parents(RUN);stopped(b,f)
 dc=json.loads(read(D1_RUN/'contract.json',c['d1_contract_sha256'])[0]);n.validate(dc);n.seed_gate(dc,p,q)
 terminal=json.loads(read(D1_RUN/'terminal.json',c['d1_terminal_sha256'])[0])
 need(terminal.get('status')==n.SUCCESS and terminal.get('worker_hold_preserved') is True and terminal.get('full_acceptance') is False and terminal.get('checks')==dict.fromkeys(('package_observation','metadata','input_canaries','generated_secrets'),True),'D1_SUCCESS')
 baseline=f.bounded(b.DPKG,30);need(sha(baseline)==c['baseline_dpkg_sha256'],'BASELINE')
 original=read(D1_RUN/'baseline-dpkg.txt',dc['baseline_dpkg_sha256'])[0];n.baseline_check(original,p);n.delta(original,baseline)
 proof=json.loads(read(SNAPSHOT,c['snapshot_sha256'])[0])
 need(proof.get('status')=='PRE_CACHE_WRITE_REPAIR_STATE_PRESERVED' and proof.get('machine_id_sha256')==MACHINE and proof.get('baseline_dpkg_sha256')==c['baseline_dpkg_sha256'] and proof.get('restore_automatically') is False and re.fullmatch('[a-f0-9-]{36}',proof.get('snapshot_id','')),'SNAPSHOT')
 n.source_current(q,p);p.canonical_config(b,a);q.log_modes(after=True);held=n.held(p);configs=p.configs(s,b)
 _,_,canaries=d.private_inputs();cursor=d.cursor();d.scan_logs(canaries,cursor);n.generated(a,dc,True,[str(D1_RUN/'apt-private.log')])
 raw,st=read(TARGET,BEFORE,True);new=transform(raw)
 RUN.mkdir(mode=0o700);os.chmod(RUN,0o700);sync(RUN.parent)
 result={'status':'FAILED_REQUIRES_OPERATOR_RECOVERY','full_acceptance':False,'resume_supported':False,'config_replaced':False,'privacy_scan_passed':False,'worker_hold_preserved':False}
 # Deferred signals cannot bypass post-write checks/terminal. No external service mutation.
 with f.signals_blocked():
  try:
   private(RUN/'contract.json',json.dumps(c).encode());private(RUN/'original.ini',raw)
   private(RUN/'intent.json',json.dumps({'status':'INTENT_BEFORE_EXACT_REPLACEMENT','before':BEFORE,'after':AFTER,'snapshot_sha256':c['snapshot_sha256']}).encode())
   stopped(b,f);n.held(p,held);need(f.bounded(b.DPKG,30)==baseline,'BASELINE_DRIFT')
   now,ns=read(TARGET,BEFORE,True);need(now==raw and identity(ns)==identity(st),'CONFIG_DRIFT')
   parents(TEMP);fd=os.open(TEMP,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
   with os.fdopen(fd,'wb') as out:
    need(os.fstat(out.fileno()).st_gid==0,'TEMP_GROUP');out.write(new);out.flush();os.fchmod(out.fileno(),0o644);os.fsync(out.fileno())
   need(identity(read(TARGET,BEFORE,True)[1])==identity(st),'CONFIG_DRIFT')
   read(TEMP,AFTER,True);os.replace(TEMP,TARGET);sync(TARGET.parent);result['config_replaced']=True
   read(TARGET,AFTER,True);need(p.configs(s,b)==configs and f.bounded(b.DPKG,30)==baseline,'UNRELATED_DRIFT')
   result['status']=SUCCESS
  finally:
   for name,fn in (
    ('worker_hold_preserved',lambda:(stopped(b,f),n.held(p,held),q.log_modes(after=True))),
    ('privacy_scan_passed',lambda:(d.scan_logs(canaries,cursor),n.generated(a,dc,True,[str(D1_RUN/'apt-private.log')])))):
    try:fn();result[name]=True
    except BaseException:result[name]=False;result['status']='FAILED_REQUIRES_OPERATOR_RECOVERY'
   private(RUN/'terminal.json',json.dumps(result).encode())
 need(result['status']==SUCCESS,'REPAIR_FAILED');return result

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for key in ('contract','contract-sha256','execute-contract'):ap.add_argument('--'+key,required=True)
 args=ap.parse_args()
 try:
  need(args.contract_sha256==args.execute_contract,'EXPLICIT_CONTRACT');c=json.loads(read(args.contract,args.contract_sha256)[0]);validate(c)
  read(Path(__file__).resolve(),c['executor_sha256']);n=load();q=n.load_c();p=q.load_b();s=p.load('application-services.py',p.UPGRADE_PIN);b=s.load_base();f=b.load_helper('fresh-install.py',b.FRESH_PIN);d=b.load_helper('database-bootstrap.py',q.DB_PIN);a=p.load('generated-secret-audit-r2.py',q.AUDIT_R2_PIN)
  print(json.dumps(apply(c,n,q,p,s,b,f,d,a)));return 0
 except BaseException:print('{"status":"BLOCKED_OR_FAILED","full_acceptance":false,"resume_supported":false}');return 78
if __name__=='__main__':raise SystemExit(main())
