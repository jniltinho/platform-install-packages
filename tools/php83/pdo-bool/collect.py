#!/usr/bin/env python3
"""Validate minimal boolean result repairs on an owned SQL database."""
import argparse,hashlib,importlib.util,json,uuid
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('exp8_api',HERE.parent/'exp8-api/collect.py')
api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
ROOT='/home/vagrant/php-pdo-bool'
def require(ok,message):
 if not ok:raise RuntimeError(message)
def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
 require(not a.output.exists(),'Evidence exists')
 selected={ROOT+'/'+n:HERE/n for n in ['probe.php','run.sh']}
 metadata=[json.loads((HERE.parents[2]/('patches/php83/held/'+name+'.json')).read_text()) for name in ['PropelPDO-bool-setAttribute','KalturaStatement-bool-results']]
 selected[api.ROOT+'/api/start-db.sh']=api.HERE/'start-db.sh'
 selected[api.ROOT+'/api/verify-source.py']=api.HERE/'verify-source.py'
 hashes={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in selected.items()}
 for name,m in zip(['PropelPDO-bool-setAttribute','KalturaStatement-bool-results'],metadata):hashes[ROOT+'/'+name+'.php']=m['after_sha256']
 check=api.remote('sha256sum '+' '.join(hashes));require(check.returncode==0,'Fixture identity command failed')
 require({l.split()[1]:l.split()[0] for l in check.stdout.splitlines()}==hashes,'Fixture identity drift')
 verify=api.remote('python3 '+api.ROOT+'/api/verify-source.py');require(verify.returncode==0,'Artifact drift');artifact=json.loads(verify.stdout)
 token=uuid.uuid4().hex;db={'datadir':'/tmp/kaltura-pdo-mysql.'+token,'unit':'php83-exp8-api-'+token};rows=[]
 try:
  start=api.remote('bash '+api.ROOT+'/api/start-db.sh '+token,120)
  require(start.returncode==0 and json.loads(start.stdout)==db,'Owned DB startup failed')
  for runtime,variant in [('74','previous'),('74','candidate'),('83','previous'),('83','candidate')]:
   command='bash '+ROOT+'/run.sh '+runtime+' '+variant+' '+db['datadir']
   run=api.remote(command,90)
   body=None
   if run.returncode==0:
    body=json.loads(run.stdout)
    require(set(body)=={'php','driver','variant','source_sha256','contracts','rows','load_diagnostics','diagnostics'},'Unexpected report fields')
    require(len(body['diagnostics'])==2 and all(d[0]==2 for d in body['diagnostics']) and {d[1] for d in body['diagnostics']}=={'probe.php','KalturaStatement.php'},'Unexpected runtime diagnostics')
    require(body['variant']==variant and len(body['rows'])==29,'Fixture case count/variant mismatch')
    require(body['source_sha256']=={m['path']:m['after_sha256' if variant=='candidate' else 'before_sha256'] for m in metadata},'Loaded class source drift')
    require(body['contracts']=={key:('bool' if variant=='candidate' else None) for key in ['PropelPDO::setAttribute','KalturaStatement::bindValue','KalturaStatement::execute']},'Return declaration mismatch')
    require(len(body['load_diagnostics'])==(0 if runtime=='74' else (5 if variant=='candidate' else 8)),'Unexpected load diagnostic count')
   rows.append({'runtime':runtime,'variant':variant,'command':command,'exit':run.returncode,'result':body,'stdout_sha256':hashlib.sha256(run.stdout.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(run.stderr.encode()).hexdigest(),'stderr_diagnostics':api.old.diagnostics(run.stderr)})
 finally:
  stop=api.remote('sudo systemctl stop '+db['unit']+'; systemctl is-active '+db['unit'],30)
  cleanup={'unit':db['unit'],'state':stop.stdout.strip(),'stopped':stop.stdout.strip() in ['inactive','failed','unknown']}
 after=api.remote('python3 '+api.ROOT+'/api/verify-source.py');require(after.returncode==0 and json.loads(after.stdout)==artifact,'Artifact changed')
 passed=len(rows)==4 and all(r['exit']==0 for r in rows) and cleanup['stopped']
 report={'schema':1,'scope':'actual native PDO/PropelPDO/KalturaStatement boolean repair; side-effect stubs, no KalturaPDO/bootstrap acceptance','artifact':artifact,'harness':hashes,'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'imported_collector_sha256':hashlib.sha256((api.HERE/'collect.py').read_bytes()).hexdigest(),'db':db,'rows':rows,'cleanup':cleanup,'functional_checks_passed':passed,'application_acceptance':False}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'functional_checks_passed':passed,'cleanup':cleanup}))
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
