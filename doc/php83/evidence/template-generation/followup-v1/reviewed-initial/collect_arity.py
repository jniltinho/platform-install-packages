#!/usr/bin/env python3
"""Future authorized four-process native observations; never generated app execution."""
import argparse,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('c',HERE.parent/'collect.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
EVIDENCE=c.ROOT/'doc/php83/evidence/template-generation/followup-v1'
STAGE='/home/vagrant/php-template-arity-v1'
def identity():
 m=json.loads((EVIDENCE/'manifest.json').read_text());expected={STAGE+'/'+n:pin for n,pin in m['fixture_sha256'].items()};expected[STAGE+'/arity-run.sh']=c.sha((HERE/'arity-run.sh').read_bytes())
 r=c.remote(['sha256sum '+' '.join(expected)]);c.require(r['exit']==0 and c.parse_checksums(r['stdout'])==expected,'Arity stage drift')
 return {'arity_stage':expected,'runtime_and_source_stage':c.identities(json.loads(c.MANIFEST.read_text()))}
def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
 with a.output.open('x') as f:f.write('{}\n')
 report={'status':'INITIALIZING','records':[],'application_acceptance':False,'arity_contract_accepted':False,'generated_application_execution':False,'harness_sha256':{n:c.sha((HERE/n).read_bytes()) for n in ['prepare_arity.py','collect_arity.py','arity-run.sh','test_prepare.py']},'manifest_sha256':c.sha((EVIDENCE/'manifest.json').read_bytes())}
 c.persist(a.output,report)
 try:
  report['identity_before']=identity();c.persist(a.output,report)
  for rt in ['74','83']:
   for case in ['empty','true']:
    command=f'bash {STAGE}/arity-run.sh {rt} {case}';report['pending']=[rt,case];c.persist(a.output,report)
    row={'runtime':rt,'case':case,'command':command,**c.remote([command])};report['records'].append(row);c.persist(a.output,report)
    c.require(type(row['exit']) is int and row['exit'] in [0,10],'Unexpected arity exit')
    row['body']=json.loads(row['stdout']);c.require(row['body']['runtime'].startswith('7.4.' if rt=='74' else '8.3.'),'Wrong runtime')
    report.pop('pending');c.persist(a.output,report)
  report['identity_after']=identity();c.require(report['identity_before']==report['identity_after'],'Runtime drift');report['status']='OBSERVED_PENDING_REVIEWED_NATIVE_CONTRACT'
 except (Exception,KeyboardInterrupt) as e:report['status']='FAILED_OR_INTERRUPTED';report['error']={'type':type(e).__name__,'message':str(e)}
 finally:c.persist(a.output,report)
 print(json.dumps({'status':report['status'],'rows':len(report['records'])}));return 2
if __name__=='__main__':sys.exit(main())
