"""One owned PHP provider file; no app bootstrap, credentials, SQL or service changes."""
import base64,grp,hashlib,importlib.util,json,os,pwd,re,socket,stat,subprocess,sys,signal
from pathlib import Path
WEB=Path('/opt/kaltura/app/api_v3/web')
class Rejected(ValueError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def root_group_exclusive():
 return not any(n!='root' for n in grp.getgrgid(0).gr_mem) and not any(u.pw_uid!=0 and u.pw_gid==0 for u in pwd.getpwall())
def trusted(info,attrs,exclusive):
 return stat.S_ISDIR(info.st_mode) and info.st_uid==info.st_gid==0 and stat.S_IMODE(info.st_mode) in ((0o755,0o775) if exclusive else (0o755,)) and not attrs
def web_fd():
 exclusive=root_group_exclusive();fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  need(trusted(os.fstat(fd),os.listxattr(fd),exclusive),'WEB_PARENT')
  for part in WEB.parts[1:]:
   nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=nxt
   need(trusted(os.fstat(fd),os.listxattr(fd),exclusive),'WEB_PARENT')
  return fd
 except BaseException:os.close(fd);raise
def check():
 need(os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline','TARGET')
 a=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10));ips={v.get('local') for r in a for v in r.get('addr_info',[])}
 need('192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}),'TARGET')
 fd=web_fd();os.close(fd)
def project(data,nonce):
 need(type(data) is dict and set(data)=={'nonce','version','sapi','modules','ini_file'},'RESPONSE_SCHEMA')
 need(data['nonce']==nonce and type(data['version']) is str and re.fullmatch(r'7\.4\.\d{1,3}',data['version']) and data['sapi']=='apache2handler','WEB_PROVIDER')
 modules=data['modules'];need(type(modules) is list and 1<=len(modules)<=200 and all(type(x) is str and re.fullmatch('[A-Za-z0-9_ ]{1,64}',x) for x in modules) and len(modules)==len(set(modules)),'MODULE_SCHEMA')
 need(data['ini_file']=='/etc/php/7.4/apache2/php.ini','INI_PATH')
 return {'version':data['version'],'sapi':data['sapi'],'modules':sorted(modules),'ini_file':data['ini_file'],'nonce_verified':True}
def php_code(nonce):
 need(type(nonce) is str and re.fullmatch('[0-9a-f]{32}',nonce),'NONCE')
 return ('<?php if ($_SERVER["REQUEST_METHOD"]!=="POST" || $_SERVER["REMOTE_ADDR"]!=="192.168.56.74" || ($_POST["nonce"]??"")!=="'+nonce+'") {http_response_code(403);exit;} header("Content-Type: application/json"); echo json_encode(["nonce"=>"'+nonce+'","version"=>PHP_VERSION,"sapi"=>PHP_SAPI,"modules"=>get_loaded_extensions(),"ini_file"=>php_ini_loaded_file()]);').encode()
def owned_probe(nonce,request):
 code=php_code(nonce);name='baseline_provider_'+nonce+'.php';parent=web_fd();fd=None;identity=None;clean=False
 try:
  prior=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGTERM,signal.SIGINT})
  try:
   fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o644,dir_fd=parent);s=os.fstat(fd);identity=(s.st_dev,s.st_ino)
   os.fchmod(fd,0o644)
   view=memoryview(code)
   while view:view=view[os.write(fd,view):]
   os.fsync(fd);os.close(fd);fd=None
  finally:signal.pthread_sigmask(signal.SIG_SETMASK,prior)
  result=project(request(nonce),nonce)
 finally:
  prior=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGTERM,signal.SIGINT})
  if fd is not None:os.close(fd)
  try:
   if identity is not None:
    f=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
    try:
     s=os.fstat(f);need(stat.S_ISREG(s.st_mode) and (s.st_dev,s.st_ino)==identity and s.st_nlink==1 and s.st_uid==0,'PROBE_REPLACED')
     need(os.read(f,len(code)+1)==code,'PROBE_DRIFT')
    finally:os.close(f)
    s=os.stat(name,dir_fd=parent,follow_symlinks=False);need((s.st_dev,s.st_ino)==identity,'PROBE_REPLACED')
    os.unlink(name,dir_fd=parent)
    try:os.stat(name,dir_fd=parent,follow_symlinks=False)
    except FileNotFoundError:clean=True
    need(clean,'PROBE_REMOVAL')
  finally:
   os.close(parent);signal.pthread_sigmask(signal.SIG_SETMASK,prior)
 return dict(result,probe_removed=clean,probe_code_sha256=hashlib.sha256(code).hexdigest())
def policy(unit):
 need(re.fullmatch('baseline-web-[a-f0-9]{8}',unit),'UNIT')
 raw=subprocess.check_output(['systemctl','show',unit+'.service','-p','IPAddressDeny','-p','IPAddressAllow','-p','NoNewPrivileges'],timeout=10).decode()
 rows=dict(x.split('=',1) for x in raw.splitlines())
 need(rows.get('NoNewPrivileges')=='yes' and set(rows.get('IPAddressDeny','').split())=={'0.0.0.0/0','::/0'} and set(rows.get('IPAddressAllow','').split())=={'127.0.0.0/8','::1/128','192.168.56.74/32'},'NETWORK_POLICY')
def install_signal_cleanup():
 def interrupted(signum,frame):
  # Ignore repeated TERM/INT while the owned-file finally clause completes.
  signal.signal(signal.SIGTERM,signal.SIG_IGN);signal.signal(signal.SIGINT,signal.SIG_IGN)
  raise Rejected('INTERRUPTED')
 signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
def main(unit):
 install_signal_cleanup();check();policy(unit)
 root=Path(__file__).resolve().parents[3];manifest=json.loads((root/'manifest.json').read_bytes())
 for n,h in manifest.items():
  p=root/n;s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o444 and s.st_nlink==1 and hashlib.sha256(p.read_bytes()).hexdigest()==h,'STAGE_PIN')
 sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'baseline-rehearsal'))
 import untimed_driver as legacy
 def request(nonce):
  packed=legacy.deadline._bounded(legacy._probe_worker,(nonce,),limit=64*1024,deadline=30)
  return legacy.strict_json(base64.b64decode(legacy.strict_json(packed)['response'],validate=True))
 result=owned_probe(os.urandom(16).hex(),request)
 result.update(status='CURRENT_APACHE_PHP74_OBSERVED_OWN_PROBE_REMOVED',baseline_acceptance=False,app_credentials_read=False,sql_executed=False)
 print(json.dumps(result,sort_keys=True));return 0
if __name__=='__main__':
 try:sys.exit(main(sys.argv[1]))
 except Exception as e:
  print(json.dumps({'status':'PROBE_FAILED_OR_INCOMPLETE','code':str(e) if isinstance(e,Rejected) else 'UNEXPECTED','baseline_acceptance':False}));sys.exit(1)
