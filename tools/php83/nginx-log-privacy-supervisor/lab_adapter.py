"""Separate bounded lab adapter. Not a service installer or production executor.

Caller must review/pin complete config include closure and forbid raw file sinks.
Only exact allowlisted binary/config pairs run; stderr/stdout never inherit a sink.
"""
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import socket
import stat
import subprocess
import time

SEVERITIES=frozenset(('emerg','alert','crit','err','warning','notice','info','debug'))
REASONS=frozenset(('permission_denied','file_missing','connect_failure','timeout','upstream_failure','invalid_request','unclassified','malformed','truncated','collector_failure','collector_started','collector_stopped','output_limit','access_success','access_redirect','access_client_error','access_server_error','access_informational'))

class Rejected(Exception):
    """Fixed public code only."""

@dataclasses.dataclass(frozen=True)
class Spec:
    binary: str
    config: str
    root: str
    socket_dir: str
    sink_dir: str
    allowlist: tuple
    seconds: float = 5
    input_limit: int = 4*1024*1024
    output_limit: int = 256*1024
    segment_limit: int = 64*1024
    fixture_roots: tuple = ()
    drain_seconds: float = 2
    socket_gid: int | None = None

def trust(path,spec,directory=False):
    p=Path(path)
    if not p.is_absolute() or p.resolve()!=p:raise Rejected('TRUST_PATH')
    uid=0
    if spec.fixture_roots:
        # Explicit disposable fixture policy; never inferred from current UID.
        boundaries=[Path(x) for x in spec.fixture_roots if p==Path(x) or Path(x) in p.parents]
        if not boundaries:raise Rejected('FIXTURE_BOUNDARY')
        boundary=max(boundaries,key=lambda x:len(x.parts));uid=os.geteuid()
        if not boundary.is_absolute() or boundary.resolve()!=boundary:raise Rejected('FIXTURE_BOUNDARY')
        bs=boundary.lstat()
        if not stat.S_ISDIR(bs.st_mode) or stat.S_IMODE(bs.st_mode)!=0o700 or bs.st_uid!=uid:raise Rejected('FIXTURE_BOUNDARY')
        chain=[];item=p
        while True:
            chain.append(item)
            if item==boundary:break
            item=item.parent
    else:
        if os.geteuid()!=0:raise Rejected('ROOT_REQUIRED')
        chain=[p,*p.parents]
    for item in chain:
        st=item.lstat()
        if st.st_uid!=uid or st.st_mode&0o022 or stat.S_ISLNK(st.st_mode):raise Rejected('TRUST_METADATA')
        if any(x.startswith('system.posix_acl') for x in os.listxattr(item,follow_symlinks=False)):raise Rejected('TRUST_ACL')
        if item!=p or directory:
            if not stat.S_ISDIR(st.st_mode):raise Rejected('TRUST_DIRECTORY')
        elif not stat.S_ISREG(st.st_mode) or st.st_nlink!=1:raise Rejected('TRUST_FILE')

