#!/usr/bin/env python3
"""Host-side collection from the two preconfigured disposable labs only."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path)
parser.add_argument('--case', action='append', choices=['registry', 'legacy-json', 'zend-json'])
args = parser.parse_args()
cases = args.case or ['registry', 'legacy-json', 'zend-json']
records = []
environments = []
folder = Path(__file__).resolve().parent
for number, host in [('74', 'baseline74'), ('83', 'php83')]:
    config = f'/tmp/kaltura-php{number}-ssh.conf'
    for mode in ['standard', 'minimal']:
        env = subprocess.run(['ssh', '-F', config, host,
            f'bash /home/vagrant/php-patch-tests/run-one.sh original environment {mode}'],
            capture_output=True, text=True, timeout=90, check=True)
        environments.append({'runtime': 'php' + number, 'mode': mode, **json.loads(env.stdout)})
        for tree in ['original', 'candidate']:
            for case in cases:
                run = subprocess.run(['ssh', '-F', config, host,
                    f'bash /home/vagrant/php-patch-tests/run-one.sh {tree} {case} {mode}'],
                    capture_output=True, text=True, timeout=90)
                records.append({'runtime': 'php' + number, 'tree': tree, 'case': case,
                                'mode': mode, 'returncode': run.returncode,
                                'stdout': run.stdout, 'stderr': run.stderr})
comparisons = []
for mode in ['standard', 'minimal']:
    for case in cases:
        baseline = next(r for r in records if r['runtime'] == 'php74'
                        and r['tree'] == 'original' and r['case'] == case and r['mode'] == mode)
        if baseline['returncode'] != 0:
            raise RuntimeError('Baseline fixture failed: ' + case)
        for runtime in ['php74', 'php83']:
            candidate = next(r for r in records if r['runtime'] == runtime
                             and r['tree'] == 'candidate' and r['case'] == case and r['mode'] == mode)
            comparisons.append({'runtime': runtime, 'case': case, 'mode': mode,
                                'matches_baseline': candidate['returncode'] == 0
                                and candidate['stdout'] == baseline['stdout']})
report = {'environments': environments,
          'diagnostic_policy': 'stdout and roundtrip parity required; stderr retained, not waived',
          'harness_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
          for p in [folder / 'behavior.php', folder / 'run-one.sh', Path(__file__)]},
          'comparisons': comparisons, 'records': records}
args.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(comparisons))
if not all(c['matches_baseline'] for c in comparisons):
    sys.exit(1)
