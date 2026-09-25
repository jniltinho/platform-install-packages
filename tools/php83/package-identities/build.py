#!/usr/bin/env python3
"""Read-only published DEB PHP payload identity inventory; never install or extract paths."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import tempfile
import zipfile

BUNDLE_SHA = '91629580441f6a896ebf9e51f0256532221715bee57a3e5a64c66ff0c4e3127b'
SOURCE_SHA = '58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
SOURCE_ROOT = 'server-Rigel-18.20.0/'
EXTENSIONS = {'.php', '.phtml', '.inc', '.php5'}


def hash_stream(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(chunk)
    return h.hexdigest()


def hash_file(path):
    with path.open('rb') as stream:
        return hash_stream(stream)


def normalize(name):
    if not name or name.startswith('/') or '\\' in name or '\x00' in name:
        raise ValueError('Unsafe member path')
    if '..' in PurePosixPath(name).parts:
        raise ValueError('Traversal member path')
    result = str(PurePosixPath(name))
    return '' if result == '.' else result


def php_path(name):
    return PurePosixPath(name).suffix.lower() in EXTENSIONS


def checksum_manifest(text):
    result = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'([0-9a-f]{64}) [ *](.+)', line)
        if not match:
            raise ValueError('Invalid checksum line')
        sha, name = match.groups()
        name = normalize(name)
        if not name.endswith('.deb') or '/' in name or name in result:
            raise ValueError('Invalid or duplicate checksum package')
        result[name] = sha
    if not result:
        raise ValueError('Empty package manifest')
    return result


def payload_inventory(stream, owner, excluded=None):
    """Paths are read as names only. PHP symlinks/hardlinks are rejected, not followed."""
    records = []
    seen = set()
    with tarfile.open(fileobj=stream, mode='r|') as archive:
        for member in archive:
            path = normalize(member.name)
            if path in seen:
                raise ValueError('Duplicate path within package: ' + path)
            seen.add(path)
            if not php_path(path):
                if excluded is not None and not member.isdir():
                    suffix = PurePosixPath(path).suffix.lower() or '(extensionless)'
                    excluded[suffix] = excluded.get(suffix, 0) + 1
                continue
            if not member.isfile():
                raise ValueError('Non-regular PHP member rejected: ' + path)
            with archive.extractfile(member) as source:
                sha = hash_stream(source)
            records.append({'path': path, 'sha256': sha, 'type': 'regular',
                'size': member.size, 'mode': member.mode,
                'uid': member.uid, 'gid': member.gid, 'owners': [owner]})
    return records


def merge_payloads(records):
    result = {}
    for row in records:
        path = row['path']
        if path not in result:
            result[path] = {**row, 'owners': list(row['owners'])}
            continue
        old = result[path]
        for key in ('sha256', 'type', 'size', 'mode', 'uid', 'gid'):
            if old[key] != row[key]:
                raise ValueError('Conflicting package payload: ' + path + ' (' + key + ')')
        old['owners'].extend(row['owners'])
    return {path: result[path] for path in sorted(result)}


def join_ledger(ledger, files):
    rows = []
    for key, original in sorted(ledger['files'].items()):
        if original['scope'] != 'packaged':
            continue
        path = original['path']
        if path not in files:
            raise ValueError('Ledger packaged path missing: ' + path)
        found = files[path]
        known = original['source_sha256']
        if known and known != found['sha256']:
            raise ValueError('Known ledger identity conflict: ' + path)
        rows.append({'ledger_file_key': key, 'path': path,
            'previous_sha256': known, 'sha256': found['sha256'],
            'status': 'known_identity_preserved' if known else 'missing_identity_resolved',
            'owners': found['owners'], 'type': found['type'],
            'semantic_classification': 'unchanged; identity resolution only'})
    return rows


def source_inventory(path):
    if hash_file(path) != SOURCE_SHA:
        raise ValueError('Original archive hash mismatch')
    result = {}
    seen = set()
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            name = normalize(member.filename)
            if name in seen:
                raise ValueError('Duplicate original archive path')
            seen.add(name)
            if member.is_dir():
                continue
            if not name.startswith(SOURCE_ROOT):
                raise ValueError('Unexpected source archive root')
            relative = name[len(SOURCE_ROOT):]
            if php_path(relative):
                with archive.open(member) as stream:
                    result[relative] = hash_stream(stream)
    return result


def reconcile(files, upstream, prior):
    prefix = 'opt/kaltura/app/'
    unchanged = []
    changed = []
    missing = []
    for path, sha in sorted(upstream.items()):
        found = files.get(prefix + path)
        if found is None:
            missing.append(path)
        elif found['sha256'] == sha:
            unchanged.append(path)
        else:
            changed.append({'path': path, 'upstream_sha256': sha, 'packaged_sha256': found['sha256']})
    extras = sorted(path for path in files if not path.startswith(prefix) or path[len(prefix):] not in upstream)
    expected_changed = sorted(prior['changed_upstream_php_files'], key=lambda r: r['path'])
    if (len(unchanged) != prior['unchanged_upstream_php_files'] or changed != expected_changed
            or missing != prior['upstream_php_not_at_expected_package_path']
            or len(extras) != prior['extra_packaged_php_files']):
        raise ValueError('Published source/package map mismatch')
    groups = {}
    for group, count in prior['extra_path_groups'].items():
        members = [p for p in extras if p == group or p.startswith(group + '/')]
        if len(members) != count:
            raise ValueError('Extra package path group mismatch: ' + group)
        groups[group] = members
    flattened = [p for rows in groups.values() for p in rows]
    if len(flattened) != len(set(flattened)) or sorted(flattened) != extras:
        raise ValueError('Extra path groups not an exact partition')
    return {'unchanged_upstream_php_files': len(unchanged), 'changed_upstream_php_files': changed,
        'upstream_php_not_at_expected_package_path': missing,
        'extra_packaged_php_files': len(extras), 'extra_paths': extras,
        'extra_path_groups': groups, 'matches_historical_map': True}


def build(repo, bundle, original):
    if hash_file(bundle) != BUNDLE_SHA:
        raise ValueError('Published bundle hash mismatch')
    evidence = repo / 'doc/php83/evidence'
    inputs = {}
    def load(name):
        path = evidence / name
        inputs[name] = hash_file(path)
        return json.loads(path.read_text())
    ledger = load('inventory-ledger/ledger.json')
    historical_map = load('source-audit/source-to-package-map.json')
    inputs['builder'] = hash_file(Path(__file__))
    packages = []
    records = []
    executable = shutil.which('dpkg-deb')
    if not executable:
        raise ValueError('dpkg-deb unavailable')
    tool = {'binary_sha256': hash_file(Path(executable)),
        'version': subprocess.check_output([executable, '--version'], text=True, timeout=15).splitlines()[0],
        'invocation': 'dpkg-deb --fsys-tarfile PRIVATE_CHECKSUM_VERIFIED_COPY.deb'}
    with tarfile.open(bundle, 'r:gz') as archive, tempfile.TemporaryDirectory(prefix='php83-package-identities-') as temporary:
        members = {}
        for member in archive.getmembers():
            name = normalize(member.name)
            if name in members:
                raise ValueError('Duplicate bundle path')
            members[name] = member
        checksum = members.get('SHA256SUMS')
        if not checksum or not checksum.isfile():
            raise ValueError('Missing regular inner checksum manifest')
        checksums = checksum_manifest(archive.extractfile(checksum).read().decode())
        package_members = {n: m for n, m in members.items() if n.endswith('.deb')}
        if set(checksums) != set(package_members):
            raise ValueError('Checksum/package set mismatch')
        for index, name in enumerate(sorted(checksums)):
            member = package_members[name]
            if not member.isfile():
                raise ValueError('Non-regular DEB member')
            # Generated fixed names, never archive-selected paths; no member extraction.
            deb = Path(temporary) / 'input.deb'
            tar = Path(temporary) / 'payload.tar'
            with archive.extractfile(member) as source, deb.open('wb') as output:
                shutil.copyfileobj(source, output)
            if hash_file(deb) != checksums[name]:
                raise ValueError('Inner package hash mismatch')
            owner = {'package_file': name, 'package_sha256': checksums[name]}
            with tar.open('wb') as output:
                process = subprocess.run([executable, '--fsys-tarfile', str(deb)], stdout=output,
                    stderr=subprocess.PIPE, timeout=180)
            if process.returncode:
                raise ValueError('dpkg-deb payload read failed for ' + name)
            excluded = {}
            with tar.open('rb') as stream:
                payload = payload_inventory(stream, owner, excluded)
            records.extend(payload)
            packages.append({**owner, 'php_payload_occurrences': len(payload),
                'excluded_nondirectory_suffix_counts': dict(sorted(excluded.items())),
                'dpkg_deb_exit': process.returncode, 'stderr_sha256': hashlib.sha256(process.stderr).hexdigest()})
            tar.unlink(); deb.unlink()
    files = merge_payloads(records)
    joins = join_ledger(ledger, files)
    upstream = source_inventory(original)
    differential = reconcile(files, upstream, historical_map)
    resolved = sum(r['status'] == 'missing_identity_resolved' for r in joins)
    expected_missing = ledger['summary']['missing_file_hashes_by_scope'].get('packaged', 0)
    if resolved != expected_missing:
        raise ValueError('Unresolved ledger denominator mismatch')
    return {'schema': 1, 'scope': 'Published package/source byte identities only; no semantic or runtime acceptance',
        'bundle_sha256': BUNDLE_SHA, 'original_archive_sha256': SOURCE_SHA,
        'inputs': inputs, 'tool': tool, 'php_extensions': sorted(EXTENSIONS),
        'suffix_scope_limit': 'All non-directory suffixes outside the selected set are counted per package but not content-inspected or classified as executable. Extensionless PHP, shebang scripts and PHP embedded in other extensions remain uninventoried semantically.',
        'link_policy': 'PHP symlink/hardlink/non-regular entries rejected. No links or member paths extracted or followed. Non-PHP links are outside the hashed PHP inventory.',
        'packages': packages, 'files': files, 'ledger_joins': joins, 'source_differential': differential,
        'summary': {'packages': len(packages), 'php_payload_occurrences': len(records),
            'unique_php_paths': len(files), 'duplicate_php_paths': sum(len(r['owners']) > 1 for r in files.values()),
            'php_nonregular_entries': 0, 'upstream_php_files': len(upstream),
            'missing_ledger_hashes_resolved': resolved, 'known_ledger_hashes_preserved': len(joins) - resolved,
            'remaining_ledger_packaged_hashes_missing': 0, 'semantic_findings_resolved': 0},
        'no_package_hooks_installation_or_vm': True, 't0_04_complete': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Refusing existing output')
    result = build(args.repo, args.bundle, args.original)
    with args.output.open('x') as output:
        json.dump(result, output, indent=2); output.write('\n')
    print(json.dumps(result['summary'], sort_keys=True))

if __name__ == '__main__':
    main()
