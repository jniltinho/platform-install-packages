#!/usr/bin/env python3
"""Actual-archive provenance, four native83 corpus processes; no whole app."""
import argparse,json,hashlib,os,tempfile
from pathlib import Path
import runtime_helper as h,validate,verify
STAGE='/home/vagrant/php-exp12-criteria-v1'
PIN='de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b'
def collect(local,output):
 raw=(local/'identities.json').read_bytes();pin=hashlib.sha256(raw).hexdigest();ids=verify.verify(local,pin)
 if ids.get('exp12_sha256')!=PIN:raise ValueError('Not exp12 artifact-derived stage')
 expected=dict(ids['files'],**{'identities.json':pin})
 def identity():
  text=h.checked('83','cd '+STAGE+' && sha256sum '+' '.join(expected));actual={}
  for line in text.splitlines():
   checksum,path=line.split()
   if path in actual:raise ValueError('Duplicate source path')
   actual[path]=checksum
  if actual!=expected:raise ValueError('Source drift')
  check=h.checked('83','python3 /home/vagrant/php-exp12-regression/api/verify-source.py');artifact=json.loads(check)
  if artifact['zip_sha256']!=PIN:raise ValueError('Actual full artifact drift')
  return {'source':actual,'artifact':artifact,'runtime':h.runtime_identity('83')}
 with output.open('x') as f:f.write('{}\n')
 result={'status':'INITIALIZING','identities':ids,'identities_sha256':pin,'records':[],'application_acceptance':False}
 def save():
  fd,name=tempfile.mkstemp(prefix=output.name+'.progress-',dir=output.parent)
  try:
   with os.fdopen(fd,'w') as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
   Path(name).replace(output)
  finally:Path(name).unlink(missing_ok=True)
 try:
  result['before']=identity();save()
  for mode in validate.MODES:
   variant,corpus=mode.split('-');cmd='bash '+STAGE+'/run.sh '+variant+' '+corpus+' '+pin;result['pending']=mode;save();r=h.remote('83',cmd);stdout=r.stdout.decode();stderr=r.stderr.decode()
   try:body=json.loads(stdout)
   except ValueError:body=None
   result['records'].append({'mode':mode,'command':cmd,'exit':r.returncode,'stdout':stdout,'stderr':stderr,'body':body});result.pop('pending');save()
  result['after']=identity()
  if result['before']!=result['after']:raise ValueError('Runtime/source/artifact drift')
  result['comparison']=validate.validate(result['records'],ids);result['status']='BOUNDED_ARTIFACT_CRITERIA_PASS'
 except (Exception,KeyboardInterrupt) as e:result['status']='FAILED_OR_INTERRUPTED';result['error']={'type':type(e).__name__,'message':str(e)}
 finally:
  if 'before' in result and 'after' not in result:
   try:result['after']=identity()
   except Exception as e:result['post_identity_error']=str(e)
  save()
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',type=Path);p.add_argument('output',type=Path);a=p.parse_args();r=collect(a.stage,a.output);print(json.dumps({'status':r['status'],'records':len(r['records'])}));raise SystemExit(0 if r['status']=='BOUNDED_ARTIFACT_CRITERIA_PASS' else 2)
