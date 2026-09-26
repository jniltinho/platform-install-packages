#!/usr/bin/env python3
"""Nine native83 read-only observations; never claims acceptance or SQL coverage."""
import argparse,hashlib,io,json,os,pathlib,subprocess,tarfile,tempfile
import compose,build,verify
STAGE='/home/vagrant/php-return-contracts-observation-v1'
SSH=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83']
COMPOSITION=build.ROOT/'doc/php83/evidence/return-contracts/composition-preparation-r2.json'
COMPOSITION_SHA='1dc5c3aaefff37ec506434132b20028281f14232219f60b896b3aeca675da024'
SNAP=build.ROOT/'tools/php83/exp12-api/runtime83-identity.py'
def validate_ids(ids):
 raw=COMPOSITION.read_bytes()
 if build.sha(raw)!=COMPOSITION_SHA:raise ValueError('Reviewed composition drift')
 expected=json.loads(raw)
 for key in ['base_zip_sha256','prerequisite_patch_sha256','prerequisite_debug_after_sha256','variants']:
  if ids.get(key)!=expected[key]:raise ValueError('Unapproved source composition: '+key)
 if set(ids['harness'])!={'probe.php','run.sh','verify.py'}:raise ValueError('Wrong harness files')
 for name in ids['harness']:
  if ids['harness'][name]!=build.sha((build.HERE/name).read_bytes()):raise ValueError('Current harness differs')
def remote(cmd,data=None):return subprocess.run(SSH+[cmd],input=data,capture_output=True,timeout=120)
def checked(cmd,data=None):
 r=remote(cmd,data)
 if r.returncode:raise RuntimeError('Remote command failed: '+r.stderr.decode(errors='replace'))
 return r.stdout.decode()
def atomic(path,data):
 fd,name=tempfile.mkstemp(dir=path.parent,prefix=path.name+'.progress-')
 try:
  with os.fdopen(fd,'w') as f:json.dump(data,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  os.replace(name,path)
 finally:pathlib.Path(name).unlink(missing_ok=True)
def prepare(archive,local):
 ids=compose.compose(archive,local)
 ids['harness']={}
 for name in ['probe.php','run.sh','verify.py']:
  data=(build.HERE/name).read_bytes();(local/name).write_bytes(data);ids['harness'][name]=build.sha(data)
 (local/'identities.json').write_text(json.dumps(ids,indent=2)+'\n');return build.sha((local/'identities.json').read_bytes())
def observe(local,output):
 raw=(local/'identities.json').read_bytes();pin=build.sha(raw);ids=verify.verify(local,pin)
 validate_ids(ids)
 for name in ['probe.php','run.sh','verify.py']:
  if ids['harness'].get(name)!=build.sha((build.HERE/name).read_bytes()):raise ValueError('Current harness differs')
 if set(ids['harness'])!={'probe.php','run.sh','verify.py'}:raise ValueError('Wrong harness files')
 output.open('x').close()
 result={'status':'INITIALIZING','records':[],'stage':STAGE,'stage_manifest_sha256':pin,'identities':ids,'collector_sha256':build.sha(pathlib.Path(__file__).read_bytes()),'application_acceptance':False}
 def snapshot(label):
  path=output.with_name(output.stem+'-'+label+'.json')
  r=subprocess.run(['python3',str(SNAP),str(path)],capture_output=True,text=True,timeout=150)
  result.setdefault('snapshot_commands',[]).append({'command':['python3',str(SNAP),str(path)],'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
  if r.returncode:raise RuntimeError('Runtime snapshot failure')
  return json.loads(path.read_text())
 def source_identity():
  stagecheck=checked('python3 '+STAGE+'/verify.py '+STAGE+' '+pin)
  full=json.loads(checked('python3 /home/vagrant/php-exp12-regression/api/verify-source.py'))
  if full.get('zip_sha256')!=build.ZIP_SHA:raise ValueError('Full source drift')
  return {'stage_verification':stagecheck,'full_source':full}
 staged=False
 try:
  result['runtime_before']=snapshot('runtime-before');atomic(output,result)
  checked('test "$(hostname)" = kaltura-php83-lab && mkdir '+STAGE)
  data=io.BytesIO()
  with tarfile.open(fileobj=data,mode='w') as tar:
   for p in sorted(local.rglob('*')):
    if p.is_file():tar.add(p,arcname=str(p.relative_to(local)),recursive=False)
  checked('tar --no-same-owner -xf - -C '+STAGE,data.getvalue())
  checked('sudo -n chown -R root:root '+STAGE+' && sudo -n chmod -R a-w '+STAGE);staged=True
  result['source_before']=source_identity();atomic(output,result)
  for variant in ['exp12','prerequisite','candidate']:
   for case in ['hierarchy','configuration','exception']:
    cmd='bash '+STAGE+'/run.sh '+variant+' '+case+' '+pin
    result['pending']=[variant,case];atomic(output,result)
    r=remote(cmd);stdout=r.stdout.decode(errors='strict');stderr=r.stderr.decode(errors='strict')
    try:body=json.loads(stdout)
    except ValueError:body=None
    result['records'].append({'variant':variant,'case':case,'command':cmd,'exit':r.returncode,'stdout':stdout,'stderr':stderr,'body':body});result.pop('pending');atomic(output,result)
  result['status']='OBSERVED_NOT_ACCEPTED'
 except (Exception,KeyboardInterrupt) as e:result['status']='FAILED_OR_INTERRUPTED';result['error']={'type':type(e).__name__,'message':str(e)}
 finally:
  if staged:
   try:result['source_after']=source_identity()
   except Exception as e:result['source_after_error']=str(e)
  try:result['runtime_after']=snapshot('runtime-after')
  except Exception as e:result['runtime_after_error']=str(e)
  if result.get('source_before')!=result.get('source_after') or result.get('runtime_before')!=result.get('runtime_after'):result['status']='IDENTITY_FAILURE_OR_INCOMPLETE'
  atomic(output,result)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--prepare-zip');p.add_argument('--local',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path);a=p.parse_args()
 if a.prepare_zip:print(prepare(a.prepare_zip,a.local))
 elif a.output:
  r=observe(a.local,a.output);print(json.dumps({'status':r['status'],'records':len(r['records'])}));raise SystemExit(2)
 else:p.error('Need --prepare-zip or --output')
