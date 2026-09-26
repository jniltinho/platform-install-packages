#!/usr/bin/env python3
import subprocess,sys,json
from pathlib import Path
mode=sys.argv[1]
if mode not in ['74','83']:raise SystemExit('Wrong lab')
host='kaltura-php74-baseline' if mode=='74' else 'kaltura-php83-lab';alias='baseline74' if mode=='74' else 'php83';conf='/tmp/kaltura-php'+mode+'-ssh.conf'
root=Path(__file__).resolve().parent/'stage-r3';meta=json.loads(Path('doc/php83/evidence/serialization-contracts/r3-stage-pin.json').read_text());remote=meta['remote_stage'];assert remote=='/home/vagrant/php-serialization-wire-cache-r3'
subprocess.run(['ssh','-T','-F',conf,alias,'test $(hostname) = '+host+' && test $(id -u) = 1000 && mkdir '+remote],check=True)
subprocess.run(['scp','-q','-F',conf,'-r',str(root)+'/.' ,alias+':'+remote+'/'],check=True)
print(json.dumps({'lab':alias,'remote':remote,'manifest_sha256':meta['manifest_sha256']}))
