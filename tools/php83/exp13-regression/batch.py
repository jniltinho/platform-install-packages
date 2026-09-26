#!/usr/bin/env python3
"""Run artifact-based focused regression, retaining errors instead of forcing OK."""
import datetime,hashlib,json,re,socket,subprocess,time,zipfile
from pathlib import Path
if not __debug__:raise RuntimeError('Optimized Python not supported')
root=Path('/home/vagrant/php-exp13-regression')
if socket.gethostname() not in ('kaltura-php74-baseline','kaltura-php83-lab'):raise SystemExit(64)
archive=root/'exp13.zip'
expected=(root/'api/artifact-sha256.txt').read_text().strip()
assert re.fullmatch('[0-9a-f]{64}',expected)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(set(z.namelist()))
 names=[]
 for i in z.infolist():
  assert not Path(i.filename).is_absolute() and ".." not in Path(i.filename).parts
  assert (i.external_attr >> 16) & 0o170000 != 0o120000
  if not i.is_dir():
   p=root/'source'/i.filename
   assert p.read_bytes()==z.read(i)
   names.append(i.filename)
 assert sorted(str(p.relative_to(root/'source')) for p in (root/'source').rglob('*') if p.is_file())==sorted(names)
prior=subprocess.run(['python3','/home/vagrant/php-exp12-regression/api/verify-source.py'],capture_output=True,text=True,timeout=60)
if prior.returncode:raise RuntimeError('Previous artifact drift')
previous_artifact=json.loads(prior.stdout)
if previous_artifact.get("zip_sha256")!="de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b":raise RuntimeError("Wrong exp12 reference pin")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'schema':1,'host':socket.gethostname(),'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'zip_sha256':sha(archive),'verified_extracted_files':len(names),'harness':{str(p.relative_to(root)):sha(p) for folder in ['tests','exp13-regression'] for p in sorted((root/folder).rglob('*')) if p.is_file()},'previous_artifact':previous_artifact,'unsupported_cases':(['exp12/php74','exp13/php74'] if socket.gethostname()=='kaltura-php74-baseline' else []),'rows':[],'application_acceptance':False}
for source in (['original'] if socket.gethostname()=='kaltura-php74-baseline' else ['original','exp12','exp13']):
 for ini in ['standard','minimal']:
  for case in ['environment','legacy-json','zend-json','doc-comment','doc-comment-export','doc-comment-consumer']:
   cmd=['bash',str(root/'exp13-regression/run-one.sh'),source,case,ini]
   start=time.monotonic_ns(); run=subprocess.run(cmd,capture_output=True,text=True,timeout=70)
   report['rows'].append({'source':source,'ini':ini,'case':case,'exit':run.returncode,'duration_ns':time.monotonic_ns()-start,'stdout':run.stdout,'stderr':run.stderr})
for verifier in [root/'api/verify-source.py',Path('/home/vagrant/php-exp12-regression/api/verify-source.py')]:
 checked=subprocess.run(['python3',str(verifier)],capture_output=True,text=True,timeout=60)
 if checked.returncode:raise RuntimeError('Post-run artifact verification failed')
 if json.loads(checked.stdout).get('zip_sha256')!=(expected if verifier.parent.parent==root else previous_artifact['zip_sha256']):raise RuntimeError('Post-run artifact pin drift')
print(json.dumps(report,indent=2))
