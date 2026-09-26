#!/usr/bin/env python3
import json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent/'stage-r1';meta=json.loads(Path('doc/php83/evidence/serialization-contracts/stage-pin.json').read_text());remote=meta['remote_stage']
assert remote=='/home/vagrant/php-serialization-wire-r1'
ssh=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83']
subprocess.run(ssh+["test $(hostname) = kaltura-php83-lab && test $(id -u) = 1000 && mkdir '"+remote+"'"],check=True)
subprocess.run(['scp','-q','-F','/tmp/kaltura-php83-ssh.conf','-r',str(root)+'/.' ,'php83:'+remote+'/'],check=True)
print(json.dumps({'remote':remote,'manifest_sha256':meta['manifest_sha256']}))
