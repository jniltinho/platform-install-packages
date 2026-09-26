#!/usr/bin/env python3
"""Record complete R2 wire/cache observations. Contract acceptance is a separate gate."""
import json,subprocess,sys,hashlib,base64
from pathlib import Path
import report_contract
from report_contract import check_prior74
KINDS=['plain','null','decorator','role','profile','cacheable'];OPS=['roundtrip','malformed','invalid-utf8'];CACHE=['hit','expired','malformed','refresh-hit','refresh-miss','invalid-utf8','read-C','read-O']
TARGETS={k:'vendor/aws/Aws/Common/Credentials/'+n+'.php' for k,n in [('plain','Credentials'),('null','NullCredentials'),('decorator','AbstractCredentialsDecorator'),('profile','RefreshableInstanceProfileCredentials'),('cacheable','CacheableCredentials')]};TARGETS.update({'role':'infra/storage/RefreshableRole.class.php','cache':'vendor/aws/Doctrine/Common/Cache/FileCache.php'})
def validate(r,mode,manifest):
 if type(r['exit']) is not int or r['exit']!=0:raise ValueError('process failure')
 b=json.loads(r['stdout'])
 if type(b) is not dict or type(b.get('runtime')) is not str or type(b.get('result')) is not dict:raise ValueError('Malformed native body shape')
 kind=r['kind'];probe='cache-probe.php' if kind=='cache' else 'probe.php'
 if b['kind']!=kind or b['operation']!=r['operation'] or not b['runtime'].startswith('7.4.' if mode=='74' else '8.3.'):raise ValueError('wrong runtime/case')
 if b['probe_sha256']!=manifest['files'][probe]:raise ValueError('probe drift')
 if not isinstance(b['loaded'],dict) or TARGETS[kind] not in b['loaded']:raise ValueError('missing full target')
 for path,digest in b['loaded'].items():
  if manifest['files'].get(r['variant']+'/'+path)!=digest:raise ValueError('loaded drift')
 if not isinstance(b['diagnostics'],list):raise ValueError('missing diagnostics')
 return b
def wiredata(w):
 if type(w) is not dict or any(type(w.get(k)) is not str for k in ['base64','sha256','format']):raise ValueError('Malformed wire shape')
 raw=base64.b64decode(w['base64'],validate=True)
 if hashlib.sha256(raw).hexdigest()!=w['sha256'] or raw[:1].decode()!=w['format']:raise ValueError('wire mismatch')
 return w['base64']
def collector_identity():
 root=Path(__file__).resolve().parent
 module=Path(report_contract.__file__).resolve()
 if module!=root/'report_contract.py':raise ValueError('Unexpected report-contract module path')
 files={'collect-r2.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'report_contract.py':hashlib.sha256(module.read_bytes()).hexdigest()}
 digest=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',', ':')).encode()).hexdigest()
 return {'schema':1,'files':files,'sha256':digest}
def prior74_wires(prior, manifest_pin, manifest, identity):
 check_prior74(prior,manifest_pin,identity)
 wires={}
 for r in prior['records']:
  b=validate(r,'74',manifest)
  if r['operation']=='roundtrip' and r['kind']!='cache':
   wires[r['kind']]=b['result']['wire'];wiredata(wires[r['kind']])
 if set(wires)!=set(KINDS):raise ValueError('Incomplete original74 wire producers')
 return wires
def consume_prior74_bytes(raw, manifest_pin, manifest, identity):
 if type(raw) is not bytes:raise ValueError('Original74 input must be exact file bytes')
 prior=json.loads(raw)
 wires=prior74_wires(prior,manifest_pin,manifest,identity)
 return wires,{'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
               'collector_closure_sha256':identity['sha256']}
def observe_process(command, payload, metadata, runner=subprocess.run):
 record=dict(metadata);record['command']=command
 record['input_sha256']=hashlib.sha256(payload.encode()).hexdigest()
 try:
  proc=runner(command,input=payload.encode(),capture_output=True,timeout=60)
  record['exit']=proc.returncode;stdout=proc.stdout;stderr=proc.stderr
 except subprocess.TimeoutExpired as e:
  record['exit']=None;record['timeout']=True;stdout=e.stdout or b'';stderr=e.stderr or b''
 except OSError as e:
  record['exit']=None;record['launch_error']=str(e);stdout=b'';stderr=b''
 for name,value in [('stdout',stdout),('stderr',stderr)]:
  if type(value) is not bytes:raise ValueError('Runner must capture bytes')
  record[name+'_base64']=base64.b64encode(value).decode()
  record[name]=value.decode('utf-8',errors='replace')
  if record[name].encode()!=value:record['invalid_utf8_output']=True
 return record
