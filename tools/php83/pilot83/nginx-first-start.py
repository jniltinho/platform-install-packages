"""Fixed .83 fresh nginx pre-first-start guard; never starts a service."""
import grp
import hashlib
import os
from pathlib import Path
import pwd
import socket
import stat
import subprocess
import sys
import tempfile

CONF = Path('/opt/kaltura/nginx/conf')
BINARY = Path('/opt/kaltura/nginx/sbin/nginx')
INIT = Path('/etc/init.d/kaltura-nginx')
PID = Path('/opt/kaltura/nginx/logs/nginx.pid')
ENV = {'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','HOME':'/root','LC_ALL':'C'}
PINS = {'etc/init.d/kaltura-nginx': '476e1b6a09a91606f3982ff443efa124118aacd3de43fd8c351910e58438e79a', 'opt/kaltura/nginx/conf/base.conf': 'f011df8b869a55df042677e3db02529c8dab96d3858b0c322e31c64b6cad07e1', 'opt/kaltura/nginx/conf/cors.conf': '97fba7f5da398ae9a3b8ea106062a60a1e0542d4b7fbde16da29b2d3f9bcd3f7', 'opt/kaltura/nginx/conf/fastcgi.conf': 'b2c3d480a58f61f3a7dc61850b461e892e36f236317765a4f2f6d558c928fa57', 'opt/kaltura/nginx/conf/fastcgi.conf.default': 'b2c3d480a58f61f3a7dc61850b461e892e36f236317765a4f2f6d558c928fa57', 'opt/kaltura/nginx/conf/fastcgi_params': 'f37852d0113de30fa6bfc3d9b180ef99383c06739530dd482a8538503afd5a58', 'opt/kaltura/nginx/conf/fastcgi_params.default': 'f37852d0113de30fa6bfc3d9b180ef99383c06739530dd482a8538503afd5a58', 'opt/kaltura/nginx/conf/http.conf.template': '4253af1e939f5f64dd5c6a52c106b2602b012a9afdeb5e3b999152b5068c2df5', 'opt/kaltura/nginx/conf/kaltura-nginx.conf.template': '3fa9c118602917bb58a356a0d11cd63cae896b350e5e03ebc121274f249b6015', 'opt/kaltura/nginx/conf/kaltura.conf.template': 'db1e3adc32030c33502191d1c05e278e8fdf31f04746e7e1955c2b4a7ce4a2d4', 'opt/kaltura/nginx/conf/koi-utf': 'b5f8a6d411db5e5d11d151d50cd1e962444732593adec0e1ef0a8c6eebec63ee', 'opt/kaltura/nginx/conf/koi-win': 'de518a9eafe86c8bc705e296d0ef26135835b46bdc0de01d1d50a630fa5d341e', 'opt/kaltura/nginx/conf/logrotate': 'a861d0e16029573a02a301c20f5a1bc4fde58d867a28d0ab7752e2155d985fde', 'opt/kaltura/nginx/conf/main.conf.template': '6fe8a74f49d870911b2c0b9cdaf108eafc587b0d5e229015e35b0d0eb733e600', 'opt/kaltura/nginx/conf/mime.types': '6f95d1d7d75e3c072907d845622a69d23110d1266c16ff122b3109b8b21f3ae9', 'opt/kaltura/nginx/conf/mime.types.default': '6f95d1d7d75e3c072907d845622a69d23110d1266c16ff122b3109b8b21f3ae9', 'opt/kaltura/nginx/conf/nginx.conf': '95363d79620c1b3eb6951711b6630a411f147bc9197bc91442c0605cf6688e46', 'opt/kaltura/nginx/conf/nginx.conf.default': '95363d79620c1b3eb6951711b6630a411f147bc9197bc91442c0605cf6688e46', 'opt/kaltura/nginx/conf/nginx.conf.template': 'fc85c42a733c3090ac72bf02c910c89228930acad4965f2087ad2ba5622926a0', 'opt/kaltura/nginx/conf/scgi_params': 'f27b2027c571ccafcfb0fbb3f54d7aeee11a984e3a0f5a1fdf14629030fc9011', 'opt/kaltura/nginx/conf/scgi_params.default': 'f27b2027c571ccafcfb0fbb3f54d7aeee11a984e3a0f5a1fdf14629030fc9011', 'opt/kaltura/nginx/conf/ssl.conf.template': 'a03132ddec157145e936e6ab4c7324b14af09ae8014580145098a277ddebefea', 'opt/kaltura/nginx/conf/uwsgi_params': '015cb581c2eb84b1a1ac9b575521d5881f791f632bfa62f34b26ba97d70c0d4f', 'opt/kaltura/nginx/conf/uwsgi_params.default': '015cb581c2eb84b1a1ac9b575521d5881f791f632bfa62f34b26ba97d70c0d4f', 'opt/kaltura/nginx/conf/vod-local-nginx.conf.template': 'bc16331bcdd369f81aff1499514c59a7806d5571052d831c80b1c7c32c491255', 'opt/kaltura/nginx/conf/vod-local.conf.template': '976fe6da937d5b70efa998143e04d8142e75493008cee49f19b0c51e7ee6c0e7', 'opt/kaltura/nginx/conf/vod-remote-nginx.conf.template': '419e7bae68cfe158c2c878ea77bbed26769f6e0dbc33f7fd15e91ee27d70d6a1', 'opt/kaltura/nginx/conf/vod-remote.conf.template': '2fe26159cdcae64948e9558b89cde7511e87f92bb3aa368a2c6bcb7eac953c66', 'opt/kaltura/nginx/conf/win-utf': '55adf050bad0cb60cbfe18649f8f17cd405fece0cc65eb78dac72c74c9dad944', 'opt/kaltura/nginx/sbin/nginx': '1a995dddd470f013258b1890cfc7c9e3b10c344461eb085de6b2ef8f991faec0'}
MACHINE = 'ad9adac39d0fb440883f0b82c8c45058596b74a6d9e98da2746e4dbdafd3aad8'

