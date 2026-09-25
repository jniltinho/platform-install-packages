#!/usr/bin/env python3
"""Record anonymous dispatch preflight failures; never report API acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path)
args = parser.parse_args()
records = []
for number, host in [('74', 'baseline74'), ('83', 'php83')]:
    result = subprocess.run([
        'ssh', '-F', f'/tmp/kaltura-php{number}-ssh.conf', host,
        'bash /home/vagrant/php-patch-tests/run-one.sh original api-dispatch standard',
    ], capture_output=True, text=True, timeout=90)
    records.append({'runtime': number, 'tree': 'original',
                    'returncode': result.returncode,
                    'stdout': result.stdout, 'stderr': result.stderr})
folder = Path(__file__).resolve().parent
args.output.write_text(json.dumps({
    'scope': 'Anonymous real dispatch with synthetic config and no database; not API acceptance',
    'harness_hashes': {name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
                       for name in ['api-bootstrap.php', 'behavior.php', 'run-one.sh', Path(__file__).name]},
    'records': records,
}, indent=2) + '\n')
print('Diagnostic recorded; configured API acceptance remains pending.')
# Preserve process failure; capture completion is not a passing dispatch test.
raise SystemExit(1 if any(r['returncode'] != 0 for r in records) else 0)
