#!/usr/bin/env python3
"""Bounded three-class behavior corpus; never infer 43-class runtime coverage."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
STAGE='/home/vagrant/php-curly-behavior-r1'
SSH=['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74']
PATHS={'google-old':'vendor/google-api-php-client/src/service/Google_Utils.php',
 'google-new':'vendor/google-api-php-client-1.1.2/src/Google/Utils.php',
 'purifier':'vendor/htmlpurifier/library/HTMLPurifier/Encoder.php'}

def require(ok,message):
 if not ok:raise RuntimeError(message)

def remote(cmd):return subprocess.run(SSH+[cmd],capture_output=True,text=True,timeout=90)

def expected(label):
 if label.startswith('google'):
  rows=[('length-'+n,v) for n,v in [('empty',0),('ascii',3),('nul',3),('binary',2),('two-byte',3),('four-byte',7),('mixed',5)]]
  for name,encoded,decoded in [('empty','',''),('ascii','Zm9v','666f6f'),('unicode','w6k','c3a9'),('binary','AP8','00ff')]:rows.extend([('base64-encode-'+name,encoded),('base64-decode-'+name,decoded)])
  rows += [('normalize-map',{'hello':2,'world':None}),('normalize-nonarray',[])]
 else:
  rows=[('clean-'+name,value) for name,value in [('empty',''),('ascii','616263'),('unicode','c3a9f09f9880'),('nul-ascii','41'),('invalid-lead','42'),('stray-continuation','41'),('overlong',''),('truncated',''),('surrogate',''),('unicode-control',''),('allowed-control','090a0d'),('nul-unicode','c3a9f09f9880')]]
  rows += [('unichr-'+str(code),value) for code,value in [(-1,''),(0,'00'),(65,'41'),(127,'7f'),(128,'c280'),(233,'c3a9'),(2047,'dfbf'),(2048,'e0a080'),(55296,''),(128512,'f09f9880'),(1114111,'f48fbfbf'),(1114112,'')]]
  rows += [('ascii-entities','A&#233;&#128512;')]
 rows += [('native-array-types',['zero',False,None,False]),('native-string-bytes',['41','00','ff']),('native-string-overread','')]
 return rows

def validate(body,label,runtime,variant,identities):
 require(set(body)=={'case','php','source_path','source_sha256','load_diagnostics','rows'},'Unexpected result fields')
 require(body['case']==label and body['source_path']==PATHS[label] and body['source_sha256']==identities[label][variant+'_sha256'],'Source identity mismatch')
 require(body['php'].startswith('7.4.' if runtime=='74' else '8.3.'),'Runtime mismatch')
 require(len(body['rows'])==len(expected(label)),'Case count mismatch')
 for row,(name,value) in zip(body['rows'],expected(label)):
  require(set(row)=={'case','value','diagnostics'} and row['case']==name and json.dumps(row['value'])==json.dumps(value),'Unexpected case value')
  warning_count={'length-two-byte':1,'length-four-byte':3,'length-mixed':1,'native-string-overread':1}.get(name,0)
  require(len(row['diagnostics'])==warning_count,'Unexpected warning count')
  for diagnostic in row['diagnostics']:
   validate_diagnostic(diagnostic)
   require(diagnostic['phase']==name and diagnostic['severity']==(8 if runtime=='74' else 2) and diagnostic['category']=='uninitialized-string-offset','Unexpected warning')
   line = next(i for i,text in enumerate((HERE/'probe.php').read_text().splitlines(),1) if "recordCase('native-string-overread'" in text) if name=='native-string-overread' else (58 if label=='google-old' else 65)
   require(diagnostic['file']==('probe.php' if name=='native-string-overread' else Path(PATHS[label]).name) and diagnostic['line']==line,'Diagnostic source mismatch')
 require(len(body['load_diagnostics'])==(1 if runtime=='74' and variant=='original' else 0),'Unexpected load diagnostics')
 for diagnostic in body['load_diagnostics']:
  validate_diagnostic(diagnostic)
  require(diagnostic['phase']=='load' and diagnostic['severity']==8192 and diagnostic['category']=='curly-offset-deprecated','Unexpected load diagnostic')
  require(diagnostic['file']==Path(PATHS[label]).name and diagnostic['line']=={'google-old':58,'google-new':65,'purifier':157}[label],'Load diagnostic source mismatch')
 return body

def validate_diagnostic(d):
 require(set(d)=={'phase','severity','file','line','category','message_sha256'},'Unexpected diagnostic fields')
 require(d['file'] in ('Google_Utils.php','Utils.php','Encoder.php','probe.php') and type(d['line'])==int and d['line']>0 and re.fullmatch('[0-9a-f]{64}',d['message_sha256']),'Invalid diagnostic identity')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('output',type=Path);a=parser.parse_args()
 require(not a.output.exists(),'Refusing existing evidence')
 identities=json.loads((REPO/'doc/php83/evidence/curly-offsets/plan-sources.json').read_text())['sources']
 require(set(identities)==set(PATHS),'Class inventory mismatch')
 expected_hashes={STAGE+'/'+name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ('probe.php','run.sh')}
 for label,path in PATHS.items():
  for variant in ('original','candidate'):expected_hashes[STAGE+'/'+variant+'/'+path]=identities[label][variant+'_sha256']
 def identity():
  run=remote('sha256sum '+' '.join(shlex.quote(p) for p in expected_hashes));require(run.returncode==0,'Remote hash command failed')
  found={line.split()[1]:line.split()[0] for line in run.stdout.splitlines()};require(found==expected_hashes,'Source/harness drift')
  code='import json,hashlib,subprocess,re;from pathlib import Path;p="/usr/bin/php7.4";q="/home/vagrant/php-mysql-probe/runtime83/php8.3";paths=[p,q,"/usr/lib/php/20190902/json.so"];print(json.dumps({"hashes":{v:hashlib.sha256(Path(v).read_bytes()).hexdigest() for v in paths},"linked_library_hashes":{v:{lib:hashlib.sha256(Path(lib).read_bytes()).hexdigest() for lib in sorted(set(re.findall(r"/[^\\s()]+",subprocess.check_output(["ldd",v],text=True))))} for v in [p,q]},"runtimes":{v:{"version":subprocess.check_output([v,"-n","-v"],text=True),"modules":subprocess.check_output([v,"-n","-m"],text=True),"ini":subprocess.check_output([v,"-n","--ini"],text=True)} for v in [p,q]},"php74_extra_module":"json.so explicitly loaded by runner; listed hash; -n module listing is before that explicit addition"}))'
  run=remote('python3 -c '+shlex.quote(code));require(run.returncode==0,'Runtime identity failed');return json.loads(run.stdout)
 runtime_identity=identity();records=[]
 for runtime,variant in [('74','original'),('74','candidate'),('83','candidate')]:
  for label in PATHS:
   command='bash '+STAGE+'/run.sh '+runtime+' '+variant+' '+label
   run=remote(command);body=None;validation_error=None
   if run.returncode==0:
    try: body=validate(json.loads(run.stdout),label,runtime,variant,identities)
    except (RuntimeError,ValueError,KeyError,TypeError) as error: validation_error=type(error).__name__+': '+str(error)
   failure_cases=[n for n,_ in expected(label) if ('Case result mismatch: '+n) in run.stderr or ('Case diagnostic count mismatch: '+n) in run.stderr]
   records.append({'runtime':runtime,'variant':variant,'case':label,'command':command,'exit':run.returncode,'validation_error':validation_error,'fixture_failure_cases':failure_cases,'result':body,'stdout_sha256':hashlib.sha256(run.stdout.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(run.stderr.encode()).hexdigest()})
 require(identity()==runtime_identity,'Post-run runtime drift')
 passed=all(r['exit']==0 and r['validation_error'] is None for r in records)
 # Runtime rows already assert exact values and version-specific diagnostics.
 comparisons=[]
 if passed:
  for label in PATHS:
   rows=[next(r['result']['rows'] for r in records if r['case']==label and r['runtime']==runtime and r['variant']==variant) for runtime,variant in [('74','original'),('74','candidate'),('83','candidate')]]
   same74=rows[0]==rows[1]
   values83=[(r['case'],r['value']) for r in rows[0]]==[(r['case'],r['value']) for r in rows[2]]
   comparisons.append({'case':label,'php74_case_values_and_diagnostics_identical':same74,'php83_case_values_identical':values83,'php83_diagnostic_severity_change_explicit':True})
   passed=passed and same74 and values83
 report={'schema':1,'scope':'3 actual classes / 43 lexical source targets; no whole-app acceptance','harness':expected_hashes,'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_identities':identities,'runtime_identity':runtime_identity,'records':records,'comparisons':comparisons,'functional_checks_passed':passed,'full_diagnostic_parity':False,'application_acceptance':False}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'functional_checks_passed':passed,'comparisons':comparisons}));return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
