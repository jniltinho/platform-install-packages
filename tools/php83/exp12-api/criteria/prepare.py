#!/usr/bin/env python3
"""Prepare, never select, cumulative Criteria repair from pinned source archives."""
import argparse
import difflib
import hashlib
import io
import json
from pathlib import Path
import zipfile

UPSTREAM = '58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
EXP11 = 'f2474f5b951bfd2d121291025c8dd4554697fb5bb4024e132987643dab6144a7'
BEFORE = '0626bb5b976ae7eedccaf5060675cd7c7ca56b22fc2c9d6c1a51ce485a303543'
PRIOR = 'e8333167c6b501c92a8ee681a3b8c63372e8bf20e81c140a242c37c75b49a89a'
TARGET = 'vendor/propel/util/Criteria.php'
MEMBER = 'server-Rigel-18.20.0/' + TARGET
ANCHOR = b'class Criteria implements IteratorAggregate {'
ATTRIBUTE = b'#[\\AllowDynamicProperties]\n'
sha = lambda data: hashlib.sha256(data).hexdigest()

def transform(data):
    if sha(data) != PRIOR:
        raise ValueError('Prior Criteria source drift')
    if data.count(ANCHOR) != 1 or data.splitlines()[37] != ANCHOR:
        raise ValueError('Unexpected declaration')
    if b'AllowDynamicProperties' in data:
        raise ValueError('Attribute already exists')
    result = data.replace(ANCHOR, ATTRIBUTE + ANCHOR, 1)
    if result.replace(ATTRIBUTE, b'', 1) != data:
        raise ValueError('Unexpected cumulative delta')
    return result

def read_pinned(path, archive_pin, member_pin):
    raw = path.read_bytes()
    if sha(raw) != archive_pin:
        raise ValueError('Archive identity drift')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive members')
        info = archive.getinfo(MEMBER)
        if (info.external_attr >> 16) & 0o170000 == 0o120000:
            raise ValueError('Symlink target')
        data = archive.read(info)
    if sha(data) != member_pin:
        raise ValueError('Member identity drift')
    return data

def prepare(original, prior, output):
    if output.exists():
        raise ValueError('Refuse existing output')
    base = read_pinned(original, UPSTREAM, BEFORE)
    previous = read_pinned(prior, EXP11, PRIOR)
    candidate = transform(previous)
    patch = ''.join(difflib.unified_diff(base.decode().splitlines(True),
        candidate.decode().splitlines(True), 'a/' + TARGET, 'b/' + TARGET)).encode()
    manifest = {'status': 'PREPARED_CUMULATIVE_EXPERIMENT_NOT_SELECTED',
        'path': TARGET, 'upstream_sha256': UPSTREAM, 'exp11_sha256': EXP11,
        'before_sha256': BEFORE, 'prior_sha256': PRIOR, 'after_sha256': sha(candidate),
        'patch_sha256': sha(patch), 'supersedes': 'Criteria-native-returns.patch',
        'preserved_prior_bytes_after_removing_attribute': True,
        'scope': 'Explicit Criteria hierarchy dynamic-property compatibility, including descendants and future dynamic writes; not marker-only.',
        'cross_engine_layout_parity': 'FAIL retained from original baseline',
        'cache_acceptance': False, 'application_acceptance': False,
        'next_zip_selected': False}
    output.mkdir(parents=True, exist_ok=False)
    (output / 'Criteria.php').write_bytes(candidate)
    (output / 'Criteria-dynamic-hierarchy.patch').write_bytes(patch)
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('original', type=Path)
    parser.add_argument('exp11', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.original, args.exp11, args.output), indent=2))
