#!/usr/bin/env python3
"""Four real-class signature observations on baseline74; never SQL acceptance."""
import argparse,hashlib,io,json,os,pathlib,subprocess,tarfile,tempfile
import prepare
import secrets
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
STAGE='/home/vagrant/php-rank-signature.'+secrets.token_hex(16)
SOURCE=ROOT/'doc/php83/evidence/rank-signature-repair/prepared-r1'
SSH=['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74']
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
 original=(SOURCE/'original.php').read_bytes();candidate=(SOURCE/'candidate.php').read_bytes()
 prepare.validate(original,candidate)
 with prepare.zipfile.ZipFile('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip') as z:
  base=z.read('server-Rigel-18.20.0/api_v3/lib/KalturaBaseService.php')
 if prepare.sha(base)!='48c4e41bfbb1072d5231e8ae8e300cb3e8bb8eb6e26a653d7925c00442a2999f':raise ValueError('Base class drift')
 data={'original.php':original,'candidate.php':candidate,'KalturaBaseService.php':base}
 for name in ['probe.php','run.sh']:data[name]=(HERE/name).read_bytes()
 return data

def observe(out):
 data=files();identities={p:prepare.sha(b) for p,b in data.items()}
 sums=''.join(h+'  '+p+'\n' for p,h in sorted(identities.items())).encode();pin=prepare.sha(sums);data['SHA256SUMS']=sums
 out.open('x').close();result={'status':'INITIALIZING','records':[],'files':identities,'checksum_manifest_sha256':pin,'collector_sha256':prepare.sha(pathlib.Path(__file__).read_bytes()),'application_acceptance':False,'stage':STAGE,'rank_positive_body_tested':False}
 def snapshot(label):
  p=out.with_name(out.stem+'-'+label+'.json');cmd=['python3',str(ROOT/'tools/php83/exp12-api/runtime-identity.py'),str(p)]
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
  checked('test "$(hostname)" = kaltura-php74-baseline && mkdir '+STAGE)
  buf=io.BytesIO()
  with tarfile.open(fileobj=buf,mode='w') as tar:
   for p,b in data.items():
    member=tarfile.TarInfo(p);member.size=len(b);member.mode=0o444;tar.addfile(member,io.BytesIO(b))
  checked('tar --no-same-owner -xf - -C '+STAGE,buf.getvalue());checked('sudo -n chown -R root:root '+STAGE+' && sudo -n chmod -R a-w '+STAGE);staged=True
  result['source_before']=source_identity();atomic(out,result)
  for mode in ['74-original','74-candidate','83-original','83-candidate']:
   runtime,variant=mode.split('-');cmd='bash '+STAGE+'/run.sh '+STAGE+' '+runtime+' '+variant+' '+pin;result['pending']=mode;atomic(out,result);r=remote(cmd)
   stdout=r.stdout.decode();stderr=r.stderr.decode()
   try:body=json.loads(stdout)
   except ValueError:body=None
   result['records'].append({'mode':mode,'command':cmd,'exit':r.returncode,'stdout':stdout,'stderr':stderr,'body':body});result.pop('pending');atomic(out,result)
  result['status']='OBSERVED_NOT_ACCEPTED'
 except (Exception,KeyboardInterrupt) as e:result['status']='FAILED_OR_INTERRUPTED';result['error']={'type':type(e).__name__,'message':'omitted; exception type only'}
 finally:
  if staged:
   try:result['source_after']=source_identity()
   except Exception as e:result['post_source_error']=type(e).__name__
  try:result['runtime_after']=snapshot('runtime-after')
  except Exception as e:result['post_runtime_error']=type(e).__name__
  if not result.get('runtime_before') or not result.get('source_before') or result.get('runtime_before')!=result.get('runtime_after') or result.get('source_before')!=result.get('source_after'):result['status']='IDENTITY_FAILURE_OR_INCOMPLETE'
  atomic(out,result)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('output',type=pathlib.Path);a=p.parse_args();r=observe(a.output);print(json.dumps({'status':r['status'],'records':len(r['records'])}));raise SystemExit(2)
