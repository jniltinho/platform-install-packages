#!/usr/bin/env python3
"""Four actual native83 observations, not a selector or SQL/API acceptance gate."""
import argparse,hashlib,io,json,os,pathlib,subprocess,tarfile,tempfile
import prepare
ROOT=prepare.ROOT;HERE=pathlib.Path(__file__).resolve().parent
STAGE='/home/vagrant/php-dispatch-rank-observation-v1'
SOURCE=ROOT/'doc/php83/evidence/dispatch-rank/preparation-r3'
SSH=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83']
def remote(cmd,data=None):return subprocess.run(SSH+[cmd],input=data,capture_output=True,timeout=120)
def checked(cmd,data=None):
 p=remote(cmd,data)
 if p.returncode:raise RuntimeError(p.stderr.decode())
 return p.stdout.decode()
def atomic(path,value):
 fd,n=tempfile.mkstemp(dir=path.parent,prefix=path.name+'.progress-')
 try:
  with os.fdopen(fd,'w') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  os.replace(n,path)
 finally:pathlib.Path(n).unlink(missing_ok=True)
def files():
 original=(SOURCE/'original.php').read_bytes()
 if prepare.sha(original)!=prepare.SOURCE_PINS[prepare.PATHS[0]]:raise ValueError('Wrong target')
 data={name+'.php':b for name,b in prepare.variants(original).items()}
 for p,pin in prepare.SOURCE_PINS.items():
  b=(SOURCE/'source'/p).read_bytes()
  if prepare.sha(b)!=pin:raise ValueError('Dependency drift')
  data['source/'+p]=b
 for name in ['dispatcher-probe.php','rank-metadata-probe.php','run.sh']:data[name]=(HERE/name).read_bytes()
 return data

def observe(out):
 data=files();identities={p:prepare.sha(b) for p,b in data.items()}
 sums=''.join(h+'  '+p+'\n' for p,h in sorted(identities.items())).encode();pin=prepare.sha(sums);data['SHA256SUMS']=sums
 out.open('x').close();result={'status':'INITIALIZING','records':[],'files':identities,'checksum_manifest_sha256':pin,'collector_sha256':prepare.sha(pathlib.Path(__file__).read_bytes()),'application_acceptance':False}
 def snapshot(label):
  p=out.with_name(out.stem+'-'+label+'.json');cmd=['python3',str(ROOT/'tools/php83/exp12-api/runtime83-identity.py'),str(p)]
  r=subprocess.run(cmd,capture_output=True,text=True,timeout=150)
  result.setdefault('snapshot_commands',[]).append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
  if r.returncode:raise RuntimeError('Runtime identity collection failed')
  return json.loads(p.read_text())
 def source_identity():
  text=checked('cd '+STAGE+' && sha256sum '+ ' '.join(sorted(data)))
  rows={}
  for line in text.splitlines():
   h,p=line.split()
   if p in rows:raise ValueError('Duplicate identity')
   rows[p]=h
  if rows!={p:prepare.sha(b) for p,b in data.items()}:raise ValueError('Stage drift')
  if checked('find '+STAGE+' -type l -print'):raise ValueError('Stage symlink')
  return rows
 staged=False
 try:
  result['runtime_before']=snapshot('runtime-before');atomic(out,result)
  checked('test "$(hostname)" = kaltura-php83-lab && mkdir '+STAGE)
  buf=io.BytesIO()
  with tarfile.open(fileobj=buf,mode='w') as tar:
   for p,b in data.items():
    member=tarfile.TarInfo(p);member.size=len(b);member.mode=0o444;tar.addfile(member,io.BytesIO(b))
  checked('tar --no-same-owner -xf - -C '+STAGE,buf.getvalue());checked('sudo -n chown -R root:root '+STAGE+' && sudo -n chmod -R a-w '+STAGE);staged=True
  result['source_before']=source_identity();atomic(out,result)
  for mode in ['original','public-comparison','attribute-comparison','rank']:
   cmd='bash '+STAGE+'/run.sh '+mode+' '+pin;result['pending']=mode;atomic(out,result);r=remote(cmd)
   stdout=r.stdout.decode();stderr=r.stderr.decode()
   try:body=json.loads(stdout)
   except ValueError:body=None
   result['records'].append({'mode':mode,'command':cmd,'exit':r.returncode,'stdout':stdout,'stderr':stderr,'body':body});result.pop('pending');atomic(out,result)
  result['status']='OBSERVED_NOT_ACCEPTED'
 except (Exception,KeyboardInterrupt) as e:result['status']='FAILED_OR_INTERRUPTED';result['error']={'type':type(e).__name__,'message':str(e)}
 finally:
  if staged:
   try:result['source_after']=source_identity()
   except Exception as e:result['post_source_error']=str(e)
  try:result['runtime_after']=snapshot('runtime-after')
  except Exception as e:result['post_runtime_error']=str(e)
  if result.get('runtime_before')!=result.get('runtime_after') or result.get('source_before')!=result.get('source_after'):result['status']='IDENTITY_FAILURE_OR_INCOMPLETE'
  atomic(out,result)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('output',type=pathlib.Path);a=p.parse_args();r=observe(a.output);print(json.dumps({'status':r['status'],'records':len(r['records'])}));raise SystemExit(2)
