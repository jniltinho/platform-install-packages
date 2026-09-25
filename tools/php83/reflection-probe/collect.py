#!/usr/bin/env python3
"""Compare native reflection and real API metadata without modifying the source ZIP."""
import argparse,hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
def require(ok,message):
 if not ok:raise RuntimeError(message)
def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--runtime',choices=['74','83']);a=p.parse_args()
 require(not a.output.exists(),'Evidence exists')
 metadata=json.loads((REPO/'patches/php83/held/KalturaActionReflector-parameter-class.json').read_text())
 expected={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['native.php','run.sh','metadata.php','metadata-cases.php','run-metadata.sh']}
 expected.update({'original.php':metadata['before_sha256'],'candidate.php':metadata['after_sha256']})
 bootstrap=hashlib.sha256((HERE.parent/'patch-tests/api-bootstrap.php').read_bytes()).hexdigest()
 records=[];comparisons=[]
 for runtime,alias in [('74','baseline74'),('83','php83')]:
  if a.runtime and runtime!=a.runtime:continue
  def remote(command):return subprocess.run(['ssh','-T','-F','/tmp/kaltura-php'+runtime+'-ssh.conf',alias,command],capture_output=True,text=True,timeout=90)
  check=remote('cd /home/vagrant/php-reflection-probe && sha256sum '+' '.join(expected))
  require(check.returncode==0,'Hash command failed')
  require({l.split()[1]:l.split()[0] for l in check.stdout.splitlines()}==expected,'Probe source drift')
  check=remote('sha256sum /home/vagrant/php-exp5-regression/tests/api-bootstrap.php')
  require(check.returncode==0 and check.stdout.split()[0]==bootstrap,'Bootstrap drift')
  verified=remote('python3 /home/vagrant/php-exp5-regression/api/verify-source.py')
  require(verified.returncode==0,'Base artifact drift');artifact=json.loads(verified.stdout)
  local=[]
  for kind,script,variants,count in [('native','run.sh',['native','candidate'],15 if runtime=='74' else 22),('metadata','run-metadata.sh',['original','candidate'],17 if runtime=='74' else 24)]:
   for variant in variants:
    result=remote('bash /home/vagrant/php-reflection-probe/'+script+' '+variant)
    require(result.returncode==0,'Reflection fixture failed: '+runtime+'/'+kind+'/'+variant)
    body=json.loads(result.stdout);require(len(body['rows'])==count,'Missing cases')
    record={'runtime':runtime,'kind':kind,'variant':variant,'exit':result.returncode,'result':body,'bootstrap_stderr':result.stderr,'base_artifact':artifact}
    records.append(record);local.append(record)
   before,after=local[-2:]
   require(before['result']['rows']==after['result']['rows'],'Reflection contract mismatch')
   if runtime=='83':require(not after['result']['warnings'],'Candidate reflection warnings remain')
   comparisons.append({'runtime':runtime,'kind':kind,'rows_equal':True,'cases':count})
  after_verify=remote('python3 /home/vagrant/php-exp5-regression/api/verify-source.py')
  require(after_verify.returncode==0 and json.loads(after_verify.stdout)==artifact,'Base source changed')
 report={'schema':1,'scope':'native ReflectionParameter contract and real KalturaActionReflector metadata; no API SQL/HTTP or shared cache acceptance','patch':metadata,'harness':expected,'bootstrap_sha256':bootstrap,'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'records':records,'comparisons':comparisons,'functional_checks_passed':True,'application_acceptance':False}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(comparisons))
if __name__=='__main__':main()
