"""One isolated native83 pipeline observation, no product writes or application."""
import argparse,hashlib,io,json,shlex,subprocess,tarfile
from pathlib import Path
import prepare,validate
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[4]
OUT=REPO/'doc/php83/evidence/baseline-rehearsal/privacy/pipeline'
STAGE='/home/vagrant/php83-privacy-pipeline-r1';SSH=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83']
sha=lambda b:hashlib.sha256(b).hexdigest()
def snapshot(label):
 output=OUT/(label+'.json')
 r=subprocess.run(['python3',str(REPO/'tools/php83/exp13-api/runtime83-identity.py'),str(output)],capture_output=True,timeout=120)
 if r.returncode:raise ValueError('Runtime snapshot failed')
 return json.loads(output.read_text())
def main(label,reuse=False):
 if label not in ['primary','claude']:raise ValueError('Known phase only')
 targets=[OUT/(label+s) for s in ['.json','.stdout','.stderr','.exit','-before.json','-after.json','-validation.json','-cleanup.json']]
 if any(p.exists() for p in targets):raise ValueError('Existing evidence')
 before=snapshot(label+'-before');unit=None
 try:
  if not reuse:
   local=Path('/tmp/php83-privacy-pipeline-native-r1')
   m=prepare.prepare(Path('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip'),local)
   (local/'guest.py').write_bytes((HERE/'guest.py').read_bytes())
   m['files']['guest.py']=sha((local/'guest.py').read_bytes())
   m['php_sha256']=before['identity']['files']['/usr/bin/php8.3']
   raw=json.dumps(m,sort_keys=True).encode();pin=sha(raw);(local/'manifest.json').write_bytes(raw)
   buff=io.BytesIO()
   with tarfile.open(fileobj=buff,mode='w') as tar:
    for p in local.rglob('*'):
     if p.is_file():
      data=p.read_bytes();i=tarfile.TarInfo(str(p.relative_to(local)));i.mode=0o444;i.size=len(data);tar.addfile(i,io.BytesIO(data))
   guard="""import socket,json,subprocess
assert socket.gethostname()=='kaltura-php83-lab'
ips={x.get('local') for link in json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10)) for x in link.get('addr_info',[])}
assert '192.168.56.83' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.74'})
"""
   cmd='set -eu; python3 -c '+shlex.quote(guard)+'; test ! -e '+STAGE+'; sudo mkdir -m0755 '+STAGE+'; sudo tar -xf - -C '+STAGE
   r=subprocess.run(SSH+[cmd],input=buff.getvalue(),capture_output=True,timeout=60)
   if r.returncode:raise ValueError('Fresh stage failed')
   (OUT/'stage.json').write_text(json.dumps({'manifest':m,'manifest_sha256':pin,'runner_sha256':sha(Path(__file__).read_bytes())},indent=2)+'\n')
  else:
   stage=json.loads((OUT/'stage.json').read_text());m=stage['manifest'];pin=stage['manifest_sha256']
   if stage['runner_sha256']!=sha(Path(__file__).read_bytes()) or m['files']['guest.py']!=sha((HERE/'guest.py').read_bytes()) or m['files']['probe.php']!=sha((HERE/'probe.php').read_bytes()):raise ValueError('Frozen harness drift')
  if m['php_sha256']!=before['identity']['files']['/usr/bin/php8.3']:raise ValueError('Baseline runtime drift')
  unit='php83-privacy-pipeline-r1-'+label
  cmd='sudo systemd-run --quiet --wait --pipe --collect --unit '+unit+' --uid=vagrant -p PrivateNetwork=yes -p PrivateTmp=yes -p ProtectSystem=strict -p ProtectHome=read-only -p NoNewPrivileges=yes -p RuntimeMaxSec=120 python3 -B '+STAGE+'/guest.py '+pin
  r=subprocess.run(SSH+[cmd],capture_output=True,timeout=150)
  for suffix,data in [('.stdout',r.stdout),('.stderr',r.stderr),('.exit',(str(r.returncode)+'\n').encode())]:(OUT/(label+suffix)).write_bytes(data)
  if r.returncode:raise ValueError('Native observation failed')
  report=json.loads(r.stdout);(OUT/(label+'.json')).write_text(json.dumps(report,indent=2)+'\n')
  if len(report['lints'])!=12 or report['exit']!=0 or any(x['exit'] for x in report['lints']):raise ValueError('PHP execution failure')
  result=validate.validate(json.loads(report['stdout']),m)
  (OUT/(label+'-validation.json')).write_text(json.dumps(result,indent=2)+'\n')
  print(json.dumps(result))
 finally:
  if unit is not None:
   cleanup=subprocess.run(SSH+['systemctl is-active '+unit],capture_output=True,text=True,timeout=15)
   state=cleanup.stdout.strip();(OUT/(label+'-cleanup.json')).write_text(json.dumps({'unit':unit,'state':state,'exit':cleanup.returncode,'inactive':state in ['inactive','unknown']})+'\n')
  after=snapshot(label+'-after')
  if before['identity']!=after['identity']:raise ValueError('Native runtime changed')
  if unit is not None and state not in ['inactive','unknown']:raise ValueError('Unit remains active')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['primary','claude']);p.add_argument('--reuse',action='store_true');a=p.parse_args();main(a.phase,a.reuse)