def pinned(path,pin,spec):
    trust(path,spec)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    with os.fdopen(fd,'rb') as f:
        st=os.fstat(f.fileno());h=hashlib.sha256()
        if not stat.S_ISREG(st.st_mode) or st.st_nlink!=1:raise Rejected('PIN')
        if st.st_size>64*1024*1024:raise Rejected('PIN_SIZE')
        while chunk:=f.read(65536):h.update(chunk)
        def identity(x):return (x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
        if identity(os.fstat(f.fileno()))!=identity(st) or identity(os.stat(path,follow_symlinks=False))!=identity(st):raise Rejected('PIN_CHANGED')
    if h.hexdigest()!=pin:raise Rejected('PIN')

def encode(event):
    if type(event) is not dict or set(event)!= {'severity','reason','count'}:raise Rejected('SANITIZER')
    if event['severity'] not in SEVERITIES or event['reason'] not in REASONS or type(event['count']) is not int or event['count'] != 1:raise Rejected('SANITIZER')
    return (json.dumps(event,separators=(',',':'))+'\n').encode('ascii')

class Sink:
    def __init__(self,root,spec):self.root=root;self.spec=spec;self.total=0;self.segment=0;self.number=0;self.fd=None;self.dirfd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    def write(self,event):
        raw=encode(event)
        if self.total+len(raw)>self.spec.output_limit:raise Rejected('OUTPUT_LIMIT')
        if self.fd is None or self.segment+len(raw)>self.spec.segment_limit:
            self.close();self.number+=1;self.segment=0
            self.fd=os.open(f'events-{self.number:04d}.jsonl',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=self.dirfd)
            os.fchmod(self.fd,0o600)
        view=memoryview(raw)
        while view:
            n=os.write(self.fd,view)
            if n<=0:raise Rejected('OUTPUT_IO')
            view=view[n:]
        self.total+=len(raw);self.segment+=len(raw)
    def close(self):
        if self.fd is not None:
            fd=self.fd;self.fd=None;os.close(fd)
    def finish(self):
        try:self.close()
        finally:os.close(self.dirfd)

def run(spec,sanitizer,stop=None):
    """Return only fixed result codes. All raw bytes stay bounded in memory.

    sanitizer supplies sanitize(bytes,truncated=bool,source='syslog') and
    LineFeed(source='stderr'). No exceptions from either escape this boundary.
    Config must explicitly use daemon off/master_process on, socket_dir/syslog,
    stderr error fallback, and reviewed safe sinks. No shell or config injection.
    """
    child=None;receiver=None;sel=None;sink=None;handlers={};result='FAILED';received=0
    interrupted=False
    def on_signal(signum,frame):
        nonlocal interrupted
        interrupted=True
    try:
        if not (0<spec.seconds<=120 and 0<spec.input_limit<=16*1024*1024 and 128<=spec.segment_limit<=spec.output_limit<=4*1024*1024):raise Rejected('LIMITS')
        root=Path(spec.root);socket_dir=Path(spec.socket_dir);sink_dir=Path(spec.sink_dir)
        if len({root,socket_dir,sink_dir})!=3:raise Rejected('SEPARATE_PATHS')
        for directory in (root,socket_dir,sink_dir):trust(directory,spec,directory=True)
        if stat.S_IMODE(sink_dir.stat().st_mode)!=0o700:raise Rejected('PRIVATE_SINK')
        if not 0<spec.drain_seconds<=2:raise Rejected('DRAIN_LIMIT')
        allowed=dict(spec.allowlist)
        if len(allowed)!=len(spec.allowlist) or not {spec.binary,spec.config,str(Path(sanitizer.__file__).resolve())}<=set(allowed):raise Rejected('ALLOWLIST')
        if Path(spec.config).parent!=root:raise Rejected('CONFIG_ROOT')
        for path,pin in allowed.items():pinned(path,pin,spec)
        receiver=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        receiver.bind(str(socket_dir/'syslog'));os.chmod(socket_dir/'syslog',0o600)
        if spec.socket_gid is not None:
            if os.geteuid()!=0 or socket_dir.stat().st_gid!=spec.socket_gid or stat.S_IMODE(socket_dir.stat().st_mode)!=0o750:raise Rejected('SOCKET_GROUP')
            os.chown(socket_dir/'syslog',0,spec.socket_gid);os.chmod(socket_dir/'syslog',0o660)
        receiver.setblocking(False)
        socket_identity=(socket_dir/'syslog').stat().st_ino
        sink=Sink(sink_dir,spec);sel=selectors.DefaultSelector();sel.register(receiver,selectors.EVENT_READ,'syslog')
        feeds={key:sanitizer.LineFeed(source='stderr') for key in ('stderr','stdout')}
        for sig in (signal.SIGTERM,signal.SIGINT):handlers[sig]=signal.signal(sig,on_signal)
        child=subprocess.Popen([spec.binary,'-p',str(root)+'/', '-c',spec.config,'-e','stderr'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,env={'PATH':'/usr/bin:/bin','LC_ALL':'C','HOME':str(root)},close_fds=True)
        for key in feeds:
            pipe=getattr(child,key);os.set_blocking(pipe.fileno(),False);sel.register(pipe,selectors.EVENT_READ,key)
        deadline=time.monotonic()+spec.seconds;draining=None;open_pipes=2
        while True:
            if interrupted or (stop is not None and stop.is_set()):result='STOPPED';break
            if time.monotonic()>=deadline:result='TIMEOUT';break
            if (socket_dir/'syslog').stat().st_ino!=socket_identity:raise Rejected('COLLECTOR_LOST')
            if child.poll() is not None and draining is None:draining=time.monotonic()+spec.drain_seconds
            if draining is not None and (time.monotonic()>=draining or open_pipes==0):
                # One bounded datagram read round remains below; pipes were drained.
                ready=sel.select(0)
                if not ready or time.monotonic()>=draining:
                    result='FAILED' if time.monotonic()>=draining else 'CHILD_EXIT';break
            for key,_ in sel.select(.05):
                if key.data=='syslog':
                    raw,_,flags,_=receiver.recvmsg(8192)
                    received+=len(raw)
                    events=[sanitizer.sanitize(raw,truncated=bool(flags&socket.MSG_TRUNC),source='syslog')]
                else:
                    raw=os.read(key.fileobj.fileno(),65536);received+=len(raw)
                    if not raw:sel.unregister(key.fileobj);open_pipes-=1;events=feeds[key.data].flush()
                    else:events=feeds[key.data].feed(raw)
                if received>spec.input_limit:raise Rejected('INPUT_LIMIT')
                for event in events:sink.write(event)
    except BaseException:
        result='FAILED'
    finally:
        def cleanup(action):
            nonlocal result
            try:action()
            except ProcessLookupError:pass
            except BaseException:result='FAILED'
        if child is not None:
            # Kill the session group even if its leader already exited.
            cleanup(lambda:os.killpg(child.pid,signal.SIGTERM))
            try:child.wait(timeout=.5)
            except subprocess.TimeoutExpired:pass
            except BaseException:result='FAILED'
            cleanup(lambda:os.killpg(child.pid,signal.SIGKILL))
            cleanup(lambda:child.wait(timeout=2))
        # After stop/reap, consume the finite tail instead of silently losing it.
        if child is not None and sel is not None and sink is not None:
            try:
                end=time.monotonic()+spec.drain_seconds
                while True:
                    if time.monotonic()>=end:raise Rejected('DRAIN_TIMEOUT')
                    ready=sel.select(.02)
                    if not ready and open_pipes==0:break
                    for key,_ in ready:
                        if key.data=='syslog':
                            raw,_,flags,_=receiver.recvmsg(8192);received+=len(raw)
                            events=[sanitizer.sanitize(raw,truncated=bool(flags&socket.MSG_TRUNC),source='syslog')]
                        else:
                            raw=os.read(key.fileobj.fileno(),65536);received+=len(raw)
                            if not raw:sel.unregister(key.fileobj);open_pipes-=1;events=feeds[key.data].flush()
                            else:events=feeds[key.data].feed(raw)
                        if received>spec.input_limit:raise Rejected('INPUT_LIMIT')
                        for event in events:sink.write(event)
                for feed in feeds.values():
                    for event in feed.flush():sink.write(event)
            except BaseException:result='FAILED'
        if sel:cleanup(sel.close)
        if child is not None:
            for pipe in (child.stdout,child.stderr):
                if pipe:cleanup(pipe.close)
        if receiver:cleanup(receiver.close)
        if sink:cleanup(sink.finish)
        for sig,old in handlers.items():cleanup(lambda sig=sig,old=old:signal.signal(sig,old))
    return {'status':result,'input_bytes':received,'child_reaped':child is None or child.poll() is not None}
