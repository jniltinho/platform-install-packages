#!/usr/bin/env python3
"""Focused Criteria return-contract validation; no SQL or full bootstrap acceptance."""
import argparse,hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
def require(ok,message):
 if not ok:raise RuntimeError(message)
def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
 require(not a.output.exists(),'Evidence already exists')
 metadata=json.loads((REPO/'patches/php83/held/Criteria-native-returns.json').read_text())
 expected={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['probe.php','run.sh']}
 expected.update({'previous.php':metadata['prior_candidate_sha256'],'candidate.php':metadata['after_sha256']})
 contracts={'Criteria::getIterator':'Traversable','CriterionIterator::rewind':'void','CriterionIterator::valid':'bool','CriterionIterator::key':'mixed','CriterionIterator::current':'mixed','CriterionIterator::next':'void'}
 records=[]
 for runtime,alias in [('74','baseline74'),('83','php83')]:
  def remote(command):return subprocess.run(['ssh','-T','-F','/tmp/kaltura-php'+runtime+'-ssh.conf',alias,command],capture_output=True,text=True,timeout=90)
  check=remote('cd /home/vagrant/php-criteria-return && sha256sum '+' '.join(expected));require(check.returncode==0,'Fixture hash command failed')
  require({l.split()[1]:l.split()[0] for l in check.stdout.splitlines()}==expected,'Fixture drift')
  verify=remote('python3 /home/vagrant/php-exp7-regression/api/verify-source.py');require(verify.returncode==0,'Base artifact drift');artifact=json.loads(verify.stdout)
  for variant in (['previous'] if runtime=='74' else ['previous','candidate']):
   command='bash /home/vagrant/php-criteria-return/run.sh '+variant
   run=remote(command);require(run.returncode==0,'Fixture failed '+runtime+'/'+variant+': '+run.stderr)
   data=json.loads(run.stdout);require(len(data['rows'])==16,'Missing rows')
   require(data['contracts']==(contracts if variant=='candidate' else dict.fromkeys(contracts)),'Signature mismatch')
   warnings=data['load_diagnostics']
   if runtime=='83' and variant=='previous':
    require(len(warnings)==6 and all(w[0]==8192 and 'Return type of ' in w[1] for w in warnings),'Missing prior return warning controls')
   else:require(warnings==[],'Unexpected load diagnostic')
   require(len(data['invalid_controls'])==2,'Missing negative controls')
   for label,value,diagnostics in data['invalid_controls']:
    require(value==[None,None] and len(diagnostics)==2,'Invalid access control changed')
    require(all(d[0]==(8 if runtime=='74' else 2) for d in diagnostics),'Unexpected invalid-access severity')
   records.append({'runtime':runtime,'variant':variant,'command':command,'exit':run.returncode,'stderr':run.stderr,'artifact':artifact,'result':data})
  after=remote('python3 /home/vagrant/php-exp7-regression/api/verify-source.py');require(after.returncode==0 and json.loads(after.stdout)==artifact,'Source artifact changed')
 require(all(r['result']['rows']==records[0]['result']['rows'] for r in records),'Functional parity failed')
 require(records[1]['result']['invalid_controls']==records[2]['result']['invalid_controls'],'Same-runtime error contract changed')
 report={'schema':1,'scope':'actual Criteria and two direct subclasses; DB lookup stub, no SQL','patch':metadata,'harness':expected,'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'records':records,'functional_checks_passed':True,'candidate_runtime':'8.3 only','application_acceptance':False}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print('16 positive rows and two invalid-iterator controls pass; six load deprecations removed')
if __name__=='__main__':main()
