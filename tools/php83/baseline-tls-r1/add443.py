"""Exclusive additive .74:443 listener. Existing TLS keys/config never rewritten."""
import argparse,json,os,signal,socket,ssl,stat,time,hashlib
from pathlib import Path
import setup_r2 as base
import render_r2 as render

STATE=Path('/var/lib/kaltura-baseline-tls-443-r1')
AVAILABLE=Path('/etc/apache2/conf-available/kaltura-baseline-tls-443-r1.conf')
ENABLED=Path('/etc/apache2/conf-enabled/kaltura-baseline-tls-443-r1.conf')
CA_SHA='5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef'
PORTS_SHA='dcada9f7ac7b7a5ce698e09e4eab52083388c67829c822e927339285fcc74410'
need=base.need

def config():
 return render.config().replace('<IfModule !ssl_module>\n LoadModule ssl_module /usr/lib/apache2/modules/mod_ssl.so\n</IfModule>\n','').replace(':8443',':443').encode()

def private_metadata(path,mode):
 base.trusted_parent(path.parent);s=path.lstat()
 need(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==mode and not os.listxattr(path),'PRIVATE_METADATA')

def existing():
 for p,h in base.PINS.items():base.read_public(Path(p),PORTS_SHA if p==str(base.PORTS) else h)
 need(base.read_public(base.AVAILABLE)==render.config().encode(),'EXISTING_TLS_CONFIG')
 s=base.ENABLED.lstat();need(stat.S_ISLNK(s.st_mode) and s.st_uid==s.st_gid==0 and os.readlink(base.ENABLED)==str(base.AVAILABLE),'EXISTING_TLS_LINK')
 for folder in (base.STATE,base.LOGDIR):
  base.trusted_parent(folder);need(stat.S_IMODE(folder.lstat().st_mode)==0o700,'PRIVATE_DIRECTORY')
 for p in [base.STATE/'ca.crt',base.STATE/'server.crt',base.STATE/'server.key',*base.LOGS]:private_metadata(p,0o600)
 need(base.sha((base.STATE/'ca.crt').read_bytes())==CA_SHA,'CA_PIN')

def handshake(port,cafile):
 ctx=ssl.create_default_context(cafile=cafile);ctx.minimum_version=ssl.TLSVersion.TLSv1_2
 with socket.create_connection((render.IP,port),timeout=5) as raw:
  with ctx.wrap_socket(raw,server_hostname=render.IP) as conn:return conn.version()

def connections(ports):
 for port in ports:
  handshake(port,str(base.STATE/'ca.crt'))
  try:handshake(port,None)
  except ssl.SSLCertVerificationError:pass
  else:raise base.Rejected('WRONG_CA_ACCEPTED')

def target():
 need(os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline','TARGET')
 rows=json.loads(base.command(['/usr/sbin/ip','-j','-4','addr']));ips={v.get('local') for r in rows for v in r.get('addr_info',[])}
 need(render.IP in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}),'TARGET')

def preflight():
 target();existing()
 for p in (STATE,AVAILABLE,ENABLED):base.trusted_parent(p.parent);need(not os.path.lexists(p),'OWNED_PATH_OCCUPIED')
 raw=base.command(['/usr/bin/ss','-H','-ltn'])
 need(base.tls_listeners(raw)==['192.168.56.74:8443'],'LISTENER_BASELINE')
 http=base.http80(raw);need(http,'HTTP80_MISSING')
 need(base.command(['/usr/bin/systemctl','is-active','apache2']).strip()==b'active','APACHE_INACTIVE')
 modules=base.command(['/usr/sbin/apache2ctl','-M']);need(b'ssl_module' in modules and b'php7_module' in modules,'MODULE_BASELINE')
 base.command(['/usr/sbin/apache2ctl','configtest']);connections([8443]);return http

def post(http,ports):
 expected=sorted(f'192.168.56.74:{p}' for p in ports)
 # Graceful reload is asynchronous; finite 5-second socket readiness window.
 for _ in range(20):
  if base.tls_listeners(base.command(['/usr/bin/ss','-H','-ltn']))==expected:break
  time.sleep(.25)
 else:raise base.Rejected('LISTENER_SCOPE')
 need(base.command(['/usr/bin/systemctl','is-active','apache2']).strip()==b'active','APACHE_INACTIVE')
 base.preserved_http_php(http);existing();connections(ports)

def main(execute=False):
 http=preflight()
 if not execute:print(json.dumps({'status':'TLS443_PREFLIGHT_ONLY','full_acceptance':False}));return 0
 STATE.mkdir(mode=0o700);need(stat.S_IMODE(STATE.lstat().st_mode)==0o700,'STATE_MODE')
 base.create(STATE/'intent.json',b'{"case":"ADDITIVE_TLS443"}',0o600)
 aid=eid=None;reload_attempted=False;conf=config()
 result={'status':'TLS443_FAILED','rollback_complete':False,'full_acceptance':False,'keys_exported':False}
 signal.signal(signal.SIGTERM,base.interrupted);signal.signal(signal.SIGINT,base.interrupted)
 try:
  prior=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGTERM,signal.SIGINT})
  try:
   aid=base.create(AVAILABLE,conf,0o644);os.symlink(str(AVAILABLE),ENABLED);s=ENABLED.lstat();eid=(s.st_dev,s.st_ino)
  finally:signal.pthread_sigmask(signal.SIG_SETMASK,prior)
  existing();base.command(['/usr/sbin/apache2ctl','configtest']);reload_attempted=True
  base.command(['/usr/bin/systemctl','reload','apache2'],60);post(http,[443,8443])
  need(base.read_public(AVAILABLE)==conf and base.same_inode(AVAILABLE,aid) and base.same_inode(ENABLED,eid) and os.readlink(ENABLED)==str(AVAILABLE),'OWNED_DRIFT')
  result.update(status='LAB_TLS443_INSTALLED_HANDSHAKE_ONLY',listeners=[443,8443],wrong_ca_rejected=True,http80_preserved=True,php7_module_preserved=True,privacy_inventory_unchanged=True,public_ca_pem_sha256=CA_SHA,http_api_tested=False)
 except Exception as e:
  result['failure_code']=str(e) if isinstance(e,base.Rejected) else 'UNEXPECTED'
  signal.signal(signal.SIGTERM,signal.SIG_IGN);signal.signal(signal.SIGINT,signal.SIG_IGN)
  try:
   if eid is not None:need(base.same_inode(ENABLED,eid) and os.readlink(ENABLED)==str(AVAILABLE),'ROLLBACK_LINK_DRIFT');ENABLED.unlink()
   if aid is not None:need(base.same_inode(AVAILABLE,aid) and base.read_public(AVAILABLE)==conf,'ROLLBACK_CONFIG_DRIFT');AVAILABLE.unlink()
   base.command(['/usr/sbin/apache2ctl','configtest'])
   if reload_attempted:base.command(['/usr/bin/systemctl','reload','apache2'],60)
   post(http,[8443]);result['rollback_complete']=True
  except Exception:result['rollback_complete']=False
 base.create(STATE/'terminal.json',json.dumps(result,sort_keys=True).encode(),0o600)
 print(json.dumps(result,sort_keys=True));return 0 if result['status']=='LAB_TLS443_INSTALLED_HANDSHAKE_ONLY' else 1

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');a=p.parse_args()
 try:raise SystemExit(main(a.execute))
 except Exception as e:print(json.dumps(base.public_failure(e)));raise SystemExit(1)
