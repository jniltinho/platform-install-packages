#!/usr/bin/env python3
"""Fresh immutable stage; invoke only after exclusive native83 grant."""
import json,subprocess
import common as c
p=c.preparation();directory=c.ROOT/p['local'];raw=(directory/'identities.json').read_bytes();c.need(c.sha(raw)==p['manifest_sha256'],'Manifest drift')
for name,digest in json.loads(raw)['files'].items():c.need(c.sha((directory/name).read_bytes())==digest,'Source drift')
ssh=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83']
subprocess.run(ssh+['test "$(hostname)" = kaltura-php83-lab && test "$(id -u)" = 1000 && mkdir '+c.REMOTE],check=True)
subprocess.run(['scp','-q','-F','/tmp/kaltura-php83-ssh.conf','-r',str(directory)+'/.','php83:'+c.REMOTE+'/'],check=True)
print('STAGED_NO_PHP_EXECUTION')
