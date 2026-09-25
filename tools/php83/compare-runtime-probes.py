#!/usr/bin/env python3
"""Compare reports from an identical harness; report failures without waiving them."""
import argparse
import json
from pathlib import Path


def compare(baseline, candidate):
    for field in ['probe_sha256', 'runner_sha256', 'wrapper_sha256', 'php_flags']:
        if field not in baseline or baseline[field] != candidate.get(field):
            raise ValueError('Incomparable harness: ' + field)
    left = baseline['results']
    right = candidate['results']
    names = [r['probe'] for r in left]
    if names != [r['probe'] for r in right] or len(set(names)) != len(names):
        raise ValueError('Different or duplicate probe sets')
    rows = []
    for a, b in zip(left, right):
        if a.get('timeout') or b.get('timeout') or None in (a['returncode'], b['returncode']):
            classification = 'incomplete: timeout or missing result'
        elif a['returncode'] == 0 and b['returncode'] != 0:
            classification = 'new failing library probe'
        elif a['returncode'] == 0 and b['returncode'] == 0:
            classification = ('successful fixed probe; inspect diagnostics'
                              if a.get('expected_output_matches') and b.get('expected_output_matches')
                              else 'output mismatch or unchecked output; investigate')
        else:
            classification = 'baseline failure; investigate before attributing regression'
        rows.append({'probe': a['probe'], 'php74_exit': a['returncode'],
                     'php83_exit': b['returncode'], 'classification': classification})
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('candidate', type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(json.loads(args.baseline.read_text()),
                             json.loads(args.candidate.read_text())), indent=2))
