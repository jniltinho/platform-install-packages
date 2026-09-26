import hashlib,json,socket,subprocess,sys
from pathlib import Path
ROOT=Path('/home/vagrant/php83-privacy-pipeline-r1');PHP='/usr/bin/php8.3'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def verify(manifest):
 result={}
 for name,pin in manifest['files'].items():
  p=ROOT/name
  if p.is_symlink() or p.stat().st_uid!=0 or p.stat().st_mode&0o222:raise ValueError('Unsafe source')
  result[name]=sha(p)
 if result!=manifest['files']:raise ValueError('Source drift')
 return result
def main(pin):
 if socket.gethostname()!='kaltura-php83-lab' or sha(ROOT/'manifest.json')!=pin:raise ValueError('Stage identity')
 m=json.loads((ROOT/'manifest.json').read_text());before=verify(m)
 if sha(PHP)!=m['php_sha256']:raise ValueError('Runtime identity')
 command=[PHP,'-n','-d','error_reporting=-1','-d','display_errors=stderr','-d','log_errors=0','-d','zend.exception_ignore_args=0']
 lints=[]
 for path in sorted(n for n in m['files'] if n.endswith('.php')):
  p=subprocess.run(command+['-l',str(ROOT/path)],capture_output=True,timeout=10)
  lints.append({'path':path,'exit':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()})
 p=subprocess.run(command+[str(ROOT/'probe.php'),str(ROOT/'source')],capture_output=True,timeout=20)
 report={'status':'SYNTHETIC_OBSERVATION_ONLY','lints':lints,'exit':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode(),'source_before':before,'source_after':verify(m),'php_sha256_after':sha(PHP),'privacy_acceptance':False}
 if report['php_sha256_after']!=m['php_sha256']:raise ValueError('Runtime changed')
 print(json.dumps(report,sort_keys=True))
if __name__=='__main__':main(sys.argv[1])
