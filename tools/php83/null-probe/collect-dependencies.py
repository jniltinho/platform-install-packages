#!/usr/bin/env python3
"""Real PermissionPeer dependency filtering, owned synthetic SQL only."""
import argparse,hashlib,importlib.util,json,uuid
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('exp5_api',HERE.parent/'exp5-api/collect.py')
api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
EXPECTED=[['empty',[]],['null',['ROOT']],['empty-dependency',['ROOT']],['zero-dependency',['ROOT']],['satisfied',['ROOT','CHILD']],['missing',[]],['transitive',[]],['whitespace-csv',['ROOT','CHILD']],['partner-feature',['CHILD']],['wrong-partner',[]]]

def require(condition,message):
 if not condition:raise RuntimeError(message)

def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
 require(not a.output.exists(),'Evidence exists')
 selected={'null-probe/'+n:HERE/n for n in ['dependencies.php','run-dependencies.sh']}
 selected.update({'tests/'+n:api.OLD/n for n in ['api-bootstrap.php','api-permission-schema.sql']})
 selected['api/start-db.sh']=api.HERE/'start-db.sh'
 hashes={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in selected.items()}
 check=api.remote('cd '+api.ROOT+' && sha256sum '+' '.join(hashes))
 require(check.returncode==0,'Hash command failed')
 require({l.split()[1]:l.split()[0] for l in check.stdout.splitlines()}==hashes,'Fixture drift')
 artifacts={}
 for source in ['exp4','exp5']:
  verify=api.remote('python3 /home/vagrant/php-'+source+'-regression/api/verify-source.py')
  require(verify.returncode==0,'Source verification failed');artifacts[source]=json.loads(verify.stdout)
 token=uuid.uuid4().hex;db={'datadir':'/tmp/kaltura-pdo-mysql.'+token,'unit':'php83-exp5-api-'+token};rows=[]
 try:
  start=api.remote('bash '+api.ROOT+'/api/start-db.sh '+token,120)
  require(start.returncode==0 and json.loads(start.stdout)==db,'Owned DB startup failed')
  for runtime in ['74','83']:
   for source in ['exp4','exp5']:
    command='bash '+api.ROOT+'/null-probe/run-dependencies.sh '+runtime+' '+source+' '+db['datadir']
    result=api.remote(command,90)
    # Never persist raw application stderr or arbitrary stdout.
    try:actual=json.loads(result.stdout)
    except ValueError:actual=None
    passed=result.returncode==0 and actual==EXPECTED
    rows.append({'runtime':runtime,'source':source,'exit':result.returncode,'matches_expected':passed,'stdout':EXPECTED if passed else None,'stderr_sha256':hashlib.sha256(result.stderr.encode()).hexdigest(),'diagnostics':api.old.diagnostics(result.stderr)})
 finally:
  stop=api.remote('sudo systemctl stop '+db['unit']+'; systemctl is-active '+db['unit'],30)
  cleanup={'unit':db['unit'],'state':stop.stdout.strip(),'stopped':stop.stdout.strip() in ['inactive','unknown','failed']}
 report={'schema':1,'scope':'real PermissionPeer::filterDependencies, actual KalturaPDO/SQL, ten synthetic dependency cases','artifacts':artifacts,'harness':hashes,'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'imported_collector_sha256':hashlib.sha256((api.HERE/'collect.py').read_bytes()).hexdigest(),'rows':rows,'cleanup':cleanup,'functional_checks_passed':all(r['matches_expected'] for r in rows) and cleanup['stopped'],'application_acceptance':False}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['functional_checks_passed'],'cleanup':cleanup}))
 return 0 if report['functional_checks_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
