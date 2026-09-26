"""Authorized lab-only runner, invoke only after independent review and exclusive74."""
import hashlib,importlib.util,io,json,shlex,subprocess,tarfile
from pathlib import Path
import prepare,validate
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[4]
OUT=REPO/'doc/php83/evidence/baseline-rehearsal/privacy/trace-policy-v1'
STAGE='/home/vagrant/privacy-trace-policy-v1';UNIT='privacy-trace-policy-v1'
SSH=['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74']
PINS={'/usr/bin/php7.4':'5ed671ea6fe1cfb9f6e7dde2b259ec5821d7e0eae95c31d103d5468f2e617c59','/usr/lib/php/20190902/json.so':'80efe3d6f144e717b9fcef7750f81736cbd55c1e91041d24be58e70c18199343','/home/vagrant/php-mysql-probe/runtime83/php8.3':'1c564e6bafa56d03359c3774be6f4c77d0edecabd2075e18556940a56747c8d7'}
s=importlib.util.spec_from_file_location('pipeline_original',HERE.parent/'pipeline/prepare.py');pipeline=importlib.util.module_from_spec(s);s.loader.exec_module(pipeline)
def sha(b):return hashlib.sha256(b).hexdigest()
def payload():
 paths=list(dict.fromkeys(list(pipeline.PATHS)+prepare.TARGETS))
 original=prepare.old.archive('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip',prepare.old.UPSTREAM,paths)
 candidate=prepare.old.archive(REPO.parent/'platform-install-packages-php83-artifacts/exp14/Rigel-18.20.0-php83-experimental.exp14.zip',prepare.PIN,paths)
 blobs={}
 for name,files,policy in [('original74',original,False),('policy74',original,True),('original83',candidate,False),('policy83',candidate,True)]:
  for path,data in files.items():blobs[name+'/'+path]=prepare.transform(path,data) if policy and path in prepare.TARGETS else data
 for name in ['probe.php','guest.py']:blobs[name]=(HERE/name).read_bytes()
 m={'files':{n:sha(b) for n,b in blobs.items()},'runtime':PINS,'status':'SYNTHETIC_NOT_APPLICATION_OVERLAY','original':prepare.old.UPSTREAM,'exp14':prepare.PIN}
 blobs['manifest.json']=json.dumps(m,sort_keys=True).encode();return blobs,m

def main():
 if (OUT/'primary.json').exists() or (OUT/'stage.json').exists():raise ValueError('Never overwrite')
 blobs,m=payload();tarbytes=io.BytesIO()
 with tarfile.open(fileobj=tarbytes,mode='w') as tar:
  for n,b in blobs.items():
   i=tarfile.TarInfo(n);i.size=len(b);i.mode=0o444;tar.addfile(i,io.BytesIO(b))
 guard='import socket,json,subprocess;assert socket.gethostname()=="kaltura-php74-baseline";a=json.loads(subprocess.check_output(["ip","-j","-4","addr"],timeout=10));ips={x.get("local") for i in a for x in i.get("addr_info",[])};assert "192.168.56.74" in ips and not ips.intersection({"192.168.56.20","192.168.56.21","192.168.56.30","192.168.56.83"})'
 command='set -eu; python3 -c '+shlex.quote(guard)+'; test ! -e '+STAGE+'; sudo mkdir -m0755 '+STAGE+'; sudo tar -xf - -C '+STAGE
 p=subprocess.run(SSH+[command],input=tarbytes.getvalue(),capture_output=True,timeout=60)
 (OUT/'stage.exit').write_text(str(p.returncode)+'\n')
 if p.returncode:raise ValueError('Stage failed')
 pin=sha(blobs['manifest.json']);(OUT/'stage.json').write_text(json.dumps({'manifest_sha256':pin,'manifest':m,'runner_sha256':sha(Path(__file__).read_bytes())},indent=2)+'\n')
 try:
  command='sudo systemd-run --quiet --wait --pipe --collect --unit '+UNIT+' --uid=vagrant -p PrivateNetwork=yes -p PrivateTmp=yes -p ProtectSystem=strict -p ProtectHome=read-only -p NoNewPrivileges=yes -p RuntimeMaxSec=180 python3 -B '+STAGE+'/guest.py '+pin
  p=subprocess.run(SSH+[command],capture_output=True,timeout=200)
  for suffix,data in [('stdout',p.stdout),('stderr',p.stderr),('exit',(str(p.returncode)+'\n').encode())]:(OUT/('primary.'+suffix)).write_bytes(data)
  if p.returncode:raise ValueError('Incomplete native run')
  report=json.loads(p.stdout);(OUT/'primary.json').write_text(json.dumps(report,indent=2)+'\n')
  if report['source_before']!=m['files'] or report['source_after']!=m['files'] or report['runtime_before']!=PINS or report['runtime_after']!=PINS:raise ValueError('Source/runtime drift')
  if [r['variant'] for r in report['processes']]!=['original74','policy74','original83','policy83']:raise ValueError('Modes')
  results=[]
  for row in report['processes']:
   if row['exit'] or any(x['exit'] for x in row['lints']):raise ValueError('Native error')
   expected={path:m['files'][row['variant']+'/'+path] for path in pipeline.PATHS}
   results.append(validate.validate(json.loads(row['stdout']),row['variant'].startswith('policy'),expected))
  (OUT/'validation.json').write_text(json.dumps(results,indent=2)+'\n')
 finally:
  cleanup=subprocess.run(SSH+['sudo systemctl stop '+UNIT+'.service; systemctl is-active '+UNIT+'.service'],capture_output=True,timeout=30)
  record={'exit':cleanup.returncode,'stdout':cleanup.stdout.decode(),'stderr':cleanup.stderr.decode()}
  (OUT/'cleanup.json').write_text(json.dumps(record,indent=2)+'\n')
  if cleanup.returncode not in (3,4) or cleanup.stdout.strip() not in (b'inactive',b'unknown'):raise ValueError('Owned unit cleanup failed')
if __name__=='__main__':main()
