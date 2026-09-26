#!/usr/bin/env python3
"""Explicitly observational private-socket SQL execution; no artifact selection."""
import argparse,io,json,os,pathlib,subprocess,tarfile,tempfile,uuid
import prepare,verify
HERE=prepare.HERE;ROOT=prepare.ROOT
SSH=['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74']
def remote(cmd,data=None):return subprocess.run(SSH+[cmd],input=data,capture_output=True,timeout=180)
def checked(cmd,data=None):
 r=remote(cmd,data)
 if r.returncode:raise RuntimeError('Remote failure: '+r.stderr.decode())
 return r.stdout.decode()
def atomic(path,data):
 fd,n=tempfile.mkstemp(dir=path.parent,prefix=path.name+'.progress-')
 try:
  with os.fdopen(fd,'w') as f:json.dump(data,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  os.replace(n,path)
 finally:pathlib.Path(n).unlink(missing_ok=True)
def validate(local,archive):
 pin=prepare.sha((local/'manifest.json').read_bytes());ids=verify.verify(local,pin)
 with tempfile.TemporaryDirectory() as t:expected=prepare.prepare(archive,pathlib.Path(t)/'rebuild')
 if ids!=expected:raise ValueError('Manifest not exact freshly reproduced authorized sources/harness')
 return pin,ids

def observe(local,archive,out):
 pin,ids=validate(local,archive);out.open('x').close()
 stage='/home/vagrant/php-return-sql.'+uuid.uuid4().hex
 result={'status':'INITIALIZING','records':[],'stage':stage,'stage_pin':pin,'identities':ids,'application_acceptance':False,'collector_sha256':prepare.sha(pathlib.Path(__file__).read_bytes())}
 def save():atomic(out,result)
 def snapshot(label):
  path=out.with_name(out.stem+'-'+label+'.json');cmd=['python3',str(ROOT/'tools/php83/exp12-api/runtime-identity.py'),str(path)]
  r=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
  result.setdefault('snapshot_commands',[]).append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});save()
  if r.returncode:raise ValueError('Runtime snapshot failed')
  return json.loads(path.read_text())
 def source():return checked('python3 '+stage+'/verify.py '+stage+' '+pin)
 staged=False
 try:
  result['runtime_before']=snapshot('runtime-before');save()
  checked('test "$(hostname)" = kaltura-php74-baseline && test "$(id -u)" = 1000 && mkdir '+stage)
  buf=io.BytesIO()
  with tarfile.open(fileobj=buf,mode='w') as tar:
   for p in sorted(local.rglob('*')):
    if p.is_file():tar.add(p,arcname=str(p.relative_to(local)),recursive=False)
  checked('tar --no-same-owner -xf - -C '+stage,buf.getvalue());checked('sudo -n chown -R root:root '+stage+' && sudo -n chmod -R a-w '+stage);staged=True
  result['source_before']=source();save()
  for cohort in ['prerequisite','candidate']:
   token=uuid.uuid4().hex;db={'datadir':'/tmp/kaltura-return-sql.'+token,'unit':'php83-return-sql-'+token}
   row={'cohort':cohort,'db':db,'status':'STARTING'};result['records'].append(row);save()
   try:
    cmd='bash '+stage+'/start-db.sh '+token;r=remote(cmd);row['startup']={'command':cmd,'exit':r.returncode,'stdout':r.stdout.decode(),'stderr':r.stderr.decode()};save()
    if r.returncode or json.loads(r.stdout)!=db:raise ValueError('DB startup identity failure')
    cmd='bash '+stage+'/run.sh '+stage+' '+cohort+' '+token+' '+pin;row['pending_command']=cmd;save();r=remote(cmd)
    row['execution']={'command':cmd,'exit':r.returncode,'stdout':r.stdout.decode(),'stderr':r.stderr.decode()}
    try:row['body']=json.loads(r.stdout)
    except ValueError:row['body']=None
    row.pop('pending_command');row['status']='OBSERVED';save()
   finally:
    # Exact freshly generated unit only; attempt even after startup/SSH failure.
    try:
     stop=remote('sudo -n systemctl stop '+db['unit']);state=remote('systemctl is-active '+db['unit']);text=state.stdout.decode().strip()
     row['cleanup']={'stop_exit':stop.returncode,'stop_stdout':stop.stdout.decode(),'stop_stderr':stop.stderr.decode(),'state_exit':state.returncode,'state':text,'stopped':state.returncode in (3,4) and text in ('inactive','failed','unknown')};save()
    except Exception as e:row['cleanup_error']=str(e);save()
   if not row.get('cleanup',{}).get('stopped'):raise ValueError('Owned unit not confirmed stopped')
  result['status']='OBSERVED_NOT_ACCEPTED'
 except (Exception,KeyboardInterrupt) as e:result['status']='FAILED_OR_INTERRUPTED';result['error']={'type':type(e).__name__,'message':str(e)}
 finally:
  if staged:
   try:result['source_after']=source()
   except Exception as e:result['post_source_error']=str(e)
  try:result['runtime_after']=snapshot('runtime-after')
  except Exception as e:result['post_runtime_error']=str(e)
  if result.get('source_before')!=result.get('source_after') or result.get('runtime_before')!=result.get('runtime_after'):result['status']='IDENTITY_FAILURE_OR_INCOMPLETE'
  save()
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--local',required=True,type=pathlib.Path);p.add_argument('--zip',required=True);p.add_argument('--output',required=True,type=pathlib.Path);a=p.parse_args();r=observe(a.local,a.zip,a.output);print(json.dumps({'status':r['status'],'records':len(r['records'])}));raise SystemExit(2)
