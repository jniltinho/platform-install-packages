"""Fresh immutable stage for approved synthetic nonce/USER. Never prints secret-bearing errors."""
import hashlib,io,json,secrets,shlex,subprocess,tarfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
OUT=ROOT/'doc/php83/evidence/baseline-rehearsal/privacy/nonce-overlay-v1'
STAGE='/home/vagrant/privacy-nonce-overlay-v1'
SSH=['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74']
FILES=['baseline-protocol/guarded_http.py','baseline-protocol/deadline_transport.py','baseline-api/transport.py','baseline-api/protocol.py','baseline-rehearsal/untimed_driver.py','baseline-rehearsal/privacy/append-window-v1/scan.py','baseline-rehearsal/privacy/journal-window-v1/scan.py','baseline-rehearsal/privacy/nonce-overlay-v1/guest.py']
def sha(b):return hashlib.sha256(b).hexdigest()
def run(command,data=None,timeout=60):return subprocess.run(SSH+[command],input=data,capture_output=True,timeout=timeout)
def check_public(value):
 if type(value) is dict:
  if set(value)&{'secret','password','ks','token','raw_body','response','canary','nonce','user_id'}:raise ValueError('Forbidden public field')
  for v in value.values():check_public(v)
 elif type(value) is list:
  for v in value:check_public(v)
def public_rows(raw,partial=False):
 lines=raw.split(b'\n')
 if partial and lines[-1]:lines=lines[:-1]
 rows=[json.loads(line) for line in lines if line.strip()];check_public(rows);return rows
def main():
 if (OUT/'primary.json').exists() or (OUT/'primary.exit').exists():raise ValueError('Never overwrite')
 if 'PENDING_REVIEW' in (HERE/'guest.py').read_text():raise ValueError('Journal contract pending; no SSH')
 freeze=json.loads((OUT/'freeze.json').read_text())
 for n,h in freeze.items():
  if sha((ROOT/n).read_bytes())!=h:raise ValueError('Reviewed source drift; no SSH')
 blobs={'tools/php83/'+n:(ROOT/'tools/php83'/n).read_bytes() for n in FILES}
 manifest={n:sha(b) for n,b in blobs.items()};unit='privacy-nonce-'+secrets.token_hex(4)
 archive=io.BytesIO()
 with tarfile.open(fileobj=archive,mode='w') as tar:
  for n,b in blobs.items():
   info=tarfile.TarInfo(n);info.size=len(b);info.mode=0o444;info.uid=0;info.gid=0;tar.addfile(info,io.BytesIO(b))
 stage=run('set -eu; test "$(hostname)" = kaltura-php74-baseline; test ! -e '+STAGE+'; sudo mkdir -m 0755 '+STAGE+'; sudo tar --no-same-permissions -xf - -C '+STAGE+'; sudo find '+STAGE+' -type f -exec chmod 0444 {} +',archive.getvalue())
 if stage.returncode:raise ValueError('Stage failure; no raw output exported')
 def verify():
  code='import hashlib,json,os,stat\nfrom pathlib import Path\nroot=Path('+repr(STAGE)+')\nexpected='+repr(manifest)+'\nfor name,h in expected.items():\n p=root/name;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_uid==0 and not s.st_mode&0o222 and hashlib.sha256(p.read_bytes()).hexdigest()==h\nprint("PINNED")'
  p=run('sudo -n python3 -',code.encode())
  if p.returncode or p.stdout.strip()!=b'PINNED':raise ValueError('Stage pin failed')
 verify();(OUT/'stage.json').write_text(json.dumps({'stage':STAGE,'unit':unit,'files':manifest},indent=2)+'\n')
 command='sudo -n systemd-run --quiet --wait --pipe --collect --unit '+unit+' -p IPAddressDeny=any -p IPAddressAllow=localhost -p IPAddressAllow=192.168.56.74/32 -p NoNewPrivileges=yes -p ProtectSystem=strict -p ProtectHome=read-only -p PrivateTmp=yes -p ReadWritePaths=/opt/kaltura/app/api_v3/web -p RuntimeMaxSec=360 python3 -B '+STAGE+'/tools/php83/baseline-rehearsal/privacy/nonce-overlay-v1/guest.py '+unit
 try:
  timed_out=False
  try:p=run(command,timeout=390)
  except subprocess.TimeoutExpired as error:
   timed_out=True;p=subprocess.CompletedProcess(command,124,error.stdout or b'',error.stderr or b'')
  (OUT/'primary.exit').write_text(str(p.returncode)+'\n')
  rows=public_rows(p.stdout,partial=timed_out)
  (OUT/'primary.json').write_text(json.dumps({'exit':p.returncode,'phase_receipts':rows,'source_files':manifest,'stderr_bytes':len(p.stderr),'timed_out':timed_out,'timeout_status':'INCOMPLETE_POSSIBLE_REQUEST_SENT' if timed_out else None},indent=2)+'\n')
  verify();print(json.dumps({'exit':p.returncode,'status':rows[-1]['status'] if rows else 'INCOMPLETE_EMPTY'}))
 finally:
  q=run('sudo -n systemctl stop '+unit+'.service',timeout=30)
  q=run('systemctl is-active '+unit+'.service',timeout=10)
  (OUT/'cleanup.json').write_text(json.dumps({'exit':q.returncode,'state':q.stdout.decode().strip()},indent=2)+'\n')
  if q.stdout.strip() not in [b'inactive',b'unknown']:raise ValueError('Own unit cleanup incomplete')
if __name__=='__main__':main()
