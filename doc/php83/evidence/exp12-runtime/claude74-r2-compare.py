#!/usr/bin/env python3
"""Compare claude74 r2 repeat (generator r2 + snapshots) and prior API/CLI74/curly/additions reports with primary; every difference path is listed, allowances are explicit."""
import hashlib, json, re, sys
from pathlib import Path

E = Path('doc/php83/evidence/exp12-runtime')
# (label, repeat, primary, allowed-difference path regexes)
PAIRS = [
    ('r2-runtime-before-vs-after', 'claude-r2-runtime-before.json', 'claude-r2-runtime-after.json', []),
    ('r2-runtime-before-vs-primary-before', 'claude-r2-runtime-before.json', 'runtime-before.json', []),
    ('r2-runtime-after-vs-primary-after', 'claude-r2-runtime-after.json', 'runtime-after.json', []),
    ('r2-runtime-before-vs-generator-primary-before', 'claude-r2-runtime-before.json', 'generator-runtime-before.json', []),
    ('r2-runtime-after-vs-generator-primary-after', 'claude-r2-runtime-after.json', 'generator-runtime-after.json', []),
    ('api', 'claude-api.json', 'api-primary.json',
     [r'^/records/\d+/duration_ns$', r'^/records/\d+/stderr_sha256$', r'^/db/(datadir|unit)$', r'^/cleanup/unit$']),
    ('cli74', 'claude-cli74.json', 'cli74-primary.json', [r'^/recorded_at_utc$', r'^/rows/\d+/duration_ns$']),
    ('curly', 'claude-curly.json', 'curly-primary.json', []),
    ('additions', 'claude-additions.json', 'additions-primary.json', []),
    ('additions-post-source', 'claude-additions-post-source.json', 'additions-post-source.json', []),
    ('additions-revalidated', 'claude-additions-revalidated.json', 'additions-primary-revalidated.json', [r'^/input_sha256$', r'^/post_source_sha256$']),
    ('generator', 'claude-generator-r2.json', 'generator-primary.json', []),
    ('generator-validation', 'claude-generator-r2-validation.json', 'generator-validation.json', [r'^/input_sha256$']),
]


def diff(a, b, path=''):
    if type(a) is not type(b):
        return [path or '/']
    if isinstance(a, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            p = f'{path}/{k}'
            out += [p] if (k in a) != (k in b) else diff(a[k], b[k], p)
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return [f'{path}#len']
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in diff(x, y, f'{path}/{i}')]
    return [] if a == b else [path or '/']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(output):
    result = {}
    for label, rep, pri, allowed in PAIRS:
        r, p = E / rep, E / pri
        paths = diff(json.loads(r.read_text()), json.loads(p.read_text()))
        unexpected = [d for d in paths if not any(re.search(a, d) for a in allowed)]
        result[label] = {'repeat': str(r), 'repeat_sha256': sha(r), 'primary': str(p), 'primary_sha256': sha(p),
                         'bytes_identical': r.read_bytes() == p.read_bytes(), 'allowances': allowed,
                         'allowed_difference_paths': sorted(set(paths) - set(unexpected)),
                         'unexpected_difference_paths': unexpected, 'match': not unexpected}
    summary = {'pairs': result, 'all_match': all(v['match'] for v in result.values()), 'application_acceptance': False,
               'comparator_sha256': sha(Path(__file__))}
    with open(output, 'x') as f:
        json.dump(summary, f, indent=2)
        f.write('\n')
    print(json.dumps({k: [v['match'], v['bytes_identical'], len(v['allowed_difference_paths']), len(v['unexpected_difference_paths'])] for k, v in result.items()}))
    return 0 if summary['all_match'] else 1


if __name__ == '__main__':
    assert diff({'a': [1, {'b': 2}]}, {'a': [1, {'b': 3}]}) == ['/a/1/b'] and diff([1], [1, 2]) == ['#len']
    sys.exit(main(sys.argv[1]))
