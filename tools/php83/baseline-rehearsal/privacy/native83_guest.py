#!/usr/bin/env python3
"""Synthetic-only isolated CLI process matrix; no app bootstrap, SQL, HTTP or auth."""
import hashlib,json,os,socket,subprocess,sys
from pathlib import Path
ROOT=Path('/home/vagrant/php83-privacy-synthetic-r1')
PHP='/usr/bin/php8.3'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pins(expected):
 actual={}
 for rel,pin in expected.items():
  p=ROOT/rel
  if p.is_symlink() or not p.is_file() or p.stat().st_uid!=0 or p.stat().st_mode&0o222:raise ValueError('Stage file unsafe')
  actual[rel]=sha(p)
 if actual!=expected:raise ValueError('Stage changed')
 return actual
def main(manifest_sha):
 if socket.gethostname()!='kaltura-php83-lab' or sha(ROOT/'manifest.json')!=manifest_sha:raise ValueError('Identity')
 manifest=json.loads((ROOT/'manifest.json').read_text());before=pins(manifest['files'])
 runtime={'php_sha256':sha(PHP),'json_provider':'builtin','php_version':subprocess.check_output([PHP,'-n','-r','echo PHP_VERSION;'],timeout=10).decode()}
 if runtime['php_sha256']!=manifest['expected_php_sha256'] or runtime['php_version']!='8.3.6':raise ValueError('Native PHP identity')
 command=[PHP,'-n','-d','display_errors=stderr','-d','log_errors=0','-d','error_reporting=-1','-d','zend.exception_ignore_args=0']
 results=[]
 for variant in ['original','privacy']:
  source=ROOT/variant
  lint=[]
  for path in ['infra/log/KalturaLog.php','api_v3/lib/KalturaFrontController.php','api_v3/lib/KalturaDispatcher.php']:
   p=subprocess.run(command+['-l',str(source/path)],capture_output=True,timeout=15)
   lint.append({'path':path,'exit':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()})
  p=subprocess.run(command+[str(ROOT/'probe.php'),str(source),variant],capture_output=True,timeout=20)
  results.append({'variant':variant,'exit':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode(),'lint':lint})
 after=pins(manifest['files'])
 if runtime['php_sha256']!=sha(PHP):raise ValueError('Runtime drift')
 return {'status':'SYNTHETIC_NATIVE_OBSERVATIONS_ONLY','source_base':manifest['source_base'],'base_archive_sha256':manifest['base_archive_sha256'],'hostname':socket.gethostname(),'runtime':runtime,'configuration':command[1:],'stage_before':before,'stage_after':after,'processes':results,'application_deployed':False,'real_auth_executed':False}
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1]),sort_keys=True))
 except Exception:
  print('Synthetic CLI identity or execution failure',file=sys.stderr);raise SystemExit(1)
