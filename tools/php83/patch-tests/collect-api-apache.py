#!/usr/bin/env python3
"""Capture loopback HTTP front-controller checks without saving KS-bearing application logs."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('api_mysql', HERE / 'collect-api-mysql.py')
mysql = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mysql)


def diagnostics(stderr):
    # Keep locations/counts, not SQL, exception arguments, token hashes or KS.
    stderr = re.sub(r'^\[[^\n]*?\] ', '', stderr, flags=re.MULTILINE)
    counts = Counter(re.findall(r'^(?:PHP )?(Deprecated|Warning|Notice|Fatal error|Parse error): .*? in (/audit/[a-zA-Z0-9_./-]+) on line (\d+)$', stderr, re.MULTILINE))
    for p, n in re.findall(r'^(/audit/[a-zA-Z0-9_./-]+) line (\d+) - ', stderr, re.MULTILINE):
        counts[('ApplicationDiagnostic', p, n)] += 1
    return [dict(severity=s, path=p, line=int(n), count=c)
            for (s, p, n), c in sorted(counts.items())]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    names = ['api-permission-schema.sql', 'api-session-schema.sql',
             'run-api-apache.sh', 'api-web-router.php', 'api-apache-inner.sh', 'api-http-client.py']
    expected = {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names}
    check = subprocess.run(['ssh', '-F', '/tmp/kaltura-php74-ssh.conf', 'baseline74',
                            'cd /home/vagrant/php-patch-tests && sha256sum ' + ' '.join(names)],
                           check=True, capture_output=True, text=True, timeout=30)
    remote = {line.split()[1]: line.split()[0] for line in check.stdout.splitlines()}
    if remote != expected:
        raise RuntimeError('Remote fixture hash mismatch')
    records = []
    for runtime in ['74', '83']:
        for tree in ['original', 'candidate']:
            command = ('bash /home/vagrant/php-patch-tests/run-api-apache.sh '
                       + runtime + ' ' + tree
                       + ' "$(cat /home/vagrant/php-mysql-probe/current-path)"')
            result = subprocess.run(['ssh', '-F', '/tmp/kaltura-php74-ssh.conf', 'baseline74', command],
                                    capture_output=True, text=True, timeout=90)
            records.append(dict(runtime=runtime, tree=tree, returncode=result.returncode,
                                stdout=result.stdout, diagnostics=diagnostics(result.stderr),
                                runtime_observations=[json.loads(line.split('PROBE_RUNTIME ', 1)[1]) for line in result.stderr.splitlines() if 'PROBE_RUNTIME {' in line],
                                signature_failure='Declaration of KalturaPDO::query() must be compatible' in result.stderr,
                                stderr_sha256=hashlib.sha256(result.stderr.encode()).hexdigest()))
    matches = mysql.comparisons(records)
    fatal = next(r for r in records if r['runtime'] == '83' and r['tree'] == 'original')['signature_failure']
    names = ['api-permission-schema.sql', 'api-session-schema.sql',
             'run-api-apache.sh', 'api-web-router.php', 'api-apache-inner.sh', 'api-http-client.py', 'collect-api-mysql.py', Path(__file__).name]
    report = dict(scope='Real web/index.php under isolated Apache mod_php HTTP and trusted HTTPS; NOT full installed AIO/FPM acceptance',
                  logs='Only diagnostic locations/counts retained; full stderr hash is provenance, not sanitized log content',
                  harness_hashes={n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names},
                  remote_harness_hashes=remote, comparisons=matches, original83_signature_failure_reproduced=fatal, records=records)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(matches))
    return 0 if fatal and all(r['matches_baseline'] for r in matches) else 1


if __name__ == '__main__':
    raise SystemExit(main())
