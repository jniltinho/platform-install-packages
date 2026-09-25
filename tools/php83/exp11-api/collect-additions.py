#!/usr/bin/env python3
"""Replay 17 reviewed candidate83 processes on the actual exp11 ZIP source.
Exact byte equivalence is bounded corpus evidence, not full application acceptance.
"""
import argparse, hashlib, importlib.util, json, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
CONTRACT=REPO/'doc/php83/evidence/exp11-runtime/addition-corpus.json'
spec=importlib.util.spec_from_file_location('exp11_addition_api',HERE/'collect.py')
api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
AUTO=['hp','core-simple','core-full','cli-version','cli-version-queue','cli-tasks-configured']
COMP=['hp-append','hp-prepend','hp-throw','hp-repeat','core-repeat','cli-append','cli-prepend','cli-throw-front','cli-throw-tail','cli-repeat']
CASES=[('ternary','matrix')]+[('autoload',x) for x in AUTO]+[('composition',x) for x in COMP]
def need(ok,message):
 if not ok:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def reference_records():
 contract=json.loads(CONTRACT.read_text()); reports={}
 need(set(contract['reports'])=={'ternary','autoload','composition'},'Corpus family inventory')
 for family,pin in contract['reports'].items():
  p=REPO/pin['path'];need(p.resolve().is_relative_to(REPO),'Unsafe corpus path')
  need(sha(p)==pin['sha256'],'Reviewed corpus drift');reports[family]=json.loads(p.read_text())
 need(reports['ternary']['summary']['positive_rows']==441,'Wrong ternary corpus')
 need(reports['autoload']['status']=='FAIL' and reports['autoload']['failed_checks']==3,'Wrong retained base failure inventory')
 need(reports['composition']['status']=='PASS' and len(reports['composition']['records'])==30,'Wrong composition corpus')
 selected={}
 for family,case in CASES:
  rows=[r for r in reports[family]['records'] if (r.get('mode')=='candidate83' if family=='ternary' else r.get('runtime')=='83' and r.get('variant')=='candidate' and r.get('case')==case)]
  need(len(rows)==1,'Missing/duplicate reference process')
  selected[(family,case)]={k:rows[0][k] for k in ['exit','stdout','stderr']}
 return contract,selected

def validate(records,expected):
 need([(r['family'],r['case']) for r in records]==CASES,'Exact17 ordered processes required')
 for r in records:
  want=expected[(r['family'],r['case'])]
  need(type(r['exit']) is int and type(want['exit']) is int,'Strict integer status required')
  need({k:r[k] for k in ['exit','stdout','stderr']}==want,'Actual artifact output differs from reviewed native83 corpus')
 return {'processes':17,'positive_processes':16,'expected_duplicate_include_fatals':1,'ternary_functional_rows':147,'all_bytes_equal_reviewed_candidate83':True,'application_acceptance':False}

def fixtures():
 files=[HERE/'run-additions.sh',HERE/'verify-source.py',HERE/'artifact.py']
 for folder in ['base-object-ternary','autoload83','autoload83-composition']:
  files.append(HERE.parent/folder/'probe.php')
  files.extend(sorted((HERE.parent/folder/'fixtures').rglob('*.php')))
 expected={}
 for p in files:
  need(not p.is_symlink(),'Symlink fixture')
  rel='api/'+p.name if p.parent==HERE else str(p.relative_to(HERE.parent))
  expected[api.ROOT+'/'+rel]=sha(p)
  if p.parent!=HERE:
   contract=json.loads(CONTRACT.read_text())
   need(contract['fixture_sha256'].get(str(p.relative_to(REPO)))==sha(p),'Reviewed fixture drift')
 return expected

def verify_fixtures(expected):
 r=api.remote('sha256sum '+' '.join(expected),60);need(r.returncode==0,'Fixture inventory command failed')
 found={}
 for line in r.stdout.splitlines():
  parts=line.split();need(len(parts)==2 and parts[1] not in found,'Malformed/duplicate fixture identity')
  found[parts[1]]=parts[0]
 need(found==expected,'Fixture drift')

def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
 need(not a.output.exists(),'Refuse existing report');pinned=api.read_pin();contract,expected=reference_records();inputs=fixtures()
 def source():
  r=api.remote('python3 '+api.ROOT+'/api/verify-source.py',90);need(r.returncode==0,'Actual artifact source verification failed')
  x=json.loads(r.stdout);need(x['zip_sha256']==pinned,'Actual artifact pin drift');return x
 verify_fixtures(inputs);before=source();records=[]
 report={'schema':1,'status':'INCOMPLETE','artifact':before,'corpus':contract,'harness':inputs,'collector_sha256':sha(__file__),'records':records,'application_acceptance':False}
 a.output.write_text(json.dumps(report,indent=2)+'\n')
 try:
  for family,case in CASES:
   command='bash '+api.ROOT+'/api/run-additions.sh '+family+' '+case
   r=api.remote(command,90)
   records.append({'family':family,'case':case,'command':command,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
   a.output.write_text(json.dumps(report,indent=2)+'\n')
  need(source()==before,'Source changed during execution');verify_fixtures(inputs)
  report['summary']=validate(records,expected);report['status']='PASS'
 except (ValueError,KeyError,TypeError,subprocess.TimeoutExpired) as e:
  report['status']='FAIL';report['error']=type(e).__name__+': '+str(e)
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'processes':len(records)}));return int(report['status']!='PASS')
if __name__=='__main__':raise SystemExit(main())
