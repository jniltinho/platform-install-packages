"""Read-only ended-unit file-window shape diagnostic. No API, credentials or raw output.
Not an exact reconstruction of discarded pattern counts; never a privacy PASS.
"""
import json,os,re,socket,stat,subprocess,time
from pathlib import Path
from urllib.parse import unquote,urlsplit
ROOT=Path('/root/kaltura-baseline-private/baseline-freeze-465479bb')
ASSET='0_ewuu0o46';ENTRY='0_wzmt2sfy'
CATEGORIES=('application','apache','nginx','system','tls')
FIELDS=('lines','owned_route_candidates','query_candidates','credential_marker_candidates','long_segments','filename_long_segments','synthetic_filename_shape','other_long_segments','unparseable_candidates')
MARKERS={'ks','kt','token','access_token','auth','authorization','session','sessionid','password','secret','signature','sig'}
class Rejected(ValueError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def category(path):
 p=Path(path);need(p.is_absolute() and '..' not in p.parts,'PATH')
 for prefix,label in (('/opt/kaltura/log/','application'),('/var/log/apache2/','apache'),('/var/log/nginx/','nginx'),('/var/lib/kaltura-baseline-tls-logs-r2/','tls')):
  if str(p).startswith(prefix):return label
 if str(p) in ('/var/log/syslog','/var/log/messages'):return 'system'
 raise Rejected('PATH')
def blank():return {k:0 for k in FIELDS}
def classify(line,counters):
 need(type(line) is bytes and len(line)<=65536,'LINE_LIMIT');counters['lines']+=1
 if ASSET.encode() not in line and ENTRY.encode() not in line:return
 # Inspect URL/path-shaped tokens only. Never return text or derived identifiers.
 for raw in re.findall(rb'(?:https?://|/)[^\s<>"\x27\x00]{1,8192}',line):
  if ASSET.encode() not in raw and ENTRY.encode() not in raw:continue
  counters['owned_route_candidates']+=1
  try:
   value=raw.decode('utf-8');value=unquote(unquote(value));p=urlsplit(value);parts=p.path.split('/')
  except (ValueError,UnicodeError):counters['unparseable_candidates']+=1;continue
  counters['query_candidates']+=int(bool(p.query))
  counters['credential_marker_candidates']+=int(any(v.lower() in MARKERS for v in parts))
  for index,part in enumerate(parts):
   if len(part)<16:continue
   counters['long_segments']+=1
   is_name=index>0 and parts[index-1]=='fileName'
   counters['filename_long_segments' if is_name else 'other_long_segments']+=1
   if is_name and re.fullmatch(r'privacy-media-[a-f0-9]{32}-short360(?:[^/]{0,128})[.]mp4',part):counters['synthetic_filename_shape']+=1

def read_boundary(number):
 p=ROOT/('boundary-'+str(number)+'.json');s=p.lstat()
 need(stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1 and s.st_size<=2*1024*1024 and not os.listxattr(p),'BOUNDARY_METADATA')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 try:
  current=os.fstat(fd);need((current.st_dev,current.st_ino,current.st_size)==(s.st_dev,s.st_ino,s.st_size),'BOUNDARY_CHANGED');raw=os.read(fd,2*1024*1024+1);need(len(raw)==s.st_size,'BOUNDARY_CHANGED')
 finally:os.close(fd)
 v=json.loads(raw);need(type(v) is dict and set(v)=={'file_marks','journal'} and type(v['file_marks']) is dict and 0<len(v['file_marks'])<=512,'BOUNDARY_SCHEMA')
 for path,mark in v['file_marks'].items():
  category(path);need(type(mark) is dict and set(mark)=={'device','inode','size','mtime_ns'} and all(type(n) is int and n>=0 for n in mark.values()),'MARK_SCHEMA')
 return v

def observe():
 need(os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline','TARGET')
 ip=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=5));ips={v.get('local') for r in ip for v in r.get('addr_info',[])};need('192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}),'TARGET')
 q=subprocess.run(['systemctl','is-active','baseline-freeze-465479bb.service'],capture_output=True,timeout=5);need(q.returncode in (3,4) and q.stdout.strip() in (b'inactive',b'unknown'),'UNIT_ACTIVE')
 for p in (ROOT.parent,ROOT):
  s=p.lstat();need(stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o700 and not os.listxattr(p),'PRIVATE_PARENT')
 start=read_boundary(3);need(start==read_boundary(4),'START_WINDOWS_DIFFER')
 until=time.monotonic()+10;total=0;files=0;result={k:blank() for k in CATEGORIES}
 for name,mark in sorted(start['file_marks'].items()):
  need(time.monotonic()<until,'DEADLINE');p=Path(name)
  for component in (p,*p.parents):need(not stat.S_ISLNK(component.lstat().st_mode),'SYMLINK')
  s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and (s.st_dev,s.st_ino)==(mark['device'],mark['inode']) and s.st_size>=mark['size'],'LOG_IDENTITY')
  count=s.st_size-mark['size'];total+=count;need(total<=64*1024*1024,'BYTE_LIMIT');files+=1
  fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
  try:
   current=os.fstat(fd);need((current.st_dev,current.st_ino,current.st_size,current.st_mtime_ns)==(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns),'LOG_CHANGED')
   os.lseek(fd,mark['size'],os.SEEK_SET);remaining=count;pending=b''
   while remaining:
    need(time.monotonic()<until,'DEADLINE');block=os.read(fd,min(65536,remaining));need(bool(block),'SHORT_READ');remaining-=len(block);pending+=block
    while b'\n' in pending:
     line,pending=pending.split(b'\n',1);classify(line,result[category(name)])
    need(len(pending)<=65536,'LINE_LIMIT')
   if pending:classify(pending,result[category(name)])
   current=os.fstat(fd);need((current.st_size,current.st_mtime_ns)==(s.st_size,s.st_mtime_ns),'LOG_CHANGED')
  finally:os.close(fd)
 return {'status':'SAVED_START_FILE_WINDOW_SHAPES_OBSERVED','files':files,'bytes':total,'sinks':result,'journal_scanned':False,'exact_prior_patterns_reconstructed':False,'cause_confirmed':False,'privacy_pass':False,'api_replayed':False,'raw_data_exported':False}
def main():
 try:r=observe()
 except Rejected as e:r={'status':'FAILED_CLOSED','code':str(e),'raw_data_exported':False,'api_replayed':False,'privacy_pass':False}
 except Exception:r={'status':'FAILED_CLOSED','code':'UNEXPECTED','raw_data_exported':False,'api_replayed':False,'privacy_pass':False}
 print(json.dumps(r,sort_keys=True));return 0 if r['status']=='SAVED_START_FILE_WINDOW_SHAPES_OBSERVED' else 2
if __name__=='__main__':raise SystemExit(main())
