#!/usr/bin/env python3
"""Exclusive authorized native83 stage and four bounded composition observations."""
import hashlib,io,json,shlex,subprocess,tarfile,tempfile
from pathlib import Path
import fixture,prepare,validate
REPO=Path(__file__).resolve().parents[4]
OUT=REPO/'doc/php83/evidence/criteria-selection'
STAGE='/home/vagrant/php-criteria-composition-v1'
def remote(runtime,command,data=None):
    alias={'74':'baseline74','83':'php83'}[runtime]
    return subprocess.run(['ssh','-T','-F','/tmp/kaltura-php'+runtime+'-ssh.conf',alias,command],input=data,capture_output=True,timeout=120)
def checked(runtime,command,data=None):
    p=remote(runtime,command,data)
    if p.returncode: raise RuntimeError(command+': '+p.stderr.decode())
    return p.stdout.decode()
def runtime_identity(runtime):
    php='/usr/bin/php'+{'74':'7.4','83':'8.3'}[runtime]
    opts=' -d extension=json' if runtime=='74' else ''
    code='echo json_encode(["version"=>PHP_VERSION,"modules"=>get_loaded_extensions(),"extension_dir"=>ini_get("extension_dir"),"ini"=>php_ini_loaded_file()]);'
    info=json.loads(checked(runtime,php+' -n'+opts+' -r '+shlex.quote(code)))
    program='''import hashlib,json,pathlib,subprocess,re
php=PATH
paths={str(pathlib.Path(php).resolve())}
for line in subprocess.check_output(['ldd',php],text=True).splitlines():
 for x in re.findall(r'(/[^\\s()]+)',line):
  if pathlib.Path(x).is_file(): paths.add(str(pathlib.Path(x).resolve()))
EXTRA
print(json.dumps({p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for p in sorted(paths)}))'''.replace('PATH',repr(php)).replace('EXTRA',"paths.add("+repr(info['extension_dir']+'/json.so')+")" if runtime=='74' else '')
    return {'php':info,'files':json.loads(checked(runtime,'python3 -c '+shlex.quote(program)))}
