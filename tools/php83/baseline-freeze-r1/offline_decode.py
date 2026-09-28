"""Linux-only pinned original-byte decoder. No URL or input path API.
Run in a dedicated single-threaded process: resource preexec limits are used.
Executable bytes are sealed; host dynamic libraries are NOT cohort-attested.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import selectors
import signal
import stat
import subprocess
import time

SIZE = 1511134
DIGEST = '612d179c75f8f2374b7ac59c2dd7edba65e38eb357b870e8ad8c2e83d63b5473'
BINARIES = {'ffmpeg': ('/usr/bin/ffmpeg', 'ed16af623947494a72e284b6eb8ff225f2da22b38b5d5069c2fd4b4ba3384e41'), 'ffprobe': ('/usr/bin/ffprobe', '272f6ebc634a63d9c8b4ca68e964119d980f25154e5aa2c35e5487da48e9a58f')}
CONTRACT = '6dbcdba82dcd6a25ff98948ff8cc4aa53f72a40b52036c7169560dd3c6227e89'
CAP = 65536
WALL = 30

class Rejected(ValueError):
    pass

def need(ok, code):
    if not ok:
        raise Rejected(code)

def sealed(data, name):
    fd = os.memfd_create(name, os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    try:
        view = memoryview(data)
        while view:
            n = os.write(fd, view)
            need(n > 0, 'MEMFD_WRITE')
            view = view[n:]
        os.lseek(fd, 0, os.SEEK_SET)
        fcntl.fcntl(fd, fcntl.F_ADD_SEALS, fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_SEAL)
        return fd
    except BaseException:
        os.close(fd)
        raise

def pinned(path, digest, limit):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= limit, 'SOURCE_SHAPE')
        chunks = []
        total = 0
        while True:
            b = os.read(fd, min(65536, limit + 1 - total))
            if not b:
                break
            chunks.append(b)
            total += len(b)
            need(total <= limit, 'SOURCE_LIMIT')
        after = os.fstat(fd)
        need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'SOURCE_CHANGED')
        data = b''.join(chunks)
        need(hashlib.sha256(data).hexdigest() == digest, 'SOURCE_PIN')
        return data
    finally:
        os.close(fd)

def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (20, 21))
    resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))

def run(executable_fd, args, media_fd):
    """Internal fixed-argv child runner; bounded separate stdout/stderr."""
    os.lseek(media_fd, 0, os.SEEK_SET)
    p = subprocess.Popen([f'/proc/self/fd/{executable_fd}', *args], pass_fds=(executable_fd, media_fd), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'}, cwd='/', start_new_session=True, preexec_fn=limits)
    sel = selectors.DefaultSelector()
    outputs = [bytearray(), bytearray()]
    deadline = time.monotonic() + WALL
    try:
        for i, stream in enumerate((p.stdout, p.stderr)):
            os.set_blocking(stream.fileno(), False)
            sel.register(stream, selectors.EVENT_READ, i)
        while sel.get_map():
            need(time.monotonic() < deadline, 'TIME_LIMIT')
            for key, _ in sel.select(min(.1, max(0, deadline-time.monotonic()))):
                b = os.read(key.fileobj.fileno(), 8192)
                if not b:
                    sel.unregister(key.fileobj)
                else:
                    outputs[key.data].extend(b)
                    need(len(outputs[key.data]) <= CAP, 'OUTPUT_LIMIT')
        # Keep the exited leader waitable until killpg: reaping first permits
        # PID/PGID reuse before cleanup and could signal an unrelated group.
        while True:
            result = os.waitid(os.P_PID, p.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
            if result is not None:
                break
            need(time.monotonic() < deadline, 'TIME_LIMIT')
            time.sleep(.01)
        need(result.si_code == os.CLD_EXITED and result.si_status == 0, 'DECODER_EXIT')
        need(not outputs[1], 'DECODER_STDERR')
        return bytes(outputs[0])
    finally:
        # Even leader exit does not authorize leaving descendants alive.
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        p.wait(timeout=5)
        sel.close()
        p.stdout.close()
        p.stderr.close()

def decode(data):
    """Decode exactly the public original fixture bytes supplied in memory."""
    need(type(data) is bytes and len(data) == SIZE, 'MEDIA_SIZE')
    need(hashlib.sha256(data).hexdigest() == DIGEST, 'MEDIA_PIN')
    source = pinned(str(Path(__file__).with_name('decode_contract.py')), CONTRACT, 16384)
    namespace = {'__name__': 'pinned_decode_contract'}
    exec(compile(source, '<pinned-contract>', 'exec'), namespace)
    fds = []
    try:
        media = sealed(data, 'public-original-media'); fds.append(media)
        executables = {}
        for name, (path, digest) in BINARIES.items():
            executable = sealed(pinned(path, digest, 16*1024*1024), 'pinned-'+name)
            fds.append(executable); executables[name] = executable
        probe_args, decode_args = namespace['commands'](media, 'original_mp4')
        raw = run(executables['ffprobe'], probe_args, media)
        try:
            probe = json.loads(raw)
            projected = namespace['validate'](probe, 'original_mp4')
        except Exception:
            raise Rejected('PROBE_CONTRACT') from None
        need(run(executables['ffmpeg'], decode_args, media) == b'', 'DECODE_STDOUT')
        projected.update(case='OFFLINE_ORIGINAL_BYTES_ONLY', full_decode_verified=True, media_bytes=SIZE, source_sha256=DIGEST, network_input_allowed=False, delivery_verified=False, dynamic_library_cohort_verified=False)
        return projected
    finally:
        for fd in reversed(fds):
            os.close(fd)
