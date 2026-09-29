"""Stage the pinned FullHD60 fixture once into a new root-owned read-only directory on Baseline74.
scp (strict pinned SSH config) to a random vagrant temp name, then root copies it with O_EXCL into
/var/lib/kaltura-baseline-long-media-r1/fullhd60.mp4 (0444), verifying size+SHA256 on both sides and
removing the temp. Never reuses an existing directory; no API, DB or Kaltura change."""
import json,secrets,sys
from pathlib import Path
import run_thumbnail_r5 as r
LOCAL=Path('/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/baseline-media-r1/fullhd60.mp4')
SIZE=117210794
SHA256='611e3644fb56fc1f12ddccd1d889258d249e36a4eca445451c16d13f5c5f5b07'
TARGET='/var/lib/kaltura-baseline-long-media-r1'
REMOTE='''import hashlib,os,socket,stat,subprocess,json
from pathlib import Path
assert os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline'
ips={a.get('local') for x in json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10)) for a in x.get('addr_info',[])}
assert '192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'})
tmp=Path(%(tmp)r);target=Path(%(target)r)
if %(cleanup_only)r:
 # Remove only our own random temp (regular, single link, vagrant-owned); never the target.
 if os.path.lexists(tmp):
  s=tmp.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==1000;tmp.unlink()
 print('CLEANED');raise SystemExit(0)
assert not os.path.lexists(target)
s=tmp.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size==%(size)d
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb',opener=lambda n,f:os.open(n,f|os.O_NOFOLLOW)) as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
assert digest(tmp)==%(sha)r
target.mkdir(mode=0o755);os.chown(target,0,0)
dst=target/'fullhd60.mp4';fd=os.open(dst,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o444)
with os.fdopen(fd,'wb') as out,open(tmp,'rb',opener=lambda n,f:os.open(n,f|os.O_NOFOLLOW)) as src:
 for b in iter(lambda:src.read(1<<20),b''):out.write(b)
 out.flush();os.fsync(out.fileno())
os.chown(dst,0,0);os.chmod(dst,0o444)
s=dst.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==s.st_gid==0 and stat.S_IMODE(s.st_mode)==0o444 and s.st_size==%(size)d and digest(dst)==%(sha)r
tmp.unlink();assert not os.path.lexists(tmp)
print('STAGED')
'''
def main():
 raw=r.pinned(LOCAL,SHA256);r.need(len(raw)==SIZE)
 r.pinned(r.CONFIG,'15f687f3db61c013654442404e916b1b2ad7f0d1835e1f30ef10ca80355ceef3',True);r.pinned(r.KEYS,'6b6a9652a16acd478a01b508962452556138ce3a3f0c2cc4584baab58f00c4c6',True)
 rc,info,_=r.bounded(['VBoxManage','showvminfo',r.UUID,'--machinereadable']);r.need(rc==0);r.host_guard(info.decode())
 tmp='/home/vagrant/.fullhd60-'+secrets.token_hex(8)+'.tmp'
 args={'tmp':tmp,'target':TARGET,'size':SIZE,'sha':SHA256,'cleanup_only':False}
 staged=False;err=0
 try:
  rc,_,_=r.bounded(['scp','-q','-o','BatchMode=yes','-o','ConnectTimeout=10','-F',str(r.CONFIG),str(LOCAL),'baseline74:'+tmp],timeout=600)
  if rc==0:
   rc,out,err=r.remote(REMOTE%args,timeout=300);staged=rc==0 and out==b'STAGED\n'
 finally:
  cleanup='NOT_NEEDED'
  if not staged:
   rc2,out2,_=r.remote(REMOTE%dict(args,cleanup_only=True),timeout=60) # temp only, target untouched
   cleanup='TEMP_CLEANED' if rc2==0 and out2==b'CLEANED\n' else 'TEMP_CLEANUP_FAILED'
 result={'status':'STAGED' if staged else 'STAGE_FAILED','target':TARGET+'/fullhd60.mp4','bytes':SIZE,'sha256':SHA256,'remote_stderr_bytes':err,'temp_cleanup':cleanup}
 print(json.dumps(result,sort_keys=True));return 0 if result['status']=='STAGED' else 2
if __name__=='__main__':
 try:sys.exit(main())
 except r.Rejected:print('{"status":"RUNNER_REJECTED"}');sys.exit(2)
