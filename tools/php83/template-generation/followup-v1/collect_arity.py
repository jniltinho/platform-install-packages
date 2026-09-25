#!/usr/bin/env python3
"""Future authorized four-process native observations; never generated app execution."""
import argparse,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('c',HERE.parent/'collect.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
EVIDENCE=c.ROOT/'doc/php83/evidence/template-generation/followup-v1'
MANIFEST_PIN='b977687b63abffee7d746f2827dc4562a19cc499865a3368fd684bbbf77e616b'
STAGE='/home/vagrant/php-template-arity-v1'
def identity():
 c.require(c.sha((EVIDENCE/'manifest.json').read_bytes())==MANIFEST_PIN,'Local manifest drift')
 m=json.loads((EVIDENCE/'manifest.json').read_text())
 c.require(set(m['fixture_sha256'])=={'empty.php','true.php'},'Fixture inventory drift')
 for name,pin in m['fixture_sha256'].items():c.require(c.sha((EVIDENCE/name).read_bytes())==pin,'Local fixture bytes drift')
 expected={STAGE+'/'+n:pin for n,pin in m['fixture_sha256'].items()};expected[STAGE+'/arity-run.sh']=c.sha((HERE/'arity-run.sh').read_bytes())
 r=c.remote(['sha256sum '+' '.join(expected)]);c.require(r['exit']==0 and c.parse_checksums(r['stdout'])==expected,'Arity stage drift')
 return {'arity_stage':expected,'runtime_and_source_stage':c.identities(json.loads(c.MANIFEST.read_text()))}
def validate_row(row):
 c.require(type(row['exit']) is int and row['exit'] in [0,10],'Unexpected arity exit')
 body=json.loads(row['stdout'])
 c.require(type(body) is dict and set(body)=={'runtime','returned','returned_type','defined','constant','diagnostics','exception'},'Unexpected body schema')
 c.require(body['runtime'].startswith('7.4.' if row['runtime']=='74' else '8.3.'),'Wrong runtime')
 c.require((body['exception'] is None)==(row['exit']==0),'Exception/exit mismatch')
 c.require(type(body['defined']) is bool and type(body['diagnostics']) is list,'Invalid observation types')
 if body['exception'] is not None:c.require(type(body['exception']) is dict and set(body['exception'])=={'class','message'},'Invalid exception schema')
 return body

def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
 with a.output.open('x') as f:f.write('{}\n')
 report={'status':'INITIALIZING','records':[],'failures':[],'application_acceptance':False,'arity_contract_accepted':False,'generated_application_execution':False,'harness_sha256':{n:c.sha((HERE/n).read_bytes()) for n in ['prepare_arity.py','collect_arity.py','arity-run.sh','test_prepare.py','test_collect_arity.py']},'manifest_sha256':c.sha((EVIDENCE/'manifest.json').read_bytes())}
 c.persist(a.output,report)
 try:
  report['identity_before']=identity();c.persist(a.output,report)
  for rt in ['74','83']:
   for case in ['empty','true']:
    command=f'bash {STAGE}/arity-run.sh {rt} {case}';report['pending']=[rt,case];c.persist(a.output,report)
    c.require(identity()==report['identity_before'],'Input/runtime drift before case')
    row={'runtime':rt,'case':case,'command':command,**c.remote([command])};report['records'].append(row);c.persist(a.output,report)
    try:row['body']=validate_row(row)
    except (ValueError,KeyError,TypeError) as e:report['failures'].append({'runtime':rt,'case':case,'error':str(e)})
    c.require(identity()==report['identity_before'],'Input/runtime drift after case')
    report.pop('pending');c.persist(a.output,report)
  report['identity_after']=identity();c.require(report['identity_before']==report['identity_after'],'Runtime drift');report['status']='FAILED_OBSERVATION_VALIDATION' if report['failures'] else 'OBSERVED_PENDING_REVIEWED_NATIVE_CONTRACT'
 except (Exception,KeyboardInterrupt) as e:report['status']='FAILED_OR_INTERRUPTED';report['error']={'type':type(e).__name__,'message':str(e)}
 finally:c.persist(a.output,report)
 print(json.dumps({'status':report['status'],'rows':len(report['records'])}));return 2
if __name__=='__main__':sys.exit(main())
