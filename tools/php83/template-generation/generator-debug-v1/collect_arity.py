#!/usr/bin/env python3
"""Four isolated numeric literal observations, never generated application execution."""
import argparse,importlib.util,json,signal,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('p',HERE/'prepare_arity.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p);c=p.v.c
STAGE='/home/vagrant/php-generator-debug-arity-v1'
HARNESS=['prepare_arity.py','collect_arity.py','arity-run.sh','test_arity.py']
def contract(row):
 c.require(type(row['exit']) is int and row['exit']==0,'Numeric literal exit')
 b=json.loads(row['stdout']);runtime=b.get('runtime');c.require(type(runtime) is str and runtime.startswith('7.4.' if row['runtime']=='74' else '8.3.'),'Runtime family')
 want={'runtime':runtime,'returned':True,'returned_type':'boolean','defined':True,'constant':0 if row['case']=='zero' else 1,'diagnostics':[],'exception':None}
 c.require(json.dumps(b,sort_keys=True)==json.dumps(want,sort_keys=True),'Numeric literal typed contract')
 c.require(row['stderr']=='','Unexpected native stderr');return b
def identity(fixtures,files,manifest):
 c.require(json.loads((fixtures/'manifest.json').read_text())==manifest,'Local fixture manifest drift')
 expected={STAGE+'/'+name:c.sha(data) for name,data in files.items()};expected[STAGE+'/arity-run.sh']=c.sha((HERE/'arity-run.sh').read_bytes())
 for name,data in files.items():c.require((fixtures/name).read_bytes()==data,'Local literal fixture drift')
 r=c.remote(['sha256sum '+' '.join(expected)]);c.require(type(r['exit']) is int and r['exit']==0 and c.parse_checksums(r['stdout'])==expected,'Arity remote source drift')
 return {'literal_stage':expected,'generation_source_and_runtime':c.identities(json.loads(c.MANIFEST.read_text()))}
def collect(report,pin,fixtures,output):
 files,manifest=p.verified(report,pin)
 with output.open('x') as f:f.write('{}\n')
 result={'status':'INITIALIZING','records':[],'failures':[],'source_report_sha256':pin,'fixture_manifest':manifest,'harness_sha256':{n:c.sha((HERE/n).read_bytes()) for n in HARNESS},'generated_application_execution':False,'application_acceptance':False}
 def interrupted(signum,frame):raise InterruptedError('signal '+str(signum))
 signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted);c.persist(output,result)
 try:
  result['identity_before']=identity(fixtures,files,manifest);c.persist(output,result)
  for rt in ['74','83']:
   for case in ['zero','one']:
    result['pending']=[rt,case];c.persist(output,result)
    c.require(identity(fixtures,files,manifest)==result['identity_before'],'Pre-case drift')
    cmd=f'bash {STAGE}/arity-run.sh {rt} {case}';row={'runtime':rt,'case':case,'command':cmd,**c.remote([cmd])};result['records'].append(row);c.persist(output,result)
    try:row['body']=contract(row)
    except (ValueError,KeyError,TypeError) as e:result['failures'].append({'runtime':rt,'case':case,'error':str(e)})
    c.require(identity(fixtures,files,manifest)==result['identity_before'],'Post-case drift');result.pop('pending');c.persist(output,result)
  result['identity_after']=identity(fixtures,files,manifest);c.require(result['identity_after']==result['identity_before'],'Post-run drift')
  c.require([(r['runtime'],r['case']) for r in result['records']]==[(r,k) for r in ['74','83'] for k in ['zero','one']],'Exact four rows')
  result['status']='FAILED_LITERAL_CONTRACT' if result['failures'] else 'OBSERVED_LITERAL_CONTRACT_SATISFIED'
 except (Exception,KeyboardInterrupt) as e:result['status']='FAILED_OR_INTERRUPTED';result['error']={'type':type(e).__name__,'message':str(e)}
 finally:c.persist(output,result)
 return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('report',type=Path);a.add_argument('sha256');a.add_argument('fixtures',type=Path);a.add_argument('output',type=Path);args=a.parse_args();r=collect(args.report,args.sha256,args.fixtures,args.output);print(json.dumps({'status':r['status'],'rows':len(r['records'])}));sys.exit(0 if r['status']=='OBSERVED_LITERAL_CONTRACT_SATISFIED' else 2)
