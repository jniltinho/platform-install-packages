"""Finite append-only file windows. No logging of patterns, bytes or their digests."""
from dataclasses import dataclass
import os
from pathlib import Path
import stat
import time


class Incomplete(RuntimeError):
    """A code only: never embed a path, pattern, OS exception or file contents."""


@dataclass(frozen=True)
class Mark:
    device: int
    inode: int
    size: int
    mtime_ns: int


@dataclass(frozen=True)
class Limits:
    bytes: int = 64 * 1024 * 1024
    seconds: float = 10
    chunk: int = 64 * 1024
    rounds: int = 3
    quiet_seconds: float = 0.05
    files: int = 512
    max_pattern: int = 8192
    patterns: int = 32


def need(ok, code):
    if not ok:
        raise Incomplete(code)


def _mark(info):
    need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'UNSAFE_FILE')
    return Mark(info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)


def snapshot(paths, *, max_files=512):
    """Capture before nonce. Caller owns effective sink discovery, including journal."""
    try:
        need(type(max_files) is int and max_files > 0, 'LIMITS')
        names = []
        for p in paths:
            need(len(names) < max_files, 'INVENTORY')
            names.append(os.fspath(p))
        need(0 < len(names) <= max_files and len(set(names)) == len(names), 'INVENTORY')
        result = {}
        for name in sorted(names):
            path = Path(name)
            need(path.is_absolute() and '..' not in path.parts, 'UNSAFE_PATH')
            for component in (path, *path.parents):
                need(not stat.S_ISLNK(component.lstat().st_mode), 'SYMLINK')
            result[name] = _mark(path.stat(follow_symlinks=False))
        return result
    except Incomplete:
        raise
    except Exception:
        raise Incomplete('SNAPSHOT_FAILED') from None


def _continuity(before, after):
    need(set(before) == set(after), 'INVENTORY_CHANGED')
    for name, old in before.items():
        new = after[name]
        need((old.device, old.inode) == (new.device, new.inode), 'IDENTITY_CHANGED')
        need(new.size >= old.size, 'TRUNCATED')
        need(new.size != old.size or new.mtime_ns == old.mtime_ns, 'REWRITTEN')


def scan_window(start, patterns, *, inventory, limits=Limits()):
    """Rescan a reusable pre-nonce snapshot; counts align with private input patterns.

    inventory() must rediscover all reviewed sinks each time, not return a cached
    list. Success covers only the returned offsets at the final observation.
    Caller MUST require zero counts plus its separate journal/configuration gate
    before USER. No claim about writes after return or malicious prefix rewriting.
    """
    try:
        return _scan(start, patterns, inventory, limits)
    except Incomplete:
        raise
    except Exception:
        raise Incomplete('SCAN_FAILED') from None


def _scan(start, patterns, inventory, limits):
    for value in (limits.bytes, limits.chunk, limits.rounds, limits.files,
                  limits.max_pattern, limits.patterns):
        need(type(value) is int and value > 0, 'LIMITS')
    import math
    for value in (limits.seconds, limits.quiet_seconds):
        need(type(value) in (int, float) and math.isfinite(value), 'LIMITS')
    need(limits.seconds > 0 and 0 <= limits.quiet_seconds < limits.seconds, 'LIMITS')
    need(isinstance(start, dict) and bool(start), 'START')
    for name, mark in start.items():
        need(type(name) is str and type(mark) is Mark, 'START')
        need(all(type(v) is int and v >= 0 for v in (mark.device, mark.inode, mark.size, mark.mtime_ns)), 'START')
    need(type(patterns) in (list, tuple) and 0 < len(patterns) <= limits.patterns, 'PATTERNS')
    need(all(type(p) is bytes and 8 <= len(p) <= limits.max_pattern for p in patterns), 'PATTERNS')
    need(callable(inventory), 'INVENTORY')
    deadline = time.monotonic() + limits.seconds
    def clock():
        need(time.monotonic() <= deadline, 'DEADLINE')
    def current():
        clock()
        result = snapshot(inventory(), max_files=limits.files)
        clock()
        return result
    offsets = {n: m.size for n, m in start.items()}
    tails = {n: b'' for n in start}
    counts = [0] * len(patterns)
    previous = start
    scanned = 0
    overlap = max(map(len, patterns)) - 1
    for round_number in range(1, limits.rounds + 1):
        cut = current()
        _continuity(previous, cut)
        observed = dict(cut)
        for name, mark in cut.items():
            need(mark.size - offsets[name] <= limits.bytes - scanned, 'BYTE_LIMIT')
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, 'rb') as stream:
                opened = _mark(os.fstat(stream.fileno()))
                _continuity({name: mark}, {name: opened})
                stream.seek(offsets[name])
                while offsets[name] < mark.size:
                    clock()
                    block = stream.read(min(limits.chunk, mark.size - offsets[name]))
                    need(bool(block), 'SHORT_READ')
                    data = tails[name] + block
                    boundary = len(tails[name])
                    for i, pattern in enumerate(patterns):
                        clock()
                        pos = data.find(pattern)
                        matches = 0
                        while pos >= 0:
                            if matches % 1024 == 0:
                                clock()
                            matches += 1
                            if pos + len(pattern) > boundary:
                                counts[i] += 1
                            pos = data.find(pattern, pos + 1)
                    tails[name] = data[-overlap:]
                    offsets[name] += len(block)
                    scanned += len(block)
                after_fd = _mark(os.fstat(stream.fileno()))
                _continuity({name: opened}, {name: after_fd})
                observed[name] = after_fd
        after = current()
        # Preserve all observed growth, not only the earlier read cutoff.
        _continuity(observed, after)
        if all(after[n].size == offsets[n] for n in after):
            clock()
            time.sleep(limits.quiet_seconds)
            final = current()
            _continuity(after, final)
            if all(final[n].size == offsets[n] for n in final):
                return {'status': 'COMPLETE_FINITE_FILE_WINDOW', 'counts': counts,
                        'scanned_bytes': scanned, 'rounds': round_number,
                        'files': len(final), 'end_offsets': offsets,
                        'uncovered_tail_bytes': 0, 'future_writes_covered': False,
                        'journal_covered': False, 'privacy_acceptance': False}
            previous = final
        else:
            previous = after
    raise Incomplete('UNDRAINED_TAIL')
