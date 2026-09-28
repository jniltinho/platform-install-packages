"""Reviewed additive lab74 nginx TLS8444. No DB/profile changes or credentials.
Requires exclusive coordinator window and separately preserved VM snapshot.
Do not send authenticated requests until mandatory privacy log enrollment.
"""
import argparse,hashlib,json,os,signal,socket,ssl,stat,time
from pathlib import Path
import observe_r2 as obs
STATE=Path('/var/lib/kaltura-baseline-media-tls-r1')
SSL=Path('/opt/kaltura/nginx/conf/ssl.conf')
BINARY='/opt/kaltura/nginx/sbin/nginx'
PID=Path('/opt/kaltura/nginx/logs/nginx.pid')
CA=Path('/var/lib/kaltura-baseline-tls-r2/ca.crt')
CA_SHA='5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef'
LEAF_SHA='33f22008e90374c3950ebd569e0d0358e040a00bd610e1c4fca292388b0732e7'
BINARY_SHA='1a995dddd470f013258b1890cfc7c9e3b10c344461eb085de6b2ef8f991faec0'
# Filled only from reviewed fixed-path native closure receipt, never CLI input.
CONFIG_PINS={'base.conf': 'f011df8b869a55df042677e3db02529c8dab96d3858b0c322e31c64b6cad07e1', 'cors.conf': '97fba7f5da398ae9a3b8ea106062a60a1e0542d4b7fbde16da29b2d3f9bcd3f7', 'http.conf': '8812898f777693e2816c7c462124b06744196791468d96b48af2b253ef111123', 'kaltura-nginx.conf': '56c4c83f7eb6926655a07bdbb0e8d075ec38356f7f8199f1f880b00f03c19372', 'kaltura.conf': 'c210cb31fc8c6aa4d498fe425a04ebc0432721be423767e8a49ff1c6b418aac9', 'main.conf': '19d13ae00a87081816835086927c4dbb6ca687eff3e45c3b3e735fd4d52fd097', 'mime.types': '6f95d1d7d75e3c072907d845622a69d23110d1266c16ff122b3109b8b21f3ae9', 'nginx.conf': '56c4c83f7eb6926655a07bdbb0e8d075ec38356f7f8199f1f880b00f03c19372', 'server.conf': 'c210cb31fc8c6aa4d498fe425a04ebc0432721be423767e8a49ff1c6b418aac9', 'ssl.conf': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'ssl.conf.template': 'a03132ddec157145e936e6ab4c7324b14af09ae8014580145098a277ddebefea'}
need=obs.need

def config():
 return f'''log_format baseline_media_tls_scalar '$status $bytes_sent $request_time';
server {{
 listen 192.168.56.74:8444 ssl;
 server_name 192.168.56.74;
 ssl_certificate /var/lib/kaltura-baseline-tls-r2/server.crt;
 ssl_certificate_key /var/lib/kaltura-baseline-tls-r2/server.key;
 ssl_protocols TLSv1.2 TLSv1.3;
 ssl_ciphers HIGH:!aNULL:!MD5:!3DES;
 access_log {STATE}/access.log baseline_media_tls_scalar;
 error_log {STATE}/error.log error;
 include /opt/kaltura/nginx/conf/server.conf;
}}
'''.encode()

def metadata_ok(row,mode,kind='regular'):
 return row.get('kind')==kind and row.get('uid')==row.get('gid')==0 and row.get('mode')==mode and not row.get('xattrs_present') and (kind!='regular' or row.get('nlink')==1)
def observe_check(allow_installed=False):
 v=obs.observe();need(type(CONFIG_PINS) is dict and set(CONFIG_PINS)==set(obs.CONFIGS),'CLOSURE_UNFROZEN')
 for name,row in v['configs'].items():
  if name in ('nginx.conf','server.conf'):
   need(row.get('kind')=='symlink' and row.get('uid')==row.get('gid')==0 and not row.get('xattrs_present'),'CONFIG_LINK_METADATA')
  else:need(metadata_ok(row,'0644'),'CONFIG_METADATA')
  if not (allow_installed and name=='ssl.conf'):need(row.get('sha256')==CONFIG_PINS[name],'CONFIG_DRIFT')
 for path,row in v['parents'].items():need(metadata_ok(row,'0700' if path==obs.CERT else '0755','directory'),'PARENT_TRUST')
 need(metadata_ok(v['binary'],'0755') and v['binary']['sha256']==BINARY_SHA,'BINARY_PIN')
 for name,row in v['certificates'].items():need(metadata_ok(row,'0600'),'CERT_METADATA')
 need(v['certificates']['ca.crt']['public_pem_sha256']==CA_SHA and v['certificates']['server.crt']['public_pem_sha256']==LEAF_SHA,'CERT_PIN')
 need(v['service']['active_state']=='active','SERVICE_INACTIVE')
 return v

def process():
 # Native SysV unit MainPID may be zero; verify pidfile + exact executable.
 need(metadata_ok(obs.metadata(PID.parent),'0755','directory'),'PID_PARENT')
 m=obs.metadata(PID);need(m.get('kind')=='regular' and m.get('uid')==0 and not int(m.get('mode','7777'),8)&0o022 and m.get('nlink')==1 and not m.get('xattrs_present'),'PID_METADATA')
 raw=obs.read(PID,32).strip();need(raw.isdigit() and int(raw)>1,'PID_SHAPE');pid=int(raw)
 a=os.stat(f'/proc/{pid}/exe');b=os.stat(BINARY);need((a.st_dev,a.st_ino)==(b.st_dev,b.st_ino),'PROCESS_BINARY')
 need(Path(f'/proc/{pid}').stat().st_uid==0,'MASTER_OWNER')
 need(obs.read(f'/proc/{pid}/cmdline',4096).startswith(b'nginx: master process '),'MASTER_COMMAND')
 return pid

