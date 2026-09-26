"""Four synthetic full-pipeline processes in fresh immutable stage; no app/bootstrap."""
import hashlib,json,socket,subprocess,sys
from pathlib import Path
ROOT=Path('/home/vagrant/privacy-trace-policy-v1')
PHP74='/usr/bin/php7.4';PHP83='/home/vagrant/php-mysql-probe/runtime83/php8.3';JSON74='/usr/lib/php/20190902/json.so'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(expected):
 for path,pin in expected.items():
  p=ROOT/path
  if p.is_symlink() or not p.is_file() or p.stat().st_uid!=0 or p.stat().st_mode&0o222 or sha(p)!=pin:raise ValueError('Unsafe/drifted source')
 return expected.copy()
def main(pin):
 if socket.gethostname()!='kaltura-php74-baseline' or sha(ROOT/'manifest.json')!=pin:raise ValueError('Lab/stage identity')
 m=json.loads((ROOT/'manifest.json').read_text());before=verify(m['files'])
 runtime={p:sha(p) for p in m['runtime']}
 if runtime!=m['runtime']:raise ValueError('Runtime identity')
 report={'status':'INCOMPLETE','source_before':before,'runtime_before':runtime,'processes':[],'application_modified':False}
 try:
  for variant,php,flags in [('original74',PHP74,['-d','extension='+JSON74]),('policy74',PHP74,['-d','extension='+JSON74]),('original83',PHP83,[]),('policy83',PHP83,[])]:
   command=[php,'-n']+flags+['-d','error_reporting=-1','-d','display_errors=stderr','-d','log_errors=0','-d','zend.exception_ignore_args=0']
   row={'variant':variant,'command':command,'lints':[]};report['processes'].append(row)
   for name in sorted(n for n in m['files'] if n.startswith(variant+'/') and n.endswith('.php')):
    p=subprocess.run(command+['-l',str(ROOT/name)],capture_output=True,timeout=10)
    row['lints'].append({'path':name,'exit':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()})
   p=subprocess.run(command+[str(ROOT/'probe.php'),str(ROOT/variant)],capture_output=True,timeout=20)
   row.update(exit=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode())
  report['status']='OBSERVED_NOT_ACCEPTED'
 except Exception as e:report['failure_class']=type(e).__name__
 finally:
  report['source_after']=verify(m['files']);report['runtime_after']={p:sha(p) for p in m['runtime']}
  print(json.dumps(report,sort_keys=True))
 return 0 if report['status']=='OBSERVED_NOT_ACCEPTED' and report['runtime_after']==runtime else 2
if __name__=='__main__':sys.exit(main(sys.argv[1]))
