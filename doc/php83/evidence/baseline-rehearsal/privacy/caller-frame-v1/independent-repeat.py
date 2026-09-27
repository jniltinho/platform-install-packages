"""Repeat frozen synthetic guest, exact same manifest/probe/source/runtime; no app."""
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
STAGE='/home/vagrant/privacy-caller-frame-v1';UNIT='privacy-caller-frame-v1-repeat'
SSH=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83']
if (R/'repeat.json').exists():raise ValueError('Never overwrite repeat')
pin=json.loads((R/'stage.json').read_text())['manifest_sha256']
if len(pin)!=64 or any(c not in '0123456789abcdef' for c in pin):raise ValueError('Pin')
try:
 cmd='sudo systemd-run --quiet --wait --pipe --collect --unit '+UNIT+' --uid=vagrant -p PrivateNetwork=yes -p PrivateTmp=yes -p ProtectSystem=strict -p ProtectHome=read-only -p NoNewPrivileges=yes -p RuntimeMaxSec=180 python3 -B '+STAGE+'/guest.py '+pin
 p=subprocess.run(SSH+[cmd],capture_output=True,timeout=200)
 for ext,data in [('exit',(str(p.returncode)+'\n').encode()),('stdout',p.stdout),('stderr',p.stderr)]:(R/('repeat.'+ext)).write_bytes(data)
 if p.returncode:raise ValueError('Repeat incomplete')
 d=json.loads(p.stdout);(R/'repeat.json').write_text(json.dumps(d,indent=2)+'\n')
 if d!=json.loads((R/'primary.json').read_text()):raise ValueError('Repeated typed report differs')
 if p.stdout!=(R/'primary.stdout').read_bytes() or p.stderr!=(R/'primary.stderr').read_bytes():raise ValueError('Native repeat channel differs')
 print('Frozen synthetic 3-process repeat exactly matches primary stdout/stderr and typed report; no whole privacy acceptance.')
finally:
 p=subprocess.run(SSH+['sudo systemctl stop '+UNIT+'.service; systemctl is-active '+UNIT+'.service'],capture_output=True,timeout=30)
 (R/'repeat-cleanup.json').write_text(json.dumps({'exit':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()},indent=2)+'\n')
 if p.returncode not in (3,4) or p.stdout.strip() not in (b'inactive',b'unknown'):raise ValueError('Owned repeat unit not inactive')
