#!/usr/bin/env python3
"""Join frozen provider observations; does not select providers or infer all uses."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
INPUTS = [
    'doc/php83/evidence/provider-runtime/primary-report.json',
    'doc/php83/evidence/provider-runtime/independent-report.json',
    'doc/php83/provider-runtime.md', 'doc/php83/apcu-cache.md',
    'doc/php83/apcu-web.md', 'doc/php83/xml-lifecycle.md',
    'doc/php83/evidence/xml-lifecycle/provider83-extraction.json',
    'doc/php83/evidence/xml-lifecycle/provider74-extraction-r2.json',
    'tools/php83/collect-provider-evidence.py',
]

def build():
    identities = {}
    for name in INPUTS:
        data = (ROOT / name).read_bytes()
        identities[name] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    rows = []
    for name in INPUTS[:2]:
        report = json.loads((ROOT / name).read_text())
        assert report['ok'] is True and report['full_T4_01_acceptance'] is False
        assert set(report['runs']) == {'noble', 'resolute', 'remi'}
        for target, run in sorted(report['runs'].items()):
            assert run['ok'] is True and run['negative_post_rejected'] is True
            assert set(run['probes']) == {'CLI', 'GET', 'POST'}
            for method, probe in sorted(run['probes'].items()):
                assert probe['ok'] is True and probe['failures'] == []
                modules = {value.lower() for value in probe['modules']}
                required = {value.lower() for value in probe['required']}
                assert len(required) == (36 if method == 'CLI' else 35)
                assert required <= modules
                rows.append({'evidence': name, 'target': target, 'method': method,
                             'php': probe['php'], 'sapi': probe['sapi'],
                             'declared_probe_requirements': sorted(required),
                             'loaded_modules': sorted(modules),
                             'soap_loaded': 'soap' in modules,
                             'legacy_apc_loaded': 'apc' in modules,
                             'apcu_loaded': 'apcu' in modules,
                             'memcache_loaded': 'memcache' in modules})
    return {'schema': 1, 'status': 'PARTIAL_PROVIDER_RECONCILIATION',
            'inputs': identities, 'rows': rows,
            'counts': {'observed_rows_including_repeats': len(rows),
                       'unique_target_method_rows': len({(r['target'],r['method']) for r in rows}),
                       'soap_absent_rows': sum(not r['soap_loaded'] for r in rows),
                       'legacy_apc_absent_rows': sum(not r['legacy_apc_loaded'] for r in rows)},
            'runtime_executed_now': False, 'provider_selected': False,
            'full_extension_use_inventory': False,
            'limitations': ['Recorded provider smoke requirements are not the final application requirement set.',
                           'Private Noble SOAP fixtures do not enable SOAP in installed services or prove other providers.',
                           'No APCu alias or unconditional legacy-APC dependency replacement accepted.',
                           'Historical snapshot, not current repository availability or independent binary ABI proof.']}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = build()
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
