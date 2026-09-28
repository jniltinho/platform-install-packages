"""Root-owned .74 endpoint diagnosis only. No auth, SQL, config writes or redirects."""
import hashlib,json,os,re,socket,ssl,stat,subprocess
from pathlib import Path
CA=Path('/var/lib/kaltura-baseline-tls-r2/ca.crt')
CA_PIN='5ca573deffda2a3f40bc104258c7c36472d2f924a2a945cec6cb1fd99f541bef'
CONFIGS=('/opt/kaltura/nginx/conf/nginx.conf','/opt/kaltura/nginx/conf/kaltura-nginx.conf','/opt/kaltura/nginx/conf/server.conf','/opt/kaltura/nginx/conf/kaltura.conf')
class Rejected(ValueError):pass
def need(ok):
 if not ok:raise Rejected('MEDIA88_OBSERVATION_REJECTED')
def config_shape(raw):
 need(type(raw) is bytes and len(raw)<=1024*1024)
 text=raw.decode('utf-8',errors='replace');text=re.sub(r'#[^\n]*','',text)
 listens=re.findall(r'\blisten\s+([^;{}\n]{1,256});',text)
 port88=[s for s in listens if re.search(r'(?:^|[\s:])88(?:\s|$)',s)]
 return {'listen88_count':len(port88),'listen88_ssl_count':sum(bool(re.search(r'\bssl\b',s)) for s in port88),'ssl_on_present':bool(re.search(r'\bssl\s+on\s*;',text)),'ssl_certificate_directive':bool(re.search(r'\bssl_certificate\s+',text)),'include_directive_count':len(re.findall(r'\binclude\s+',text)),'configuration_effective_proven':False}
def config(path):
 p=Path(path)
 if not os.path.lexists(p):return {'state':'ABSENT'}
 m=p.lstat();info={'state':'LINK_NOT_FOLLOWED' if stat.S_ISLNK(m.st_mode) else 'REGULAR','uid':m.st_uid,'gid':m.st_gid,'mode':stat.S_IMODE(m.st_mode)}
 if stat.S_ISLNK(m.st_mode):return info
 if not (stat.S_ISREG(m.st_mode) and m.st_uid==0 and m.st_nlink==1 and m.st_size<=1024*1024 and not m.st_mode&0o022):
  info['state']='UNTRUSTED_NOT_READ';return info
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 try:
  before=os.fstat(fd);need((before.st_dev,before.st_ino)==(m.st_dev,m.st_ino));raw=os.read(fd,1024*1024+1);need(len(raw)<=1024*1024)
 finally:os.close(fd)
 info.update(config_shape(raw));return info
def status_line(data):
 if type(data) is not bytes or len(data)>1024:return None
 match=re.match(rb'HTTP/1\.[01] ([1-5][0-9]{2})(?: |\r\n)',data)
 return int(match[1]) if match else None
def http88():
 result={'request':'GET_ROOT_NO_CREDENTIALS','status':None,'transport':'FAILED'}
 try:
  with socket.create_connection(('192.168.56.74',88),timeout=3) as s:
   s.settimeout(3);s.sendall(b'GET / HTTP/1.0\r\nHost: 192.168.56.74\r\nConnection: close\r\n\r\n');raw=s.recv(1024);result['status']=status_line(raw);result['transport']='CONNECTED'
 except (OSError,ValueError):pass
 return result
def tls88(ca):
 ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT);ctx.minimum_version=ssl.TLSVersion.TLSv1_2;ctx.load_verify_locations(cadata=ca.decode('ascii'))
 result={'pinned_ca_verified':False,'status':'FAILED','reason':'UNOBSERVED'}
 try:
  with socket.create_connection(('192.168.56.74',88),timeout=3) as raw:
   with ctx.wrap_socket(raw,server_hostname='192.168.56.74') as secure:
    result.update(pinned_ca_verified=True,status='TLS_CONNECTED',reason='NONE')
 except ssl.SSLCertVerificationError:result['reason']='CERTIFICATE_REJECTED'
 except ssl.SSLError as e:result['reason']='WRONG_VERSION_NUMBER' if e.reason=='WRONG_VERSION_NUMBER' else 'OTHER_TLS_ERROR'
 except OSError:result['reason']='CONNECTION_FAILED'
 return result
def main():
 need(os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline')
 info=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=5));ips={v.get('local') for row in info for v in row.get('addr_info',[])};need('192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}))
 m=CA.lstat();need(stat.S_ISREG(m.st_mode) and m.st_uid==0 and m.st_nlink==1 and m.st_size<=16384 and stat.S_IMODE(m.st_mode)==0o600);ca=CA.read_bytes();need(hashlib.sha256(ca).hexdigest()==CA_PIN)
 result={'schema':1,'scope':'PORT88_NO_AUTH_READ_ONLY_DIAGNOSIS','configurations':{str(i):config(n) for i,n in enumerate(CONFIGS)},'http88':http88(),'tls88':tls88(ca),'configuration_changed':False,'application_acceptance':False}
 print(json.dumps(result,sort_keys=True))
if __name__=='__main__':
 try:main()
 except Exception:print(json.dumps({'status':'MEDIA88_OBSERVATION_REJECTED'}));raise SystemExit(2)
