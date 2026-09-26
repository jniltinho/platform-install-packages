#!/usr/bin/env python3
"""Stage reviewed local fixture only; requires coordinator's exclusive VM grant."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
raw=(ROOT/'doc/php83/evidence/exp13-xml/preparation.json').read_bytes()
if hashlib.sha256(raw).hexdigest()!='30b70f69246cf542853b79dc3fb3e2f175ce25e5810eb813d70f0d5daa99a5c7':raise ValueError('Preparation identity')
p=json.loads(raw)
ssh=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83']
subprocess.run(ssh+['test "$(hostname)" = kaltura-php83-lab && test "$(id -u)" = 1000'],check=True)
for data in p['stages'].values():
 local=ROOT/data['local'];raw=(local/'identities.json').read_bytes()
 if hashlib.sha256(raw).hexdigest()!=data['manifest_sha256']:raise ValueError('Manifest drift')
 for name,digest in json.loads(raw)['files'].items():
  if hashlib.sha256((local/name).read_bytes()).hexdigest()!=digest:raise ValueError('Source drift')
 if data['remote'] not in ['/home/vagrant/php-exp13-xml-matrix-r1','/home/vagrant/php-exp13-xml-chain-r1']:raise ValueError('Forbidden destination')
 subprocess.run(ssh+['mkdir '+data['remote']],check=True)
 subprocess.run(['scp','-q','-F','/tmp/kaltura-php83-ssh.conf','-r',str(local)+'/.','php83:'+data['remote']+'/'],check=True)
print('STAGED_ONLY_NO_PHP')
