"""Exact additional root-private TLS log inventory for existing finite scanners."""
import os,stat
from pathlib import Path
DIRECTORY=Path('/var/lib/kaltura-baseline-tls-logs-r2')
FILES=('access.log','error.log')
class Rejected(ValueError):pass
def need(ok):
 if not ok:raise Rejected('TLS_LOG_METADATA')
def paths():
 # Directory and root ancestors must not be substitutable by nonroot writers.
 for p in (Path('/'),Path('/var'),Path('/var/lib'),DIRECTORY):
  s=p.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and not s.st_mode&0o022 and not os.listxattr(p))
 need(stat.S_IMODE(DIRECTORY.lstat().st_mode)==0o700)
 need({p.name for p in DIRECTORY.iterdir()}==set(FILES))
 result=[]
 for n in FILES:
  p=DIRECTORY/n;s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and not os.listxattr(p));result.append(p)
 return result

def extend(existing):
 """Call on EVERY snapshot/rescan, never only initial inventory."""
 original=list(existing());extra=paths()
 need(not set(map(str,original))&set(map(str,extra)))
 return sorted(original+extra,key=str)
