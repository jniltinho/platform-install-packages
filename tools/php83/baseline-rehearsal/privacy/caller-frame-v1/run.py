"""Exclusive native83 only; fresh stage, no application writes, private synthetic sink."""
import io,json,shlex,subprocess,tarfile
from pathlib import Path
import prepare,validate
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[4]
OUT=REPO/'doc/php83/evidence/baseline-rehearsal/privacy/caller-frame-v1'
STAGE='/home/vagrant/privacy-caller-frame-v1';UNIT='privacy-caller-frame-v1'
SSH=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83']
PIN='1c564e6bafa56d03359c3774be6f4c77d0edecabd2075e18556940a56747c8d7'
def main():
 if (OUT/'stage.json').exists() or (OUT/'primary.json').exists():raise ValueError('Fresh phase required')
 blobs,m,patch=prepare.payload(REPO.parent/'platform-install-packages-php83-artifacts/exp14/Rigel-18.20.0-php83-experimental.exp14.zip',prepare.policy.PIN)
 m['php_sha256']=PIN;m['runner_sha256']=prepare.sha(Path(__file__).read_bytes());blobs['manifest.json']=json.dumps(m,sort_keys=True).encode()
 (OUT/'caller.patch').write_bytes(patch)
 tarbytes=io.BytesIO()
 with tarfile.open(fileobj=tarbytes,mode='w') as tar:
  for n,b in blobs.items():
   i=tarfile.TarInfo(n);i.size=len(b);i.mode=0o444;tar.addfile(i,io.BytesIO(b))
 guard='import socket,json,subprocess;assert socket.gethostname()=="kaltura-php83-lab";a=json.loads(subprocess.check_output(["ip","-j","-4","addr"],timeout=10));ips={x.get("local") for i in a for x in i.get("addr_info",[])};assert "192.168.56.83" in ips and not ips.intersection({"192.168.56.20","192.168.56.21","192.168.56.30","192.168.56.74"})'
 p=subprocess.run(SSH+['set -eu; python3 -c '+shlex.quote(guard)+'; test ! -e '+STAGE+'; sudo mkdir -m0755 '+STAGE+'; sudo tar -xf - -C '+STAGE+'; sudo find '+STAGE+' -type d -exec chmod 0555 {} +'],input=tarbytes.getvalue(),capture_output=True,timeout=60)
 (OUT/'stage.exit').write_text(str(p.returncode)+'\n');(OUT/'stage.stderr').write_bytes(p.stderr)
 if p.returncode:raise ValueError('Stage failed')
 pin=prepare.sha(blobs['manifest.json']);(OUT/'stage.json').write_text(json.dumps({'manifest_sha256':pin,'manifest':m},indent=2)+'\n')
 try:
  command='sudo systemd-run --quiet --wait --pipe --collect --unit '+UNIT+' --uid=vagrant -p PrivateNetwork=yes -p PrivateTmp=yes -p ProtectSystem=strict -p ProtectHome=read-only -p NoNewPrivileges=yes -p RuntimeMaxSec=180 python3 -B '+STAGE+'/guest.py '+pin
  p=subprocess.run(SSH+[command],capture_output=True,timeout=200)
  for suffix,data in [('stdout',p.stdout),('stderr',p.stderr),('exit',(str(p.returncode)+'\n').encode())]:(OUT/('primary.'+suffix)).write_bytes(data)
  if p.returncode:raise ValueError('Native run incomplete')
  r=json.loads(p.stdout);(OUT/'primary.json').write_text(json.dumps(r,indent=2)+'\n')
  if r['source_before']!=m['files'] or r['source_after']!=m['files'] or r['runtime_before']!=PIN or r['runtime_after']!=PIN:raise ValueError('Source/runtime drift')
  if [x['variant'] for x in r['processes']]!=['original','overlay','repaired']:raise ValueError('Inventory')
  results=[]
  for row in r['processes']:
   if type(row['exit']) is not int or row['exit']!=0 or any(type(x['exit']) is not int or x['exit']!=0 for x in row['lints']):raise ValueError('Native error')
   body=json.loads(row['stdout'])
   if not body['runtime'].startswith('8.3.'):raise ValueError('Runtime family')
   sources={p:m['files'][row['variant']+'/'+p] for p in prepare.pipeline.PATHS}
   results.append(validate.validate(body,row['variant'],sources))
  (OUT/'validation.json').write_text(json.dumps(results,indent=2)+'\n')
 finally:
  c=subprocess.run(SSH+['sudo systemctl stop '+UNIT+'.service; systemctl is-active '+UNIT+'.service'],capture_output=True,timeout=30)
  (OUT/'cleanup.json').write_text(json.dumps({'exit':c.returncode,'stdout':c.stdout.decode(),'stderr':c.stderr.decode()},indent=2)+'\n')
  if c.returncode not in (3,4) or c.stdout.strip() not in (b'inactive',b'unknown'):raise ValueError('Cleanup failed')
if __name__=='__main__':main()
