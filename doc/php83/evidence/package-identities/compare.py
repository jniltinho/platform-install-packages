"""Exact independent package inventory parity, not finding adjudication."""
import hashlib, json
from pathlib import Path
base = Path(__file__).resolve().parent
reports = [base/name for name in ('primary.json', 'primary-repeat.json', 'claude.json')]
def require(value, message):
    if not value: raise RuntimeError(message)
raw = [p.read_bytes() for p in reports]
require(raw[0] == raw[1] == raw[2], 'Independent bytes differ')
j = json.loads(raw[0])
repo = base.parents[3]
for name, sha in j['inputs'].items():
    source = repo/'tools/php83/package-identities/build.py' if name == 'builder' else repo/'doc/php83/evidence'/name
    require(hashlib.sha256(source.read_bytes()).hexdigest() == sha, 'Input drift: '+name)
require(j['summary']['packages'] == len(j['packages']) == 17, 'Package count')
require(j['summary']['unique_php_paths'] == len(j['files']) == 13454, 'File count')
require(len(j['ledger_joins']) == 941, 'Join count')
require(sum(r['status'] == 'missing_identity_resolved' for r in j['ledger_joins']) == 792, 'Resolved count')
require(sum(r['status'] == 'known_identity_preserved' for r in j['ledger_joins']) == 149, 'Preserved count')
for row in j['ledger_joins']:
    require(row['sha256'] == j['files'][row['path']]['sha256'], 'Payload join mismatch')
    require(row['owners'] == j['files'][row['path']]['owners'], 'Owner mismatch')
    require(not row['previous_sha256'] or row['previous_sha256'] == row['sha256'], 'Prior hash drift')
result = {'independent_reports': [p.name for p in reports], 'all_bytes_identical': True,
          'sha256': hashlib.sha256(raw[0]).hexdigest(), 'inputs_still_match': True,
          'packages': 17, 'php_family_files': 13454, 'resolved_missing':792, 'preserved_known':149,
          'semantic_findings_resolved':0, 't0_04_complete':False,
          'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(base/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print('Three byte-identical inventories and all941 joins verified')
