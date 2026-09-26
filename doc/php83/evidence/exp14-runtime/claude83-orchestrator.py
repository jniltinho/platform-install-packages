#!/usr/bin/env python3
"""Native83 exp14 independent repeat (CLI36 + snapshots): ordered phases, append-only ledger, finally after-snapshot."""
import datetime, hashlib, json, os, subprocess, sys
from pathlib import Path

E = 'doc/php83/evidence/exp14-runtime'
T = 'tools/php83/exp14-api'
LEDGER = Path(E) / 'claude83-execution-ledger.jsonl'
TIMEOUT = 1200
# (phase, command, output, stdout_is_output, expected_exit)
PHASES = [
 ('claude83-runtime-before', ['python3', f'{T}/runtime83-identity.py', f'{E}/claude83-runtime-before.json'], f'{E}/claude83-runtime-before.json', False, 0),
 ('claude83-original-before', ['python3',f'{T}/original-source-identity.py','83',f'{E}/claude83-original-before.json'],f'{E}/claude83-original-before.json',False,0),
 ('claude-cli83', ['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83','python3 /home/vagrant/php-exp14-regression/exp14-regression/batch.py'], f'{E}/claude-cli83.json', True, 0),
]
FINAL = ('claude83-runtime-after', ['python3', f'{T}/runtime83-identity.py', f'{E}/claude83-runtime-after.json'], f'{E}/claude83-runtime-after.json', False, 0)



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
        f.write(json.dumps({'phase': 'orchestrator', 'recorded_at_utc': now(), 'orchestrator_sha256': sha(__file__), 'executor': 'Actual OpenCode Muse CLI independent executor (historical claude output label retained)', 'host_scope': 'native83 only'}, sort_keys=True) + '\n')
    stopped = None
    try:
        for p in PHASES:
            if not run(*p):
                stopped = p[0]
                break
    finally:
        original_after_ok = run('claude83-original-after',['python3',f'{T}/original-source-identity.py','83',f'{E}/claude83-original-after.json'],f'{E}/claude83-original-after.json',False,0)
        after_ok = run(*FINAL) and original_after_ok
        append({'phase': 'orchestrator-terminal', 'recorded_at_utc': now(), 'stopped_at_unexpected_exit': stopped, 'after_snapshot_exit_as_expected': after_ok})
    return 0 if stopped is None and after_ok else 1


if __name__ == '__main__':
    sys.exit(main())
