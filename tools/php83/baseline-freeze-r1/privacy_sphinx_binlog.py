"""Sphinx RT binlog files under the log tree: full-content scan instead of append windows.
Operator decision 2026-09-28 after thumbnail r4 FILES_REWRITTEN: binlog.meta is rewritten in place with
constant size (binlog_path=/opt/kaltura/log/sphinx/data), which the append-window scanner rejects.
exclude() removes exactly this closed directory from EVERY append inventory (canonical, alias-checked);
scan() pins the directory by descriptor, opens each file relative to it without following links, verifies
the opened inode against its marks, reads it whole and counts private patterns. It runs in every ACCEPTED
audit (an audit that fails earlier already fails the round). Exports counts/sizes only, never names beyond
the fixed set, bytes or digests. Limitation: content written and then deleted between audits (binlog
rotation) is not observed."""
import os,re,stat,time
from pathlib import Path
DIRECTORY=Path('/opt/kaltura/log/sphinx/data')
NAME=re.compile(r'binlog\.(?:meta|lock|[0-9]{3,6})')
FILE_LIMIT=16*1024*1024
class Rejected(ValueError):pass
def need(ok,code='SPHINX_BINLOG_METADATA'):
 if not ok:raise Rejected(code)
def _open_dir():
 s=DIRECTORY.parent.lstat();need(stat.S_ISDIR(s.st_mode) and not s.st_mode&0o002)
 fd=os.open(DIRECTORY,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 s=os.fstat(fd)
 if not (stat.S_ISDIR(s.st_mode) and not s.st_mode&0o002):os.close(fd);raise Rejected('SPHINX_BINLOG_METADATA')
 return fd
def _names(dfd):
 names=sorted(os.listdir(dfd));need(0<len(names)<=64 and all(NAME.fullmatch(n) for n in names));return names
def _marks(dfd,names):
 out={}
 for n in names:
  s=os.stat(n,dir_fd=dfd,follow_symlinks=False);need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size<=FILE_LIMIT);out[n]=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)
 return out
def paths():
 dfd=_open_dir()
 try:names=_names(dfd);_marks(dfd,names)
 finally:os.close(dfd)
 return [DIRECTORY/n for n in names]
def exclude(existing):
 """Call on EVERY snapshot/rescan, like the other inventory adapters."""
 original=[Path(p) for p in existing()];need(len(set(map(str,original)))==len(original))
 paths() # the excluded directory must hold only the closed binlog name set
 real=DIRECTORY.resolve(strict=True)
 kept=[p for p in original if p!=DIRECTORY and DIRECTORY not in p.parents]
 for p in kept: # no alias to or into the directory
  q=p.resolve(strict=True);need(q!=real and real not in q.parents)
 return sorted(kept,key=str)
def _read(dfd,name,mark):
 fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=dfd)
 with os.fdopen(fd,'rb') as f:
  s=os.fstat(f.fileno());need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==mark and s.st_nlink==1,'SPHINX_BINLOG_UNSTABLE')
  data=f.read(mark[2]+1)
  s=os.fstat(f.fileno());need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==mark,'SPHINX_BINLOG_UNSTABLE')
 need(len(data)==mark[2],'SPHINX_BINLOG_UNSTABLE');return data
def scan(patterns,attempts=5,pause=0.2):
 need(type(patterns) in (list,tuple) and 0<len(patterns)<=72 and all(type(v) is bytes and 8<=len(v)<=8192 for v in patterns),'SPHINX_BINLOG_PATTERNS')
 for _ in range(attempts):
  dfd=_open_dir()
  try:
   dir_before=os.fstat(dfd);counts=[0]*len(patterns);total=0
   try:
    names=_names(dfd);before=_marks(dfd,names)
    for n in names:
     data=_read(dfd,n,before[n]);total+=len(data)
     for i,v in enumerate(patterns):
      pos=data.find(v)
      while pos>=0:counts[i]+=1;pos=data.find(v,pos+1)
    stable=_names(dfd)==names and _marks(dfd,names)==before
   except FileNotFoundError:stable=False # rotation removed a file mid-scan: retry
   except Rejected as error:
    if str(error)!='SPHINX_BINLOG_UNSTABLE':raise # bad metadata fails closed, no retry
    stable=False
   now,path=os.fstat(dfd),DIRECTORY.lstat() # one snapshot each; no split dev/ino reads
   same_dir=(now.st_dev,now.st_ino)==(dir_before.st_dev,dir_before.st_ino)==(path.st_dev,path.st_ino)
   if stable and same_dir:
    return {'status':'COMPLETE_FULL_CONTENT_SCAN','counts':counts,'files':len(names),'bytes':total,'deleted_between_audits_covered':False}
  finally:os.close(dfd)
  time.sleep(pause)
 raise Rejected('SPHINX_BINLOG_UNSTABLE')
def validate(v,patterns=None):
 """Public projection check (runner side)."""
 need(type(v) is dict and set(v)=={'status','counts','files','bytes','deleted_between_audits_covered','audit'},'SPHINX_BINLOG_SCHEMA')
 need(v['status']=='COMPLETE_FULL_CONTENT_SCAN' and v['deleted_between_audits_covered'] is False and type(v['counts']) is list and 0<len(v['counts'])<=72,'SPHINX_BINLOG_SCHEMA')
 need(all(type(v[k]) is int and v[k]>=0 for k in ('files','bytes','audit')) and 1<=v['audit']<=128 and v['files']<=64 and all(type(c) is int and c>=0 for c in v['counts']),'SPHINX_BINLOG_SCHEMA')
 return dict(v)
CODES=('SPHINX_BINLOG_METADATA','SPHINX_BINLOG_UNSTABLE','SPHINX_BINLOG_PATTERNS','SPHINX_BINLOG_SCHEMA','SPHINX_BINLOG_PIN')
