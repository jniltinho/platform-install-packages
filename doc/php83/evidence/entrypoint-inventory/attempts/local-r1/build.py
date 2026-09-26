#!/usr/bin/env python3
"""Offline deterministic entrypoint-candidate inventory (synthetic-only verified).

Reads user-provided published bundle + original ZIP paths given on the command
line, but this session does NOT execute it on real inputs. No package install,
no maintainer-script execution, no member-path extraction, no network, no VM.
DEB bytes are only streamed through ``dpkg-deb --ctrl-tarfile/--fsys-tarfile``
into repo-owned scratch files and parsed as tar names/bytes in memory; archive
links are recorded, never followed.

Safe-parsing patterns (normalize, hash helpers, checksum manifest, duplicate
and traversal rejection) intentionally mirror tools/php83/package-identities/
build.py. Scope is candidate inventory only: no active-runtime, reachability,
or exhaustive-entrypoint claims. Not a hostile-archive resource sandbox.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

BUNDLE_SHA = '91629580441f6a896ebf9e51f0256532221715bee57a3e5a64c66ff0c4e3127b'
SOURCE_SHA = '58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
SOURCE_ROOT = 'server-Rigel-18.20.0/'
PHP_EXTENSIONS = {'.php', '.phtml', '.inc', '.php5'}
MAINTAINER_SCRIPTS = {'preinst', 'postinst', 'prerm', 'postrm', 'config'}
SCAN_SIZE_LIMIT = 2 * 1024 * 1024
LINE_EXCERPT_LIMIT = 300

INTERPRETER_RE = re.compile(
    r'(?P<interp>(?:/usr/(?:local/)?bin/php[0-9.]*)|\bphp[0-9.]*(?:-cgi|-cli|-fpm)?\b)'
    r'[ \t]+(?P<target>"[^"\n]{1,300}"|\'[^\'\n]{1,300}\'|[^\s;|&`"\']{1,300})'
)
DYNAMIC_CHARS_RE = re.compile(r'[\$\*\?`\[\]\{\}~]|[$][({]')
SHEBANG_PHP_RE = re.compile(r'^#!.*php', re.IGNORECASE)


def hash_stream(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(chunk)
    return h.hexdigest()


def hash_file(path):
    with Path(path).open('rb') as stream:
        return hash_stream(stream)


def normalize(name):
    if not name or name.startswith('/') or '\\' in name or '\x00' in name:
        raise ValueError('Unsafe member path')
    cleaned = name
    if cleaned.startswith('./'):
        cleaned = cleaned[2:]
    if not cleaned or cleaned.startswith('/') or '\\' in cleaned or '\x00' in cleaned:
        raise ValueError('Unsafe member path')
    if '..' in PurePosixPath(cleaned).parts:
        raise ValueError('Traversal member path')
    result = str(PurePosixPath(cleaned))
    return '' if result == '.' else result


def php_path(name):
    return PurePosixPath(name).suffix.lower() in PHP_EXTENSIONS


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


def _member_kind(member):
    if member.isdir():
        return 'dir'
    if member.issym():
        return 'symlink'
    if member.islnk():
        return 'hardlink'
    if member.isfile():
        return 'regular'
    if member.isfifo():
        return 'fifo'
    if member.ischr() or member.isblk():
        return 'device'
    return 'other'


def classify_config(path):
    tags = []
    lower = path.lower()
    if lower.startswith('etc/cron') or lower == 'etc/crontab' or 'cron.d' in lower \
            or lower.startswith('var/spool/cron'):
        tags.append('cron')
    if 'systemd/system' in lower or lower.endswith('.service') and 'systemd' in lower:
        tags.append('systemd')
    if lower.startswith('etc/init.d/') or lower.startswith('etc/init/') \
            or lower.startswith('etc/default/'):
        tags.append('init')
    if lower.startswith('etc/nginx/') or lower.startswith('etc/apache2/') \
            or lower.startswith('etc/httpd/') or lower.startswith('etc/php/'):
        tags.append('webconfig')
    return tags


def is_generated_client_candidate(path):
    lower = path.lower()
    marker = ('generated' in lower or 'gen_client' in lower or 'gen-client' in lower
              or 'api_client' in lower or 'api-client' in lower or '/client/' in lower)
    if not marker:
        return False
    return php_path(path) or PurePosixPath(path).suffix == ''


def scan_php_invocations(text, source_path, owner):
    findings = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in INTERPRETER_RE.finditer(line):
            raw = match.group('target').strip().strip('"\'')
            dynamic = bool(DYNAMIC_CHARS_RE.search(raw))
            literal = (not dynamic) and raw.lower().endswith(
                tuple(PHP_EXTENSIONS)) and '..' not in PurePosixPath(raw).parts
            findings.append({
                'source_path': source_path,
                'line': lineno,
                'line_excerpt': line.strip()[:LINE_EXCERPT_LIMIT],
                'interpreter': match.group('interp'),
                'target': raw[:LINE_EXCERPT_LIMIT],
                'target_class': 'literal_php' if literal else 'unresolved_dynamic',
                'owners': [owner],
            })
    return findings


def _decode_scan_text(data):
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return data.decode('utf-8', errors='replace')


def parse_control_stream(stream, owner):
    records = []
    file_bytes = {}
    seen = set()
    with tarfile.open(fileobj=stream, mode='r|') as archive:
        for member in archive:
            path = normalize(member.name)
            if path in seen:
                raise ValueError('Duplicate control path: ' + path)
            seen.add(path)
            kind = _member_kind(member)
            row = {'path': path, 'type': kind, 'size': member.size,
                   'mode': member.mode, 'uid': member.uid, 'gid': member.gid,
                   'owners': [owner]}
            if kind in ('symlink', 'hardlink'):
                row['linkname'] = member.linkname[:LINE_EXCERPT_LIMIT]
                records.append(row)
                continue
            if kind != 'regular':
                records.append(row)
                continue
            with archive.extractfile(member) as source:
                data = source.read()
            row['sha256'] = hashlib.sha256(data).hexdigest()
            records.append(row)
            file_bytes[path] = data
    invocations = []
    scripts = []
    for row in records:
        base = PurePosixPath(row['path']).name
        if row['type'] == 'regular' and base in MAINTAINER_SCRIPTS:
            scripts.append(row)
            text = _decode_scan_text(file_bytes[row['path']])
            invocations.extend(scan_php_invocations(text, row['path'], owner))
    return records, scripts, invocations, file_bytes


def parse_data_stream(stream, owner, excluded=None):
    records = []
    seen = set()
    invocations = []
    candidates = []
    skipped_oversize = 0
    with tarfile.open(fileobj=stream, mode='r|') as archive:
        for member in archive:
            path = normalize(member.name)
            if path in seen:
                raise ValueError('Duplicate data path within package: ' + path)
            seen.add(path)
            kind = _member_kind(member)
            row = {'path': path, 'type': kind, 'size': member.size,
                   'mode': member.mode, 'uid': member.uid, 'gid': member.gid,
                   'owners': [owner]}
            if kind == 'dir':
                records.append(row)
                continue
            if kind in ('symlink', 'hardlink'):
                row['linkname'] = member.linkname[:LINE_EXCERPT_LIMIT]
                records.append(row)
                if php_path(member.linkname) or php_path(path):
                    candidates.append({**row, 'candidate_class': 'php_link_candidate',
                                       'note': 'recorded, never followed'})
                continue
            if kind != 'regular':
                records.append(row)
                if excluded is not None:
                    excluded['nonregular:' + kind] = excluded.get('nonregular:' + kind, 0) + 1
                continue
            records.append(row)
            suffix = PurePosixPath(path).suffix.lower() or '(extensionless)'
            config_tags = classify_config(path)
            executable = bool(member.mode & 0o111)
            interesting = (php_path(path) or suffix == '(extensionless)'
                           or executable or config_tags
                           or is_generated_client_candidate(path))
            if not interesting:
                if excluded is not None:
                    excluded[suffix] = excluded.get(suffix, 0) + 1
                continue
            if member.size > SCAN_SIZE_LIMIT:
                skipped_oversize += 1
                if excluded is not None:
                    excluded['oversize_skipped'] = excluded.get('oversize_skipped', 0) + 1
                candidates.append({**row, 'sha256': None,
                                   'candidate_class': 'oversize_unscanned',
                                   'note': 'content not inspected; size over limit'})
                continue
            with archive.extractfile(member) as source:
                data = source.read()
            digest = hashlib.sha256(data).hexdigest()
            row['sha256'] = digest
            text = _decode_scan_text(data[:SCAN_SIZE_LIMIT])
            first_line = text.splitlines()[0] if text.splitlines() else ''
            shebang_php = bool(SHEBANG_PHP_RE.match(first_line.strip()))
            has_php_tag = '<?php' in data[:8192].decode('utf-8', errors='ignore').lower()
            classes = []
            if php_path(path):
                classes.append('php_family')
            if suffix == '(extensionless)' and (shebang_php or has_php_tag or executable):
                classes.append('extensionless_php_candidate')
            if shebang_php:
                classes.append('shebang_php')
            if executable:
                classes.append('executable')
            classes.extend('config:' + tag for tag in config_tags)
            if is_generated_client_candidate(path):
                classes.append('generated_client_candidate')
            if config_tags:
                invocations.extend(scan_php_invocations(text, path, owner))
            if classes:
                entry = {**row, 'candidate_class': '+'.join(sorted(classes))}
                if shebang_php:
                    entry['shebang'] = first_line.strip()[:LINE_EXCERPT_LIMIT]
                candidates.append(entry)
            elif excluded is not None:
                excluded[suffix] = excluded.get(suffix, 0) + 1
    return records, candidates, invocations, skipped_oversize


def _ensure_repo_scratch(repo, work_dir):
    repo = Path(repo).resolve()
    default = repo / 'tools/php83/entrypoint-inventory/.work'
    root = Path(work_dir).resolve() if work_dir else default
    if root != repo and repo not in root.parents:
        raise ValueError('Scratch directory must live inside the repository')
    root.mkdir(parents=True, exist_ok=True)
    return repo, root


def source_php_count(original):
    if hash_file(original) != SOURCE_SHA:
        raise ValueError('Original archive hash mismatch')
    count = 0
    seen = set()
    with zipfile.ZipFile(original) as archive:
        for member in archive.infolist():
            name = normalize(member.filename)
            if name in seen:
                raise ValueError('Duplicate original archive path')
            seen.add(name)
            if member.is_dir():
                continue
            if not name.startswith(SOURCE_ROOT):
                raise ValueError('Unexpected source archive root')
            if php_path(name[len(SOURCE_ROOT):]):
                count += 1
    return count


def build(repo, bundle, original, work_dir=None):
    if hash_file(bundle) != BUNDLE_SHA:
        raise ValueError('Published bundle hash mismatch')
    repo, scratch_root = _ensure_repo_scratch(repo, work_dir)
    evidence = repo / 'doc/php83/evidence'
    inputs = {}
    for name in ('inventory-ledger/ledger.json',
                 'source-audit/source-to-package-map.json',
                 'package-identities/primary.json'):
        path = evidence / name
        inputs[name] = hash_file(path)
    inputs['builder'] = hash_file(Path(__file__))
    executable = shutil.which('dpkg-deb')
    if not executable:
        raise ValueError('dpkg-deb unavailable')
    tool = {'binary_sha256': hash_file(Path(executable)),
            'version': subprocess.check_output(
                [executable, '--version'], text=True, timeout=15).splitlines()[0],
            'invocations': ['dpkg-deb --ctrl-tarfile PRIVATE_CHECKSUM_VERIFIED_COPY.deb',
                            'dpkg-deb --fsys-tarfile PRIVATE_CHECKSUM_VERIFIED_COPY.deb']}
    packages = []
    all_candidates = []
    all_invocations = []
    control_total = 0
    data_total = 0
    data_regular = 0
    data_dirs = 0
    data_links = 0
    excluded = {}
    literal_count = 0
    dynamic_count = 0
    with tarfile.open(bundle, 'r:gz') as archive, \
            tempfile.TemporaryDirectory(prefix='php83-entrypoint-inventory-',
                                        dir=str(scratch_root)) as temporary:
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
            deb = Path(temporary) / ('input-%d.deb' % index)
            ctrl_tar = Path(temporary) / ('ctrl-%d.tar' % index)
            data_tar = Path(temporary) / ('data-%d.tar' % index)
            with archive.extractfile(member) as source, deb.open('wb') as output:
                shutil.copyfileobj(source, output)
            if hash_file(deb) != checksums[name]:
                raise ValueError('Inner package hash mismatch')
            owner = {'package_file': name, 'package_sha256': checksums[name]}
            for flag, target in (('--ctrl-tarfile', ctrl_tar), ('--fsys-tarfile', data_tar)):
                with target.open('wb') as output:
                    process = subprocess.run(
                        [executable, flag, str(deb)], stdout=output,
                        stderr=subprocess.PIPE, timeout=180)
                if process.returncode:
                    raise ValueError('dpkg-deb %s read failed for %s' % (flag, name))
            with ctrl_tar.open('rb') as stream:
                ctrl_records, scripts, ctrl_inv, _ = parse_control_stream(stream, owner)
            with data_tar.open('rb') as stream:
                data_records, candidates, data_inv, _ = parse_data_stream(
                    stream, owner, excluded)
            control_total += len(ctrl_records)
            data_total += len(data_records)
            data_regular += sum(1 for r in data_records if r['type'] == 'regular')
            data_dirs += sum(1 for r in data_records if r['type'] == 'dir')
            data_links += sum(1 for r in data_records
                              if r['type'] in ('symlink', 'hardlink'))
            all_candidates.extend(candidates)
            all_invocations.extend(ctrl_inv + data_inv)
            packages.append({**owner,
                             'control_members': len(ctrl_records),
                             'maintainer_scripts': sorted(r['path'] for r in scripts),
                             'data_members': len(data_records),
                             'entrypoint_candidates': len(candidates)})
            for stale in (deb, ctrl_tar, data_tar):
                try:
                    stale.unlink()
                except FileNotFoundError:
                    pass
    upstream_php = source_php_count(original)
    literal_count = sum(1 for f in all_invocations if f['target_class'] == 'literal_php')
    dynamic_count = sum(1 for f in all_invocations
                        if f['target_class'] == 'unresolved_dynamic')
    by_class = {}
    for entry in all_candidates:
        by_class[entry['candidate_class']] = by_class.get(entry['candidate_class'], 0) + 1
    return {'schema': 1,
            'scope': 'Entrypoint-candidate inventory only; literal evidence with '
                     'dynamic paths unresolved. No active-runtime, reachability, '
                     'or exhaustive-entrypoint claim.',
            'bundle_sha256': BUNDLE_SHA, 'original_archive_sha256': SOURCE_SHA,
            'inputs': inputs, 'tool': tool,
            'php_extensions': sorted(PHP_EXTENSIONS),
            'maintainer_scripts': sorted(MAINTAINER_SCRIPTS),
            'config_taxonomy': ['cron', 'systemd', 'init', 'webconfig'],
            'link_policy': 'Links recorded with target names only; never followed, '
                           'extracted, or executed.',
            'execution_policy': 'Maintainer scripts and payload files are parsed '
                                'as text only; nothing is installed or executed.',
            'packages': packages, 'candidates': sorted(
                all_candidates, key=lambda r: (r['path'], str(r['owners']))),
            'php_invocations': sorted(
                all_invocations, key=lambda r: (r['source_path'], r['line'])),
            'summary': {'packages': len(packages),
                        'control_members_total': control_total,
                        'data_members_total': data_total,
                        'data_regular': data_regular,
                        'data_directories': data_dirs,
                        'data_links': data_links,
                        'entrypoint_candidates': len(all_candidates),
                        'candidates_by_class': dict(sorted(by_class.items())),
                        'php_invocations_literal': literal_count,
                        'php_invocations_unresolved_dynamic': dynamic_count,
                        'excluded_suffix_counts': dict(sorted(excluded.items())),
                        'upstream_php_files': upstream_php,
                        'semantic_findings_resolved': 0},
            'no_package_hooks_installation_or_vm': True,
            'no_runtime_or_reachability_claim': True,
            't0_04_complete': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, default=None)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Refusing existing output')
    result = build(args.repo, args.bundle, args.original, args.work_dir)
    with args.output.open('x') as output:
        json.dump(result, output, indent=2)
        output.write('\n')
    print(json.dumps(result['summary'], sort_keys=True))


if __name__ == '__main__':
    main()
