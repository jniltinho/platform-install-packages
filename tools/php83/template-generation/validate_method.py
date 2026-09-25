#!/usr/bin/env python3
"""Explicit source-derived method contract; never contacts a VM."""
import argparse,base64,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('collector',HERE/'collect.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
VALUES={'string':['plain.php'],'absolute':['plain.php'],'list':['plain.php','nested/item.php'],'keys':{'first':'plain.php','7':'nested/item.php'},'empty-list':[],'empty-name':[''],'zero-name':['0'],'leading':['plain.php'],'outside':['outside/plain.php'],'nonrelative':['/tmp/template-audit/plain.php'],'empty-target':['/plain.php'],'finder':['nested/item.php','plain.php'],'invalid':None}
BYPASS=['nonrelative','empty-target','invalid']
PREFIX='vendor/symfony/vendor/pake/'
LOADED=[PREFIX+x+'.class.php' for x in ['pakeApp','pakeException','pakeFinder','pakeGetopt','pakeGlobToRegex','pakeNumberCompare']]
def same(a,b):return json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':'))
def diagnostic(phase,file,line,message):return {'phase':phase,'severity':8192,'message':message,'file':'/audit/source/'+PREFIX+file+'.class.php','line':line}
def expected_diagnostics(runtime,variant,case):
 ds=[]
 if variant=='original':
  for file,lines in [('pakeGetopt',[53,53,60,84,104,104,109,152,172,192]),('pakeFinder',[526,526,527,528,529,529])]:
   for line in lines:ds.append(diagnostic('load',file,line,'Array and string offset access syntax with curly braces is deprecated'))
 if runtime=='74' and variant in ['original','exp10'] and case not in BYPASS:ds.append(diagnostic('case','pakeApp',357,'Function create_function() is deprecated'))
 return ds

def validate(report):
 manifest=json.loads(c.MANIFEST.read_text());cases={'method':list(VALUES)}
 c.require(report['status']=='OBSERVED_PENDING_REVIEWED_CONTRACT' and report['phase']=='method' and report['failures']==[],'Observation incomplete')
 c.require(report['runtime_acceptance'] is False and report['application_acceptance'] is False,'Invalid observation acceptance')
 c.validate_matrix(report['records'],cases)
 c.require(same(report['identity_before'],report['identity_after']),'Identity drift')
 identity=report['identity_before'];reference=json.loads(c.REFERENCE.read_text())['identity'];c.require(same(identity['runtime'],reference),'Expected runtime mismatch')
 expectedstage={c.STAGE+'/'+name:c.sha((HERE/name).read_bytes()) for name in ['probe.php','run.sh']}
 for path,pins in manifest['files'].items():
  for variant in ['original','exp10','candidate']:expectedstage[c.STAGE+'/'+variant+'/'+path]=pins[variant]
 c.require(same(identity['stage'],expectedstage),'Expected stage mismatch')
 c.require(identity['snapshot_helper_sha256']==c.SNAPSHOT_PIN,'Snapshot helper mismatch')
 c.require(report['input_pins']=={str(c.MANIFEST):c.sha(c.MANIFEST.read_bytes()),str(c.CASES):c.sha(c.CASES.read_bytes())},'Report input pins mismatch')
 # Execution harness is the frozen r3 list; validator/tests added afterward are local proof tools.
 c.require(report['harness_sha256']=={name:c.sha((HERE/name).read_bytes()) for name in c.HARNESS},'Execution harness mismatch')
 outputs={name:{'sha256':c.sha(b'fixture'),'base64':base64.b64encode(b'fixture').decode()} for name in ['nested/item.php','plain.php']}
 for r in report['records']:
  b=c.parse_record(r,manifest);case=r['case'];runtime=r['runtime'];variant=r['variant'];exception=None;value=VALUES[case]
  if case=='invalid':exception={'class':'pakeException','message':'Wrong argument type (must be a list, a string or a pakeFinder object).','file':'/audit/source/'+PREFIX+'pakeApp.class.php','line':349}
  elif runtime=='83' and variant=='exp10' and case not in BYPASS:exception={'class':'Error','message':'Call to undefined function create_function()','file':'/audit/source/'+PREFIX+'pakeApp.class.php','line':357};value=None
  ds=expected_diagnostics(runtime,variant,case)
  c.require(type(r['exit']) is int and r['exit']==(10 if exception else 0),'Golden exit mismatch')
  for field,expected in [('value',value),('exception',exception),('diagnostics',ds),('outputs',outputs),('logs',''),('loaded',{p:manifest['files'][p][variant] for p in LOADED})]:c.require(same(b[field],expected),'Golden '+field+' mismatch in '+str((runtime,variant,case)))
  stderr=''.join('Deprecated: '+d['message']+' in '+d['file']+' on line '+str(d['line'])+'\n' for d in ds)
  c.require(r['stderr']==stderr and r['stderr_sha256']==c.sha(stderr.encode()),'Exact native stderr mismatch')
  c.require(r['lints']==[],'Method outputs are fixture data, not generated PHP')
 return {'scope':'pakeApp relative-path method only','rows':65,'positive_results':50,'expected_exceptions':15,'undefined_create_function_controls':10,'explicit_value_type_key_contract':True,'exact_diagnostics_native_stderr':True,'generation_acceptance':False,'application_acceptance':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('report',type=Path);p.add_argument('output',type=Path);a=p.parse_args();c.require(not a.output.exists(),'Refuse overwrite');r=json.loads(a.report.read_text());summary=validate(r)
 a.output.write_text(json.dumps({'input':str(a.report),'input_sha256':c.sha(a.report.read_bytes()),'validator_sha256':c.sha(Path(__file__).read_bytes()),'summary':summary},indent=2)+'\n');print(json.dumps(summary))
if __name__=='__main__':main()
