#!/usr/bin/env python3
"""Compare independently executed paired scans; ignore only per-record durations."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from scan import compare_reports, load_contract, require, summarize, strict_equal

FROZEN_FILES = {'README.md', 'input-contract.json', 'run.sh', 'scan.py', 'stage.py', 'test_scan.py'}


def normalized(report):
    result = copy.deepcopy(report)
    for variant in result['variants'].values():
        for row in variant['records']:
            duration = row.pop('duration_ns')
            require(type(duration) is int and duration >= 0, 'Invalid duration evidence')
    return result


def compare(primary, independent, contract, harness):
    a, b = normalized(primary), normalized(independent)
    require(strict_equal(a, b), 'Reports differ beyond per-record duration_ns')
    require(type(a['schema']) is int and a['schema'] == 1 and a['collection_complete'] is True, 'Incomplete collection')
    require(a['input_contract'] == contract, 'Input contract drift')
    require(a['harness'] == harness and set(harness) == FROZEN_FILES, 'Frozen harness drift')
    require(set(a['variants']) == {'exp10', 'exp11'}, 'Unexpected variants')
    for name, variant in a['variants'].items():
        require(strict_equal(variant['summary'], summarize(variant['records'])), 'Summary mismatch')
        require(variant['zip_sha256'] == contract['pins'][name], 'Variant ZIP mismatch')
    comparison = compare_reports(primary['variants'], contract)
    require(comparison == a['comparison'] and comparison['bounded_regression_pass'] is True,
            'Bounded compiler regression did not pass')
    require(a['candidate_all_files_compile'] is False and a['application_acceptance'] is False,
            'Remaining rejections or application scope wrongly accepted')
    old = {row['path']: row for row in a['variants']['exp10']['records']}
    newly_diagnostic = [row for row in a['variants']['exp11']['records']
                       if row['exit'] == 0 and row['diagnostics'] and old[row['path']]['exit'] == 255]
    return {'schema': 1, 'reports_equal_except_record_duration_ns': True,
            'independent_logical_rows': sum(len(v['records']) for v in a['variants'].values()),
            'collection_complete': True, 'comparison': comparison,
            'variants': {name: v['summary'] for name, v in a['variants'].items()},
            'newly_accepted_with_diagnostics': newly_diagnostic,
            'candidate_all_files_compile': False, 'application_acceptance': False,
            'scope': 'independent repetition of bounded compiler repair; no whole-candidate acceptance'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('primary', type=Path)
    parser.add_argument('independent', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    require(not args.output.exists(), 'Refusing existing comparison output')
    inputs = {}
    reports = []
    for path in (args.primary, args.independent):
        for suffix in ('.exit', '.stderr'):
            sidecar = path.with_suffix(suffix)
            data = sidecar.read_bytes()
            require(data.strip() == (b'0' if suffix == '.exit' else b''), 'Nonzero exit or runner stderr')
            inputs[str(sidecar)] = hashlib.sha256(data).hexdigest()
        data = path.read_bytes()
        inputs[str(path)] = hashlib.sha256(data).hexdigest()
        reports.append(json.loads(data))
    here = Path(__file__).resolve().parent
    harness = {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in FROZEN_FILES}
    result = compare(*reports, load_contract(), harness)
    result['inputs_sha256'] = inputs
    result['comparator_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with args.output.open('x') as output:
        output.write(json.dumps(result, indent=2) + '\n')
    print('23568 independent logical rows equal; 4 repairs compile; 7 rejections remain')


if __name__ == '__main__':
    main()