def need(value):
    if not value: raise ValueError('PRIVATE_NGINX_GUARD')
def digest(data):return hashlib.sha256(data).hexdigest()
def identity(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def no_acl(path):need(not set(os.listxattr(path,follow_symlinks=False)) & {'system.posix_acl_access','system.posix_acl_default'})
def root_group():need(set(grp.getgrgid(0).gr_mem)<={'root'} and all(p.pw_name=='root' for p in pwd.getpwall() if p.pw_gid==0))
def parents(path):
    for p in reversed(Path(path).parents):
        s=p.lstat();need(stat.S_ISDIR(s.st_mode) and (s.st_uid,s.st_gid)==(0,0) and not s.st_mode&0o002);no_acl(p)
def read(path,cap=8*1024*1024):
    path=Path(path);parents(path);s=path.lstat();need(stat.S_ISREG(s.st_mode) and (s.st_uid,s.st_gid)==(0,0) and s.st_nlink==1 and not s.st_mode&0o002 and s.st_size<=cap);no_acl(path)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        need(identity(os.fstat(fd))==identity(s));data=b''
        while len(data)<=cap:
            part=os.read(fd,min(65536,cap+1-len(data)))
            if not part:break
            data+=part
        need(len(data)==s.st_size and identity(os.fstat(fd))==identity(path.lstat())==identity(s));return data
    finally:os.close(fd)
def absent(path):need(not os.path.lexists(path))
def context():
    need(os.geteuid()==0 and socket.gethostname()=='kaltura-php83-lab');root_group()
    need(digest(read('/etc/machine-id'))==MACHINE)
    absent('/etc/default/nginx')
    for base in ('/etc/systemd/system','/run/systemd/system','/usr/lib/systemd/system','/lib/systemd/system'):
        for service in ('nginx','kaltura-nginx'):
            absent(base+'/'+service+'.service');absent(base+'/'+service+'.service.d')
    absent(PID)
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():continue
        try:
            name=(proc/'comm').read_text().strip();exe=os.readlink(proc/'exe')
        except FileNotFoundError:continue
        except ProcessLookupError:continue
        need(name!='nginx' and not exe.endswith('/nginx') and not exe.endswith('/nginx (deleted)'))
    for path in (BINARY,INIT):need(digest(read(path))==PINS[str(path).lstrip('/')])
def source_files():
    return {key.removeprefix('opt/kaltura/nginx/conf/'):pin for key,pin in PINS.items() if key.startswith('opt/kaltura/nginx/conf/')}
def templates():
    output={}
    for name,pin in source_files().items():
        if name=='nginx.conf':continue
        raw=read(CONF/name);need(digest(raw)==pin)
        if name.endswith('.template'):output[name]=raw
    return output
def expected_rendered(source):
    replacements={b'@NGINX_CONF_PATH@':str(CONF).encode(),b'@LOG_DIR@':b'/opt/kaltura/log/nginx',b'@PID_FILE_PATH@':str(PID).encode(),b'@VOD_PACKAGER_PORT@':b'88',b'@VOD_PACKAGER_HOST@':b'192.168.56.83',b'@RTMP_PORT@':b'1935'}
    result={}
    for name,raw in source.items():
        if name=='ssl.conf.template':continue
        for old,new in replacements.items():raw=raw.replace(old,new)
        if name in ('kaltura-nginx.conf.template','kaltura.conf.template'):
            for old,new in {b'@STATIC_FILES_PATH@':b'/opt/kaltura/nginx/static',b'@PROTOCOL@':b'http',b'@WWW_HOST@':b'192.168.56.83'}.items():raw=raw.replace(old,new)
        result[name.removesuffix('.template')]=raw
    result.pop('nginx.conf');result['ssl.conf']=b''
    return result
def bound(raw):
    for old,new in [(b'\t\tlisten 88;',b'\t\tlisten 192.168.56.83:88;'),(b'        listen 1935;',b'        listen 192.168.56.83:1935;')]:
        need(raw.count(old)==1);raw=raw.replace(old,new)
    return raw
def symlinks():
    for name,target in [('nginx.conf','kaltura-nginx.conf'),('server.conf','kaltura.conf')]:
        p=CONF/name;s=p.lstat();need(stat.S_ISLNK(s.st_mode) and (s.st_uid,s.st_gid)==(0,0) and os.readlink(p)==str(CONF/target));no_acl(p)
def inventory(names):need({p.name for p in CONF.iterdir()}==set(names))
def runtime_roots():
    # Existing hook recursively changes only these dedicated roots. Require empty.
    for name in ('/opt/kaltura/log/nginx','/var/tmp/hlsme','/var/tmp/dashme','/var/tmp/rec'):
        p=Path(name);s=p.lstat();need(stat.S_ISDIR(s.st_mode) and (s.st_uid,s.st_gid)==(0,0) and not s.st_mode&0o022);no_acl(p);need(not any(p.iterdir()))
        for ancestor in p.parents:
            x=ancestor.lstat();need(stat.S_ISDIR(x.st_mode));no_acl(ancestor)
            if str(ancestor)=='/opt/kaltura/log':
                need((x.st_uid,x.st_gid,stat.S_IMODE(x.st_mode))==(0,33,0o1770));continue
            need((x.st_uid,x.st_gid)==(0,0))
            need(not x.st_mode&0o002 or (str(ancestor)=='/var/tmp' and stat.S_IMODE(x.st_mode)==0o1777))
def pre():
    context();templates();inventory(source_files());need(digest(read(CONF/'nginx.conf'))==PINS['opt/kaltura/nginx/conf/nginx.conf']);runtime_roots()
def post():
    context();source=templates();expected=expected_rendered(source);symlinks();inventory(set(source_files())|set(expected)|{'server.conf'})
    for name,data in expected.items():need(read(CONF/name)==data)
    path=CONF/'kaltura-nginx.conf';before=path.lstat();new=bound(expected['kaltura-nginx.conf'])
    fd,tmp=tempfile.mkstemp(prefix='.pilot83-binding-',dir=CONF)
    try:
        with os.fdopen(fd,'wb') as stream:
            os.fchmod(stream.fileno(),stat.S_IMODE(before.st_mode));os.fchown(stream.fileno(),before.st_uid,before.st_gid);stream.write(new);stream.flush();os.fsync(stream.fileno())
        need(identity(path.lstat())==identity(before));os.replace(tmp,path)
        d=os.open(CONF,os.O_DIRECTORY);os.fsync(d);os.close(d)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    expected['kaltura-nginx.conf']=new
    result=subprocess.run([str(BINARY),'-t','-c',str(CONF/'nginx.conf')],env=ENV,capture_output=True,timeout=20)
    need(result.returncode==0)
    context();templates();symlinks();inventory(set(source_files())|set(expected)|{'server.conf'})
    for name,data in expected.items():need(read(CONF/name)==data)
if __name__=='__main__':
    try:
        need(len(sys.argv)==2 and sys.argv[1] in ('pre','post'))
        (pre if sys.argv[1]=='pre' else post)()
    except Exception:
        raise SystemExit(92)
