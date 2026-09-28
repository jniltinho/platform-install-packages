"""Exclusive baseline74 TLS configuration; root operator only after source review."""
import argparse,hashlib,json,os,re,secrets,signal,socket,ssl,stat,subprocess,resource
from pathlib import Path
import render
STATE=Path(render.PRIVATE);PORTS=Path('/etc/apache2/ports.conf')
AVAILABLE=Path('/etc/apache2/conf-available/kaltura-baseline-tls-r1.conf')
ENABLED=Path('/etc/apache2/conf-enabled/kaltura-baseline-tls-r1.conf')
LOGS=[Path('/var/log/apache2/baseline_tls_r1_'+k+'.log') for k in ('access','error')]
PINS={str(PORTS):render.PORTS_SHA,'/etc/apache2/apache2.conf':'96e05361253da0d9be1ec6c7c9003cbbb261ba65b659bd6e40ca0eac43093c43','/opt/kaltura/app/configurations/apache/kaltura.conf':'71cae12776233315de4a3af5605c4f4221db3d82f08ee4ef4bb914e53f2ef795'}
class Rejected(ValueError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def sha(b):return hashlib.sha256(b).hexdigest()
def command(argv,timeout=30):
 # Capture in bounded anonymous memory, never print raw config/openssl output.
 out=os.memfd_create('tls-output',os.MFD_CLOEXEC);err=os.memfd_create('tls-error',os.MFD_CLOEXEC)
 def limits():resource.setrlimit(resource.RLIMIT_FSIZE,(65536,65536))
 try:
  p=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True,preexec_fn=limits,env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C','LC_ALL':'C'})
  try:rc=p.wait(timeout=timeout)
  except BaseException:
   try:os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   p.wait(timeout=10);raise
  os.lseek(out,0,0);os.lseek(err,0,0);a=os.read(out,65537);b=os.read(err,65537)
  need(len(a)<=65536 and len(b)<=65536,'COMMAND_OUTPUT');need(rc==0,'COMMAND_FAILED');return a
 finally:os.close(out);os.close(err)
def trusted_parent(path):
 import grp,pwd
 exclusive=not any(x!='root' for x in grp.getgrgid(0).gr_mem) and not any(x.pw_uid!=0 and x.pw_gid==0 for x in pwd.getpwall())
 for p in [Path('/'),*reversed(path.parents[:-1]),path]:
  s=p.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==0 and not s.st_mode&0o002 and (not s.st_mode&0o020 or s.st_gid==0 and exclusive) and not os.listxattr(p),'PARENT_TRUST')
def read_public(path,pin=None):
 trusted_parent(path.parent);s=path.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o644 and not os.listxattr(path),'CONFIG_METADATA')
 raw=path.read_bytes();need(len(raw)<=1024*1024 and (pin is None or sha(raw)==pin),'CONFIG_PIN');return raw

def tls_listeners(raw):
 result=[]
 for line in raw.decode('ascii').splitlines():
  cols=line.split();need(len(cols)>=4,'SOCKET_SHAPE');local=cols[3]
  if local.rsplit(':',1)[-1] in ('443','8443'):result.append(local)
 return sorted(result)
def preflight():
 need(os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline','TARGET')
 rows=json.loads(command(['/usr/sbin/ip','-j','-4','addr']));ips={v.get('local') for r in rows for v in r.get('addr_info',[])}
 need('192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}),'TARGET')
 for p in (STATE,AVAILABLE,ENABLED,*LOGS):trusted_parent(p.parent);need(not os.path.lexists(p),'OWNED_PATH_OCCUPIED')
 before={p:read_public(Path(p),h) for p,h in PINS.items()}
 need(tls_listeners(command(['/usr/bin/ss','-H','-ltn']))==[],'TLS_LISTENER_EXISTS')
 need(command(['/usr/bin/systemctl','is-active','apache2']).strip()==b'active','APACHE_NOT_ACTIVE')
 modules=command(['/usr/sbin/apache2ctl','-M'])
 need(b'ssl_module' not in modules and b'gnutls_module' not in modules and b'php7_module' in modules,'MODULE_BASELINE')
 for p in ['/usr/lib/apache2/modules/mod_ssl.so','/usr/bin/openssl']:
  s=Path(p).lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==0 and not s.st_mode&0o022,'BINARY_TRUST')
 command(['/usr/sbin/apache2ctl','configtest']);render.ports_after(before[str(PORTS)])
 return before

def create(path,data,mode):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode)
 with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),mode)
 s=path.lstat();return (s.st_dev,s.st_ino)
def same_inode(path,identity):
 s=path.lstat();return (s.st_dev,s.st_ino)==identity
def replace_ports(expected,data):
 need(read_public(PORTS)==expected,'PORTS_DRIFT')
 p=PORTS.parent/('.baseline-tls-r1-'+secrets.token_hex(8));ident=create(p,data,0o644)
 try:
  need(read_public(PORTS)==expected,'PORTS_DRIFT');os.replace(p,PORTS)
 finally:
  if p.exists() and same_inode(p,ident):p.unlink()

