"""Fixed root-only 120-second lab service. No native command escapes supervision."""
import hashlib
import grp
import pwd
import socket
import subprocess
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import uuid

BASE=Path('/usr/local/lib/kaltura-nginx-lab')
MANIFEST=Path('/etc/kaltura-nginx-lab/manifest.json')
CONFIG=Path('/opt/kaltura/nginx/conf/kaltura-nginx.conf')
SOCKET=Path('/run/kaltura-php83-nginx-log')
LOGS=Path('/var/lib/kaltura-php83-nginx-log-sink')
BINARY=Path('/opt/kaltura/nginx/sbin/nginx')
ADAPTER_PIN='090c5e8faaf9a0fc468ad31994b2077cc8b50858b3577a0d1c7e327433be1af5'
SANITIZER_PIN='b44f3cdc8c38c6c00a1ef099c0a4742650b3b209e70814924115c1c5f146fffb'
BINARY_PIN='1a995dddd470f013258b1890cfc7c9e3b10c344461eb085de6b2ef8f991faec0'

def identity(st):return (st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_gid,st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
def trusted(path,directory=False):
    p=Path(path)
    if not p.is_absolute() or p.resolve()!=p:raise ValueError('TRUST')
    for item in (p,*p.parents):
        st=item.lstat()
        if st.st_uid!=0 or st.st_mode&0o022 or stat.S_ISLNK(st.st_mode):raise ValueError('TRUST')
        if any(x.startswith('system.posix_acl') for x in os.listxattr(item,follow_symlinks=False)):raise ValueError('ACL')
        if item!=p or directory:
            if not stat.S_ISDIR(st.st_mode):raise ValueError('DIRECTORY')
        elif not stat.S_ISREG(st.st_mode) or st.st_nlink!=1:raise ValueError('FILE')
def read(path,pin=None,limit=8*1024*1024):
    trusted(path)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    with os.fdopen(fd,'rb') as stream:
        before=os.fstat(stream.fileno());raw=stream.read(limit+1)
        if len(raw)>limit or identity(before)!=identity(os.fstat(stream.fileno())) or identity(before)!=identity(os.stat(path,follow_symlinks=False)):raise ValueError('CHANGED')
    if pin is not None and hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('PIN')
    return raw

def validate_contract(contract):
    if type(contract) is not dict or set(contract)!={'schema','seconds','socket_gid','files'}:raise ValueError('CONTRACT')
    if type(contract['schema']) is not int or contract['schema']!=1 or type(contract['seconds']) is not int or contract['seconds']!=120:raise ValueError('LIFETIME')
    if type(contract['socket_gid']) is not int or contract['socket_gid']!=7373:raise ValueError('GROUP')
    files=contract['files']
    if type(files) is not dict or not 4<=len(files)<=256:raise ValueError('FILES')
    required={str(BINARY):BINARY_PIN,str(BASE/'lab_adapter.py'):ADAPTER_PIN,str(BASE/'sanitizer.py'):SANITIZER_PIN}
    if any(files.get(path)!=pin for path,pin in required.items()) or str(CONFIG) not in files:raise ValueError('REQUIRED_PIN')
    for path,pin in files.items():
        p=Path(path)
        if type(pin) is not str or len(pin)!=64 or any(x not in '0123456789abcdef' for x in pin):raise ValueError('PIN')
        if path not in required and not (p.parent==CONFIG.parent and p.name not in ('.','..')):raise ValueError('CLOSURE_PATH')
    return files

def load(name,path,pin):
    raw=read(path,pin)
    spec=importlib.util.spec_from_loader(name,loader=None,origin=str(path));module=importlib.util.module_from_spec(spec);module.__file__=str(path)
    sys.modules[name]=module
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module

def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('DUPLICATE_KEY')
        result[key]=value
    return result

def lab_identity():
    if os.geteuid()!=0 or os.getegid()!=0 or socket.gethostname()!='kaltura-php83-lab':raise ValueError('LAB_IDENTITY')
    read('/etc/machine-id','ad9adac39d0fb440883f0b82c8c45058596b74a6d9e98da2746e4dbdafd3aad8',limit=128)
    result=subprocess.run(['/usr/sbin/ip','-j','-4','addr'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=5,env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LC_ALL':'C'},check=True)
    if len(result.stdout)>65536:raise ValueError('IP_LIMIT')
    ips={v.get('local') for x in json.loads(result.stdout) for v in x.get('addr_info',[])}
    if '192.168.56.83' not in ips or ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.74'}):raise ValueError('LAB_IP')
    marker=Path('/opt/kaltura/maintenance')
    read(marker,'0646494af6f2cd1696b3b2c08e17a9ef32927dc93a03330b5ab0675467e12d52',limit=128)
    st=marker.stat()
    if st.st_gid!=0 or stat.S_IMODE(st.st_mode)!=0o644:raise ValueError('HOLD')
    user=pwd.getpwnam('kaltura');group=grp.getgrnam('kaltura')
    if user.pw_uid!=7373 or user.pw_gid!=7373 or group.gr_gid!=7373 or set(group.gr_mem)!={'www-data'}:raise ValueError('WORKER_GROUP')
    if any(p.pw_gid==7373 and p.pw_name!='kaltura' for p in pwd.getpwall()):raise ValueError('GROUP_MEMBERS')

def execute():
    lab_identity()
    contract=json.loads(read(MANIFEST,limit=65536),object_pairs_hook=unique_object);files=validate_contract(contract)
    for path,pin in files.items():read(path,pin)
    trusted(CONFIG.parent,directory=True)
    observed={str(p) for p in CONFIG.parent.iterdir()}
    expected={p for p in files if Path(p).parent==CONFIG.parent}
    links={CONFIG.parent/'nginx.conf':CONFIG,CONFIG.parent/'server.conf':CONFIG.parent/'kaltura.conf'}
    if str(CONFIG.parent/'kaltura.conf') not in files:raise ValueError('SERVER_CONFIG')
    for link,target in links.items():
        st=link.lstat()
        if not stat.S_ISLNK(st.st_mode) or st.st_uid!=0 or st.st_gid!=0 or st.st_nlink!=1 or os.readlink(link)!=str(target):raise ValueError('CONFIG_LINK')
        if os.listxattr(link,follow_symlinks=False):raise ValueError('LINK_XATTR')
    expected.update(str(p) for p in links)
    if observed!=expected:raise ValueError('CLOSURE_INVENTORY')
    # Full exact closure is externally reviewed; runtime never discovers includes.
    for directory in (SOCKET,LOGS):trusted(directory,directory=True)
    if stat.S_IMODE(SOCKET.stat().st_mode)!=0o750 or SOCKET.stat().st_gid!=0 or list(SOCKET.iterdir()):raise ValueError('SOCKET_DIRECTORY')
    # This exact empty RuntimeDirectory is owned by this service and recreated
    # by systemd on each activation; no application log parent is modified.
    os.chown(SOCKET,0,contract['socket_gid'])
    if (LOGS.stat().st_uid,LOGS.stat().st_gid,stat.S_IMODE(LOGS.stat().st_mode))!=(0,0,0o700):raise ValueError('LOG_DIRECTORY')
    if os.path.lexists(SOCKET/'syslog'):raise ValueError('SOCKET_EXISTS')
    run=LOGS/('run-'+uuid.uuid4().hex);run.mkdir(mode=0o700);os.chown(run,0,0)
    adapter=load('kaltura_lab_adapter',BASE/'lab_adapter.py',ADAPTER_PIN)
    sanitizer=load('kaltura_lab_sanitizer',BASE/'sanitizer.py',SANITIZER_PIN)
    spec=adapter.Spec(str(BINARY),str(CONFIG),str(CONFIG.parent),str(SOCKET),str(run),tuple(files.items()),seconds=120,socket_gid=contract['socket_gid'])
    result=adapter.run(spec,sanitizer)
    # Terminal data is fixed; no raw OS or child exception is ever serialized.
    status=result.get('status')
    if status not in ('STOPPED','TIMEOUT','CHILD_EXIT','FAILED'):status='FAILED'
    raw=(json.dumps({'status':status,'child_reaped':result.get('child_reaped') is True},sort_keys=True)+'\n').encode()
    fd=os.open(run/'terminal.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as output:output.write(raw)
    # RuntimeDirectory removal is systemd-owned; stale socket is never guessed away.
    return 0 if status=='STOPPED' and result.get('child_reaped') is True else 1

def main():
    try:return execute()
    except BaseException:return 1
if __name__=='__main__':raise SystemExit(main())
