"""Coordinator-granted lab74 installation only; never auth. No raw remote error export."""
import base64,hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent; REPO=HERE.parents[4]
OUT=REPO/'doc/php83/evidence/baseline-rehearsal/privacy/application-overlay-v1'
LOCAL=Path('/tmp/php83-application-overlay-v1-r2-prepared')
REMOTE='/home/vagrant/privacy-application-overlay-v1'
def sha(b):return hashlib.sha256(b).hexdigest()
def payload():
 freeze=json.loads((OUT/'prep-r2-freeze.json').read_text())
 for p,h in freeze['files'].items():
  if sha((REPO/p).read_bytes())!=h:raise ValueError('Reviewed source drift')
 m=(LOCAL/'manifest.json').read_bytes(); manifest=json.loads(m)
 if manifest!=json.loads((OUT/'preparation-r2.json').read_text()):raise ValueError('Reviewed preparation drift')
 blobs={'manifest.json':base64.b64encode(m).decode()}
 for name,pin in manifest['files'].items():
  p=Path(name)
  if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe member')
  b=(LOCAL/p).read_bytes()
  if sha(b)!=pin:raise ValueError('Stage drift')
  blobs[name]=base64.b64encode(b).decode()
 return {'blobs':blobs,'pin':sha(m)}
GUEST=r'''
import base64,hashlib,json,os,socket,stat,subprocess
from pathlib import Path
assert os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline'
a=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10));ips={v.get('local') for x in a for v in x.get('addr_info',[])}
assert '192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'})
root=Path('/home/vagrant/privacy-application-overlay-v1');private=Path('/var/lib/kaltura-php83-lab/privacy-overlay-v1-launch')
assert not root.exists() and not root.is_symlink() and not private.exists() and not private.is_symlink()
for p in private.parents:
 if p.exists():assert not p.is_symlink() and p.stat().st_uid==0 and not p.stat().st_mode&0o022
private.mkdir(parents=True,mode=0o700);os.chmod(private,0o700)
root.mkdir(mode=0o700)
for name,encoded in DATA['blobs'].items():
 p=root/name;assert not Path(name).is_absolute() and '..' not in Path(name).parts
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(base64.b64decode(encoded,validate=True));p.chmod(0o444)
for p in sorted([p for p in root.rglob('*') if p.is_dir()],reverse=True):p.chmod(0o555)
root.chmod(0o555)
assert hashlib.sha256((root/'manifest.json').read_bytes()).hexdigest()==DATA['pin']
# Native recipe has bounded subprocesses and rollback. Its private stderr is never printed.
try:
 p=subprocess.run(['python3',str(root/'guest.py'),DATA['pin']],capture_output=True,timeout=1200)
 for name,data in [('stdout',p.stdout),('stderr',p.stderr)]:
  fd=os.open(private/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 report={'exit':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest(),'stderr_bytes':len(p.stderr),'manifest_sha256':DATA['pin']}
 try:report['receipt']=json.loads(p.stdout)
 except ValueError:report['status']='INCOMPLETE_NO_PUBLIC_RECEIPT'
 print(json.dumps(report))
except subprocess.TimeoutExpired:
 print(json.dumps({'status':'INCOMPLETE_TIMEOUT_MANUAL_RECOVERY_NO_AUTH','manifest_sha256':DATA['pin']}))
'''
def main():
 target=OUT/'application-primary.json'
 if target.exists() or (OUT/'application-primary.exit').exists():raise ValueError('Never overwrite')
 data=payload();code=('DATA='+repr(data)+'\n'+GUEST).encode()
 try:p=subprocess.run(['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74','sudo -n python3 -'],input=code,capture_output=True,timeout=1250)
 except subprocess.TimeoutExpired:
  target.write_text(json.dumps({'status':'INCOMPLETE_SSH_TIMEOUT_REMOTE_STATE_UNKNOWN_NO_AUTH'})+'\n');raise
 (OUT/'application-primary.exit').write_text(str(p.returncode)+'\n')
 (OUT/'application-primary-stderr-sha256.txt').write_text(sha(p.stderr)+'\n')
 if p.returncode:raise ValueError('Remote failure: private diagnostics not exported')
 report=json.loads(p.stdout);report['launcher_sha256']=sha(code)
 target.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'exit':report.get('exit'),'status':report.get('receipt',report).get('status')}))
if __name__=='__main__':main()
