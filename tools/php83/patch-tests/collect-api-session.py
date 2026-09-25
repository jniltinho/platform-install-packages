#!/usr/bin/env python3
"""Capture bounded session checks without saving KS-bearing application logs."""
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
    counts = Counter(re.findall(r'^(?:PHP )?(Deprecated|Warning|Notice|Fatal error|Parse error): .*? in (/audit/[a-zA-Z0-9_./-]+) on line (\d+)$', stderr, re.MULTILINE))
    return [dict(severity=s, path=p, line=int(n), count=c)
            for (s, p, n), c in sorted(counts.items())]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    records = []
    for runtime in ['74', '83']:
        for tree in ['original', 'candidate']:
            command = ('bash /home/vagrant/php-patch-tests/run-api-session.sh '
                       + runtime + ' ' + tree
                       + ' "$(cat /home/vagrant/php-mysql-probe/current-path)"')
            result = subprocess.run(['ssh', '-F', '/tmp/kaltura-php74-ssh.conf', 'baseline74', command],
                                    capture_output=True, text=True, timeout=90)
            records.append(dict(runtime=runtime, tree=tree, returncode=result.returncode,
                                stdout=result.stdout, diagnostics=diagnostics(result.stderr),
                                signature_failure='Declaration of KalturaPDO::query() must be compatible' in result.stderr,
                                stderr_sha256=hashlib.sha256(result.stderr.encode()).hexdigest()))
    matches = mysql.comparisons(records)
    fatal = next(r for r in records if r['runtime'] == '83' and r['tree'] == 'original')['signature_failure']
    names = ['api-bootstrap.php', 'api-permission-schema.sql', 'api-session.php', 'api-session-schema.sql',
             'run-api-session.sh', 'collect-api-mysql.py', Path(__file__).name]
    report = dict(scope='Direct SessionService action + real KS parse/validation and synthetic SQL; NOT HTTP/authenticated dispatcher acceptance',
                  logs='Only diagnostic locations/counts retained; full stderr hash is provenance, not sanitized log content',
                  harness_hashes={n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names},
                  comparisons=matches, original83_signature_failure_reproduced=fatal, records=records)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(matches))
    return 0 if fatal and all(r['matches_baseline'] for r in matches) else 1


if __name__ == '__main__':
    raise SystemExit(main())
