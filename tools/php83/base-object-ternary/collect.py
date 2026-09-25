#!/usr/bin/env python3
"""Read-only frozen-stage execution; refuses existing output. No staging or SQL."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
STAGE='/home/vagrant/php-base-object-ternary-r2'
HARNESS_FILES=('build.py','collect.py','probe.php','run.sh','test_ternary.py')
MODES=['original74','candidate74','candidate83','original83']
SSH=['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74']
def need(ok,msg):
 if not ok:raise ValueError(msg)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def identity():
 manifest=json.loads((ROOT/'patches/php83/held/base-object-ternary/manifest.json').read_text())
 expected={STAGE+'/'+x:digest(HERE/x) for x in ['run.sh','probe.php']}
 for row in manifest['files']:
  for variant,key in [('original','before_sha256'),('candidate','after_sha256')]:expected[STAGE+'/'+variant+'/'+row['path']]=row[key]
 r=subprocess.run(SSH+['sha256sum '+' '.join(expected)],capture_output=True,text=True,timeout=60)
 need(r.returncode==0,'Identity command failed');need({x.split()[1]:x.split()[0] for x in r.stdout.splitlines()}==expected,'Remote input drift')
 return expected

def native_deprecations(ds):
 return ''.join('Deprecated: '+d['message']+' in /audit/source/alpha/apps/kaltura/lib/'+d['file']+' on line '+str(d['line'])+'\n' for d in ds)

def validate(records):
 need(type(records) is list and [r['mode'] for r in records]==MODES,'Exact four ordered unique runtime controls required')
 for row in records:need(type(row['exit']) is int and row['exit']==(255 if row['mode']=='original83' else 0),'Unexpected process exit')
 positive={r['mode']:json.loads(r['stdout']) for r in records if r['exit']==0}
 a=positive['original74'];need(a['version'].startswith('7.4.'),'Original runtime')
 need(len(a['rows'])==147 and len({r['case'] for r in a['rows']})==147,'Case inventory')
 for row in records:
  need(row['stderr_sha256']==hashlib.sha256(row['stderr'].encode()).hexdigest(),'Stderr hash mismatch')
 for mode,b in positive.items():
  need(b['version'].startswith('8.3.' if mode=='candidate83' else '7.4.'),'Runtime mismatch')
  need(b['rows']==a['rows'],'Functional/side effect drift')
  ds=b['diagnostics']
  manifest=json.loads((ROOT/'patches/php83/held/base-object-ternary/manifest.json').read_text())
  need(b['hashes']=={r['path']:r['before_sha256' if mode=='original74' else 'after_sha256'] for r in manifest['files']},'Executed source hash drift')
  need(len(ds)==(1 if mode=='original74' else 5 if mode=='candidate83' else 0),'Unexpected diagnostics')
  if mode=='candidate83':
   expected=[]
   for method,line,typ in [('current',473,'mixed'),('next',487,'void'),('key',480,'mixed'),('valid',494,'bool'),('rewind',465,'void')]:
    expected.append({'phase':'load','severity':8192,'message':f'Return type of myBaseObject::{method}() should either be compatible with Iterator::{method}(): {typ}, or the #[\\ReturnTypeWillChange] attribute should be used to temporarily suppress the notice','file':'myBaseObject.class.php','line':line})
   need(ds==expected,'Retained Iterator diagnostic drift')
  if mode=='original74':need(ds[0]=={'phase':'load','severity':8192,'message':'Unparenthesized `a ? b : c ? d : e` is deprecated. Use either `(a ? b : c) ? d : e` or `a ? b : (c ? d : e)`','file':'baseObjectUtils.class.php','line':474},'Load warning drift')
  row=next(r for r in records if r['mode']==mode)
  need(row['stderr']==native_deprecations(ds),'Native stderr does not match exact JSON diagnostics')
  for i in range(10):
   for j in range(13):
    # Fixed finite truth tables, not reimplementing the nested ternary expression.
    prefix=['','','','','','<0 ','<node ','<1 ','<1 ','<-1 '][i]
    suffix='/>\n' if i>=5 and j in [6,7,8,9,11,12] else '>\n'
    need(b['rows'][i*13+j]=={'case':f'matrix-{i}-{j}','value':prefix+suffix,'trace':[]},'Golden truth table mismatch')
 fatal=records[3]
 expected_fatal=native_deprecations(positive['candidate83']['diagnostics'])+'Fatal error: Unparenthesized `a ? b : c ? d : e` is not supported. Use either `(a ? b : c) ? d : e` or `a ? b : (c ? d : e)` in /audit/source/alpha/apps/kaltura/lib/baseObjectUtils.class.php on line 474\n'
 need(fatal['stderr']==expected_fatal and fatal['stdout']=='','Exact original83 fatal channel contract mismatch')
 return {'functional_cases_per_positive_mode':147,'positive_rows':441,'original83_expected_fatal':True,'load_deprecation_removed_explicitly':True,'retained_php83_dependency_deprecations':5,'application_acceptance':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args();need(not a.output.exists(),'Refusing overwrite')
 before=identity();records=[]
 for runtime,variant in [('74','original'),('74','candidate'),('83','candidate'),('83','original')]:
  command=SSH+[f'bash {STAGE}/run.sh {runtime} {variant}'];r=subprocess.run(command,capture_output=True,text=True,timeout=90)
  records.append({'mode':variant+runtime,'command':command,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'stderr_sha256':hashlib.sha256(r.stderr.encode()).hexdigest()})
 need(identity()==before,'Input drift after run')
 try:summary=validate(records);error=None
 except (ValueError,KeyError,TypeError) as e:summary=None;error=str(e)
 report={'schema':1,'harness_sha256':{name:digest(HERE/name) for name in HARNESS_FILES},'input_sha256':before,'records':records,'summary':summary,'validation_error':error}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(summary or {'error':error}));return 0 if error is None else 1
if __name__=='__main__':sys.exit(main())
