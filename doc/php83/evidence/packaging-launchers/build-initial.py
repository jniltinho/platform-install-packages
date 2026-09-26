#!/usr/bin/env python3
"""Repository-local literal launcher candidates; no archive or runtime access."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess

ROOT = Path(__file__).resolve().parents[4]
SCOPES = ['deb', 'RPM/SOURCES', 'build', '.github/workflows']
HELPER = 'tools/php83/entrypoint-inventory/build.py'
HELPER_SHA = 'd2ed28e1df69479a2f795861c1713966cab0d4ba2f32511afcc15dd3702b3202'
LIMIT = 2 * 1024 * 1024

def digest(data):
    return hashlib.sha256(data).hexdigest()

def build():
    helper = ROOT / HELPER
    if digest(helper.read_bytes()) != HELPER_SHA:
        raise ValueError('Reviewed literal matcher changed')
    spec = importlib.util.spec_from_file_location('literal_matcher', helper)
    scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scanner)
    listing = subprocess.check_output(['git', 'ls-files', '-s', '-z', '--', *SCOPES], cwd=ROOT)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    files, findings, seen = [], [], set()
    for record in listing.split(b'\0'):
        if not record:
            continue
        header, rawpath = record.split(b'\t', 1)
        mode, blob, stage = header.decode().split()
        name = rawpath.decode('utf-8')
        if stage != '0' or name in seen or name.startswith('/') or '..' in Path(name).parts:
            raise ValueError('Unmerged, duplicate or unsafe tracked member')
        seen.add(name)
        path = ROOT / name
        metadata = path.lstat()
        row = {'path': name, 'git_mode': mode, 'indexed_blob': blob,
               'working_tree_size': metadata.st_size}
        files.append(row)
        if not stat.S_ISREG(metadata.st_mode):
            row['disposition'] = 'nonregular_not_followed'
            continue
        if metadata.st_size > LIMIT:
            row['disposition'] = 'oversize_unscanned'
            continue
        data = path.read_bytes()
        row['sha256'] = digest(data)
        if b'\0' in data:
            row['disposition'] = 'binary_unscanned'
            continue
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            row['disposition'] = 'nonutf8_unscanned'
            continue
        owner = {'repository_commit_context': commit, 'source_path': name,
                 'working_tree_sha256': row['sha256']}
        calls = scanner.scan_php_invocations(text, name, owner)
        row['disposition'] = 'text_scanned'
        row['candidate_rows'] = len(calls)
        findings.extend(calls)
    counts = {key: sum(r['disposition'] == key for r in files)
              for key in sorted({r['disposition'] for r in files})}
    if sum(counts.values()) != len(files):
        raise ValueError('Member accounting mismatch')
    for row in files:
        if 'sha256' in row and digest((ROOT / row['path']).read_bytes()) != row['sha256']:
            raise ValueError('Working source changed during scan')
    return {'schema': 1, 'status': 'REPOSITORY_LITERAL_CANDIDATES_ONLY',
            'scopes': SCOPES, 'repository_commit_context': commit,
            'listing_sha256': digest(listing), 'builder_sha256': digest(Path(__file__).read_bytes()),
            'matcher': {'path': HELPER, 'sha256': HELPER_SHA},
            'files': files, 'candidate_rows': findings,
            'summary': {'tracked_members': len(files), 'dispositions': counts,
                        'files_with_candidates': sum(bool(f.get('candidate_rows')) for f in files),
                        'candidate_rows': len(findings)},
            'archive_access': False, 'application_execution': False,
            'active_entrypoint_proven': False, 'T0_04_complete': False,
            'limitations': ['Regex overmatches and misses some shell constructions; not shell execution analysis.',
                            'Working bytes hashed independently; commit is context, not a claim that all bytes match HEAD.',
                            'No original ZIP or published package input; not a substitute for denied archive operation.',
                            'No deployed-path, source-target, package-owner or reachability join.']}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = build()
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps(result['summary'], sort_keys=True))
