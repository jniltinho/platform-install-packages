"""Coordinator only: explicit check, then separate bounded owned-probe execution."""
import argparse,base64,hashlib,importlib.util,json,os,secrets,stat,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
STAGE='/var/lib/kaltura-baseline-web-r1'
RUNTIME='tools/php83/baseline-freeze-r1/run_r2.py'
RUNTIME_PIN='6bbcbc935598d4f6edf5267359e2f97b6368f60cfd57917d582b406e74bbf6ae'
PINS=json.loads((HERE/'pins.json').read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def support():
 p=ROOT/RUNTIME
 if sha(p.read_bytes())!=RUNTIME_PIN:raise ValueError('RUNNER_PIN')
 spec=importlib.util.spec_from_file_location('web_bounded_support',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def blobs():
 result={}
 for n,h in PINS.items():
  b=(ROOT/n).read_bytes()
  if sha(b)!=h:raise ValueError('SOURCE_PIN')
  result[n]=b
 return result
def remote_guard():
 return '''import os,stat,socket,json,subprocess
from pathlib import Path
assert os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline'
a=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10));ips={v.get('local') for r in a for v in r.get('addr_info',[])}
assert '192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'})
for n in ['/','/var','/var/lib']:
 p=Path(n);s=p.lstat();assert stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and not s.st_mode&0o022 and not os.listxattr(p)
stage=Path('''+repr(STAGE)+''');assert not os.path.lexists(stage)
'''
def check(s,b):
 s.pinned(s.CONFIG,'15f687f3db61c013654442404e916b1b2ad7f0d1835e1f30ef10ca80355ceef3',True)
 s.pinned(s.KEYS,'6b6a9652a16acd478a01b508962452556138ce3a3f0c2cc4584baab58f00c4c6',True)
 if (ROOT/'deb/php74-baseline/.vagrant/machines/baseline74/virtualbox/id').read_text().strip()!=s.UUID:raise ValueError('VAGRANT_IDENTITY')
 rc,raw,_=s.bounded(['VBoxManage','showvminfo',s.UUID,'--machinereadable']);s.need(rc==0);host=s.host_guard(raw.decode())
 guest=b['tools/php83/baseline-web-runtime-r1/guest.py'].decode()
 code=remote_guard()+"ns={'__name__':'probe_check'};exec("+repr(guest)+",ns);ns['check']();print('CHECKED')\n"
 rc,raw,_=s.remote(code);s.need(rc==0 and raw==b'CHECKED\n');return host
def stage_code(b):
 payload={n:base64.b64encode(v).decode() for n,v in b.items()}
 return remote_guard()+'''import base64,hashlib
payload='''+repr(payload)+'''
manifest='''+repr(PINS)+'''
stage.mkdir(mode=0o755)
for name,encoded in payload.items():
 raw=base64.b64decode(encoded,validate=True);assert hashlib.sha256(raw).hexdigest()==manifest[name]
 p=stage/name;p.parent.mkdir(parents=True,exist_ok=True)
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o444)
 with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
fd=os.open(stage/'manifest.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o444)
with os.fdopen(fd,'w') as f:json.dump(manifest,f);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o444)
print('STAGED')
'''
def unit_command(unit):
 if not __import__('re').fullmatch('baseline-web-[0-9a-f]{8}',unit):raise ValueError('UNIT')
 return 'sudo -n systemd-run --quiet --wait --pipe --collect --unit '+unit+' -p IPAddressDeny=any -p IPAddressAllow=localhost -p IPAddressAllow=192.168.56.74/32 -p NoNewPrivileges=yes -p ProtectSystem=strict -p ProtectHome=read-only -p PrivateTmp=yes -p ReadWritePaths=/opt/kaltura/app/api_v3/web -p RuntimeMaxSec=60 /usr/bin/python3 -B '+STAGE+'/tools/php83/baseline-web-runtime-r1/guest.py '+unit

def project(raw):
 import guest
 r=json.loads(raw)
 expected={'version','sapi','modules','ini_file','nonce_verified','probe_removed','probe_code_sha256','status','baseline_acceptance','app_credentials_read','sql_executed'}
 if set(r)!=expected or r['status']!='CURRENT_APACHE_PHP74_OBSERVED_OWN_PROBE_REMOVED' or any(r[k] is not False for k in ['baseline_acceptance','app_credentials_read','sql_executed']) or r['nonce_verified'] is not True or r['probe_removed'] is not True:raise ValueError('RESULT_SCHEMA')
 guest.project({'nonce':'0'*32,**{k:r[k] for k in ['version','sapi','modules','ini_file']}},'0'*32)
 if not __import__('re').fullmatch('[a-f0-9]{64}',r['probe_code_sha256']):raise ValueError('HASH')
 return r

def main(output,execute=False):
 path=Path(output)
 if path.exists() or path.is_symlink():raise ValueError('OUTPUT_EXISTS')
 s=support();b=blobs();host=check(s,b)
 result={'status':'CHECKED_NOT_EXECUTED','host':host,'source_pins':PINS,'runner_sha256':sha(Path(__file__).read_bytes()),'baseline_acceptance':False,'guest_exit':None,'unit_inactive':None}
 if execute:
  unit='baseline-web-'+secrets.token_hex(4);result['unit']=unit
  rc,raw,_=s.remote(stage_code(b));s.need(rc==0 and raw==b'STAGED\n')
  try:
   try:
    rc,raw,err=s.bounded(s.SSH+[unit_command(unit)],timeout=90,cap=128*1024)
    result.update(guest_exit=rc,stderr_bytes=err,status='FAILED_OR_INCOMPLETE')
    if rc==0 and err==0:result['provider']=project(raw);result['status']='CURRENT_WEB_OBSERVATION_CAPTURED'
   except Exception:result['status']='FAILED_OR_INCOMPLETE'
  finally:
   try:
    s.bounded(s.SSH+['sudo -n systemctl stop '+unit+'.service'],timeout=20,cap=4096)
    rc,raw,_=s.bounded(s.SSH+['systemctl is-active '+unit+'.service'],timeout=15,cap=4096)
    result['unit_inactive']=rc in (3,4) and raw.strip() in (b'inactive',b'unknown')
   except Exception:result['unit_inactive']=False
  try:
   rc,raw,_=s.bounded(['VBoxManage','showvminfo',s.UUID,'--machinereadable']);result['host_unchanged']=rc==0 and s.host_guard(raw.decode())==host
  except Exception:result['host_unchanged']=False
  if not result['unit_inactive'] or not result['host_unchanged']:result['status']='FAILED_OR_INCOMPLETE'
 with path.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({'status':result['status'],'baseline_acceptance':False}))
 return 0 if result['status'] in ('CHECKED_NOT_EXECUTED','CURRENT_WEB_OBSERVATION_CAPTURED') else 1
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args()
 try:sys.exit(main(a.output,a.execute))
 except Exception:print('{"status":"REJECTED","baseline_acceptance":false}');sys.exit(1)
