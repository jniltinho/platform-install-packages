#!/usr/bin/env python3
"""Bounded negative-task/native-arity proof, never application acceptance."""
import argparse,ast,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('a',HERE/'collect_arity.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);c=a.c
E=a.EVIDENCE;CONTRACT=E/'native-contract.json';CONTRACT_PIN='e7aadadcaf124f60ed04570f32764b7656a8e4b14b5ad4bacc1d87b3285ed34a'
CASES=['missing-module','missing-admin-model','unknown-batch','existing-module','missing-skeleton','readonly-output']
def same(x,y):return json.dumps(x,sort_keys=True,separators=(',',':'))==json.dumps(y,sort_keys=True,separators=(',',':'))
def common_identity(identity):
 m=json.loads(c.MANIFEST.read_text());expected={c.STAGE+'/'+n:c.sha((HERE.parent/n).read_bytes()) for n in ['probe.php','run.sh']}
 for path,pins in m['files'].items():
  for variant in ['original','exp10','candidate']:expected[c.STAGE+'/'+variant+'/'+path]=pins[variant]
 c.require(same(identity['stage'],expected),'Source stage drift')
 c.require(c.sha(c.REFERENCE.read_bytes())==c.REFERENCE_PIN and same(identity['runtime'],json.loads(c.REFERENCE.read_text())['identity']),'Runtime reference drift')
 program=next(ast.literal_eval(n.value) for n in ast.parse(c.SNAPSHOT.read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REMOTE' for t in n.targets))
 c.require(identity['snapshot_helper_sha256']==c.SNAPSHOT_PIN==c.sha(c.SNAPSHOT.read_bytes()) and identity['snapshot_program_sha256']==c.sha(program.encode()),'Snapshot source drift')
def validate_negative(report):
 c.require(c.sha(CONTRACT.read_bytes())==CONTRACT_PIN,'Contract drift');contract=json.loads(CONTRACT.read_text());m=json.loads(c.MANIFEST.read_text())
 c.require(report['phase']=='negative' and report['status']=='OBSERVED_PENDING_REVIEWED_CONTRACT' and report['failures']==[],'Incomplete negative observations')
 c.require('pending' not in report and 'terminal_error' not in report,'Pending or terminal error')
 for k in ['application_acceptance','runtime_acceptance','generated_syntax_acceptance']:c.require(report[k] is False,'Invalid acceptance flag')
 c.validate_matrix(report['records'],{'negative':CASES});c.require(same(report['identity_before'],report['identity_after']),'Runtime/source drift');common_identity(report['identity_before'])
 c.require(report['harness_sha256']=={n:c.sha((HERE.parent/n).read_bytes()) for n in c.HARNESS},'Execution harness drift')
 c.require(report['input_pins']=={str(c.MANIFEST):c.sha(c.MANIFEST.read_bytes()),str(c.CASES):c.sha(c.CASES.read_bytes())},'Input pins drift')
 exceptions={'missing-module':('sfPakeGenerator.php',115,'You must provide your module name.'),'missing-admin-model':('sfPakePropelAdminGenerator.php',23,'You must provide your model class name.'),'unknown-batch':('sfPakeGenerator.php',181,'The specified batch "unknown" does not exist.'),'existing-module':('sfPakeGenerator.php',125,'The directory "/tmp/template-audit/apps/auditapp/modules/AuditModule" already exists.'),'missing-skeleton':('sfPakeGenerator.php',188,'The skeleton you specified could not be found.')}
 counts={'exceptions':0,'legacy_zero_exit_without_output':0,'empty_files_before_missing_skeleton_exception':0,'retained_removed_function_controls':0,'lint_success_empty_files':0}
 for r in report['records']:
  b=c.parse_record(r,m);rt=r['runtime'];v=r['variant'];case=r['case'];early=(rt,v)==('83','exp10') and case in ['missing-skeleton','readonly-output'];error=None
  if early:error={'class':'Error','message':'Call to undefined function create_function()','file':'/audit/source/vendor/symfony/vendor/pake/pakeApp.class.php','line':357};counts['retained_removed_function_controls']+=1
  elif case in exceptions:
   file,line,message=exceptions[case];error={'class':'Exception','message':message,'file':'/audit/source/vendor/symfony-data/tasks/'+file,'line':line}
  outputs={'batch/audit_job.php':{'sha256':c.sha(b''),'base64':''}} if case=='missing-skeleton' and not early else []
  native=contract['negative_native'][rt+'|'+v+'|'+case]
  for field,value in [('value',None),('exception',error),('outputs',outputs),('diagnostics',native['diagnostics']),('logs',native['logs']),('loaded',{p:pins[v] for p,pins in m['files'].items() if '/skeleton/' not in p})]:c.require(same(b[field],value),'Negative '+field+' mismatch')
  c.require(type(r['exit']) is int and r['exit']==(10 if error else 0),'Negative expected exit mismatch')
  c.require(r['command']==f'bash {c.STAGE}/run.sh {rt} {v} negative {case}','Wrong command')
  stderr=''.join({2:'Warning',8192:'Deprecated'}[d['severity']]+': '+d['message']+' in '+d['file']+' on line '+str(d['line'])+'\n' for d in native['diagnostics'])
  c.require(r['stderr']==stderr and r['stderr_sha256']==c.sha(stderr.encode()),'Negative native stderr drift')
  lints=[]
  if outputs:
   counts['empty_files_before_missing_skeleton_exception']+=1
   lints=[{'path':'batch/audit_job.php','runtime':rt,'exit':0,'stdout':'No syntax errors detected in Standard input code\n','stderr':''} for rt in ['74','83']];counts['lint_success_empty_files']+=2
  c.require(same(r['lints'],lints),'Negative lint matrix mismatch')
  counts['exceptions' if error else 'legacy_zero_exit_without_output']+=1
 c.require(counts=={'exceptions':26,'legacy_zero_exit_without_output':4,'empty_files_before_missing_skeleton_exception':4,'retained_removed_function_controls':2,'lint_success_empty_files':8},'Negative outcome counts')
 return {'rows':30,**counts,'generation_success':False,'application_acceptance':False}
def validate_arity(report):
 c.require(report['status']=='OBSERVED_PENDING_REVIEWED_NATIVE_CONTRACT' and report['failures']==[] and 'pending' not in report and 'error' not in report,'Incomplete arity observations')
 for k in ['application_acceptance','arity_contract_accepted','generated_application_execution']:c.require(report[k] is False,'Unapproved arity flag')
 c.require([(r['runtime'],r['case']) for r in report['records']]==[('74','empty'),('74','true'),('83','empty'),('83','true')],'Arity exact matrix')
 c.require(same(report['identity_before'],report['identity_after']),'Arity identity drift');identity=report['identity_before'];common_identity(identity['runtime_and_source_stage'])
 c.require(report['manifest_sha256']==a.MANIFEST_PIN==c.sha((E/'manifest.json').read_bytes()),'Arity manifest drift');manifest=json.loads((E/'manifest.json').read_text())
 expected={a.STAGE+'/'+name:pin for name,pin in manifest['fixture_sha256'].items()};expected[a.STAGE+'/arity-run.sh']=c.sha((HERE/'arity-run.sh').read_bytes());c.require(identity['arity_stage']==expected,'Arity stage drift')
 for name,pin in manifest['fixture_sha256'].items():c.require(c.sha((E/name).read_bytes())==pin,'Local fixture drift')
 c.require(report['harness_sha256']=={n:c.sha((HERE/n).read_bytes()) for n in ['prepare_arity.py','collect_arity.py','arity-run.sh','test_prepare.py','test_collect_arity.py']},'Arity execution harness drift')
 for r in report['records']:
  body=a.validate_row(r);rt=r['runtime'];case=r['case'];empty=case=='empty';diagnostics=[];error=None
  if empty and rt=='74':diagnostics=[{'severity':2,'message':'define() expects at least 2 parameters, 1 given','line':9}]
  if empty and rt=='83':error={'class':'ArgumentCountError','message':'define() expects at least 2 arguments, 1 given'}
  expectedbody={'runtime':body['runtime'],'returned':None if empty else True,'returned_type':'NULL' if empty else 'boolean','defined':not empty,'constant':None if empty else 1,'diagnostics':diagnostics,'exception':error}
  c.require(same(body,expectedbody) and same(r['body'],body),'Exact native arity body')
  stderr='Warning: define() expects at least 2 parameters, 1 given in /audit/case.php on line 9\n' if empty and rt=='74' else ''
  c.require(r['stderr']==stderr and type(r['exit']) is int and r['exit']==(10 if error else 0),'Exact arity exit/stderr')
  c.require(r['command']==f'bash {a.STAGE}/arity-run.sh {rt} {case}','Arity command mismatch')
 return {'rows':4,'empty74_warning_null_undefined':True,'empty83_argument_count_error_undefined':True,'true_controls':2,'generated_application_execution':False,'application_acceptance':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('kind',choices=['negative','arity']);p.add_argument('input',type=Path);p.add_argument('output',type=Path);args=p.parse_args();c.require(not args.output.exists(),'Refuse overwrite');result=(validate_negative if args.kind=='negative' else validate_arity)(json.loads(args.input.read_text()));args.output.write_text(json.dumps({'input_sha256':c.sha(args.input.read_bytes()),'validator_sha256':c.sha(Path(__file__).read_bytes()),'summary':result},indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
