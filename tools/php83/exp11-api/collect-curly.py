#!/usr/bin/env python3
"""Actual exp11 artifact execution, linked to the prior 74/83 class corpus."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]

def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
api=module('exp11_api',HERE/'collect.py')
behavior=module('curly_behavior',HERE.parent/'curly-offsets/collect.py')

def require(ok,message):
 if not ok:raise RuntimeError(message)

def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
 pinned=api.read_pin();require(not a.output.exists(),'Refusing existing evidence')
 identities=json.loads((REPO/'doc/php83/evidence/curly-offsets/plan-sources.json').read_text())['sources']
 baseline_path=REPO/'doc/php83/evidence/curly-offsets/behavior-primary.json'
 baseline=json.loads(baseline_path.read_text())
 probe_sha=hashlib.sha256((behavior.HERE/'probe.php').read_bytes()).hexdigest()
 require(baseline['functional_checks_passed'] is True and baseline['harness'][behavior.STAGE+'/probe.php']==probe_sha,'Prior corpus/probe identity mismatch')
 expected={api.ROOT+'/api/'+name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ('run-curly.sh','verify-source.py','artifact.py')}
 expected[api.ROOT+'/tests/curly-offsets-probe.php']=probe_sha
 checked=api.remote('sha256sum '+' '.join(expected),30)
 require(checked.returncode==0 and {line.split()[1]:line.split()[0] for line in checked.stdout.splitlines()}==expected,'Fixture drift')
 def verify():
  r=api.remote('python3 '+api.ROOT+'/api/verify-source.py',60);require(r.returncode==0,'Artifact verification failed');artifact=json.loads(r.stdout);require(artifact['zip_sha256']==pinned,'Artifact pin mismatch');return artifact
 artifact=verify();records=[]
 for label in behavior.PATHS:
  command='bash '+api.ROOT+'/api/run-curly.sh '+label;r=api.remote(command,90);body=None;validation_error=None
  if r.returncode==0:
   try:body=behavior.validate(json.loads(r.stdout),label,'83','candidate',identities)
   except (RuntimeError,ValueError,KeyError,TypeError) as error:validation_error=type(error).__name__+': '+str(error)
  expected_prior=next(row['result'] for row in baseline['records'] if row['runtime']=='83' and row['variant']=='candidate' and row['case']==label)
  records.append({'case':label,'command':command,'exit':r.returncode,'validation_error':validation_error,'result':body,'matches_prior_actual_candidate83':body==expected_prior,'stdout_sha256':hashlib.sha256(r.stdout.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(r.stderr.encode()).hexdigest()})
 require(verify()==artifact,'Post-run artifact drift')
 passed=all(r['exit']==0 and r['validation_error'] is None and r['matches_prior_actual_candidate83'] for r in records)
 report={'schema':1,'scope':'actual exp11 artifact, three class files, 68 cases; no all63-file runtime acceptance','artifact':artifact,'harness':expected,'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'imported_validator_sha256':hashlib.sha256((behavior.HERE/'collect.py').read_bytes()).hexdigest(),'prior_corpus_sha256':hashlib.sha256(baseline_path.read_bytes()).hexdigest(),'records':records,'functional_checks_passed':passed,'application_acceptance':False}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'functional_checks_passed':passed,'rows':len(records)}));return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
