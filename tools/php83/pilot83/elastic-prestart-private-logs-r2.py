"""Private .83 first-start guard; exact ES configuration delta, no service calls."""
import hashlib,json,os,stat,socket,subprocess
from pathlib import Path
RUN=Path('/var/lib/kaltura-php83-phase-d2')
CONFIG=Path('/etc/elasticsearch/elasticsearch.yml')
HEAP=Path('/etc/elasticsearch/jvm.options.d/kaltura.options')
MACHINE='ad9adac39d0fb440883f0b82c8c45058596b74a6d9e98da2746e4dbdafd3aad8'
NATIVE={'/etc/elasticsearch/elasticsearch.yml.orig':'d8fe12be5cccdbca1c560dfaf0c0cb109e8cfe50dc048e490027b4b9b7884dae','/etc/elasticsearch/jvm.options':'2fd473a5e6583d781b88af60bf36e4e31f6bedc2ee93ee954f71532a3f6fc82e','/etc/elasticsearch/log4j2.properties':'37b5e7403dde2f6508c37148adb04005daf694c64d62e8fb1c23579618df339a','/etc/default/elasticsearch':'8a547e30479cb900c3995ebb37149c2efead1241c670de2747f961fb32fe18a2'}
BEFORE_PIN='290463b297413de01dfcb5164350d707ed647186f20022e50861b374d4b1308c'
AFTER_PIN='c0b3b4b9b0a6549f7cf33b8d678101a51adfd0bceadb788344418e2af792d8bb'
LOGS=Path('/var/lib/kaltura-php83-elasticsearch-logs')
EXTRA=b'network.host: 127.0.0.1\ningest.geoip.downloader.enabled: false\n'
def need(ok,code):
 if not ok:raise ValueError(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def trusted_parents(path):
 for p in Path(path).parents:
  s=p.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==0 and not s.st_mode&0o022 and not os.listxattr(p,follow_symlinks=False),'PARENT_TRUST')
def checked(path,modes,pin=None):
 trusted_parents(path);fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 try:
  s=os.fstat(fd);need(stat.S_ISREG(s.st_mode) and (s.st_uid,s.st_gid,s.st_nlink)==(0,112,1) and stat.S_IMODE(s.st_mode) in modes and not os.listxattr(fd),'FILE_METADATA')
  raw=os.read(fd,1048577);need(len(raw)<=1048576 and (pin is None or sha(raw)==pin),'FILE_PIN')
  after=os.fstat(fd);need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'FILE_CHANGED')
  return raw,(s.st_dev,s.st_ino),stat.S_IMODE(s.st_mode)
 finally:os.close(fd)
def syncdir(path):
 fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
def receipt(path,data):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(json.dumps(data,sort_keys=True).encode());f.flush();os.fsync(f.fileno())
 syncdir(path.parent)
def content(raw):
 need(sha(raw)==BEFORE_PIN and b'network.host:' not in raw and b'ingest.geoip.downloader.enabled:' not in raw,'RENDERED_PIN')
 need(raw.count(b'path.logs: /opt/kaltura/log/elasticsearch\n')==1,'LOG_PATH_CARDINALITY')
 out=raw.replace(b'path.logs: /opt/kaltura/log/elasticsearch\n',b'path.logs: /var/lib/kaltura-php83-elasticsearch-logs\n')+EXTRA;need(sha(out)==AFTER_PIN,'AFTER_PIN');return out

