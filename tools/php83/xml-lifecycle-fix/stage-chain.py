import hashlib,io,json,subprocess,tarfile,sys
from pathlib import Path
stage=Path('/tmp/php-xml-lifecycle-fix-chain-prep-r1');prefix=Path(sys.argv[1]);mb=(stage/'identities.json').read_bytes();m=json.loads(mb)
for p,h in m['files'].items():
 if hashlib.sha256((stage/p).read_bytes()).hexdigest()!=h:raise ValueError('Local drift')
for ext in ['command.json','stdout','stderr','exit']:
 if Path(str(prefix)+'.'+ext).exists():raise ValueError('Refuse overwrite')
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w') as tar:
 for p in sorted(stage.iterdir()):tar.add(p,arcname=p.name)
base='/home/vagrant/php-xml-lifecycle-fix-chain-r1';cmd=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83',f'set -eu; test "$(hostname)" = kaltura-php83-lab; test "$(id -u)" = 1000; test ! -e {base}; mkdir {base}; tar -xf - -C {base}; find {base} -type f -exec chmod 0444 {{}} +; find {base} -type d -exec chmod 0555 {{}} +']
r=subprocess.run(cmd,input=buf.getvalue(),capture_output=True,timeout=60)
for ext,b in [('command.json',(json.dumps(cmd)+'\n').encode()),('stdout',r.stdout),('stderr',r.stderr),('exit',(str(r.returncode)+'\n').encode())]:Path(str(prefix)+'.'+ext).write_bytes(b)
print(json.dumps({'stage_exit':r.returncode,'manifest_sha256':hashlib.sha256(mb).hexdigest()}));sys.exit(r.returncode)
