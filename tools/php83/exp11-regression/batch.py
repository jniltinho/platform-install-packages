#!/usr/bin/env python3
"""Run artifact-based focused regression, retaining errors instead of forcing OK."""
import datetime,hashlib,json,re,socket,subprocess,time,zipfile
from pathlib import Path
if not __debug__:raise RuntimeError('Optimized Python not supported')
root=Path('/home/vagrant/php-exp11-regression')
if socket.gethostname() not in ('kaltura-php74-baseline','kaltura-php83-lab'):raise SystemExit(64)
archive=root/'exp11.zip'
expected=(root/'api/artifact-sha256.txt').read_text().strip()
assert re.fullmatch('[0-9a-f]{64}',expected)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
with zipfile.ZipFile(archive) as z:
 names=[]
 for i in z.infolist():
  if not i.is_dir():
   p=root/'source'/i.filename
   assert p.read_bytes()==z.read(i)
   names.append(i.filename)
 assert sorted(str(p.relative_to(root/'source')) for p in (root/'source').rglob('*') if p.is_file())==sorted(names)
prior=subprocess.run(['python3','/home/vagrant/php-exp10-regression/api/verify-source.py'],capture_output=True,text=True,timeout=60)
if prior.returncode:raise RuntimeError('Previous artifact drift')
previous_artifact=json.loads(prior.stdout)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'schema':1,'host':socket.gethostname(),'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'zip_sha256':sha(archive),'verified_extracted_files':len(names),'harness':{str(p.relative_to(root)):sha(p) for folder in ['tests','exp11-regression'] for p in sorted((root/folder).rglob('*')) if p.is_file()},'previous_artifact':previous_artifact,'unsupported_cases':(['exp10/php74','exp11/php74'] if socket.gethostname()=='kaltura-php74-baseline' else []),'rows':[],'application_acceptance':False}
for source in (['original'] if socket.gethostname()=='kaltura-php74-baseline' else ['original','exp10','exp11']):
 for ini in ['standard','minimal']:
  for case in ['environment','legacy-json','zend-json','doc-comment','doc-comment-export','doc-comment-consumer']:
   cmd=['bash',str(root/'exp11-regression/run-one.sh'),source,case,ini]
   start=time.monotonic_ns(); run=subprocess.run(cmd,capture_output=True,text=True,timeout=70)
   report['rows'].append({'source':source,'ini':ini,'case':case,'exit':run.returncode,'duration_ns':time.monotonic_ns()-start,'stdout':run.stdout,'stderr':run.stderr})
for verifier in [root/'api/verify-source.py',Path('/home/vagrant/php-exp10-regression/api/verify-source.py')]:
 checked=subprocess.run(['python3',str(verifier)],capture_output=True,text=True,timeout=60)
 if checked.returncode:raise RuntimeError('Post-run artifact verification failed')
 if json.loads(checked.stdout).get('zip_sha256')!=(expected if verifier.parent.parent==root else previous_artifact['zip_sha256']):raise RuntimeError('Post-run artifact pin drift')
print(json.dumps(report,indent=2))
