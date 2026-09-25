#!/usr/bin/env python3
"""Exact exp9-to-exp10 application delta; no ZIP extraction or source execution."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

PREVIOUS = 'cb61e4cd11009bbf9e6e362dfafa5ef2f4af22da817c75fedbd7741a08e44cbc'
CURRENT = 'de177e6cbaedf3a3207661c2325f466cce37febb73190f3a49d31f24b740c053'
MANIFEST = 'db4c2b6dfff31f9fd64e05f29e0ccd79b2049e85e7c27ee29b2783605db387aa'
ROOT = 'server-Rigel-18.20.0/'
META = ROOT + '.php83-experimental/'
sha = lambda data: hashlib.sha256(data).hexdigest()


def verify(previous_bytes, current_bytes, manifest_bytes):
    if sha(previous_bytes) != PREVIOUS or sha(current_bytes) != CURRENT or sha(manifest_bytes) != MANIFEST:
        raise ValueError('Pinned artifact or selection identity mismatch')
    manifest = json.loads(manifest_bytes)
    with zipfile.ZipFile(io.BytesIO(previous_bytes)) as before, zipfile.ZipFile(io.BytesIO(current_bytes)) as after:
        prior, current = set(before.namelist()), set(after.namelist())
        if len(prior) != len(before.namelist()) or len(current) != len(after.namelist()):
            raise ValueError('Duplicate ZIP member')
        app_before = {p for p in prior if not p.startswith(META)}
        app_after = {p for p in current if not p.startswith(META)}
        if app_before != app_after:
            raise ValueError('Application members added or removed')
        old_manifest = json.loads(before.read(META + 'manifest.json'))
        if len(old_manifest['patches']) != 16 or manifest['patches'][:16] != old_manifest['patches']:
            raise ValueError('Prior16 selection not exactly preserved')
        additions = manifest['patches'][16:]
        if len(additions) != 43 or len({p['path'] for p in manifest['patches']}) != 59:
            raise ValueError('Wrong cumulative denominator')
        expected_changes = {ROOT + row['path'] for row in additions}
        changed = {p for p in app_before if before.read(p) != after.read(p)}
        if changed != expected_changes:
            raise ValueError('Unexpected exp9-to-exp10 application delta')
        for row in additions:
            name = ROOT + row['path']
            if sha(before.read(name)) != row['before_sha256'] or sha(after.read(name)) != row['after_sha256']:
                raise ValueError('New source transformation identity mismatch')
        for row in old_manifest['patches']:
            name = ROOT + row['path']
            if before.read(name) != after.read(name) or sha(after.read(name)) != row['after_sha256']:
                raise ValueError('Prior source result changed')
        expected_prior_metadata = {META + name for name in ['manifest.json','README.txt'] + [p['patch'] for p in old_manifest['patches']]}
        expected_current_metadata = {META + name for name in ['manifest.json','README.txt'] + [p['patch'] for p in manifest['patches']]}
        if prior - app_before != expected_prior_metadata or current - app_after != expected_current_metadata:
            raise ValueError('Unexpected metadata member set')
        shared_changed = {p for p in expected_prior_metadata if before.read(p) != after.read(p)}
        if shared_changed != {META + 'manifest.json'}:
            raise ValueError('Prior embedded patch or README changed')
        for row in manifest['patches']:
            if sha(after.read(META + row['patch'])) != row['sha256']:
                raise ValueError('Embedded patch identity mismatch')
        embedded = json.loads(after.read(META + 'manifest.json'))
        if any(embedded.get(k) != v for k,v in manifest.items()) or embedded['manifest_sha256'] != MANIFEST:
            raise ValueError('Embedded current selection mismatch')
        return {'previous_zip_sha256':PREVIOUS,'current_zip_sha256':CURRENT,
            'manifest_sha256':MANIFEST,'application_changes':sorted(changed),
            'application_changes_count':len(changed),'all_other_application_bytes_identical':True,
            'prior16_source_results_preserved':True,'prior16_selection_entries_preserved':True,
            'application_members_added_or_removed':[],
            'previous_metadata_members':len(expected_prior_metadata),
            'current_metadata_members':len(expected_current_metadata),
            'new_metadata_members':sorted(expected_current_metadata - expected_prior_metadata),
            'changed_shared_metadata':sorted(shared_changed),
            'current_regular_files':sum(not entry.is_dir() for entry in after.infolist()),
            'current_zip_entries':len(current),'application_acceptance':False}


def main():
    parser=argparse.ArgumentParser()
    for name in ['previous','current','manifest','output']:
        parser.add_argument(name,type=Path)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Refusing overwrite')
    result=verify(args.previous.read_bytes(),args.current.read_bytes(),args.manifest.read_bytes())
    result['verifier_sha256']=sha(Path(__file__).read_bytes())
    with args.output.open('x') as output:json.dump(result,output,indent=2);output.write('\n')
    print(json.dumps({'application_changes':result['application_changes_count'],
        'prior16_preserved':True,'metadata_members':result['current_metadata_members'],
        'current_zip_sha256':CURRENT},sort_keys=True))

if __name__=='__main__':main()
