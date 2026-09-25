#!/usr/bin/env python3
"""Check the bounded parser diagnostic reduction without accepting other warnings."""
import argparse
import json
from pathlib import Path

PATHS = {'/audit/app/api_v3/lib/reflection/KalturaDocCommentParser.php',
         '/audit/app/api_v3/lib/reflection/KalturaServicesMap.php'}


def compare(before, after):
    select = lambda report: next(r for r in report['records'] if r['runtime'] == '83' and r['tree'] == 'candidate')
    old, new = select(before), select(after)
    count = lambda row: sum(d['count'] for d in row['diagnostics'] if d['path'] in PATHS)
    result = dict(selected_before=count(old), selected_after=count(new),
                  stdout_unchanged=old['returncode'] == new['returncode'] == 0 and old['stdout'] == new['stdout'],
                  same_harness_hashes=before['harness_hashes'] == after['harness_hashes'])
    result['passed'] = result['selected_before'] > 0 and result['selected_after'] == 0 and result['stdout_unchanged'] and result['same_harness_hashes']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = compare(json.loads(args.before.read_text()), json.loads(args.after.read_text()))
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
