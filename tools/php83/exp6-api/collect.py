#!/usr/bin/env python3
"""Serialized API matrix against a new owned synthetic DB; never save KS logs."""
import argparse,hashlib,importlib.util,json,re,shlex,subprocess,time,uuid
from pathlib import Path
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'patch-tests'
spec=importlib.util.spec_from_file_location('apache_diagnostics',OLD/'collect-api-apache.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
SSH=['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74']
ROOT='/home/vagrant/php-exp6-regression'
HTTP_EXPECTED=[]
for kind in (0,2):
 HTTP_EXPECTED.append(['http-session-start',kind,True])
 for method in ('GET','POST'):HTTP_EXPECTED.append(['http-session-get',kind,method,True])
for label,code in [('missing','SERVICE_FORBIDDEN'),('malformed','INVALID_KS'),('expired','INVALID_KS'),('wrong-secret','START_SESSION_ERROR'),('escalation','START_SESSION_ERROR')]:
 HTTP_EXPECTED.append(['http-rejected',label,code])
EXPECTED_STDOUT=json.dumps(HTTP_EXPECTED)+'\n'+json.dumps(['untrusted-ca-rejected',True])+'\n'+json.dumps(HTTP_EXPECTED)+'\n'


def remote(command,timeout=200):
 return subprocess.run(SSH+[command],capture_output=True,text=True,timeout=timeout)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);args=ap.parse_args()
 if args.output.exists():raise RuntimeError('Refusing to overwrite prior evidence')
 selected={f'api/{n}':HERE/n for n in ['run-apache.sh','start-db.sh','verify-source.py']}
 selected.update({f'tests/{n}':OLD/n for n in ['api-permission-schema.sql','api-session-schema.sql','api-web-router.php','api-apache-inner.sh','api-http-client.py']})
 expected={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in selected.items()}
 check=remote('cd '+ROOT+' && sha256sum '+' '.join(expected),30)
 if check.returncode:raise RuntimeError('Fixture hash command failed')
 found={line.split()[1]:line.split()[0] for line in check.stdout.splitlines()}
 if found!=expected:raise RuntimeError('Remote fixture drift')
 verify=remote('python3 '+ROOT+'/api/verify-source.py',60)
 if verify.returncode:raise RuntimeError('Extracted ZIP verification failed')
 artifact=json.loads(verify.stdout)
 previous=remote('python3 /home/vagrant/php-exp5-regression/api/verify-source.py',60)
 if previous.returncode:raise RuntimeError('exp5 reference source drift')
 previous_artifact=json.loads(previous.stdout)
 token=uuid.uuid4().hex
 db={'datadir':'/tmp/kaltura-pdo-mysql.'+token,'unit':'php83-exp6-api-'+token}
 records=[];cleanup={}
 try:
  start=remote('bash '+ROOT+'/api/start-db.sh '+token,120)
  if start.returncode:raise RuntimeError('Owned synthetic DB startup failed; inspect lab setup log')
  if json.loads(start.stdout)!=db:raise RuntimeError('Unexpected DB identity')
  for runtime in ['74','83']:
   for tree in ['original','exp5','exp6']:
    command='bash '+ROOT+'/api/run-apache.sh '+runtime+' '+tree+' '+shlex.quote(db['datadir'])
    t=time.monotonic_ns();run=remote(command)
    observations=[json.loads(line.split('PROBE_RUNTIME ',1)[1]) for line in run.stderr.splitlines() if 'PROBE_RUNTIME {' in line]
    records.append({'runtime':runtime,'tree':tree,'returncode':run.returncode,'stdout':run.stdout if run.stdout in ('',EXPECTED_STDOUT) else '', 'stdout_whitelisted':run.stdout in ('',EXPECTED_STDOUT),'stdout_sha256':hashlib.sha256(run.stdout.encode()).hexdigest(),'duration_ns':time.monotonic_ns()-t,'diagnostics':old.diagnostics(run.stderr),'runtime_observations':observations,'signature_failure':'Declaration of KalturaPDO::query() must be compatible' in run.stderr,'stderr_sha256':hashlib.sha256(run.stderr.encode()).hexdigest()})
 finally:
  stop=remote('sudo systemctl stop '+shlex.quote(db['unit'])+'; systemctl is-active '+shlex.quote(db['unit']),30)
  cleanup={'unit':db['unit'],'is_active_output':stop.stdout.strip(),'stopped':stop.stdout.strip() in ['inactive','failed','unknown']}
 baseline=next(r for r in records if r['runtime']=='74' and r['tree']=='original')
 comparisons=[{'runtime':r['runtime'],'tree':r['tree'],'matches_baseline':baseline['returncode']==0 and r['returncode']==0 and r['stdout']==baseline['stdout']} for r in records if r['tree'] in ['exp5','exp6']]
 control=next(r for r in records if r['runtime']=='83' and r['tree']=='original')
 passed=baseline['stdout']==EXPECTED_STDOUT and all(r['stdout_whitelisted'] for r in records) and control['returncode']!=0 and control['signature_failure'] and all(r['matches_baseline'] for r in comparisons) and cleanup['stopped']
 report={'schema':1,'scope':'actual exp6 ZIP web/index.php, synthetic SQL, Apache HTTP/trustedHTTPS; NOT AIO/FPM acceptance','artifact':artifact,'previous_artifact':previous_artifact,'harness':expected,'imported_helper_sha256':{n:hashlib.sha256((OLD/n).read_bytes()).hexdigest() for n in ['collect-api-apache.py','collect-api-mysql.py']},'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'db':db,'cleanup':cleanup,'records':records,'comparisons':comparisons,'original83_signature_control':control['signature_failure'],'functional_checks_passed':passed,'application_acceptance':False}
 args.output.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'functional_checks_passed':passed,'comparisons':comparisons,'cleanup':cleanup}))
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
