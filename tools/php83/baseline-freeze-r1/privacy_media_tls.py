"""Immutable mandatory nginx TLS8444 log inventory extension.
Compose after existing legacy + Apache TLS inventory on every snapshot/rescan.
Never treat private mode as permission for secret-bearing log content.
"""
import os,stat
from pathlib import Path
DIRECTORY=Path('/var/lib/kaltura-baseline-media-tls-r1')
FILES=('access.log','error.log')
EXPECTED={'intent.json','ssl.before','terminal.json',*FILES}
class Rejected(ValueError):pass
def need(ok):
 if not ok:raise Rejected('MEDIA_TLS_LOG_METADATA')
def paths():
 for p in (Path('/'),Path('/var'),Path('/var/lib'),DIRECTORY):
  s=p.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and not s.st_mode&0o022 and not os.listxattr(p))
 need(stat.S_IMODE(DIRECTORY.lstat().st_mode)==0o700)
 need({p.name for p in DIRECTORY.iterdir()}==EXPECTED)
 result=[]
 for name in sorted(EXPECTED):
  p=DIRECTORY/name;s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and not os.listxattr(p))
  if name in FILES:result.append(p)
 return result
def extend(existing):
 original=list(existing());extra=paths();need(len(set(map(str,original)))==len(original));need(not set(map(str,original))&set(map(str,extra)))
 return sorted(original+extra,key=str)
