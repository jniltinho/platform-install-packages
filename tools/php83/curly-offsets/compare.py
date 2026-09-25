#!/usr/bin/env python3
"""Compare independently executed curly-only evidence; never application acceptance."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'doc/php83/evidence/curly-offsets'

def read(name):
    return json.loads((EVIDENCE / name).read_text())

def require(condition, message):
    if not condition:
        raise ValueError(message)

def main():
    first, second = read('primary-lab.json'), read('claude-lab.json')
    differences = [key for key in first if first[key] != second.get(key)]
    require(set(first) == set(second), 'Report field drift')
    # Non-authoritative PHPCBF human progress includes truncated random temp paths
    # and elapsed time. Every authoritative tool, source, token and compiler field
    # still compares exactly; both complete summaries remain in original evidence.
    normalized_summaries = [re.sub(r'^\.\.\.\S*?/candidate/', '.../candidate/', body['fix_stdout'], flags=re.M) for body in (first, second)]
    require(normalized_summaries[0] == normalized_summaries[1], 'PHPCBF summary changed beyond temporary path prefixes')
    for body in (first, second):
        require('A TOTAL OF 155 ERRORS WERE FIXED IN 43 FILES' in body['fix_stdout'], 'Unexpected PHPCBF summary')
        require(re.fullmatch(r'\nTime: [0-9.]+ secs; Memory: 38MB\n', body['fix_stderr']) is not None, 'Unexpected PHPCBF stderr')
        body.pop('fix_stdout')
        body.pop('fix_stderr')
    require(first == second, 'Authoritative PHPCBF/source/token/compile drift')
    require(len(first['rows']) == 43, 'Cohort drift')
    require(sum(len(row['proof']['offset_pairs']) for row in first['rows']) == 153, 'Pair drift')
    require(read('primary-token-controls.json') == read('claude-token-controls.json'), 'Native controls differ')
    require(read('claude-token-controls.json')['passed'] is True, 'Native controls failed')
    before, after = read('claude-runtime-before.json'), read('claude-runtime-after.json')
    for body in (before, after):
        for obj in body['objects'].values():
            obj['ldd'] = re.sub(r'\(0x[0-9a-f]+\)', '(ASLR)', obj['ldd'])
    require(before == after, 'Runtime/config/module/library drift beyond ldd ASLR addresses')
    require((EVIDENCE / 'behavior-primary.json').read_bytes() == (EVIDENCE / 'behavior-claude.json').read_bytes(), 'Behavior evidence not byte identical')
    behavior = read('behavior-primary.json')
    require(behavior['functional_checks_passed'] is True, 'Behavior failure')
    require(len(behavior['records']) == 9 and sum(len(r['result']['rows']) for r in behavior['records']) == 204, 'Behavior denominator drift')
    for line in (EVIDENCE / 'primary-frozen-tools-r2.sha256').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, 'Frozen tool drift: ' + name)
    inputs = ['primary-lab.json','claude-lab.json','primary-token-controls.json','claude-token-controls.json','claude-runtime-before.json','claude-runtime-after.json','behavior-primary.json','behavior-claude.json','primary-frozen-tools-r2.sha256']
    result = {'passed': True, 'compile_files': 43, 'offset_pairs': 153,
              'native_control_cases': 11, 'behavior_processes': 9, 'behavior_rows': 204,
              'lab_differing_fields': differences,
              'comparison_exclusions': ['PHPCBF fix_stdout line-leading truncated temporary-path prefixes only', 'PHPCBF fix_stderr elapsed time, fixed validated shape', 'ldd hexadecimal ASLR addresses only'],
              'inputs': {n: hashlib.sha256((EVIDENCE / n).read_bytes()).hexdigest() for n in inputs},
              'comparison_tool_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'application_acceptance': False}
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
