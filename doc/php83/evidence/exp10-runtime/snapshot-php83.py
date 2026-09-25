#!/usr/bin/env python3
"""Owned php83lab read-only native CLI runtime snapshot; no application code."""
import hashlib,json,subprocess,sys
from pathlib import Path
REMOTE=r'''
import hashlib,json,os,re,socket,subprocess
from pathlib import Path
if socket.gethostname()!='kaltura-php83-lab' or os.geteuid()!=1000:raise RuntimeError('Wrong lab')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=30)
php='/usr/bin/php8.3';paths=[Path(php)]+sorted(Path('/usr/lib/php/20230831').glob('*.so'));files={str(p):digest(p) for p in paths};linked={}
for path in paths:
 text=run(['/usr/bin/ldd',str(path)])
 if 'not found' in text:raise RuntimeError('Missing runtime library')
 linked[str(path)]={p:digest(p) for p in sorted(set(re.findall(r'/[^\s()]+',text)))}
runtimes={}
for mode,flags in [('standard',[]),('minimal',['-n'])]:
 version=run([php]+flags+['-v']);ini=run([php]+flags+['--ini']);modules=run([php]+flags+['-m'])
 if not version.startswith('PHP 8.3.'):raise RuntimeError('Wrong runtime')
 configs=sorted(set(re.findall(r'(/[^,\s]+\.ini)',ini)))
 if any(not p.startswith('/etc/php/8.3/') for p in configs):raise RuntimeError('Unexpected INI path')
 runtimes[mode]={'version':version,'ini':ini,'modules':modules,'configuration_sha256':{p:digest(p) for p in configs}}
print(json.dumps({'host':socket.gethostname(),'files':files,'linked_libraries':linked,'runtimes':runtimes},sort_keys=True))
'''
p=Path(sys.argv[1]);assert not p.exists()
command=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83','python3 -']
r=subprocess.run(command,input=REMOTE,capture_output=True,text=True,timeout=120)
if r.returncode:raise RuntimeError('Runtime snapshot failed')
body=json.loads(r.stdout);p.write_text(json.dumps({'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'command':command,'identity':body,'exit':r.returncode,'stderr_sha256':hashlib.sha256(r.stderr.encode()).hexdigest()},indent=2)+'\n')
print(json.dumps({'files':len(body['files']),'modes':len(body['runtimes'])}))