def create(path,data,mode):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode)
 with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),mode)
 s=path.lstat();return s.st_dev,s.st_ino

def replace_ssl(expected,new):
 need(obs.read(SSL,1048576)==expected and metadata_ok(obs.metadata(SSL),'0644'),'SSL_DRIFT')
 temp=SSL.with_name('.baseline-media-tls-r1.tmp');identity=create(temp,new,0o644)
 try:
  need(obs.read(SSL,1048576)==expected,'SSL_DRIFT');os.replace(temp,SSL)
 finally:
  if os.path.lexists(temp) and (temp.lstat().st_dev,temp.lstat().st_ino)==identity:temp.unlink()
 return identity

def handshake(port,cafile):
 c=ssl.create_default_context(cafile=cafile);c.minimum_version=ssl.TLSVersion.TLSv1_2
 with socket.create_connection(('192.168.56.74',port),timeout=5) as s:
  with c.wrap_socket(s,server_hostname='192.168.56.74') as t:need(t.version() in ('TLSv1.2','TLSv1.3'),'TLS_VERSION')
def check_ports(expected):
 for _ in range(30):
  if obs.listeners(obs.command(['/usr/bin/ss','-H','-ltn']))==expected:return
  time.sleep(.2)
 raise obs.Rejected('LISTENER_DRIFT')
def reload_master(pid):
 fd=os.pidfd_open(pid)
 try:
  need(process()==pid,'MASTER_CHANGED');signal.pidfd_send_signal(fd,signal.SIGHUP)
 finally:os.close(fd)
def preflight():
 v=observe_check();need(not os.path.lexists(STATE),'STATE_OCCUPIED');need(not os.path.lexists(SSL.with_name('.baseline-media-tls-r1.tmp')),'TEMP_OCCUPIED')
 need(v['listeners']=={'80':['WILDCARD'],'88':['WILDCARD'],'443':['TARGET'],'8443':['TARGET'],'8444':[]},'LISTENER_BASELINE')
 need(v['configs']['ssl.conf']['bytes']==0,'SSL_NOT_EMPTY')
 pid=process();return v['listeners'],pid

def main(execute=False):
 ports,pid=preflight()
 if not execute:return {'status':'MEDIA_TLS8444_PREFLIGHT_ONLY','full_acceptance':False}
 STATE.mkdir(mode=0o700);need(metadata_ok(obs.metadata(STATE),'0700','directory'),'STATE_MODE')
 create(STATE/'intent.json',b'{"case":"LAB_NGINX_TLS8444_ADDITIVE"}',0o600)
 identity=None;reload_attempted=False;new=config();result={'status':'MEDIA_TLS8444_FAILED','rollback_complete':False,'full_acceptance':False}
 def interrupted(*args):raise obs.Rejected('INTERRUPTED')
 signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
 try:
  create(STATE/'ssl.before',b'',0o600)
  for name in ('access.log','error.log'):create(STATE/name,b'',0o600)
  oldmask=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGTERM,signal.SIGINT})
  try:identity=replace_ssl(b'',new)
  finally:signal.pthread_sigmask(signal.SIG_SETMASK,oldmask)
  observe_check(True);obs.command([BINARY,'-t','-p',obs.BASE+'/', '-c',obs.BASE+'/conf/nginx.conf'])
  reload_attempted=True;reload_master(pid)
  expected=dict(ports);expected['8444']=['TARGET'];check_ports(expected)
  for port in (443,8443,8444):handshake(port,str(CA))
  try:handshake(8444,None)
  except ssl.SSLCertVerificationError:pass
  else:raise obs.Rejected('WRONG_CA_ACCEPTED')
  observe_check(True);need(obs.read(SSL,1048576)==new,'SSL_DRIFT')
  result.update(status='LAB_MEDIA_TLS8444_HANDSHAKE_ONLY',rollback_complete=False,http88_listener_preserved=True,apache443_8443_handshake_preserved=True,wrong_ca_rejected=True,private_logs=[str(STATE/'access.log'),str(STATE/'error.log')],credential_requests_authorized=False,profile_database_changed=False)
  create(STATE/'terminal.json',json.dumps(result,sort_keys=True).encode(),0o600)
  return result
 except Exception as error:
  result.update(status='MEDIA_TLS8444_FAILED',failure_code=str(error) if isinstance(error,obs.Rejected) else 'UNEXPECTED')
  signal.signal(signal.SIGTERM,signal.SIG_IGN);signal.signal(signal.SIGINT,signal.SIG_IGN)
  try:
   if identity is not None:
    s=SSL.lstat();need((s.st_dev,s.st_ino)==identity and obs.read(SSL,1048576)==new,'ROLLBACK_DRIFT');replace_ssl(new,b'')
   obs.command([BINARY,'-t','-p',obs.BASE+'/', '-c',obs.BASE+'/conf/nginx.conf'])
   if reload_attempted:reload_master(pid)
   check_ports(ports);result['rollback_complete']=True
  except Exception:pass
 try:create(STATE/'terminal.json',json.dumps(result,sort_keys=True).encode(),0o600)
 except Exception:result['failure_receipt_persisted']=False
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');a=p.parse_args()
 try:
  r=main(a.execute);print(json.dumps(r,sort_keys=True));raise SystemExit(1 if r['status']=='MEDIA_TLS8444_FAILED' else 0)
 except Exception as e:
  print(json.dumps({'status':'MEDIA_TLS8444_REJECTED','code':str(e) if isinstance(e,obs.Rejected) else 'UNEXPECTED','full_acceptance':False}));raise SystemExit(2)
