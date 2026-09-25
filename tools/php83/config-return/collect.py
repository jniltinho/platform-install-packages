#!/usr/bin/env python3
"""Test actual Zend_Config returns against unchanged 7.4/8.3 and held 8.3 only."""
import argparse,hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
def require(value,message):
 if not value:raise RuntimeError(message)
def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
 require(not a.output.exists(),'Refusing to replace evidence')
 metadata=json.loads((REPO/'patches/php83/held/Zend-Config-return-types.json').read_text())
 harness={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['probe.php','run.sh']}
 expected=dict(harness,**{'candidate.php':metadata['after_sha256']})
 contracts={'count':'int','current':'mixed','key':'mixed','next':'void','rewind':'void','valid':'bool'}
 records=[]
 for runtime,alias in [('74','baseline74'),('83','php83')]:
  def remote(command):return subprocess.run(['ssh','-T','-F','/tmp/kaltura-php'+runtime+'-ssh.conf',alias,command],capture_output=True,text=True,timeout=90)
  check=remote('cd /home/vagrant/php-config-return && sha256sum '+' '.join(expected))
  require(check.returncode==0,'Fixture hash command failed')
  require({l.split()[1]:l.split()[0] for l in check.stdout.splitlines()}==expected,'Fixture drift')
  verify=remote('python3 /home/vagrant/php-exp6-regression/api/verify-source.py');require(verify.returncode==0,'Base ZIP drift');artifact=json.loads(verify.stdout)
  for variant in (['original'] if runtime=='74' else ['original','candidate']):
   command='bash /home/vagrant/php-config-return/run.sh '+variant
   run=remote(command);require(run.returncode==0,'Fixture failed: '+runtime+'/'+variant+' '+run.stderr)
   data=json.loads(run.stdout);require(len(data['rows'])==16,'Missing cases')
   require(data['contracts']==(contracts if variant=='candidate' else dict.fromkeys(contracts)),'Return contract mismatch')
   warnings=data['warnings']
   if runtime=='83' and variant=='original':
    require(len(warnings)==6 and all(w[0]==8192 and 'Return type of Zend_Config::' in w[1] for w in warnings),'Original deprecation control missing')
   else:require(warnings==[],'Unexpected diagnostic')
   records.append({'runtime':runtime,'variant':variant,'command':command,'exit':run.returncode,'stderr':run.stderr,'artifact':artifact,'result':data})
  after=remote('python3 /home/vagrant/php-exp6-regression/api/verify-source.py');require(after.returncode==0 and json.loads(after.stdout)==artifact,'Base ZIP changed')
 require(all(r['result']['rows']==records[0]['result']['rows'] for r in records),'Functional output mismatch')
 report={'schema':1,'patch':metadata,'harness':expected,'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'records':records,'functional_checks_passed':True,'candidate_runtime':'8.3 only; no candidate7.4 compatibility claim','application_acceptance':False}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print('16 cases agree across original74/original83/candidate83; six candidate return contracts and warning controls pass')
if __name__=='__main__':main()