def stopped():
 result=subprocess.run(['/usr/bin/systemctl','show','elasticsearch','--property=ActiveState,MainPID'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20,env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LC_ALL':'C','HOME':'/root'})
 need(result.returncode==0 and set(result.stdout.splitlines())=={b'ActiveState=inactive',b'MainPID=0'},'ES_NOT_STOPPED')
 for entry in Path('/proc').iterdir():
  if entry.name.isdecimal():
   try:
    with (entry/'cmdline').open('rb') as f:raw=f.read(1048577)
   except FileNotFoundError:continue
   need(len(raw)<=1048576 and b'org.elasticsearch.bootstrap.Elasticsearch' not in raw,'ES_PROCESS_PRESENT')
def private_logs(mode,empty=False):
 trusted_parents(LOGS)
 fd=os.open(LOGS,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  s=os.fstat(fd);need((s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(112,112,mode) and not os.listxattr(fd),'LOG_DIRECTORY_METADATA')
  if empty:need(not os.listdir(fd),'LOG_DIRECTORY_NOT_FRESH')
  return (s.st_dev,s.st_ino)
 finally:os.close(fd)
def fresh_logs():
 trusted_parents(LOGS)
 need(not os.path.lexists(LOGS),'LOG_DIRECTORY_NOT_FRESH')
def create_private_logs():
 fresh_logs();LOGS.mkdir(mode=0o700)
 fd=os.open(LOGS,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try:
  s=os.fstat(fd);need((s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(0,0,0o700) and not os.listxattr(fd) and not os.listdir(fd),'LOG_DIRECTORY_CHANGED')
  identity=(s.st_dev,s.st_ino);os.fchown(fd,112,112);os.fchmod(fd,0o700);os.fsync(fd)
 finally:os.close(fd)
 syncdir(LOGS.parent);need(private_logs(0o700,True)==identity,'LOG_DIRECTORY_CHANGED')
 return identity
def apply():
 need(os.geteuid()==os.getegid()==0 and socket.gethostname()=='kaltura-php83-lab','LAB_IDENTITY')
 need(sha(Path('/etc/machine-id').read_bytes())==MACHINE,'MACHINE');stopped()
 trusted_parents(RUN/'prestart-mode-intent.json');s=RUN.lstat();need(stat.S_ISDIR(s.st_mode) and (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(0,0,0o700),'RUN_TRUST')
 for path,pin in NATIVE.items():checked(path,{0o640},pin)
 fresh_logs()
 old,identity,oldmode=checked(CONFIG,{0o600,0o640,0o644,0o660,0o664},BEFORE_PIN);new=content(old)
 heap,heapid,heapmode=checked(HEAP,{0o600,0o640,0o644,0o660,0o664});need(heap==b'-Xms1g\n-Xmx1g\n','HEAP_PIN')
 need({p.name for p in HEAP.parent.iterdir()}=={'kaltura.options'},'HEAP_OPTIONS_SET')
 receipt(RUN/'prestart-mode-intent.json',{'status':'INTENT_BEFORE_MUTATION','config_before_sha256':sha(old),'config_after_sha256':sha(new),'config_inode':identity,'config_mode_before':oct(oldmode),'heap_inode':heapid,'heap_mode_before':oct(heapmode),'resume_supported':False})
 create_private_logs()
 # Exclusive deterministic temp name; never remove/reuse an existing candidate.
 temp=CONFIG.with_name('.pilot83-es-r7.yml')
 fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:
  st=os.fstat(f.fileno());need((st.st_uid,st.st_gid)==(0,112),'TEMP_METADATA');f.write(new);f.flush();os.fchmod(f.fileno(),0o640);os.fsync(f.fileno())
 need(checked(CONFIG,{oldmode},BEFORE_PIN)[1]==identity,'CONFIG_INODE_DRIFT');os.replace(temp,CONFIG);syncdir(CONFIG.parent)
 fd=os.open(HEAP,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 try:
  st=os.fstat(fd);need((st.st_dev,st.st_ino)==heapid and sha(os.read(fd,1024))==sha(heap),'HEAP_DRIFT');os.fchmod(fd,0o640);os.fsync(fd)
 finally:os.close(fd)
 syncdir(HEAP.parent);checked(CONFIG,{0o640},AFTER_PIN);checked(HEAP,{0o640},sha(heap))
 for path,pin in NATIVE.items():checked(path,{0o640},pin)
 stopped()
 receipt(RUN/'prestart-mode-complete.json',{'status':'EXACT_PRIVATE_ES_PRESTART_CONFIG_READY','config_sha256':AFTER_PIN,'native_modes':'0640','network':'127.0.0.1','geoip_downloader':False,'service_started':False,'daemon_logs':'/var/lib/kaltura-php83-elasticsearch-logs','daemon_logs_mode':'0700'})
def main():
 try:apply();return 0
 except BaseException:print('PRIVATE_ES_PRESTART_GUARD_FAILED');return 92
if __name__=='__main__':raise SystemExit(main())
