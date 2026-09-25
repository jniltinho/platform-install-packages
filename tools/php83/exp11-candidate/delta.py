#!/usr/bin/env python3
"""Independent byte-level exp10-to-exp11 archive delta, without PHP execution."""
import argparse
import io
import json
from pathlib import Path
import zipfile
import selected

stage = selected.stage
EXP10_PIN = 'de177e6cbaedf3a3207661c2325f466cce37febb73190f3a49d31f24b740c053'


def compare(old_bytes, new_bytes, prior, current):
    stage.require(current['patches'][:59] == prior['patches'] and len(current['patches']) == 63, 'Selection prefix/count drift')
    prefix = current['upstream_root'] + '/'
    meta = prefix + '.php83-experimental/'
    new_rows = current['patches'][59:]
    stage.require([r['path'] for r in new_rows] == stage.TARGETS, 'New target order drift')
    with zipfile.ZipFile(io.BytesIO(old_bytes)) as old, zipfile.ZipFile(io.BytesIO(new_bytes)) as new:
        left, right = set(old.namelist()), set(new.namelist())
        stage.require(len(left) == len(old.namelist()) and len(right) == len(new.namelist()), 'Duplicate ZIP members')
        expected_added = {meta + r['patch'] for r in new_rows}
        stage.require(not left - right and right - left == expected_added, 'Unexpected additions/removals')
        changed = {p for p in left if old.read(p) != new.read(p)}
        expected_changed = {prefix + r['path'] for r in new_rows} | {meta + 'manifest.json'}
        stage.require(changed == expected_changed, 'Unexpected content delta')
        for r in prior['patches']:
            p = prefix + r['path']
            stage.require(old.read(p) == new.read(p) and stage.digest(new.read(p)) == r['after_sha256'], 'Prior target drift')
        for r in new_rows:
            p = prefix + r['path']
            stage.require(stage.digest(old.read(p)) == r['before_sha256'] and stage.digest(new.read(p)) == r['after_sha256'], 'New target hash mismatch')
            stage.require(stage.digest(new.read(meta + r['patch'])) == r['sha256'], 'New patch hash mismatch')
        embedded = json.loads(new.read(meta + 'manifest.json'))
        stage.require(all(embedded.get(k) == v for k, v in current.items()), 'Embedded selected metadata mismatch')
    return {'status': 'PASS_LAB_ARTIFACT_DELTA_ONLY', 'exp10_sha256': stage.digest(old_bytes),
            'exp11_sha256': stage.digest(new_bytes), 'prior_targets_preserved': 59,
            'changed_application_paths': [r['path'] for r in new_rows],
            'changed_metadata': [meta + 'manifest.json'], 'added_metadata': sorted(expected_added),
            'exp10_entries': len(left), 'exp11_entries': len(right),
            'all_other_entry_bytes_identical': True, 'application_acceptance': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['exp10', 'exp11', 'output']: p.add_argument(name, type=Path)
    args = p.parse_args()
    stage.require(not args.output.exists(), 'Refuse existing delta report')
    old_bytes, new_bytes = args.exp10.read_bytes(), args.exp11.read_bytes()
    stage.require(stage.digest(old_bytes) == EXP10_PIN, 'Exp10 pin mismatch')
    current = selected.validate_selected(stage.MANIFEST.read_bytes(), selected.SELECTED.read_bytes())
    path, pin = stage.INPUTS['prior']
    prior_bytes = stage.repo_bytes(path)
    stage.require(stage.digest(prior_bytes) == pin, 'Prior manifest drift')
    result = compare(old_bytes, new_bytes, json.loads(prior_bytes), current)
    result['verifier_sha256'] = stage.digest(Path(__file__).read_bytes())
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))

if __name__ == '__main__': main()
