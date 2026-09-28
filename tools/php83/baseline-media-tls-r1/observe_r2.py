"""Read-only fixed-path baseline74 nginx/TLS metadata; no key bytes or raw config.
Coordinator executes only after review. No API, service transition or TLS request.
"""
import hashlib,json,os,re,resource,signal,socket,stat,subprocess
from pathlib import Path
BASE='/opt/kaltura/nginx'
CERT='/var/lib/kaltura-baseline-tls-r2'
CONFIGS=('nginx.conf','kaltura-nginx.conf','server.conf','kaltura.conf','ssl.conf','ssl.conf.template','main.conf','http.conf','base.conf','cors.conf','mime.types')
class Rejected(ValueError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def command(args):
 out=os.memfd_create('public-observe-out',os.MFD_CLOEXEC);err=os.memfd_create('public-observe-err',os.MFD_CLOEXEC)
 def limits():
  resource.setrlimit(resource.RLIMIT_FSIZE,(65536,65536));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 try:
  p=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=out,stderr=err,env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LC_ALL':'C'},start_new_session=True,preexec_fn=limits)
  try:p.wait(timeout=10)
  except BaseException:
   try:os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   p.wait(timeout=5);raise Rejected('COMMAND_TIMEOUT') from None
  need(p.returncode==0,'COMMAND_FAILED');os.lseek(out,0,0);data=os.read(out,65537);need(len(data)<=65536,'COMMAND_LIMIT');return data
 finally:os.close(out);os.close(err)
def metadata(path):
 p=Path(path)
 if not os.path.lexists(p):return {'exists':False}
 s=p.lstat()
 return {'exists':True,'kind':'directory' if stat.S_ISDIR(s.st_mode) else 'regular' if stat.S_ISREG(s.st_mode) else 'symlink' if stat.S_ISLNK(s.st_mode) else 'other','uid':s.st_uid,'gid':s.st_gid,'mode':format(stat.S_IMODE(s.st_mode),'04o'),'nlink':s.st_nlink,'xattrs_present':bool(os.listxattr(p,follow_symlinks=False))}
def read(path,cap):
 fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
 try:
  s=os.fstat(fd);need(stat.S_ISREG(s.st_mode) and s.st_size<=cap,'FILE_SHAPE')
  data=b''
  while True:
   chunk=os.read(fd,min(65536,cap+1-len(data)))
   if not chunk:break
   data+=chunk;need(len(data)<=cap,'FILE_LIMIT')
  t=os.fstat(fd);need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns),'FILE_CHANGED');return data
 finally:os.close(fd)
def shape(raw):
 need(type(raw) is bytes and len(raw)<=1048576,'CONFIG_LIMIT')
 # Closed facts only; no directive operands/unknown text exported.
 lines=raw.splitlines();active=[x.strip() for x in lines if x.strip() and not x.lstrip().startswith(b'#')]
 return {'empty':not raw,'include_ssl_exact':sum(bool(re.fullmatch(rb'include\s+(?:/opt/kaltura/nginx/conf/)?ssl\.conf\s*;',x)) for x in active),'include_server_exact':sum(bool(re.fullmatch(rb'include\s+(?:/opt/kaltura/nginx/conf/)?server\.conf\s*;',x)) for x in active),'include_count':sum(bool(re.match(rb'include\s',x)) for x in active),'listen_count':sum(bool(re.match(rb'listen\s',x)) for x in active),'tls_listen_count':sum(bool(re.match(rb'listen\s.*\bssl\b',x)) for x in active),'has_template_tokens':b'@' in raw,'access_log_directives':sum(bool(re.match(rb'access_log\s',x)) for x in active),'error_log_directives':sum(bool(re.match(rb'error_log\s',x)) for x in active)}
def config(name):
 p=Path(BASE)/'conf'/name; m=metadata(p)
 if not m['exists']:return m
 if m['kind']=='symlink':
  target=os.readlink(p); allowed={'nginx.conf':'kaltura-nginx.conf','server.conf':'kaltura.conf'}
  need(name in allowed and target in (allowed[name],str(p.parent/allowed[name])),'CONFIG_LINK')
  p=p.parent/allowed[name];m['resolved_fixed_target']=allowed[name]
  need(metadata(p)['kind']=='regular','CONFIG_LINK_TARGET')
 else:need(m['kind']=='regular','CONFIG_TYPE')
 raw=read(p,1048576);m.update(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),shape=shape(raw));return m
