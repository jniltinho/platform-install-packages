"""Local fixture guardian. Not a service installer or production executor.

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
    allowlist: tuple
    seconds: float = 5
    input_limit: int = 4*1024*1024
    output_limit: int = 256*1024
    segment_limit: int = 64*1024
    require_root: bool = True

def pinned(path, pin):
    p=Path(path)
    if not p.is_absolute() or p.is_symlink() or p.resolve()!=p: raise Rejected('PIN')
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
    with os.fdopen(fd,'rb') as f:
        st=os.fstat(f.fileno())
        if not stat.S_ISREG(st.st_mode) or st.st_mode & 0o022 or st.st_nlink != 1: raise Rejected('PIN')
        h=hashlib.sha256()
        while chunk:=f.read(65536):h.update(chunk)
    if h.hexdigest()!=pin:raise Rejected('PIN')

def encode(event):
    if type(event) is not dict or set(event)!= {'severity','reason','count'}:raise Rejected('SANITIZER')
    if event['severity'] not in SEVERITIES or event['reason'] not in REASONS or type(event['count']) is not int or event['count'] != 1:raise Rejected('SANITIZER')
    return (json.dumps(event,separators=(',',':'))+'\n').encode('ascii')

class Sink:
    def __init__(self,root,spec):self.root=root;self.spec=spec;self.total=0;self.segment=0;self.number=0;self.fd=None
    def write(self,event):
        raw=encode(event)
        if self.total+len(raw)>self.spec.output_limit:raise Rejected('OUTPUT_LIMIT')
        if self.fd is None or self.segment+len(raw)>self.spec.segment_limit:
            self.close();self.number+=1;self.segment=0
            self.fd=os.open(self.root/f'events-{self.number:04d}.jsonl',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
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

def run(spec,sanitizer,stop=None):
    """Return only fixed result codes. All raw bytes stay bounded in memory.

    sanitizer supplies sanitize(bytes,truncated=bool,source='syslog') and
    LineFeed(source='stderr'). No exceptions from either escape this boundary.
    Config must explicitly use daemon off/master_process on, this root/syslog,
    stderr error fallback, and reviewed safe sinks. No shell or config injection.
    """
    child=None;receiver=None;sel=None;sink=None;handlers={};result='FAILED';received=0
    interrupted=False
    def on_signal(signum,frame):
        nonlocal interrupted
        interrupted=True
    try:
        if spec.require_root and os.geteuid()!=0:raise Rejected('ROOT_REQUIRED')
        if not (0<spec.seconds<=120 and 0<spec.input_limit<=16*1024*1024 and 128<=spec.segment_limit<=spec.output_limit<=4*1024*1024):raise Rejected('LIMITS')
        root=Path(spec.root)
        st=root.lstat()
        if not root.is_absolute() or root.resolve()!=root or root.is_symlink() or not stat.S_ISDIR(st.st_mode) or st.st_uid!=os.geteuid() or stat.S_IMODE(st.st_mode)!=0o700:raise Rejected('ROOT')
        allowed=dict(spec.allowlist)
        if set(allowed)!={spec.binary,spec.config}:raise Rejected('ALLOWLIST')
        if Path(spec.config).parent!=root:raise Rejected('CONFIG_ROOT')
        for path,pin in allowed.items():pinned(path,pin)
        receiver=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        receiver.bind(str(root/'syslog'));receiver.setblocking(False)
        socket_identity=(root/'syslog').stat().st_ino
        sink=Sink(root,spec);sel=selectors.DefaultSelector();sel.register(receiver,selectors.EVENT_READ,'syslog')
        feeds={key:sanitizer.LineFeed(source='stderr') for key in ('stderr','stdout')}
        for sig in (signal.SIGTERM,signal.SIGINT):handlers[sig]=signal.signal(sig,on_signal)
        child=subprocess.Popen([spec.binary,'-p',str(root)+'/', '-c',spec.config,'-e','stderr'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True,env={'PATH':'/usr/bin:/bin','LC_ALL':'C','HOME':str(root)},close_fds=True)
        for key in feeds:
            pipe=getattr(child,key);os.set_blocking(pipe.fileno(),False);sel.register(pipe,selectors.EVENT_READ,key)
        deadline=time.monotonic()+spec.seconds
        while True:
            if interrupted or (stop is not None and stop.is_set()):result='STOPPED';break
            if time.monotonic()>=deadline:result='TIMEOUT';break
            if (root/'syslog').stat().st_ino!=socket_identity:raise Rejected('COLLECTOR_LOST')
            if child.poll() is not None:result='CHILD_EXIT';break
            for key,_ in sel.select(.05):
                if key.data=='syslog':
                    raw,_,flags,_=receiver.recvmsg(8192)
                    received+=len(raw)
                    events=[sanitizer.sanitize(raw,truncated=bool(flags&socket.MSG_TRUNC),source='syslog')]
                else:
                    raw=os.read(key.fileobj.fileno(),65536);received+=len(raw)
                    if not raw:sel.unregister(key.fileobj);events=feeds[key.data].flush()
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
            for pipe in (child.stdout,child.stderr):
                if pipe:cleanup(pipe.close)
        if sel:cleanup(sel.close)
        if receiver:cleanup(receiver.close)
        if sink:cleanup(sink.close)
        for sig,old in handlers.items():cleanup(lambda sig=sig,old=old:signal.signal(sig,old))
    return {'status':result,'input_bytes':received,'child_reaped':child is None or child.poll() is not None}
