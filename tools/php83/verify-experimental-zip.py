#!/usr/bin/env python3
"""Verify the exact content delta and repeated build identity of a lab ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
for name in ['original', 'candidate', 'repeat', 'manifest', 'output']:
    parser.add_argument(name, type=Path)
a = parser.parse_args()
sha = lambda data: hashlib.sha256(data).hexdigest()
manifest_bytes = a.manifest.read_bytes()
m = json.loads(manifest_bytes)
source_bytes = a.original.read_bytes()
first_bytes, second_bytes = a.candidate.read_bytes(), a.repeat.read_bytes()
if sha(source_bytes) != m['upstream_sha256'] or first_bytes != second_bytes:
    raise ValueError('Original checksum or repeated build identity mismatch')
prefix = m['upstream_root'] + '/'
expected = {prefix + e['path']: e for e in m['patches']}
metadata_dir = prefix + '.php83-experimental/'
expected_added = {metadata_dir + name for name in ['manifest.json', 'README.txt']}
expected_added.update(metadata_dir + e['patch'] for e in m['patches'])
# Read the already-hashed byte snapshots, never reopen mutable inputs by path.
import io
with zipfile.ZipFile(io.BytesIO(source_bytes)) as before, zipfile.ZipFile(io.BytesIO(first_bytes)) as after:
    prior, current = set(before.namelist()), set(after.namelist())
    if len(current) != len(after.namelist()) or len(prior) != len(before.namelist()):
        raise ValueError('Duplicate archive members')
    if prior - current or current - prior != expected_added:
        raise ValueError('Unexpected archive additions/removals')
    changed = sorted(p for p in prior if before.read(p) != after.read(p))
    if set(changed) != set(expected):
        raise ValueError('Unexpected modified files')
    for path, entry in expected.items():
        if sha(before.read(path)) != entry['before_sha256'] or sha(after.read(path)) != entry['after_sha256']:
            raise ValueError('Changed-file hash mismatch: ' + path)
        if sha(after.read(metadata_dir + entry['patch'])) != entry['sha256']:
            raise ValueError('Embedded patch hash mismatch')
    embedded = json.loads(after.read(metadata_dir + 'manifest.json'))
    if any(embedded.get(key) != value for key, value in m.items()):
        raise ValueError('Embedded manifest mismatch')
    if embedded['manifest_sha256'] != sha(manifest_bytes):
        raise ValueError('Embedded manifest input hash mismatch')
    builder_hash = sha(Path(__file__).with_name('build-experimental-zip.py').read_bytes())
    if embedded['builder_sha256'] != builder_hash:
        raise ValueError('Builder version mismatch')
    if before.comment != after.comment:
        raise ValueError('Upstream archive comment lost')
    for name in prior:
        if before.getinfo(name).comment != after.getinfo(name).comment:
            raise ValueError('Entry comment lost')
report = {'zip_sha256': sha(first_bytes), 'repeat_build_sha256': sha(second_bytes),
          'upstream_sha256': sha(source_bytes), 'builder_sha256': builder_hash,
          'manifest_sha256': sha(manifest_bytes), 'verifier_sha256': sha(Path(__file__).read_bytes()),
          'original_entries': len(prior), 'changed_files': changed,
          'added_metadata': sorted(expected_added), 'missing_original_entries': [],
          'two_builds_identical': True, 'all_other_original_entry_bytes_identical': True,
          'archive_and_entry_comments_preserved': True,
          'metadata_policy': 'sorted entries; fixed timestamps; normalized modes; recorded Python/zlib'}
a.output.write_text(json.dumps(report, indent=2) + '\n')
print(report['zip_sha256'])