def public_cert_hash(raw):
 need(type(raw) is bytes and len(raw)<=16384 and re.fullmatch(rb'\s*-----BEGIN CERTIFICATE-----[A-Za-z0-9+/=\r\n]+-----END CERTIFICATE-----\s*',raw) is not None,'CERT_PUBLIC_PEM')
 return hashlib.sha256(raw).hexdigest()
def certificate_metadata():
 result={n:metadata(CERT+'/'+n) for n in ('ca.crt','server.crt','server.key')}
 for n in ('ca.crt','server.crt'):
  need(result[n].get('kind')=='regular','CERT_TYPE')
  result[n]['public_pem_sha256']=public_cert_hash(read(CERT+'/'+n,16384))
 return result
def listeners(raw):
 result={str(p):[] for p in (80,88,443,8443,8444)}
 for line in raw.decode('ascii').splitlines():
  row=line.split();need(len(row)>=4,'SOCKET_SHAPE');local=row[3];port=local.rsplit(':',1)[-1]
  if port in result:
   host=local.rsplit(':',1)[0].strip('[]');kind='TARGET' if host=='192.168.56.74' else 'LOOPBACK' if host in ('127.0.0.1','::1') else 'WILDCARD' if host in ('*','0.0.0.0','::') else 'OTHER'
   result[port].append(kind)
 return {p:sorted(rows) for p,rows in result.items()}
def observe():
 need(os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline','TARGET')
 rows=json.loads(command(['/usr/sbin/ip','-j','-4','addr']));ips={a.get('local') for r in rows for a in r.get('addr_info',[])}
 need('192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}),'TARGET')
 # Refuse ancestor symlinks before any fixed content read. Report actual modes,
 # do not chmod or prematurely turn observation into mutation authorization.
 parents=['/','/opt','/opt/kaltura',BASE,BASE+'/conf',BASE+'/sbin','/var','/var/lib',CERT]
 parentmeta={p:metadata(p) for p in parents};need(all(v.get('kind')=='directory' for v in parentmeta.values()),'PARENT_TYPE')
 configs={n:config(n) for n in CONFIGS}
 binary=BASE+'/sbin/nginx';bm=metadata(binary);need(bm.get('kind')=='regular','BINARY_TYPE');b=read(binary,32*1024*1024);bm.update(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
 certs=certificate_metadata()
 service=command(['/usr/bin/systemctl','show','kaltura-nginx','--property=ActiveState,SubState,MainPID','--no-pager']).decode('ascii')
 props=dict(line.split('=',1) for line in service.splitlines() if '=' in line)
 need(set(props)=={'ActiveState','SubState','MainPID'} and props['MainPID'].isdigit(),'SERVICE_SHAPE')
 state=props['ActiveState'] if props['ActiveState'] in ('active','inactive','failed','activating','deactivating') else 'OTHER'
 sub=props['SubState'] if props['SubState'] in ('running','dead','exited','failed','start','stop') else 'OTHER'
 ports=listeners(command(['/usr/bin/ss','-H','-ltn']))
 return {'case':'BASELINE74_MEDIA_TLS_READONLY_SHAPE_R2','parents':parentmeta,'configs':configs,'binary':bm,'certificates':certs,'service':{'active_state':state,'sub_state':sub,'main_pid_present':int(props['MainPID'])>0},'listeners':ports,'port8444_free_observed':not ports['8444'],'configuration_mutated':False,'private_key_read':False,'tls_verified':False,'mutation_authorized_by_receipt':False}
if __name__=='__main__':
 try: print(json.dumps(observe(),sort_keys=True))
 except Rejected as e: print(json.dumps({'case':'BASELINE74_MEDIA_TLS_READONLY_SHAPE_R2','status':'FAILED','code':str(e)}));raise SystemExit(2)
 except Exception: print(json.dumps({'case':'BASELINE74_MEDIA_TLS_READONLY_SHAPE_R2','status':'FAILED','code':'OBSERVATION_FAILED'}));raise SystemExit(2)
