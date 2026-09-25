#!/usr/bin/env python3
"""Collect the synthetic connection/hydration/serializer probe on baseline74.

Requires the dedicated socket-only server and held source already prepared.
Does not start a server or change sources. Stop the probe server after use.
"""
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
comparisons = []
failures = []
for runtime in ['74', '83']:
    for tree in ['original', 'candidate']:
        command = ('d=$(cat /home/vagrant/php-mysql-probe/current-path); '
                   f'bash /home/vagrant/php-patch-tests/run-mysql-types.sh {runtime} {tree} "$d" init')
        run = subprocess.run(['ssh', '-F', '/tmp/kaltura-php74-ssh.conf', 'baseline74', command],
                             capture_output=True, text=True, timeout=90)
        records.append({'runtime': runtime, 'tree': tree, 'returncode': run.returncode,
                        'stdout': run.stdout, 'stderr': run.stderr})
        expected = 255 if runtime == '83' and tree == 'original' else 0
        if run.returncode != expected:
            failures.append(f'{runtime}/{tree}: unexpected exit {run.returncode}')
        if expected == 255 and 'Declaration of DebugPDO::query() must be compatible' not in run.stderr:
            failures.append('Original 8.3 did not reproduce the signature blocker')
if not failures:
    base = json.loads(records[0]['stdout'])['results']
    for record in records:
        if record['returncode']:
            continue
        values = json.loads(record['stdout'])['results']
        if len(values) != 4:
            failures.append('Expected four configurations')
        for before, after in zip(base, values):
            raw_match = after['raw_json'] == before['raw_json']
            hydrated_match = after['hydrated_json'] == before['hydrated_json']
            expected_raw = not (record['runtime'] == '83' and after['case'] == 'unspecified')
            if not hydrated_match or raw_match != expected_raw or after['case'] != before['case']:
                failures.append(f"Unexpected contract result: {record['runtime']}/{after['case']}")
            comparisons.append({'runtime': record['runtime'], 'tree': record['tree'],
                                'case': after['case'], 'raw_json_matches_74': raw_match,
                                'hydrated_json_matches_74': hydrated_match})
folder = Path(__file__).resolve().parent
report = {'policy': 'Characterization only: the known raw JSON mismatch is recorded, not waived',
          'records': records, 'comparisons': comparisons, 'failures': failures,
          'harness_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in [folder / 'mysql-init.php', folder / 'run-mysql-types.sh', Path(__file__)]},
          'source_patch': 'held/DebugPDO-query-v3.json',
          'runtime_provenance': '../mysql-types/runtime-inputs.txt; v2 source hash superseded by v3'}
args.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'failures': failures, 'comparisons': comparisons}))
sys.exit(bool(failures))
