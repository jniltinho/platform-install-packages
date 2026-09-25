#!/usr/bin/env python3
"""Run artifact-based focused regression, retaining errors instead of forcing OK."""
import datetime,hashlib,json,socket,subprocess,time,zipfile
from pathlib import Path
root=Path('/home/vagrant/php-exp6-regression')
if socket.gethostname() not in ('kaltura-php74-baseline','kaltura-php83-lab'):raise SystemExit(64)
archive=root/'exp6.zip'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='da11cbb9cc58e4e67d4eb8c875d651f272941c7d37d1209c63a02a48e4ba30be'
with zipfile.ZipFile(archive) as z:
 names=[]
 for i in z.infolist():
  if not i.is_dir():
   p=root/'source'/i.filename
   assert p.read_bytes()==z.read(i)
   names.append(i.filename)
 assert sorted(str(p.relative_to(root/'source')) for p in (root/'source').rglob('*') if p.is_file())==sorted(names)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'schema':1,'host':socket.gethostname(),'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'zip_sha256':sha(archive),'verified_extracted_files':len(names),'harness':{str(p.relative_to(root)):sha(p) for folder in ['tests','exp6-regression'] for p in sorted((root/folder).rglob('*')) if p.is_file()},'rows':[],'application_acceptance':False}
for source in ['original','exp6']:
 for ini in ['standard','minimal']:
  for case in ['environment','legacy-json','zend-json','doc-comment','doc-comment-export','doc-comment-consumer']:
   cmd=['bash',str(root/'exp6-regression/run-one.sh'),source,case,ini]
   start=time.monotonic_ns(); run=subprocess.run(cmd,capture_output=True,text=True,timeout=70)
   report['rows'].append({'source':source,'ini':ini,'case':case,'exit':run.returncode,'duration_ns':time.monotonic_ns()-start,'stdout':run.stdout,'stderr':run.stderr})
print(json.dumps(report,indent=2))
