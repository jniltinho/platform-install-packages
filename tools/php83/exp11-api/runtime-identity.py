#!/usr/bin/env python3
"""Fresh baseline74 interpreter/module/library/config hashes, never app execution."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from artifact import read_pin

REMOTE = r'''
import hashlib,json,os,re,socket,subprocess
from pathlib import Path
if socket.gethostname()!='kaltura-php74-baseline' or os.geteuid()!=1000:
 raise RuntimeError('Unexpected lab identity')
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def run(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=30)
root=Path('/home/vagrant/php-mysql-probe/runtime83')
php74=Path('/usr/bin/php7.4');php83=root/'php8.3'
modules74=sorted(Path('/usr/lib/php/20190902').glob('*.so'))
modules83=sorted(root.glob('*.so'))
required83=['libphp8.3.so','mysqlnd.so','pdo.so','pdo_mysql.so','posix.so','ctype.so','iconv.so']
if any(not (root/name).is_file() for name in required83):raise RuntimeError('Missing copied runtime module')
apache=[Path('/usr/sbin/apache2')]+[Path('/usr/lib/apache2/modules')/name for name in ['libphp7.4.so','mod_mpm_prefork.so','mod_authz_core.so','mod_alias.so','mod_ssl.so','mod_socache_shmcb.so']]
paths=sorted(set([php74,php83]+modules74+modules83+apache))
identities={str(path):{'sha256':digest(path),'resolved_path':str(path.resolve())} for path in paths}
libraries={}
for path in paths:
 listing=run(['/usr/bin/ldd',str(path)])
 if 'not found' in listing:raise RuntimeError('Missing linked library')
 libraries[str(path)]={p:digest(p) for p in sorted(set(re.findall(r'/[^\s()]+',listing)))}
runtimes={}
for label,path,flags in [('php74-standard',php74,[]),('php74-minimal',php74,['-n']),('php83-minimal',php83,['-n'])]:
 command=[str(path)]+flags
 version=run(command+['-v']);ini=run(command+['--ini']);module_list=run(command+['-m'])
 if not version.startswith('PHP '+('7.4.' if label.startswith('php74') else '8.3.')):raise RuntimeError('Unexpected runtime version')
 config_paths=sorted(set(re.findall(r'(/[^,\s]+\.ini)',ini)))
 if any(not p.startswith('/etc/php/7.4/') for p in config_paths):raise RuntimeError('Unexpected configuration path')
 runtimes[label]={'command':command,'version':version,'ini':ini,'modules':module_list,'configuration_sha256':{p:digest(p) for p in config_paths}}
print(json.dumps({'host':socket.gethostname(),'uid':os.geteuid(),'files':identities,'linked_libraries':libraries,'runtimes':runtimes},sort_keys=True))
'''

def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
 pinned=read_pin()
 if a.output.exists():raise RuntimeError('Refusing existing runtime identity evidence')
 command=['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74','python3 -']
 result=subprocess.run(command,input=REMOTE,capture_output=True,text=True,timeout=150)
 if result.returncode:raise RuntimeError('Runtime identity collection failed; no application was run')
 data=json.loads(result.stdout)
 report={'schema':1,'scope':'fresh baseline74 PHP/Apache modules, linked libraries and INI file hashes; no application-body execution',
         'artifact_pin':pinned,'command':command,'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'remote_program_sha256':hashlib.sha256(REMOTE.encode()).hexdigest(),'identity':data,'exit':result.returncode,'stderr_sha256':hashlib.sha256(result.stderr.encode()).hexdigest()}
 a.output.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'files':len(data['files']),'runtime_modes':len(data['runtimes']),'output':str(a.output)}))

if __name__=='__main__':main()
