#!/usr/bin/env python3
"""Bounded exact delta contract; prior native diagnostic observations are explicit."""
import argparse,base64,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('c',HERE/'collect.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
BASELINE=c.ROOT/'doc/php83/evidence/template-generation/generation-primary-r4.json'
BASELINE_PIN='43074293abfe7a9bda134a6305a72adf66e4139b6888d13e220d93a674696a86'

def expected_body(prior,variant,manifest):
 import re
 b=json.loads(prior['stdout']);case=prior['case'];changed=False
 b['loaded']={p:manifest['files'][p][variant] for p in b['loaded']}
 if variant=='debug' and case.split('-')[-1] in ['false','zero']:
  c.require(len(b['outputs'])==1,'Unexpected false-case output count')
  for item in b['outputs'].values():
   data=base64.b64decode(item['base64'],validate=True)
   pattern=rb"(define\('SF_DEBUG',[ \t]*)(\);)"
   data,n=re.subn(pattern,lambda m:m[1]+b'0'+m[2],data)
   c.require(n==1,'Expected exactly one literal empty DEBUG call')
   item.update(base64=base64.b64encode(data).decode(),sha256=c.sha(data));changed=True
 return b,changed

def validate(report):
 c.require(c.sha(BASELINE.read_bytes())==BASELINE_PIN,'Prior observation pin drift');prior=json.loads(BASELINE.read_text())
 c.require(c.sha(c.MANIFEST.read_bytes())=='2c9d61197bbe27c448792d256c93a6645018e022d38eec089c938c9660000f0b','Manifest pin drift');m=json.loads(c.MANIFEST.read_text());cases={'generate':json.loads(c.CASES.read_text())['modes']['generate']}
 c.require(report['phase']=='generate' and report['status']=='OBSERVED_PENDING_REVIEWED_CONTRACT' and report['failures']==[],'Incomplete observations')
 c.require('pending' not in report and 'terminal_error' not in report,'Interrupted run')
 for k in ['runtime_acceptance','generated_syntax_acceptance','application_acceptance']:c.require(report[k] is False,'Unapproved flag')
 c.require(c.sha(c.CASES.read_bytes())=='eae8ad799e7d66f2cbf0e583170ded28c35c9b1699ad46cd91e146771f536e67','Pinned case matrix drift');c.require(c.validate_matrix(report['records'],cases)==72,'Exact72 required')
 c.require(report['identity_before']==report['identity_after'],'Identity drift')
 i=report['identity_before'];expected={c.STAGE+'/'+n:c.sha((HERE/n).read_bytes()) for n in ['probe.php','run.sh']}
 for path,pins in m['files'].items():
  for v in ['original','exp10','prerequisite','debug']:expected[c.STAGE+'/'+v+'/'+path]=pins[v]
 c.require(i['stage']==expected,'Wrong source stage')
 for k in ['runtime','snapshot_helper_sha256','snapshot_program_sha256']:c.require(i[k]==prior['identity_before'][k],'Runtime snapshot mismatch')
 c.require(report['harness_sha256']=={n:c.sha((HERE/n).read_bytes()) for n in c.HARNESS},'Harness drift')
 c.require(report['input_pins']=={str(c.MANIFEST):c.sha(c.MANIFEST.read_bytes()),str(c.CASES):c.sha(c.CASES.read_bytes())},'Input drift')
 gold={(r['runtime'],r['case']):r for r in prior['records'] if r['variant']=='candidate'}
 changes=0
 for row in report['records']:
  old=gold[row['runtime'],row['case']];body=c.parse_record(row,m);want,changed=expected_body(old,row['variant'],m);changes+=int(changed)
  c.require(json.dumps(body,sort_keys=True)==json.dumps(want,sort_keys=True),'Exact generated/body contract mismatch')
  for k in ['exit','stderr','stderr_sha256','lints']:c.require(json.dumps(row[k],sort_keys=True)==json.dumps(old[k],sort_keys=True),'Native/lint drift: '+k)
  c.require(row['command']==f"bash {c.STAGE}/run.sh {row['runtime']} {row['variant']} generate {row['case']}",'Wrong command')
 c.require(changes==12,'Expected exactly12 changed output rows')
 return {'rows':72,'changed_debug_outputs':12,'unchanged_output_rows':60,'application_acceptance':False,'native_contract_source':str(BASELINE),'native_contract_independent_oracle':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args();result=validate(json.loads(a.input.read_text()))
 with a.output.open('x') as f:json.dump({'summary':result,'input_sha256':c.sha(a.input.read_bytes()),'validator_sha256':c.sha(Path(__file__).read_bytes())},f,indent=2);f.write('\n')
 print(json.dumps(result))
