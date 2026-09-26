"""Read-only installed files and logger metadata, no bootstrap or live credentials."""
import hashlib,json,os,re,socket,stat,subprocess,sys
from pathlib import Path
APP=Path('/opt/kaltura/app')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main(payload):
 if socket.gethostname()!='kaltura-php74-baseline':raise ValueError('Host guard')
 p=subprocess.run(['ip','-j','-4','addr'],capture_output=True,timeout=10,check=True)
 ips={a.get('local') for link in json.loads(p.stdout) for a in link.get('addr_info',[])}
 if '192.168.56.74' not in ips or ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}):raise ValueError('Address guard')
 runtime={p:sha(Path(p).read_bytes()) for p in payload['runtime']}
 if runtime!=payload['runtime']:raise ValueError('Runtime drift')
 files={};ok=True
 for name,expected in payload['sources'].items():
  p=APP/name;s=p.lstat()
  regular=stat.S_ISREG(s.st_mode) and s.st_nlink==1
  actual=sha(p.read_bytes()) if regular else None
  files[name]={'sha256':actual,'expected_sha256':expected,'regular_single_link':regular,'uid':s.st_uid,'gid':s.st_gid,'mode':oct(stat.S_IMODE(s.st_mode)),'matches':actual==expected}
  ok=ok and regular and actual==expected
 result={'status':'INSTALLED_READ_ONLY_SOURCE_JOIN','files':files,'all_sources_match_original':ok,'application_changed':False,'full_effective_config_attested':False}
 if ok:
  p=subprocess.run(['/usr/bin/php7.4','-n','-d','extension=/usr/lib/php/20190902/json.so','-d','error_reporting=-1','-d','display_errors=stderr','-d','log_errors=0','-r',payload['logger_code']],capture_output=True,timeout=20)
  result['logger_audit_exit']=p.returncode
  result['logger_stderr_bytes']=len(p.stderr)
  # No raw errors/config values are exported on failed parsing.
  if p.returncode==0:result['disk_logger']=json.loads(p.stdout)
  else:result['status']='CONFIG_READ_FAILED_NO_VALUES_EXPORTED'
 result['sources_unchanged_after']=all(sha((APP/n).read_bytes())==v['sha256'] for n,v in files.items() if v['regular_single_link'])
 result['runtime_unchanged_after']=all(sha(Path(p).read_bytes())==v for p,v in runtime.items())
 result['http_requests']=0;result['private_user_credential_file_read']=False;result['logger_cache_config_values_loaded_guest_only']=ok
 print(json.dumps(result,sort_keys=True))
if __name__=='__main__':
 try:main(PAYLOAD)
 except Exception:print(json.dumps({'status':'READ_ONLY_AUDIT_REJECTED','no_values_exported':True}));sys.exit(1)
