"""Native83 isolated fixture; root-owned immutable source and interpreter pins."""
import hashlib,json,socket,subprocess,sys
from pathlib import Path
ROOT=Path('/home/vagrant/privacy-caller-frame-v1');PHP='/usr/bin/php8.3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(files):
 for n,h in files.items():
  p=ROOT/n
  if p.is_symlink() or not p.is_file() or p.stat().st_uid!=0 or p.stat().st_mode&0o222 or sha(p)!=h:raise ValueError('Source identity')
 return files.copy()
def main(pin):
 if socket.gethostname()!='kaltura-php83-lab' or sha(ROOT/'manifest.json')!=pin:raise ValueError('Lab/manifest')
 m=json.loads((ROOT/'manifest.json').read_text());before=verify(m['files'])
 if sha(PHP)!=m['php_sha256']:raise ValueError('PHP identity')
 cmd=[PHP,'-n','-d','error_reporting=-1','-d','display_errors=stderr','-d','log_errors=0','-d','zend.exception_ignore_args=0']
 report={'status':'INCOMPLETE','source_before':before,'runtime_before':sha(PHP),'processes':[]}
 try:
  for variant in ['original','overlay','repaired']:
   row={'variant':variant,'lints':[]};report['processes'].append(row)
   for n in sorted(p for p in m['files'] if p.endswith('.php') and (p.startswith(variant+'/') or p=='probe.php')):
    p=subprocess.run(cmd+['-l',str(ROOT/n)],capture_output=True,timeout=10);row['lints'].append({'path':n,'exit':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()})
   p=subprocess.run(cmd+[str(ROOT/'probe.php'),str(ROOT/variant)],capture_output=True,timeout=20);row.update(exit=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode())
  report['status']='OBSERVED_ONLY'
 finally:
  report['source_after']=verify(m['files']);report['runtime_after']=sha(PHP);print(json.dumps(report,sort_keys=True))
 return 0 if report['status']=='OBSERVED_ONLY' and report['runtime_after']==report['runtime_before'] else 2
if __name__=='__main__':sys.exit(main(sys.argv[1]))
