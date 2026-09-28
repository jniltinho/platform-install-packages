"""Only fixed failure labels/counts from the one owned ended unit; no log/cursor output."""
import json,os,re,socket,stat,time
from pathlib import Path
ROOT=Path('/root/kaltura-baseline-private/baseline-freeze-8d1d3751')
CODES=['BOOT_CHANGED', 'BYTE_LIMIT', 'COMPLETE_FINITE_FILE_WINDOW', 'COMPLETE_FINITE_JOURNAL_WINDOW', 'CURSOR_CONTINUITY', 'DEADLINE', 'DUPLICATE_JSON_FIELD', 'EMPTY_JOURNAL', 'END_CURSOR_MISSING', 'IDENTITY_CHANGED', 'INVALID_JSON', 'INVENTORY', 'INVENTORY_CHANGED', 'JOURNAL_PROCESS', 'JOURNAL_STDERR', 'JOURNAL_TIMEOUT', 'LATEST_IDENTITY', 'LIMITS', 'OBSERVED_CURSOR_MISSING', 'OBSERVED_TAIL_MISSING', 'PATTERNS', 'RECORD_IDENTITY', 'RECORD_LIMIT', 'REWRITTEN', 'SCAN_FAILED', 'SHORT_READ', 'SNAPSHOT_FAILED', 'START', 'START_CURSOR_MISSING', 'SYMLINK', 'TAIL_REGRESSED', 'TRUNCATED', 'UNDRAINED_JOURNAL_TAIL', 'UNDRAINED_TAIL', 'UNSAFE_FILE', 'UNSAFE_PATH', 'UNSUPPORTED_FIELD', '_BOOT_ID', '__CURSOR']
PHASES={'files_initial','journal','files_after_journal'}
def need(ok):
 if not ok:raise ValueError('REJECTED')
def main():
 try:
  need(os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline')
  for p in (ROOT.parent,ROOT):
   s=p.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==0 and stat.S_IMODE(s.st_mode)==0o700 and not os.listxattr(p))
  until=time.monotonic()+5;names=[]
  with os.scandir(ROOT) as it:
   for row in it:need(len(names)<128 and time.monotonic()<until);names.append(row.name)
  boundaries=[];failures=[]
  for name in sorted(names):
   need(time.monotonic()<until)
   p=ROOT/name;s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==0 and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600 and s.st_size<=2*1024*1024 and not os.listxattr(p))
   match=re.fullmatch(r'boundary-([1-9][0-9]{0,2})[.]json',name)
   if match:boundaries.append(int(match[1]));continue
   match=re.fullmatch(r'failure-([1-9][0-9]{0,2})-(files_initial|journal|files_after_journal)[.]json',name);need(match is not None)
   fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
   try:
    opened=os.fstat(fd);need((opened.st_dev,opened.st_ino,opened.st_size)==(s.st_dev,s.st_ino,s.st_size));raw=os.read(fd,2*1024*1024+1);need(len(raw)==s.st_size)
   finally:os.close(fd)
   value=json.loads(raw);need(type(value) is dict and set(value)=={'phase','code','current_file_marks'} and value['phase']==match[2] and value['phase'] in PHASES and value['code'] in CODES)
   failures.append({'audit_number':int(match[1]),'phase':value['phase'],'code':value['code']})
  result={'status':'OWNED_PRIVATE_FAILURE_METADATA_OBSERVED','boundary_count':len(boundaries),'boundary_numbers':sorted(boundaries),'scanner_failures':failures,'raw_data_exported':False,'api_replayed':False,'privacy_pass':False}
 except Exception:result={'status':'FAILED_CLOSED','raw_data_exported':False,'api_replayed':False}
 print(json.dumps(result,sort_keys=True));return 0 if result['status']=='OWNED_PRIVATE_FAILURE_METADATA_OBSERVED' else 2
if __name__=='__main__':raise SystemExit(main())
