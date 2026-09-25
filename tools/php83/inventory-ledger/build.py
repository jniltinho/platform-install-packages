#!/usr/bin/env python3
"""Offline evidence join. A matched source identity never proves a finding fixed."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

ORIGINAL = '58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
CANDIDATE = 'cb61e4cd11009bbf9e6e362dfafa5ef2f4af22da817c75fedbd7741a08e44cbc'
ROOT = 'server-Rigel-18.20.0/'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def archive_hashes(path, expected):
    if digest(path.read_bytes()) != expected:
        raise ValueError('Archive identity mismatch')
    result = {}
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            name = member.filename
            if not name.startswith(ROOT) or '..' in PurePosixPath(name).parts:
                raise ValueError('Unexpected archive path')
            relative = name[len(ROOT):]
            if relative in result:
                raise ValueError('Duplicate archive path')
            result[relative] = digest(archive.read(member))
    return result

def source_path(path, scope):
    if scope == 'raw':
        return path
    prefix = 'opt/kaltura/app/'
    return path[len(prefix):] if path.startswith(prefix) else None

def identity(path, sha):
    return (sha + ':' + path) if sha else ('unresolved:' + path)

def build(repo, original, candidate):
    evidence = repo / 'doc/php83/evidence'
    inputs = {}
    def read(name, csv_input=False):
        data = (evidence / name).read_bytes()
        inputs[name] = {'sha256': digest(data), 'bytes': len(data)}
        return list(csv.DictReader(data.decode().splitlines())) if csv_input else json.loads(data)
    manifest = read('exp9-candidate/manifest.json')
    if manifest['upstream_sha256'] != ORIGINAL or manifest['revision'] != 'exp9':
        raise ValueError('Wrong manifest identity')
    original_hashes = archive_hashes(original, ORIGINAL)
    candidate_hashes = archive_hashes(candidate, CANDIDATE)
    patches = {p['path']: p for p in manifest['patches']}
    if len(patches) != len(manifest['patches']):
        raise ValueError('Duplicate patch target')
    for path, patch in patches.items():
        if original_hashes.get(path) != patch['before_sha256'] or candidate_hashes.get(path) != patch['after_sha256']:
            raise ValueError('Manifest source identity mismatch')
        if digest((repo / patch['source_patch']).read_bytes()) != patch['sha256']:
            raise ValueError('Patch identity mismatch')
    changed = {p for p in original_hashes if candidate_hashes.get(p) != original_hashes[p]}
    if changed != set(patches):
        raise ValueError('Unmanifested application delta')
    inventory = read('source-audit/archive-inventory.json')
    overlay = read('source-audit/source-to-package-map.json')
    compile_report = read('source-audit/php74-vs-php83-compile.json')
    raw_syntax = read('source-audit/syntax-findings.json')
    packaged_syntax = read('source-audit/packaged-syntax-findings.json')
    package_hashes = {}
    for row in packaged_syntax['diagnostic_files'] + compile_report['files']:
        path, sha = row['path'], row['sha256']
        if path in package_hashes and package_hashes[path] != sha:
            raise ValueError('Conflicting packaged identities')
        package_hashes[path] = sha
    files = {}
    def register(path, scope, sha=None):
        upstream = source_path(path, scope)
        if scope == 'raw':
            expected = original_hashes.get(path)
            if sha and sha != expected:
                raise ValueError('Raw finding source identity mismatch')
            sha = expected
        elif sha is None:
            sha = package_hashes.get(path)
        key = identity(scope + ':' + path, sha)
        if key not in files:
            same_upstream = bool(sha and upstream and original_hashes.get(upstream) == sha)
            patch = patches.get(upstream) if same_upstream else None
            files[key] = {'scope': scope, 'path': path, 'source_sha256': sha,
                'identity_status': 'supported' if sha else 'unresolved',
                'upstream_path_candidate': upstream,
                'upstream_identity_matches': same_upstream,
                'selected_patch': patch['patch'] if patch else None,
                'candidate_sha256': patch['after_sha256'] if patch else None,
                'active_entrypoint_status': 'unresolved',
                'semantic_finding_status': 'unresolved'}
        return key
    findings = []
    for scope, name in [('raw','static-findings.csv'),('packaged','packaged-static-findings.csv')]:
        ref = 'source-audit/' + name
        rows = read(ref, True)
        for index, row in enumerate(rows):
            findings.append({'id': scope + '-static-' + str(index),
                'file_key': register(row['path'],scope), 'evidence': ref,
                'record_index': index, 'line': int(row['line']), 'rule': row['rule'],
                'reported_classification': row['classification'],
                'classification': 'unverified static candidate',
                'reason': 'No per-finding semantic adjudication imported; patch/path overlap is not resolution.'})
    for scope, name, report in [('raw','syntax-findings.json',raw_syntax),('packaged','packaged-syntax-findings.json',packaged_syntax)]:
        for index,row in enumerate(report['diagnostic_files']):
            findings.append({'id':scope+'-syntax-'+str(index),
                'file_key':register(row['path'],scope,row['sha256']),
                'evidence':'source-audit/'+name,'record_index':index,
                'classification':'confirmed compiler rejection' if row['returncode'] else 'compiler diagnostic',
                'reported_classification':row['classification'],
                'runtime_reachability':'unresolved'})
    differential = []
    for index,row in enumerate(compile_report['files']):
        differential.append({'file_key':register(row['path'],'packaged',row['sha256']),
            'classification':row['classification'], 'evidence':'source-audit/php74-vs-php83-compile.json',
            'record_index':index,'runtime_reachability':'unresolved'})
    runtime_name='exp9-api/codex.json'
    runtime=read(runtime_name)
    if runtime['artifact']['zip_sha256'] != CANDIDATE:
        raise ValueError('Wrong runtime artifact')
    selected=[r for r in runtime['records'] if r['runtime']=='83' and r['tree']=='exp9']
    if len(selected)!=1:
        raise ValueError('Expected one exp9 runtime row')
    diagnostics=[]
    for index,row in enumerate(selected[0]['diagnostics']):
        prefix='/audit/app/'
        path=row['path'][len(prefix):] if row['path'].startswith(prefix) else None
        sha=candidate_hashes.get(path)
        diagnostics.append({'evidence':runtime_name,'record_tree':'exp9','diagnostic_index':index,
            'path':row['path'],'source_sha256':sha,'identity_status':'supported' if sha else 'unresolved',
            'line':row['line'],'count':row['count'],'severity':row['severity'],
            'classification':'observed bounded runtime diagnostic',
            'semantic_cause':'unresolved by this ledger',
            'matching_upstream_file_key':register(path, 'raw') if path in original_hashes else None})
    dependencies=[]
    for vendor in inventory['vendor_directories']:
        prefix='vendor/'+vendor+'/'
        licenses=[{'path':p,'sha256':original_hashes.get(p)} for p in inventory['license_files'] if p.startswith(prefix)]
        dependencies.append({'directory':prefix,'version_attribution':'unresolved',
            'license_attribution':'unresolved','candidate_license_files':licenses,
            'note':'License filename/prefix is discovery evidence, not license interpretation or complete transitive inventory.'})
    counts=Counter(f['scope'] for f in files.values() if not f['source_sha256'])
    return {'schema':1,'scope':'Offline evidence identity/accounting join; no semantic adjudication, execution or T0-04 completion',
        'original_archive_sha256':ORIGINAL,'candidate_archive_sha256':CANDIDATE,
        'inputs':inputs,'files':files,'findings':findings,'compile_differential':differential,
        'runtime_diagnostics':diagnostics,'dependencies':dependencies,
        'packaging_overlay':{'evidence':'source-audit/source-to-package-map.json',**overlay},
        'summary':{'static_findings':sum('static' in r['id'] for r in findings),
            'syntax_findings':sum('syntax' in r['id'] for r in findings),
            'file_identity_records':len(files),'missing_file_hashes_by_scope':dict(counts),
            'compile_classifications':dict(Counter(r['classification'] for r in differential)),
            'runtime_diagnostic_groups':len(diagnostics),'runtime_diagnostic_events':sum(r['count'] for r in diagnostics),
            'selected_patch_targets':len(patches),'dependency_directories':len(dependencies),
            'unresolved_dependency_versions':len(dependencies),'unresolved_license_attributions':len(dependencies),
            'unresolved_active_entrypoints':len(files),'semantic_findings_resolved_by_this_join':0},
        'remaining':['Per-finding semantic adjudication and active-entrypoint evidence',
            'Exact packaged-file identities not present in imported diagnostic reports',
            'Complete dependency, generated-client, overlay and transitive license attribution',
            'Pinned analyzer blind-spot and manual review accounting',
            'Current candidate whole-tree syntax/static rerun and independent review'],
        't0_04_complete':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[3])
    ap.add_argument('--original',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise ValueError('Refusing overwrite')
    result=build(a.repo,a.original,a.candidate)
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result['summary'],sort_keys=True))
if __name__=='__main__':main()
