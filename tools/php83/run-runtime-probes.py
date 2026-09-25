#!/usr/bin/env python3
"""Run fixed public-library probes, not full Kaltura acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('root', type=Path)
p.add_argument('php')
p.add_argument('output', type=Path)
a = p.parse_args()
root = a.root.resolve(strict=True)
probe = Path(__file__).with_name('runtime-probes.php')
records = []
for name in ['zend_application', 'zend_registry', 'zend_config', 'propel_load', 'legacy_json']:
    run = subprocess.run([a.php, '-d', 'allow_url_fopen=0', '-d', 'allow_url_include=0',
                          str(probe), str(root), name], capture_output=True, text=True, timeout=30)
    records.append({'probe': name, 'returncode': run.returncode,
                    'stdout': run.stdout.replace(str(root), '<public-app>'),
                    'stderr': run.stderr.replace(str(root), '<public-app>')})
a.output.write_text(json.dumps({'php': subprocess.check_output([a.php, '-v'], text=True).splitlines()[0],
    'probe_sha256': hashlib.sha256(probe.read_bytes()).hexdigest(),
    'scope': 'Fixed unpatched library probes; no full application reachability claim',
    'results': records}, indent=2) + '\n')
print([(x['probe'], x['returncode']) for x in records])
