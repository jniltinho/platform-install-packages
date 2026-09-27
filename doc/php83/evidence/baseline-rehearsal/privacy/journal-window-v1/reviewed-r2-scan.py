"""Finite guest-private journal cursor windows; never publish journal values/cursors."""
from dataclasses import dataclass, field
import json
import math
import resource
import subprocess
import tempfile
import time


class Incomplete(RuntimeError):
    pass


@dataclass(frozen=True)
class Cursor:
    token: str = field(repr=False)
    boot: str = field(repr=False)


@dataclass(frozen=True)
class Limits:
    bytes: int = 8 * 1024 * 1024
    seconds: float = 15
    records: int = 10000
    rounds: int = 3
    patterns: int = 32
    pattern_bytes: int = 8192


def need(ok, code):
    if not ok:
        raise Incomplete(code)


class Budget:
    def __init__(self, limits):
        for value in (limits.bytes, limits.records, limits.rounds, limits.patterns, limits.pattern_bytes):
            need(type(value) is int and value > 0, 'LIMITS')
        need(type(limits.seconds) in (int, float) and math.isfinite(limits.seconds) and limits.seconds > 0, 'LIMITS')
        self.limits = limits
        self.deadline = time.monotonic() + limits.seconds
        self.bytes = 0
    def remaining(self):
        value = self.deadline - time.monotonic()
        need(value > 0, 'DEADLINE')
        return value


def _fetch(arguments, budget):
    """Private unnamed0600 files; cap child output independently of Python parsing."""
    cap = budget.limits.bytes - budget.bytes
    need(cap > 0, 'BYTE_LIMIT')
    def bound_child():
        resource.setrlimit(resource.RLIMIT_FSIZE, (cap, cap))
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        try:
            result = subprocess.run(['journalctl', '--no-pager', '--output=json', '--all'] + arguments,
                                    stdout=out, stderr=err, timeout=budget.remaining(),
                                    preexec_fn=bound_child, check=False)
        except subprocess.TimeoutExpired:
            raise Incomplete('JOURNAL_TIMEOUT') from None
        budget.remaining()
        need(type(result.returncode) is int and result.returncode == 0, 'JOURNAL_PROCESS')
        err.seek(0)
        need(not err.read(1), 'JOURNAL_STDERR')
        out.seek(0);raw = out.read(cap + 1)
        need(len(raw) <= cap, 'BYTE_LIMIT')
        budget.bytes += len(raw)
        return raw


def _object(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, 'DUPLICATE_JSON_FIELD')
        out[key] = value
    return out


def _records(raw, budget):
    rows = []
    for line in raw.splitlines():
        budget.remaining()
        need(bool(line) and len(rows) < budget.limits.records, 'RECORD_LIMIT')
        row = json.loads(line, object_pairs_hook=_object,
                         parse_constant=lambda _: (_ for _ in ()).throw(Incomplete('INVALID_JSON')))
        need(type(row) is dict and type(row.get('__CURSOR')) is str and bool(row['__CURSOR']) and
             type(row.get('_BOOT_ID')) is str and bool(row['_BOOT_ID']), 'RECORD_IDENTITY')
        rows.append(row)
    need(bool(rows), 'EMPTY_JOURNAL')
    return rows


def _snapshot(budget):
    rows = _records(_fetch(['--lines=1'], budget), budget)
    need(len(rows) == 1, 'LATEST_IDENTITY')
    return Cursor(rows[0]['__CURSOR'], rows[0]['_BOOT_ID'])


def snapshot(*, limits=Limits()):
    try:
        return _snapshot(Budget(limits))
    except Incomplete:
        raise
    except Exception:
        raise Incomplete('SNAPSHOT_FAILED') from None


def _values(value):
    if type(value) is str:
        yield value.encode('utf-8')
    elif type(value) is list:
        if value and all(type(x) is int and 0 <= x <= 255 for x in value):
            yield bytes(value)
        else:
            need(bool(value), 'UNSUPPORTED_FIELD')
            for item in value:
                yield from _values(item)
    else:
        # --all should prevent truncated nulls. Unknown encodings fail closed.
        raise Incomplete('UNSUPPORTED_FIELD')


def scan_window(start, patterns, *, limits=Limits()):
    try:
        return _scan(start, patterns, Budget(limits))
    except Incomplete:
        raise
    except Exception:
        raise Incomplete('SCAN_FAILED') from None


def _scan(start, patterns, budget):
    need(type(start) is Cursor and type(start.token) is str and bool(start.token) and
         type(start.boot) is str and bool(start.boot), 'START')
    need(type(patterns) in (list, tuple) and 0 < len(patterns) <= budget.limits.patterns and
         all(type(x) is bytes and 8 <= len(x) <= budget.limits.pattern_bytes for x in patterns), 'PATTERNS')
    anchor = start
    counts = [0] * len(patterns)
    seen = {start.token}
    scanned_records = 0
    pending = []
    for round_number in range(1, budget.limits.rounds + 1):
        end = _snapshot(budget)
        need(end.boot == start.boot, 'BOOT_CHANGED')
        rows = _records(_fetch(['--cursor=' + anchor.token], budget), budget)
        need(rows[0]['__CURSOR'] == anchor.token and rows[0]['_BOOT_ID'] == start.boot, 'START_CURSOR_MISSING')
        tokens = [row['__CURSOR'] for row in rows]
        need(len(tokens) == len(set(tokens)) and all(row['_BOOT_ID'] == start.boot for row in rows), 'CURSOR_CONTINUITY')
        need(all(token not in seen for token in tokens[1:]), 'CURSOR_CONTINUITY')
        need(tokens[1:1 + len(pending)] == pending, 'OBSERVED_TAIL_MISSING')
        need(end.token in tokens, 'END_CURSOR_MISSING')
        cutoff = tokens.index(end.token)
        pending = tokens[cutoff + 1:]
        for row in rows[1:cutoff + 1]:
            token = row['__CURSOR']
            seen.add(token)
            scanned_records += 1
            need(scanned_records <= budget.limits.records, 'RECORD_LIMIT')
            for value in row.values():
                for data in _values(value):
                    for i, pattern in enumerate(patterns):
                        budget.remaining()
                        counts[i] += data.count(pattern)
        latest = _snapshot(budget)
        need(latest.boot == start.boot, 'BOOT_CHANGED')
        if latest == end:
            need(not pending, 'TAIL_REGRESSED')
            return {'status': 'COMPLETE_FINITE_JOURNAL_WINDOW', 'counts': counts,
                    'scanned_bytes': budget.bytes, 'records': scanned_records,
                    'rounds': round_number, 'cutoff_covered': True,
                    'future_writes_covered': False, 'files_covered': False,
                    'privacy_acceptance': False}
        need(latest.token not in seen, 'TAIL_REGRESSED')
        anchor = end
    raise Incomplete('UNDRAINED_JOURNAL_TAIL')