if __name__=='__main__':
 mode=sys.argv[1];out=Path(sys.argv[2]);assert mode in ['74','83'] and not out.exists()
 evidence=Path('doc/php83/evidence/serialization-contracts');meta=json.loads((evidence/'r3-stage-pin.json').read_text());manifest=json.loads((evidence/'r3-stage-identities.json').read_text());reference=json.loads((evidence/'r3-reference-wires.json').read_text());records=[];wires={};errors=[]
 if hashlib.sha256((evidence/'r3-reference-wires.json').read_bytes()).hexdigest()!=manifest['files']['reference-wires.json']:raise ValueError('Reference drift')
 variants=['original'] if mode=='74' else ['original','candidate'];cachevariants=['original'] if mode=='74' else ['original','cachefix','candidate']
 identity=collector_identity();old74={};input_report74=None
 if manifest.get('collector_closure')!=identity:raise ValueError('Stage does not pin current collector closure')
 if hashlib.sha256((evidence/'r3-stage-identities.json').read_bytes()).hexdigest()!=meta['manifest_sha256']:raise ValueError('Local stage manifest drift')
 if mode=='83':
  raw=Path(sys.argv[3]).read_bytes()
  old74,input_report74=consume_prior74_bytes(raw,meta['manifest_sha256'],manifest,identity)
 def run(variant,kind,op,payload='',writer=None):
  conf='/tmp/kaltura-php'+mode+'-ssh.conf';alias='baseline74' if mode=='74' else 'php83'
  command=['ssh','-T','-F',conf,alias,'bash '+meta['remote_stage']+'/run.sh '+variant+' '+kind+' '+op+' '+meta['manifest_sha256']]
  r=observe_process(command,payload,{'variant':variant,'kind':kind,'operation':op,'writer':writer});records.append(r)
  try:
   if r.get('invalid_utf8_output'):raise ValueError('Invalid UTF-8 native output; raw bytes retained')
   return validate(r,mode,manifest)
  except (ValueError,KeyError,TypeError,AttributeError) as e:errors.append({'variant':variant,'kind':kind,'operation':op,'writer':writer,'error':str(e)});return None
 for variant in variants:
  for kind in KINDS:
   for op in OPS:
    b=run(variant,kind,op)
    if b and op=='roundtrip':
     try:wires[variant+'/'+kind]=b['result']['wire'];wiredata(wires[variant+'/'+kind])
     except (ValueError,KeyError) as e:errors.append({'error':'missing/invalid wire','variant':variant,'kind':kind})
 for reader in variants:
  for writer in ['original','candidate']:
   for kind in KINDS:
    source=reference if mode=='74' else wires
    if writer+'/'+kind in source:run(reader,kind,'read',wiredata(source[writer+'/'+kind]),writer+'83' if mode=='74' else writer+'83-r2')
  if mode=='83':
   for kind in KINDS:run(reader,kind,'read',wiredata(old74[kind]),'original74')
 for variant in cachevariants:
  for case in CACHE:
   payload=wiredata(reference[('original' if case=='read-C' else 'candidate')+'/plain']) if case.startswith('read-') else ''
   run(variant,'cache',case,payload,'recorded83-C' if case=='read-C' else 'recorded83-O' if case=='read-O' else None)
 expected=38 if mode=='74' else 96
 if len(records)!=expected:errors.append({'error':'incomplete matrix','expected':expected,'actual':len(records)})
 final_identity=collector_identity()
 if final_identity!=identity:errors.append({'error':'Collector closure changed during observation'})
 report={'status':'OBSERVED_NOT_ACCEPTED' if not errors else 'INCOMPLETE_OR_EXECUTION_FAILED','application_acceptance':False,'mode':mode,'collector_sha256':identity['files']['collect-r2.py'],'collector_closure':identity,'collector_closure_after':final_identity,'execution_phase':manifest['phase'],'input_report74':input_report74,'stage_manifest_sha256':meta['manifest_sha256'],'records':records,'errors':errors}
 out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'records':len(records),'errors':len(errors)}));sys.exit(bool(errors))
