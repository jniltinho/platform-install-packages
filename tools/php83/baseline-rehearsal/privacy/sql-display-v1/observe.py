"""Four observational cohorts, separate fresh private DBs, no application DB."""
import argparse,hashlib,io,json,os,subprocess,tarfile,tempfile,uuid
from pathlib import Path
import prepare,verify
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
SSH=['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74']
COHORTS=('original74','display74','exp14statement83','display83')
SNAP=ROOT/'tools/php83/exp12-api/runtime-identity.py'
SNAP_PIN='f2985a7d3f054c3a743535009e0ad2937545d05e1c0d9e7c936a24acf13da463'
sha=lambda b:hashlib.sha256(b).hexdigest()
def remote(cmd,data=None):return subprocess.run(SSH+[cmd],input=data,capture_output=True,timeout=180)
def checked(cmd,data=None):
 r=remote(cmd,data)
 if r.returncode:raise RuntimeError('REMOTE_FAILED')
 return r.stdout
def atomic(path,data):
 fd,name=tempfile.mkstemp(dir=path.parent,prefix=path.name+'.progress-')
 try:
  with os.fdopen(fd,'w') as f:json.dump(data,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  os.replace(name,path)
 finally:Path(name).unlink(missing_ok=True)
def runtime_files(report):
 identity=report['identity'];out={n:v['sha256'] for n,v in identity['files'].items()}
 for libs in identity['linked_libraries'].values():
  for n,h in libs.items():
   if n in out and out[n]!=h:raise ValueError('RUNTIME_JOIN_CONFLICT')
   out[n]=h
 if not out:raise ValueError('EMPTY_RUNTIME')
 return out
def inputs(local,original,candidate):
 # Reproduce approved transformations from both pinned archives, not arbitrary local bytes.
 with tempfile.TemporaryDirectory() as d:
  fresh=Path(d)/'rebuild';expected=prepare.prepare(original,candidate,fresh)
  if json.loads((local/'manifest.json').read_text())!=expected:raise ValueError('SOURCE_MANIFEST_DRIFT')
  a={str(p.relative_to(fresh)):sha(p.read_bytes()) for p in fresh.rglob('*') if p.is_file()}
  b={str(p.relative_to(local)):sha(p.read_bytes()) for p in local.rglob('*') if p.is_file()}
  if any(p.is_symlink() for p in local.rglob('*')) or a!=b:raise ValueError('SOURCE_FILES_DRIFT')
 if sha(SNAP.read_bytes())!=SNAP_PIN:raise ValueError('SNAPSHOT_HELPER_DRIFT')
 return expected
def observe(local,original,candidate,out):
 proof=inputs(local,original,candidate);out.open('x').close()
 stage='/home/vagrant/php-display-sql.'+uuid.uuid4().hex
 result={'status':'INITIALIZING','records':[],'stage':stage,'source_proof':proof,'application_acceptance':False,'collector_sha256':sha(Path(__file__).read_bytes())}
 def save():atomic(out,result)
 def snapshot(label):
  path=out.with_name(out.stem+'-'+label+'.json')
  r=subprocess.run(['python3',str(SNAP),str(path)],capture_output=True,timeout=180)
  result.setdefault('snapshot_commands',[]).append({'helper':str(SNAP.relative_to(ROOT)),'sha256':SNAP_PIN,'exit':r.returncode});save()
  if r.returncode:raise ValueError('RUNTIME_SNAPSHOT_FAILED')
  return json.loads(path.read_text())
 staged=False;pin=None
 try:
  result['runtime_before']=snapshot('runtime-before');save()
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);blobs={}
   for cohort in ['original','exp14']:
    for name in ['original.php','KalturaStatement.php']:blobs[cohort+'/'+name]=(local/cohort/name).read_bytes()
   for name in ['probe.php','run.sh','start-db.sh','verify.py']:blobs[name]=(HERE/name).read_bytes()
   manifest={'files':{n:sha(b) for n,b in blobs.items()},'runtime_files':runtime_files(result['runtime_before']),'source_proof':proof}
   raw=json.dumps(manifest,sort_keys=True,indent=2).encode()+b'\n';pin=sha(raw);blobs['runner-manifest.json']=raw
   for n,b in blobs.items():p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   verify.verify(root,pin,check_runtime=False)
   archive=io.BytesIO()
   with tarfile.open(fileobj=archive,mode='w') as tar:
    for n,b in sorted(blobs.items()):
     info=tarfile.TarInfo(n);info.size=len(b);info.mode=0o444;tar.addfile(info,io.BytesIO(b))
   result['stage_pin']=pin;result['identities']=manifest;save()
   checked('test "$(hostname)" = kaltura-php74-baseline && test "$(id -u)" = 1000 && mkdir '+stage)
   checked('tar --no-same-owner -xf - -C '+stage,archive.getvalue())
   checked('sudo -n chown -R root:root '+stage+' && sudo -n chmod -R a-w '+stage);staged=True
  def source():return checked('python3 -B '+stage+'/verify.py '+stage+' '+pin).decode()
  result['source_before']=source();save()
  for cohort in COHORTS:
   token=uuid.uuid4().hex;db={'datadir':'/tmp/kaltura-display-sql.'+token,'unit':'php83-display-sql-'+token}
   row={'cohort':cohort,'db':db,'status':'STARTING'};result['records'].append(row);save()
   try:
    cmd='bash '+stage+'/start-db.sh '+token;r=remote(cmd)
    row['startup']={'command':cmd,'exit':r.returncode,'stdout':r.stdout.decode(),'stderr':r.stderr.decode()};save()
    if r.returncode or json.loads(r.stdout)!=db:raise ValueError('DB_STARTUP_IDENTITY')
    cmd='bash '+stage+'/run.sh '+stage+' '+cohort+' '+token+' '+pin;row['pending_command']=cmd;save()
    try:r=remote(cmd)
    except subprocess.TimeoutExpired as e:r=subprocess.CompletedProcess(cmd,124,e.stdout or b'',e.stderr or b'')
    row['execution']={'command':cmd,'exit':r.returncode,'stdout':r.stdout.decode(),'stderr':r.stderr.decode()}
    try:row['body']=json.loads(r.stdout)
    except ValueError:row['body']=None
    row.pop('pending_command');row['status']='OBSERVED';save()
   finally:
    try:
     stop=remote('sudo -n systemctl stop '+db['unit']);state=remote('systemctl is-active '+db['unit']);text=state.stdout.decode().strip()
     row['cleanup']={'stop_exit':stop.returncode,'state_exit':state.returncode,'state':text,'stopped':state.returncode in (3,4) and text in ('inactive','failed','unknown')};save()
    except Exception as e:row['cleanup_error_type']=type(e).__name__;save()
   if not row.get('cleanup',{}).get('stopped'):raise ValueError('OWNED_UNIT_NOT_STOPPED')
   if row['execution']['exit']!=0 or row['body'] is None:raise ValueError('PROBE_FAILED')
  result['status']='OBSERVED_NOT_ACCEPTED'
 except (Exception,KeyboardInterrupt) as e:result['status']='FAILED_OR_INTERRUPTED';result['error_type']=type(e).__name__
 finally:
  if staged:
   try:result['source_after']=checked('python3 -B '+stage+'/verify.py '+stage+' '+pin).decode()
   except Exception as e:result['post_source_error_type']=type(e).__name__
  try:result['runtime_after']=snapshot('runtime-after')
  except Exception as e:result['post_runtime_error_type']=type(e).__name__
  if result.get('source_before')!=result.get('source_after') or result.get('runtime_before')!=result.get('runtime_after'):result['status']='IDENTITY_FAILURE_OR_INCOMPLETE'
  save()
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--local',required=True,type=Path);p.add_argument('--original',required=True,type=Path);p.add_argument('--candidate',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();r=observe(a.local,a.original,a.candidate,a.output);print(json.dumps({'status':r['status'],'records':len(r['records'])}));raise SystemExit(2)
