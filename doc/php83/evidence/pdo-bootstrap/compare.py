"""Require exact typed probe parity between the two independent executions."""
import hashlib, json
from pathlib import Path
here = Path(__file__).resolve().parent
load = lambda name: json.loads((here/name).read_text())
a, b = load('codex-r2.json'), load('claude.json')
def require(value):
    if not value: raise RuntimeError('Independent bootstrap comparison failed')
require(a['functional_checks_passed'] and b['functional_checks_passed'])
for field in ('artifacts', 'harness', 'collector_sha256', 'imported_helper_sha256'):
    require(a[field] == b[field])
require(len(a['rows']) == len(b['rows']) == 2)
for x, y in zip(a['rows'], b['rows']):
    for field in ('variant', 'exit', 'result', 'diagnostics'):
        require(json.dumps(x[field], sort_keys=True) == json.dumps(y[field], sort_keys=True))
    require(x['exit'] == 0 and len(x['result']['rows']) == 23)
previous, candidate = [r['result']['rows'] for r in a['rows']]
allowed = {'set-supported', 'set-unsupported', 'cache-set-on', 'cache-set-off', 'execute-bound', 'execute-array', 'execute-false', 'dryrun-insert', 'dryrun-select'}
changed = []
for x, y in zip(previous, candidate):
    require(x[0] == y[0])
    if json.dumps(x) != json.dumps(y):
        require(x[0] in allowed and x[1] is None and isinstance(y[1], bool))
        changed.append(x[0])
require(set(changed) == allowed)
report = {'independent_exact_typed_rows': 46, 'intentional_null_to_bool_slots': changed,
          'other_rows_identical': True, 'real_dependency_count': 7,
          'harness_identities_equal': True, 'application_acceptance': False,
          'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(here/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print('Independent real-bootstrap typed comparison passed')
