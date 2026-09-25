#!/usr/bin/env python3
"""Compare real API dispatch over the isolated synthetic MariaDB fixture."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def comparisons(records):
    baseline = next(r for r in records if r['runtime'] == '74' and r['tree'] == 'original')
    return [{'runtime': r['runtime'], 'matches_baseline': baseline['returncode'] == 0
             and r['returncode'] == 0 and r['stdout'] == baseline['stdout']}
            for r in records if r['tree'] == 'candidate']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    records = []
    for runtime in ['74', '83']:
        for tree in ['original', 'candidate']:
            command = ('bash /home/vagrant/php-patch-tests/run-api-mysql.sh '
                       + runtime + ' ' + tree
                       + ' "$(cat /home/vagrant/php-mysql-probe/current-path)"')
            result = subprocess.run(['ssh', '-F', '/tmp/kaltura-php74-ssh.conf',
                                     'baseline74', command], capture_output=True, text=True, timeout=90)
            controls = [json.loads(line.removeprefix('PDO_CONTROL '))
                        for line in result.stderr.splitlines() if line.startswith('PDO_CONTROL ')]
            records.append({'runtime': runtime, 'tree': tree, 'returncode': result.returncode,
                            'stdout': result.stdout, 'stderr': result.stderr, 'pdo_controls': controls})
    matches = comparisons(records)
    original83 = next(r for r in records if r['runtime'] == '83' and r['tree'] == 'original')
    fatal_reproduced = original83['returncode'] != 0 and 'Declaration of KalturaPDO::query() must be compatible' in original83['stderr']
    folder = Path(__file__).resolve().parent
    report = {'scope': 'CLI dispatch using real DbManager/KalturaPDO/permission queries; no HTTP or authenticated session',
              'host': 'kaltura-php74-baseline; PHP 8.3 executable/modules copied from isolated .83',
              'harness_hashes': {name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
                                 for name in ['api-bootstrap.php', 'api-permission-schema.sql', 'behavior.php',
                                              'run-api-mysql.sh', Path(__file__).name]},
              'original83_signature_failure_reproduced': fatal_reproduced,
              'comparisons': matches, 'records': records}
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(matches))
    return 0 if fatal_reproduced and all(r['matches_baseline'] for r in matches) else 1


if __name__ == '__main__':
    raise SystemExit(main())
