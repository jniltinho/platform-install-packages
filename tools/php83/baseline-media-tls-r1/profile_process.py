"""Private bounded native PHP child transport; no raw-output printing.
Caller retains original privacy boundaries for every outcome. Dedicated
single-threaded coordinator process required for preexec resource limits.
"""
import hashlib,os,resource,selectors,signal,stat,subprocess,time
from pathlib import Path
PHP=Path('/usr/bin/php7.4')
CAP=65536
class Rejected(ValueError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def verified(path,pin,limit):
 s=path.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==0 and s.st_nlink==1 and not s.st_mode&0o022 and s.st_size<=limit and not os.listxattr(path),'PROCESS_SOURCE_METADATA')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  a=os.fstat(fd);data=b''
  while True:
   c=os.read(fd,min(65536,limit+1-len(data)))
   if not c:break
   data+=c;need(len(data)<=limit,'PROCESS_SOURCE_LIMIT')
  b=os.fstat(fd);need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns),'PROCESS_SOURCE_DRIFT')
  need(hashlib.sha256(data).hexdigest()==pin,'PROCESS_SOURCE_PIN');return data
 finally:os.close(fd)
def limits():
 resource.setrlimit(resource.RLIMIT_CPU,(45,46));resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
def invoke(payload,phase,payload_pin,php_pin):
 need(phase in ('prepare','apply'),'PROCESS_PHASE');need(type(payload) is Path or isinstance(payload,Path),'PROCESS_PATH')
 need(payload.is_absolute() and payload.name=='delivery_profile_split.php' and '..' not in payload.parts,'PROCESS_PATH')
 for p in payload.parents:
  s=p.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==0 and not s.st_mode&0o022 and not os.listxattr(p),'PROCESS_PARENT')
 verified(payload,payload_pin,262144);verified(PHP,php_pin,32*1024*1024)
 return _execute([str(PHP),'-d','display_errors=0',str(payload),phase])
def _execute(argv):
 p=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={'PATH':'/usr/bin:/bin','LC_ALL':'C','HOME':'/root'},cwd='/opt/kaltura/app',start_new_session=True,preexec_fn=limits)
 sel=selectors.DefaultSelector();output=[bytearray(),bytearray()];end=time.monotonic()+60;status=None;failure=None
 try:
  for i,stream in enumerate((p.stdout,p.stderr)):
   os.set_blocking(stream.fileno(),False);sel.register(stream,selectors.EVENT_READ,i)
  while sel.get_map():
   need(time.monotonic()<end,'PROCESS_TIMEOUT')
   for key,_ in sel.select(.1):
    raw=os.read(key.fileobj.fileno(),8192)
    if not raw:sel.unregister(key.fileobj)
    else:
     remaining=CAP-len(output[key.data]);output[key.data].extend(raw[:remaining]);need(len(raw)<=remaining,'PROCESS_OUTPUT_LIMIT')
  while True:
   row=os.waitid(os.P_PID,p.pid,os.WEXITED|os.WNOHANG|os.WNOWAIT)
   if row is not None:
    status=row.si_status if row.si_code==os.CLD_EXITED else -row.si_status;break
   need(time.monotonic()<end,'PROCESS_TIMEOUT');time.sleep(.02)
 except Rejected as e:failure=str(e)
 except BaseException:
  failure='PROCESS_INTERRUPTED'
 finally:
  try:os.killpg(p.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  p.wait(timeout=5);sel.close();p.stdout.close();p.stderr.close()
 # Return raw PRIVATE bytes only to outer scanner; never public serialization.
 return {'exit':status,'failure':failure,'stdout_private':bytes(output[0]),'stderr_private':bytes(output[1])}
