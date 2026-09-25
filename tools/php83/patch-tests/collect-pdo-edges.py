#!/usr/bin/env python3
"""Collect bounded native-PDO controls; not full application acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path)
args = parser.parse_args()
records = []
failures = []
expected = {
    'fetch-into': {'name': 'alpha', 'seenByConstructor': 'ctor:initial'},
    'props-late': {'name': 'alpha', 'seenByConstructor': 'marker:initial'},
    'positional-column': ['alpha'],
    'named-num': [['alpha']],
    'mixed-named': [['alpha']],
}
for number, host in [('74', 'baseline74'), ('83', 'php83')]:
    config = f'/tmp/kaltura-php{number}-ssh.conf'
    for tree in ['original', 'candidate']:
        command = f'bash /home/vagrant/php-patch-tests/run-one.sh {tree} debug-pdo-edges standard'
        run = subprocess.run(['ssh', '-F', config, host, command], capture_output=True,
                             text=True, timeout=90)
        record = {'runtime': 'php' + number, 'tree': tree, 'returncode': run.returncode,
                  'stdout': run.stdout, 'stderr': run.stderr}
        records.append(record)
        if number == '83' and tree == 'original':
            if run.returncode == 0 or 'Declaration of DebugPDO::query() must be compatible' not in run.stderr:
                failures.append('Original 8.3 failure differs from pinned signature blocker')
            continue
        if run.returncode != 0:
            failures.append(f'{host}/{tree}: execution failed')
            continue
        values = json.loads(run.stdout)
        wanted = 12 if number == '74' else 24
        if len(values) - 1 != wanted:
            failures.append(f'{host}/{tree}: unexpected case count')
        for value in values[1:]:
            name = value['1']
            if not value['matches_native']:
                failures.append(f'{host}/{tree}/{name}: differs from native PDO')
            if name in expected:
                for cls in ['PDO', 'DebugPDO']:
                    if value['2'][cls] != ['return', expected[name]]:
                        failures.append(f'{host}/{tree}/{name}/{cls}: positive fixture did not succeed')
    if number == '74' and all(r['returncode'] == 0 for r in records[:2]):
        if records[0]['stdout'] != records[1]['stdout']:
            failures.append('Patched 7.4 edge output differs from original')
folder = Path(__file__).resolve().parent
report = {'policy': 'Native return/error controls; diagnostics retained, not waived; no release approval',
          'harness_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [folder / 'behavior.php', folder / 'debug-pdo-edges.php',
                                       folder / 'run-one.sh', Path(__file__)]},
          'records': records, 'failures': failures}
args.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'failures': failures, 'candidate_native_comparisons': 36}))
sys.exit(bool(failures))
