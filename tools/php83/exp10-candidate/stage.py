#!/usr/bin/env python3
"""Validate/stage exact reviewed exp10 patch inputs only; never build a ZIP."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

REPO = Path(__file__).resolve().parents[3]
MANIFEST = REPO / 'doc/php83/evidence/exp10-candidate/manifest.json'
ORIGINAL = '58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_relative(path):
    if not path or PurePosixPath(path).is_absolute() or any(p in ('', '.', '..') for p in path.split('/')) or '\\' in path:
        raise ValueError('Unsafe input path')
    return path


def validate(archive):
    payload = MANIFEST.read_bytes()
    manifest = json.loads(payload)
    source = archive.read_bytes()
    if digest(source) != ORIGINAL or manifest['upstream_sha256'] != ORIGINAL:
        raise ValueError('Original archive identity mismatch')
    if manifest['revision'] != 'exp10' or manifest['target_php'] != '8.3' or manifest['upstream_root'] != 'server-Rigel-18.20.0':
        raise ValueError('Wrong candidate identity')
    provenance = manifest['selection_provenance']
    prior_bytes = (REPO / safe_relative(provenance['prior_manifest'])).read_bytes()
    held_bytes = (REPO / safe_relative(provenance['additional_held_manifest'])).read_bytes()
    if digest(prior_bytes) != provenance['prior_manifest_sha256'] or digest(held_bytes) != provenance['additional_held_manifest_sha256']:
        raise ValueError('Selection provenance drift')
    prior = json.loads(prior_bytes)
    held = json.loads(held_bytes)
    expected = list(prior['patches'])
    expected.extend({'patch':Path(row['patch']).name,'sha256':row['patch_sha256'],
        'path':row['path'],'before_sha256':row['before_sha256'],'after_sha256':row['after_sha256'],
        'source_patch':row['patch']} for row in held['files'])
    if len(prior['patches']) != 16 or len(held['files']) != 43 or manifest['patches'] != expected:
        raise ValueError('Cumulative selection differs from exact16+43 inputs')
    paths = [safe_relative(row['path']) for row in expected]
    names = [safe_relative(row['patch']) for row in expected]
    if len(paths) != 59 or len(set(paths)) != 59 or len(set(names)) != 59 or any('/' in n or not n.endswith('.patch') for n in names):
        raise ValueError('Source target/patch leaf collision')
    patches = {}
    import io
    with zipfile.ZipFile(io.BytesIO(source)) as upstream:
        if len(upstream.namelist()) != len(set(upstream.namelist())):
            raise ValueError('Duplicate upstream archive member')
        for entry in expected:
            patch_path = REPO / safe_relative(entry['source_patch'])
            if patch_path.is_symlink() or not patch_path.resolve().is_relative_to(REPO):
                raise ValueError('Unsafe patch source')
            data = patch_path.read_bytes()
            if digest(data) != entry['sha256']:
                raise ValueError('Patch bytes drift')
            original = upstream.read(manifest['upstream_root'] + '/' + entry['path'])
            if digest(original) != entry['before_sha256']:
                raise ValueError('Original target identity mismatch')
            patches[entry['patch']] = data
    return payload, patches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    if args.check_only == bool(args.output):
        parser.error('Choose exactly --check-only or --output NEW_DIRECTORY')
    payload, patches = validate(args.original)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'manifest.json').write_bytes(payload)
        for name, data in patches.items():
            (args.output / name).write_bytes(data)
    print(json.dumps({'selection_only':True,'zip_built':False,'targets':59,
        'prior_entries_preserved':16,'additional_disjoint_entries':43,
        'source_or_leaf_collisions':0,'all_patch_and_upstream_input_hashes_match':True,
        'manifest_sha256':digest(payload),'staged':bool(args.output)},sort_keys=True))

if __name__ == '__main__':
    main()
