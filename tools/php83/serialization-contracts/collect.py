#!/usr/bin/env python3
"""Bounded observations, not an acceptance comparator. Refuse overwriting reports."""
import json,subprocess,sys,hashlib,base64
from pathlib import Path
KINDS=['plain','null','decorator','role','profile','cacheable'];VARIANTS=['original','candidate'];OPS=['roundtrip','malformed','invalid-utf8']
def validate(record,variant,kind,op,manifest):
 if type(record['exit']) is not int or record['exit']!=0:raise ValueError('process failed')
 b=json.loads(record['stdout'])
 if b['kind']!=kind or b['operation']!=op or not b['runtime'].startswith('8.3.'):raise ValueError('wrong case/runtime')
 if b['probe_sha256']!=manifest['files']['probe.php']:raise ValueError('probe drift')
 if not isinstance(b['loaded'],dict) or not b['loaded']:raise ValueError('missing source load proof')
 for path,digest in b['loaded'].items():
  if manifest['files'].get(variant+'/'+path)!=digest:raise ValueError('loaded drift')
 target={'plain':'vendor/aws/Aws/Common/Credentials/Credentials.php','null':'vendor/aws/Aws/Common/Credentials/NullCredentials.php','decorator':'vendor/aws/Aws/Common/Credentials/AbstractCredentialsDecorator.php','role':'infra/storage/RefreshableRole.class.php','profile':'vendor/aws/Aws/Common/Credentials/RefreshableInstanceProfileCredentials.php','cacheable':'vendor/aws/Aws/Common/Credentials/CacheableCredentials.php'}[kind]
 if target not in b['loaded']:raise ValueError('target not loaded')
 if not isinstance(b['diagnostics'],list):raise ValueError('diagnostics missing')
 return b
if __name__=='__main__':
 out=Path(sys.argv[1]);assert not out.exists()
 evidence=Path('doc/php83/evidence/serialization-contracts');meta=json.loads((evidence/'stage-pin.json').read_text());manifest=json.loads((evidence/'stage-identities.json').read_text());records=[];wires={};errors=[]
 def run(variant,kind,op,payload='',writer=None):
  command=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83','bash '+meta['remote_stage']+'/run.sh '+variant+' '+kind+' '+op+' '+meta['manifest_sha256']]
  try:
   p=subprocess.run(command,input=payload,capture_output=True,text=True,timeout=60);r={'variant':variant,'kind':kind,'operation':op,'writer':writer,'command':command,'input_sha256':hashlib.sha256(payload.encode()).hexdigest(),'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr};records.append(r)
   return validate(r,variant,kind,op,manifest)
  except (ValueError,KeyError,subprocess.TimeoutExpired) as e:errors.append({'variant':variant,'kind':kind,'operation':op,'writer':writer,'error':str(e)});return None
 for variant in VARIANTS:
  for kind in KINDS:
   for op in OPS:
    body=run(variant,kind,op)
    if body and op=='roundtrip':
     try:
      wire=body['result']['wire'];raw=base64.b64decode(wire['base64'],validate=True)
      if hashlib.sha256(raw).hexdigest()!=wire['sha256']:raise ValueError('wire hash')
      wires[(variant,kind)]=wire['base64']
     except (ValueError,KeyError) as e:errors.append({'variant':variant,'kind':kind,'error':'missing/invalid native wire: '+str(e)})
 for reader in VARIANTS:
  for writer in VARIANTS:
   for kind in KINDS:
    if (writer,kind) in wires:run(reader,kind,'read',wires[(writer,kind)],writer)
 if len(records)!=60:errors.append({'error':'incomplete matrix','actual':len(records),'expected':60})
 report={'status':'OBSERVED_NOT_ACCEPTED' if not errors else 'INCOMPLETE_OR_EXECUTION_FAILED','application_acceptance':False,'original74':'PENDING_SEPARATE_LAB','collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'stage_manifest_sha256':meta['manifest_sha256'],'records':records,'errors':errors}
 out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'records':len(records),'errors':len(errors)}));sys.exit(bool(errors))
