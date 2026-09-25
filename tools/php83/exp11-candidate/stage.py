#!/usr/bin/env python3
"""Prepare unapproved exp11 inputs with exact private-copy replay; never build a ZIP."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tempfile
import zipfile

REPO = Path(__file__).resolve().parents[3]
MANIFEST = REPO / 'doc/php83/evidence/exp11-candidate/manifest.json'
ORIGINAL = '58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
ROOT = 'server-Rigel-18.20.0'
INPUTS = {
    'prior': ('doc/php83/evidence/exp10-candidate/manifest.json', 'db4c2b6dfff31f9fd64e05f29e0ccd79b2049e85e7c27ee29b2783605db387aa'),
    'ternary': ('patches/php83/held/base-object-ternary/manifest.json', 'df50a1afaf236d33153f8e2f6e1b865457875c6657c87ec1aa0b345fee709700'),
    'purifier': ('patches/php83/held/autoload83/HTMLPurifier-autoload.json', 'd914414f8fa00ff793f714797c3788241b1231dcbf99296640adbbe110874b2d'),
    'cli': ('patches/php83/held/autoload83/symfony-cli-autoload.json', 'b3052352913617f362807c75a6cb30cc0b72c5731d291282440c6cad0f5b8ecb'),
    'core': ('patches/php83/held/symfony-bootstrap.json', 'd467a1b95baf5367ca807180ebabce222e9cb2f7f9f4f429271ed0e08431ecca'),
}
TARGETS = ['alpha/apps/kaltura/lib/baseObjectUtils.class.php',
           'vendor/htmlpurifier/library/HTMLPurifier.autoload.php',
           'vendor/symfony-data/bin/symfony.php', 'vendor/symfony/util/sfCore.class.php']


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_relative(value):
    require(isinstance(value, str) and value and not PurePosixPath(value).is_absolute()
            and all(p not in ('', '.', '..') for p in value.split('/'))
            and '\\' not in value and not any(ord(c) < 32 for c in value), 'Unsafe input path')
    return value


def repo_bytes(relative):
    path = REPO / safe_relative(relative)
    require(not path.is_symlink() and path.resolve().is_relative_to(REPO.resolve()), 'Unsafe repository source')
    return path.read_bytes()


def provenance():
    return [{'role': role, 'path': path, 'sha256': pin} for role, (path, pin) in INPUTS.items()]


def normalize(row, source_patch, patch_hash):
    return {'patch': PurePosixPath(source_patch).name, 'sha256': patch_hash,
            'path': row['path'], 'before_sha256': row['before_sha256'],
            'after_sha256': row['after_sha256'], 'source_patch': source_patch}


def expected_selection(documents):
    prior = documents['prior']
    require(prior['revision'] == 'exp10' and prior['upstream_sha256'] == ORIGINAL
            and prior['upstream_root'] == ROOT and prior['target_php'] == '8.3', 'Wrong prior identity')
    require(len(prior['patches']) == 59, 'Expected 59 prior entries')
    ternary = documents['ternary']
    changed = [r for r in ternary['files'] if r['before_sha256'] != r['after_sha256']]
    require(len(changed) == 1 and changed[0]['path'] == TARGETS[0], 'Unexpected ternary changed set')
    additional = [normalize(changed[0], 'patches/php83/held/base-object-ternary/base-object-ternary.patch', ternary['patch_sha256'])]
    for role, target in [('purifier', TARGETS[1]), ('cli', TARGETS[2])]:
        row = documents[role]
        require(row['path'] == target, 'Wrong autoload target')
        source = str(PurePosixPath(INPUTS[role][0]).parent / row['patch'])
        additional.append(normalize(row, source, row['sha256']))
    core = [r for r in documents['core']['files'] if r['path'] == TARGETS[3]]
    require(len(core) == 1, 'Missing/duplicate existing sfCore metadata')
    additional.append(normalize(core[0], core[0]['patch'], core[0]['patch_sha256']))
    expected = prior['patches'] + additional
    paths = [safe_relative(r['path']) for r in expected]
    leaves = [safe_relative(r['patch']) for r in expected]
    require(len(expected) == len(set(paths)) == len(set(leaves)) == 63
            and all('/' not in p and p.endswith('.patch') for p in leaves), 'Source or patch leaf collision')
    for row in expected:
        safe_relative(row['source_patch'])
        for field in ('sha256', 'before_sha256', 'after_sha256'):
            require(isinstance(row[field], str) and re.fullmatch('[0-9a-f]{64}', row[field]), 'Invalid SHA256 field')
    return expected


def apply_exact(entries, originals, patches):
    results = []
    with tempfile.TemporaryDirectory(prefix='php83-exp11-selection-') as directory:
        root = Path(directory)
        for entry in entries:
            target = root / entry['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(originals[entry['path']])
        for entry in entries:
            data = patches[entry['patch']]
            headers = [line for line in data.splitlines() if line.startswith((b'--- ', b'+++ '))]
            require(headers == [('--- a/' + entry['path']).encode(), ('+++ b/' + entry['path']).encode()],
                    'Unexpected patch target headers')
            run = subprocess.run(['patch', '--batch', '--forward', '--fuzz=0', '--no-backup-if-mismatch', '-p1'],
                                 input=data, cwd=root, capture_output=True, timeout=60,
                                 env=dict(os.environ, LC_ALL='C'))
            text = (run.stdout + run.stderr).decode(errors='replace')
            require(run.returncode == 0 and not any(word in text.lower() for word in ('offset', 'fuzz', 'reversed', 'skipping')),
                    'Patch did not apply exactly: ' + entry['patch'])
            require(digest((root / entry['path']).read_bytes()) == entry['after_sha256'], 'Resulting source hash mismatch')
            results.append({'path': entry['path'], 'patch': entry['patch'], 'exit': run.returncode,
                            'after_sha256': entry['after_sha256'], 'diagnostics': text})
        require({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == set(originals),
                'Unexpected replay output files')
        for entry in entries:
            require(digest((root / entry['path']).read_bytes()) == entry['after_sha256'], 'Cumulative output drift')
    return results


def validate(archive):
    payload = MANIFEST.read_bytes()
    manifest = json.loads(payload)
    require(manifest['status'] == 'PREPARED_NOT_SELECTED' and manifest['revision'] == 'exp11'
            and manifest['target_php'] == '8.3' and manifest['upstream_root'] == ROOT
            and manifest['upstream_sha256'] == ORIGINAL, 'Wrong prepared candidate identity/status')
    require(manifest['selection_provenance'] == provenance(), 'Provenance declaration drift')
    documents = {}
    for role, (path, pin) in INPUTS.items():
        data = repo_bytes(path)
        require(digest(data) == pin, 'Pinned metadata drift: ' + role)
        documents[role] = json.loads(data)
    entries = expected_selection(documents)
    require(manifest['patches'] == entries, 'Selection differs from exact ordered 59+4 inputs')
    archive_data = Path(archive).read_bytes()
    require(digest(archive_data) == ORIGINAL, 'Original archive identity mismatch')
    originals, patches = {}, {}
    with zipfile.ZipFile(io.BytesIO(archive_data)) as upstream:
        names = upstream.namelist()
        require(len(names) == len(set(names)), 'Duplicate original ZIP entry')
        for entry in entries:
            member = upstream.getinfo(ROOT + '/' + entry['path'])
            require(not stat.S_ISLNK(member.external_attr >> 16) and not member.is_dir(), 'Nonregular original target')
            data = upstream.read(member)
            require(digest(data) == entry['before_sha256'], 'Original target identity mismatch')
            patch = repo_bytes(entry['source_patch'])
            require(digest(patch) == entry['sha256'], 'Patch byte drift')
            originals[entry['path']] = data
            patches[entry['patch']] = patch
        # The ternary manifest also pins unmodified helpers, not additional patches.
        for row in documents['ternary']['files']:
            data = upstream.read(ROOT + '/' + safe_relative(row['path']))
            require(digest(data) == row['before_sha256'], 'Ternary helper input drift')
            if row['path'] != TARGETS[0]:
                require(row['before_sha256'] == row['after_sha256'], 'Unselected ternary helper changed')
    replay = apply_exact(entries, originals, patches)
    report = {'schema': 1, 'status': 'PREPARED_NOT_SELECTED', 'selection_approved': False,
              'zip_built': False, 'runtime_executed': False, 'targets': 63,
              'prior_entries_preserved_exactly': 59, 'additional_disjoint_entries': 4,
              'source_or_patch_leaf_collisions': 0, 'upstream_sha256': ORIGINAL,
              'manifest_sha256': digest(payload), 'preflight_sha256': digest(Path(__file__).read_bytes()),
              'metadata_provenance': provenance(), 'exact_private_copy_replays': replay,
              'application_acceptance': False}
    return payload, patches, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--output', type=Path, help='Fresh patch-input staging directory, not an artifact build')
    parser.add_argument('--report', type=Path, help='Fresh local preflight JSON report')
    args = parser.parse_args()
    require(args.check_only != bool(args.output), 'Choose --check-only or --output NEW_DIRECTORY')
    if args.output:
        require(not args.output.exists(), 'Refuse existing staging directory')
    if args.report:
        require(not args.report.exists(), 'Refuse existing report')
    payload, patches, report = validate(args.original)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'manifest.json').write_bytes(payload)
        for name, data in patches.items():
            (args.output / name).write_bytes(data)
    report['patch_inputs_staged'] = bool(args.output)
    if args.report:
        with args.report.open('x') as output:
            output.write(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'exact_private_copy_replays'}, sort_keys=True))


if __name__ == '__main__':
    main()
