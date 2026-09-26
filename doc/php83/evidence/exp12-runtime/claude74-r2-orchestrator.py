#!/usr/bin/env python3
"""Independent baseline74 exp12 r2 repeat (generator72 + snapshots only): ordered phases, append-only ledger, finally after-snapshot."""
import datetime, hashlib, json, os, subprocess, sys
from pathlib import Path

E = 'doc/php83/evidence/exp12-runtime'
T = 'tools/php83/exp12-api'
LEDGER = Path(E) / 'claude74-r2-execution-ledger.jsonl'
TIMEOUT = 900
# (phase, command, output, stdout_is_output, expected_exit)
PHASES = [
    ('claude-r2-runtime-before', ['python3', f'{T}/runtime-identity.py', f'{E}/claude-r2-runtime-before.json'], f'{E}/claude-r2-runtime-before.json', False, 0),
    ('claude-generator-r2', ['python3', f'{T}/generator/collect.py', '--phase', 'generate', f'{E}/claude-generator-r2.json'], f'{E}/claude-generator-r2.json', False, 2),
    ('claude-generator-r2-validation', ['python3', f'{T}/generator/validate.py', f'{E}/claude-generator-r2.json', f'{E}/claude-generator-r2-validation.json'], f'{E}/claude-generator-r2-validation.json', False, 0),
]
FINAL = ('claude-r2-runtime-after', ['python3', f'{T}/runtime-identity.py', f'{E}/claude-r2-runtime-after.json'], f'{E}/claude-r2-runtime-after.json', False, 0)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    p = Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def append(entry):
    with LEDGER.open('a') as f:
        f.write(json.dumps(entry, sort_keys=True) + '\n')
        f.flush()
        os.fsync(f.fileno())


def run(phase, command, output, stdout_is_output, expected):
    streams = {k: Path(E) / f'{phase}.{k}' for k in ('stdout', 'stderr', 'exit')}
    targets = [Path(output), *streams.values()]
    if any(p.exists() for p in targets):
        raise FileExistsError(f'{phase}: refusing to overwrite existing evidence')
    started = now()
    try:
        r = subprocess.run(command, capture_output=True, timeout=TIMEOUT, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        code, out, err, note = r.returncode, r.stdout, r.stderr, None
    except subprocess.TimeoutExpired as e:
        code, out, err, note = None, e.stdout or b'', e.stderr or b'', f'timeout {TIMEOUT}s'
    finished = now()
    for p, data in [(streams['stdout'], out), (streams['stderr'], err), (streams['exit'], f'{code}\n'.encode())]:
        with p.open('xb') as f:
            f.write(data)
    if stdout_is_output:
        with Path(output).open('xb') as f:
            f.write(out)
    entry = {'phase': phase, 'command': command, 'started_at_utc': started, 'finished_at_utc': finished,
             'process_exit': code, 'expected_exit': expected, 'exit_as_expected': code == expected,
             'output': output, 'output_sha256': sha(output),
             **{f'{k}_path': str(p) for k, p in streams.items()}, **{f'{k}_sha256': sha(p) for k, p in streams.items()}}
    if note:
        entry['note'] = note
    append(entry)
    return code == expected


def main():
    with LEDGER.open('x') as f:
        f.write(json.dumps({'phase': 'orchestrator', 'recorded_at_utc': now(), 'orchestrator_sha256': sha(__file__), 'executor': 'Claude Code CLI (claude-opus-5-5)', 'host_scope': 'baseline74 only'}, sort_keys=True) + '\n')
    stopped = None
    try:
        for p in PHASES:
            if not run(*p):
                stopped = p[0]
                break
    finally:
        after_ok = run(*FINAL)
        append({'phase': 'orchestrator-terminal', 'recorded_at_utc': now(), 'stopped_at_unexpected_exit': stopped, 'after_snapshot_exit_as_expected': after_ok})
    return 0 if stopped is None and after_ok else 1


if __name__ == '__main__':
    sys.exit(main())
