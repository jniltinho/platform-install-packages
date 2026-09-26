#!/usr/bin/env python3
"""Coordinator-granted exclusive83, synthetic class files only; never deploy application."""
import hashlib,io,json,shlex,subprocess,tarfile
from pathlib import Path
import prepare,compare
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'doc/php83/evidence/baseline-rehearsal/privacy'
STAGE='/home/vagrant/php83-privacy-synthetic-r1';SSH=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83']
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
 if any((OUT/name).exists() for name in ['native83-primary.json','native83-primary.exit','native83-stage.json']):raise ValueError('Refuse overwrite')
 deps=['vendor/ZendFramework/library/Zend/Log/Formatter/Simple.php','vendor/ZendFramework/library/Zend/Log/Formatter/Interface.php']
 original=prepare.archive(ROOT.parent/'platform-install-packages-php83-artifacts/exp12/Rigel-18.20.0-php83-experimental.exp12.zip',prepare.EXP12,prepare.TARGETS+deps)
 inventory=json.loads((ROOT/'doc/php83/evidence/return-contracts/native-primary-runtime-before.json').read_text())['identity']
 expected_php=inventory['files']['/usr/bin/php8.3']
 blobs={}
 for path,raw in original.items():
  blobs['original/'+path]=raw;blobs['privacy/'+path]=prepare.transform(path,raw) if path in prepare.TARGETS else raw
 blobs['probe.php']=(HERE/'probe.php').read_bytes();blobs['native83_guest.py']=(HERE/'native83_guest.py').read_bytes()
 manifest={'files':{p:sha(raw) for p,raw in blobs.items()},'expected_php_sha256':expected_php,'status':'SYNTHETIC_ONLY_NOT_APPLICATION_DEPLOYMENT','source_base':'unmodified exp12 versus exp12 plus privacy; original label is pair-control, not upstream ZIP','base_archive_sha256':prepare.EXP12}
 manifest_bytes=json.dumps(manifest,sort_keys=True).encode();manifest_sha=sha(manifest_bytes);blobs['manifest.json']=manifest_bytes
 archive=io.BytesIO()
 with tarfile.open(fileobj=archive,mode='w') as tar:
  for name,raw in blobs.items():
   info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o444;tar.addfile(info,io.BytesIO(raw))
 guard='''import socket,json,subprocess
assert socket.gethostname()=="kaltura-php83-lab"
a=json.loads(subprocess.check_output(["ip","-j","-4","addr"],timeout=10))
ips={x.get("local") for link in a for x in link.get("addr_info",[])}
assert "192.168.56.83" in ips and not ips.intersection({"192.168.56.20","192.168.56.21","192.168.56.30","192.168.56.74"})
'''
 command='set -eu; python3 -c '+shlex.quote(guard)+'; test ! -e '+STAGE+'; sudo mkdir -m0755 '+STAGE+'; sudo tar -xf - -C '+STAGE+'; sudo find '+STAGE+' -type f -exec chmod 0444 {} +'
 p=subprocess.run(SSH+[command],input=archive.getvalue(),capture_output=True,timeout=60)
 if p.returncode:raise ValueError('Fresh safe staging failed')
 (OUT/'native83-stage.json').write_text(json.dumps({'stage':STAGE,'manifest_sha256':manifest_sha,'manifest':manifest,'runner_sha256':sha(Path(__file__).read_bytes())},indent=2)+'\n')
 command='sudo systemd-run --quiet --wait --pipe --collect --unit php83-privacy-synthetic-r1 --uid=vagrant -p PrivateNetwork=yes -p PrivateTmp=yes -p ProtectSystem=strict -p ProtectHome=read-only -p NoNewPrivileges=yes -p RuntimeMaxSec=120 python3 -B '+STAGE+'/native83_guest.py '+manifest_sha
 p=subprocess.run(SSH+[command],capture_output=True,timeout=150)
 (OUT/'native83-primary.exit').write_text(str(p.returncode)+'\n');(OUT/'native83-primary.stderr').write_bytes(p.stderr)
 if p.returncode:raise ValueError('Synthetic native runner failed')
 observation=json.loads(p.stdout)
 (OUT/'native83-primary.json').write_text(json.dumps(observation,indent=2)+'\n')
 if len(observation['processes'])!=2:raise ValueError('Native process count')
 reports=[]
 for i,variant in enumerate(['original','privacy']):
  row=observation['processes'][i]
  if row['variant']!=variant or row['exit'] or any(x['exit'] for x in row['lint']):raise ValueError('Native execution failed')
  reports.append(json.loads(row['stdout']))
 expected=[]
 for variant in ['original','privacy']:
  expected.append({name:manifest['files'][variant+'/'+path] for name,path in zip(['log','front','dispatcher','formatter','formatter_interface'],prepare.TARGETS+deps)})
 result=compare.compare(*reports,'8.3',*expected)
 (OUT/'native83-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
