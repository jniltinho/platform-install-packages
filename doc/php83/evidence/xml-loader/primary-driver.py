import io,tarfile,subprocess,json,os
from pathlib import Path
E=Path('doc/php83/evidence/xml-loader');env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
def run(name,cmd,stdin=None):
 for suffix in ['stdout','stderr','exit']:
  if (E/(name+'.'+suffix)).exists():raise RuntimeError('existing')
 r=subprocess.run(cmd,input=stdin,capture_output=True,timeout=1100,env=env)
 (E/(name+'.stdout')).write_bytes(r.stdout);(E/(name+'.stderr')).write_bytes(r.stderr);(E/(name+'.exit')).write_text(str(r.returncode)+'\n')
 print(name,r.returncode,flush=True);return r
b=io.BytesIO()
with tarfile.open(fileobj=b,mode='w') as t:
 for p in sorted(Path('/tmp/php-xml-loader-prep-r1').iterdir()):t.add(p,arcname=p.name)
for rt,conf,alias,host,helper in [
 ('74','/tmp/kaltura-php74-ssh.conf','baseline74','kaltura-php74-baseline','tools/php83/exp11-api/runtime-identity.py'),
 ('83','/tmp/kaltura-php83-ssh.conf','php83','kaltura-php83-lab','doc/php83/evidence/exp10-runtime/snapshot-php83.py')]:
 cmd=['ssh','-T','-F',conf,alias,'set -eu; test "$(hostname)" = '+host+'; test "$(id -u)" = 1000; test ! -e /home/vagrant/php-xml-loader-r1; mkdir /home/vagrant/php-xml-loader-r1; tar -xf - -C /home/vagrant/php-xml-loader-r1; chmod 0444 /home/vagrant/php-xml-loader-r1/*; chmod 0555 /home/vagrant/php-xml-loader-r1']
 assert run('stage'+rt,cmd,b.getvalue()).returncode==0
 assert run('runtime'+rt+'-before',['python3',helper,str(E/('runtime'+rt+'-before.json'))]).returncode==0
 r=run('primary'+rt,['python3','tools/php83/xml-loader/collect.py',rt,'/tmp/php-xml-loader-prep-r1',str(E/('primary'+rt+'.json'))])
 assert run('runtime'+rt+'-after',['python3',helper,str(E/('runtime'+rt+'-after.json'))]).returncode==0
