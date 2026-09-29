"""Log files created inside an audit window are scanned from offset 0 (whole content is in-window).
Phase A (long upload) failed BATCH_PRIVACY with INVENTORY_CHANGED because workers create daily logs
(e.g. batch/extractmedia-0-<date>.log) on their first job. The append-window scanner requires a fixed
file set, so augment() adds every inventory path missing from the round-start snapshot with a zero
offset; an empty new file keeps its current mtime, so a later same-size touch is still REWRITTEN.
A per-window registry (keyed by the start snapshot object) remembers every new file ever admitted with
its identity and largest observed size, across retries and across audit_once calls of the same window:
a new file that vanishes, changes identity or shrinks fails closed, so a match can never be dropped by
retrying without it. scan() retries only INVENTORY_CHANGED (bounded) and rechecks new files afterwards.
An inventoried file renamed to a new path is rejected. Adapter errors (Rejected) fail closed as
UNEXPECTED in the guest. Exports nothing itself."""
import os,stat,time
CODES=('NEW_LOG_METADATA','NEW_LOG_LIMIT','NEW_LOG_VANISHED','NEW_LOG_TRUNCATED')
class Rejected(ValueError):pass
def need(ok,code='NEW_LOG_METADATA'):
 if not ok:raise Rejected(code)
_WINDOWS={} # id(start) -> (start, {path: [dev, ino, max_size]}); start kept alive so ids are not reused
def _seen(start):
 entry=_WINDOWS.get(id(start))
 if entry is None or entry[0] is not start:
  # One guest process audits only a handful of windows; a bound fails closed instead of evicting records.
  need(len(_WINDOWS)<32,'NEW_LOG_LIMIT');entry=_WINDOWS[id(start)]=(start,{})
 return entry[1]
def _check_seen(seen):
 for name,(dev,ino,size) in seen.items():
  try:s=os.lstat(name)
  except FileNotFoundError:raise Rejected('NEW_LOG_VANISHED') from None
  need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and (s.st_dev,s.st_ino)==(dev,ino),'NEW_LOG_VANISHED')
  need(s.st_size>=size,'NEW_LOG_TRUNCATED');seen[name][2]=s.st_size
def augment(start,inventory,mark_type,limit=64):
 seen=_seen(start);_check_seen(seen)
 out=dict(start);known={(m.device,m.inode) for m in start.values()};current=set()
 for p in inventory():
  name=os.fspath(p);current.add(name)
  if name in out:continue
  s=os.lstat(name);need(stat.S_ISREG(s.st_mode) and s.st_nlink==1)
  need((s.st_dev,s.st_ino) not in known) # an inventoried file renamed to a new path is not new
  if name in seen:need(seen[name][:2]==[s.st_dev,s.st_ino],'NEW_LOG_VANISHED');need(s.st_size>=seen[name][2],'NEW_LOG_TRUNCATED')
  else:seen[name]=[s.st_dev,s.st_ino,s.st_size]
  seen[name][2]=max(seen[name][2],s.st_size)
  out[name]=mark_type(s.st_dev,s.st_ino,0,s.st_mtime_ns if s.st_size==0 else 0)
 need(set(seen)<=current,'NEW_LOG_VANISHED');need(len(seen)<=limit,'NEW_LOG_LIMIT')
 return out
def scan(files,start,patterns,inventory,attempts=5,pause=1.0):
 """files: the pinned append-window scanner module (scan_window, Mark, Incomplete)."""
 for i in range(attempts):
  try:result=files.scan_window(augment(start,inventory,files.Mark),patterns,inventory=inventory)
  except files.Incomplete as error:
   if str(error)!='INVENTORY_CHANGED' or i==attempts-1:raise
   time.sleep(pause);continue
  _check_seen(_seen(start));return result