def certificates():
 old=os.umask(0o077)
 try:
  command(['/usr/bin/openssl','req','-x509','-newkey','rsa:3072','-sha256','-nodes','-days','7','-subj','/CN=KalturaBaselineLabCA','-keyout',str(STATE/'ca.key'),'-out',str(STATE/'ca.crt'),'-addext','basicConstraints=critical,CA:TRUE,pathlen:0','-addext','keyUsage=critical,keyCertSign,cRLSign'],60)
  command(['/usr/bin/openssl','req','-new','-newkey','rsa:3072','-sha256','-nodes','-subj','/CN=192.168.56.74','-keyout',str(STATE/'server.key'),'-out',str(STATE/'server.csr')],60)
  create(STATE/'leaf.ext',render.leaf_extensions().encode(),0o600)
  command(['/usr/bin/openssl','x509','-req','-in',str(STATE/'server.csr'),'-CA',str(STATE/'ca.crt'),'-CAkey',str(STATE/'ca.key'),'-set_serial','0x'+secrets.token_hex(16),'-days','7','-sha256','-extfile',str(STATE/'leaf.ext'),'-out',str(STATE/'server.crt')])
  for n in ['ca.key','ca.crt','server.key','server.csr','server.crt','leaf.ext']:
   p=STATE/n;s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600,'CERT_METADATA')
  command(['/usr/bin/openssl','verify','-CAfile',str(STATE/'ca.crt'),'-verify_ip',render.IP,str(STATE/'server.crt')])
 finally:os.umask(old)
def handshake(cafile):
 context=ssl.create_default_context(cafile=cafile);context.minimum_version=ssl.TLSVersion.TLSv1_2
 with socket.create_connection((render.IP,8443),timeout=5) as raw:
  with context.wrap_socket(raw,server_hostname=render.IP) as conn:return conn.version()
def interrupted(signum,frame):
 signal.signal(signal.SIGTERM,signal.SIG_IGN);signal.signal(signal.SIGINT,signal.SIG_IGN);raise Rejected('INTERRUPTED')
def main(execute=False):
 before=preflight()
 if not execute:print(json.dumps({'status':'TLS_PREFLIGHT_ONLY','full_acceptance':False}));return 0
 STATE.mkdir(mode=0o700);os.chmod(STATE,0o700)
 create(STATE/'intent.json',json.dumps({'status':'INTENT','before_pins':PINS}).encode(),0o600)
 for p,b in before.items():create(STATE/(Path(p).name+'.before'),b,0o600)
 changed=False;available_id=None;enabled_id=None;restart=False;after=render.ports_after(before[str(PORTS)]);conf=render.config().encode()
 result={'status':'TLS_SETUP_FAILED','rollback_complete':False,'full_acceptance':False,'keys_exported':False}
 signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
 try:
  certificates()
  for p in LOGS:create(p,b'',0o600)
  prior=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGTERM,signal.SIGINT})
  try:
   available_id=create(AVAILABLE,conf,0o644)
   replace_ports(before[str(PORTS)],after);changed=True
   os.symlink(str(AVAILABLE),ENABLED);s=ENABLED.lstat();enabled_id=(s.st_dev,s.st_ino)
  finally:signal.pthread_sigmask(signal.SIG_SETMASK,prior)
  command(['/usr/sbin/apache2ctl','configtest']);restart=True
  command(['/usr/bin/systemctl','restart','apache2'],60)
  need(command(['/usr/bin/systemctl','is-active','apache2']).strip()==b'active','APACHE_NOT_ACTIVE')
  need(tls_listeners(command(['/usr/bin/ss','-H','-ltn']))==['192.168.56.74:8443'],'LISTENER_SCOPE')
  version=handshake(str(STATE/'ca.crt'))
  try:handshake(None)
  except ssl.SSLCertVerificationError:pass
  else:raise Rejected('WRONG_CA_ACCEPTED')
  for p,h in PINS.items():
   if p!=str(PORTS):read_public(Path(p),h)
  need(read_public(PORTS)==after and read_public(AVAILABLE)==conf and same_inode(ENABLED,enabled_id) and os.readlink(ENABLED)==str(AVAILABLE),'AFTER_DRIFT')
  ca=(STATE/'ca.crt').read_bytes();der=ssl.PEM_cert_to_DER_cert(ca.decode())
  result.update(status='LAB_TLS_INSTALLED_TRUSTED_HANDSHAKE_ONLY',tls_version=version,public_ca_pem_sha256=sha(ca),public_ca_der_sha256=sha(der),wrong_ca_rejected=True,listener='192.168.56.74:8443',http_api_tested=False)
 except Exception as e:
  result['failure_code']=str(e) if isinstance(e,Rejected) else 'UNEXPECTED'
  signal.signal(signal.SIGTERM,signal.SIG_IGN);signal.signal(signal.SIGINT,signal.SIG_IGN)
  try:
   if enabled_id is not None:need(same_inode(ENABLED,enabled_id) and os.readlink(ENABLED)==str(AVAILABLE),'ROLLBACK_LINK_DRIFT');ENABLED.unlink()
   if changed:replace_ports(after,before[str(PORTS)])
   if available_id is not None:need(same_inode(AVAILABLE,available_id) and read_public(AVAILABLE)==conf,'ROLLBACK_CONFIG_DRIFT');AVAILABLE.unlink()
   command(['/usr/sbin/apache2ctl','configtest'])
   if restart:command(['/usr/bin/systemctl','restart','apache2'],60)
   need(command(['/usr/bin/systemctl','is-active','apache2']).strip()==b'active' and tls_listeners(command(['/usr/bin/ss','-H','-ltn']))==[],'ROLLBACK_STATE')
   result['rollback_complete']=True
  except Exception:result['rollback_complete']=False
 create(STATE/'terminal.json',json.dumps(result,sort_keys=True).encode(),0o600)
 print(json.dumps(result,sort_keys=True));return 0 if result['status']=='LAB_TLS_INSTALLED_TRUSTED_HANDSHAKE_ONLY' else 1
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');a=p.parse_args()
 try:raise SystemExit(main(a.execute))
 except Exception:print('{"status":"TLS_REJECTED_OR_INCOMPLETE","full_acceptance":false}');raise SystemExit(1)
