"""Isolated Unix datagram prototype. Not a deployed service or privacy acceptance."""
import argparse,json,os,signal,socket,stat,sys,time
from pathlib import Path
from sanitizer import sanitize,event,MAX_DATAGRAM
MAX_OUTPUT=1024*1024
MAX_EVENTS=10000
MAX_SECONDS=300
def need(ok):
 if not ok:raise ValueError('COLLECTOR_GUARD')
def directory(path,owner):
 path=Path(path)
 for parent in path.parents:
  s=parent.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid in (0,owner) and not s.st_mode&0o022)
 s=path.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==owner and stat.S_IMODE(s.st_mode)==0o700 and not os.listxattr(path,follow_symlinks=False))
def append(fd,value,written):
 raw=(json.dumps(value,separators=(',',':'))+'\n').encode()
 # Reserve a fixed final diagnostic event rather than truncate an event.
 if written+len(raw)>MAX_OUTPUT-256:return None
 offset=0
 while offset<len(raw):
  n=os.write(fd,raw[offset:]);need(n>0);offset+=n
 return written+len(raw)
def run(root,seconds=MAX_SECONDS,max_events=MAX_EVENTS,prototype=False,socket_path=None):
 need(type(seconds) is int and 1<=seconds<=MAX_SECONDS and type(max_events) is int and 1<=max_events<=MAX_EVENTS)
 need(prototype or os.geteuid()==0)
 root=Path(root);directory(root,os.geteuid());output=root/'events.jsonl';address=Path(socket_path) if socket_path is not None else root/'input.sock'
 directory(address.parent,os.geteuid());need(len(os.fsencode(address))<108)
 # Caller creates fresh0700 directory. Never reuse stale socket/output or unlink others.
 need(not os.path.lexists(output) and not os.path.lexists(address))
 fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 sock=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM);identity=None;old={};stopped=[False];written=0
 try:
  s=os.fstat(fd);need(stat.S_ISREG(s.st_mode) and s.st_uid==os.geteuid() and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600)
  sock.bind(str(address));os.chmod(address,0o600);s=address.lstat();identity=(s.st_dev,s.st_ino);sock.settimeout(.2)
  def stop(signum,frame):stopped[0]=True
  for sig in (signal.SIGTERM,signal.SIGINT):old[sig]=signal.signal(sig,stop)
  written=append(fd,event('notice','collector_started'),written);deadline=time.monotonic()+seconds;count=0
  while not stopped[0] and time.monotonic()<deadline and count<max_events:
   try:raw,anc,flags,peer=sock.recvmsg(MAX_DATAGRAM,0)
   except socket.timeout:continue
   value=sanitize(raw,bool(flags&socket.MSG_TRUNC));del raw;count+=1
   new=append(fd,value,written)
   if new is None:
    # Guarded reserved space, enum only, no original event retained.
    os.write(fd,(json.dumps(event('warning','output_limit'))+'\n').encode());break
   written=new
  append(fd,event('notice','collector_stopped'),written);os.fsync(fd)
  return {'status':'PROTOTYPE_FINISHED','events':count,'privacy_acceptance':False}
 except BaseException:
  try:append(fd,event('err','collector_failure'),written);os.fsync(fd)
  except BaseException:pass
  raise RuntimeError('COLLECTOR_FAILED') from None
 finally:
  for sig,handler in old.items():signal.signal(sig,handler)
  sock.close();os.close(fd)
  if identity is not None:
   try:
    s=address.lstat()
    if stat.S_ISSOCK(s.st_mode) and (s.st_dev,s.st_ino)==identity:address.unlink()
   except FileNotFoundError:pass

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',required=True);p.add_argument('--seconds',type=int,default=MAX_SECONDS);p.add_argument('--events',type=int,default=MAX_EVENTS);p.add_argument('--isolated-prototype',action='store_true');p.add_argument('--socket');a=p.parse_args()
 try:print(json.dumps(run(a.directory,a.seconds,a.events,a.isolated_prototype,a.socket)));return 0
 except BaseException:print('{"status":"COLLECTOR_FAILED","privacy_acceptance":false}');return 1
if __name__=='__main__':raise SystemExit(main())
