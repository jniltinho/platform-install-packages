"""Two exact lab paths, nofollow dirfd walks, no value/hash output."""
import grp,os,pwd,stat
from pathlib import Path
class Rejected(ValueError):pass
def need(ok):
 if not ok:raise Rejected('CREDENTIAL_METADATA')
def read_fixed(path):
 allowed={'/opt/kaltura/app/configurations/db.ini':(7373,33,0o640,131072),'/root/kaltura-baseline-private/mysql-password':(0,0,0o600,256)}
 need(path in allowed)
 uid,gid,mode,cap=allowed[path]
 if uid:
  need(pwd.getpwuid(7373).pw_name=='kaltura' and grp.getgrgid(33).gr_name=='www-data')
 exclusive=not any(n!='root' for n in grp.getgrgid(0).gr_mem) and not any(u.pw_uid!=0 and u.pw_gid==0 for u in pwd.getpwall())
 fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC);prefix=''
 try:
  parts=Path(path).parts
  for part in parts[1:-1]:
   new=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd);os.close(fd);fd=new;prefix+='/'+part;s=os.fstat(fd)
   expected=0o775 if prefix=='/opt/kaltura/app/configurations' else 0o700 if prefix in ('/root','/root/kaltura-baseline-private') else 0o755
   need(s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==expected and not os.listxattr(fd))
   if expected==0o775:need(exclusive)
  child=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=fd)
  try:
   a=os.fstat(child);need(stat.S_ISREG(a.st_mode) and (a.st_uid,a.st_gid,stat.S_IMODE(a.st_mode),a.st_nlink)==(uid,gid,mode,1) and a.st_size<=cap and not os.listxattr(child))
   raw=os.read(child,cap+1);b=os.fstat(child)
   need(len(raw)<=cap and len(raw)==a.st_size and (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns));return raw
  finally:os.close(child)
 finally:os.close(fd)
