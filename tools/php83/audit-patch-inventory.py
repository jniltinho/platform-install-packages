#!/usr/bin/env python3
"""Offline identity/application audit. Never promotes or combines held patches."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def confined(root, relative):
    """Reject traversal and symlink escapes, even for paths not yet present."""
    if not isinstance(relative, str) or not relative or '\\' in relative:
        raise ValueError('invalid relative path')
    path = PurePosixPath(relative)
    if path.is_absolute() or any(x in ('', '.', '..') for x in relative.split('/')):
        raise ValueError('unsafe relative path: ' + relative)
    result = root.joinpath(*path.parts)
    if not result.resolve().is_relative_to(root.resolve()):
        raise ValueError('symlink escape: ' + relative)
    return result


def entries(repo):
    root = repo / 'patches/php83'
    manifest_path = confined(repo, 'patches/php83/manifest.json')
    manifest = json.loads(manifest_path.read_text())
    records = []
    documents = [(manifest_path, 'active', manifest, manifest['patches'])]
    for file in sorted((root / 'held').rglob('*.json')):
        confined(repo, file.relative_to(repo).as_posix())
        metadata = json.loads(file.read_text())
        documents.append((file, 'held', metadata, metadata.get('files', [metadata])))
    for file, scope, metadata, items in documents:
        for item in items:
            name = item.get('patch')
            if name is None:
                name = 'core_compile.yml.patch' if file.stem == 'core_compile' else file.stem + '.patch'
            # Symfony's files[] uses repository-relative paths; other formats
            # use paths relative to the metadata document.
            if name.startswith('patches/'):
                patch_rel = name
            else:
                confined(file.parent, name)
                patch_rel = (file.parent.relative_to(repo) / name).as_posix()
            patch = confined(repo, patch_rel)
            expected_scope = root / ('held' if scope == 'held' else '')
            if not patch.resolve().is_relative_to(expected_scope.resolve()):
                raise ValueError('patch outside metadata scope: ' + patch_rel)
            if scope == 'active' and patch.resolve().is_relative_to((root / 'held').resolve()):
                raise ValueError('active metadata references held patch')
            sha = item.get('sha256', item.get('patch_sha256'))
            if 'sha256' in item and 'patch_sha256' in item and item['sha256'] != item['patch_sha256']:
                raise ValueError('conflicting patch hashes: ' + patch_rel)
            for value in (sha, item.get('before_sha256'), item.get('after_sha256')):
                if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
                    raise ValueError('invalid or missing hash: ' + patch_rel)
            records.append(dict(patch=patch_rel, path=item['path'], scope=scope,
                                metadata=file.relative_to(repo).as_posix(),
                                status=item.get('status', metadata.get('status', 'unknown')),
                                patch_sha256=sha, before_sha256=item['before_sha256'],
                                after_sha256=item['after_sha256']))
    return records


def apply_isolated(source, patch, path):
    # Permit precisely one ordinary unified file diff. Patch headers cannot
    # point at arbitrary files, create files, or select another source target.
    headers = [line.split('\t', 1)[0] for line in patch.decode('utf-8').splitlines()
               if line.startswith(('--- ', '+++ '))]
    if headers != ['--- a/' + path, '+++ b/' + path]:
        raise ValueError('patch headers do not match the sole declared path')
    with tempfile.TemporaryDirectory(prefix='php83-patch-audit-') as temporary:
        root = Path(temporary)
        target = confined(root, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source)
        run = subprocess.run(['patch', '--batch', '--fuzz=0', '--forward', '-p1'],
                             input=patch, cwd=root, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, env={**os.environ, 'LC_ALL': 'C'},
                             timeout=30, check=False)
        output = run.stdout.decode('utf-8', errors='replace')
        if run.returncode or re.search(r'offset|reversed|fuzz|failed|previously applied', output, re.I):
            raise ValueError('non-exact patch application: ' + output.strip())
        files = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        if files != {path}:
            raise ValueError('patch created unexpected files')
        return target.read_bytes(), output.strip()


def audit(repo, source_root):
    repo, source_root = Path(repo).resolve(), Path(source_root).resolve()
    report = dict(schema=1, promotion=False, stacking=False, entries=[], alternative_groups=[], errors=[])
    try:
        if not source_root.is_dir():
            raise ValueError('source root is not a directory')
        records = entries(repo)
        if not records:
            report['errors'].append('empty patch inventory')
        actual = set()
        for file in (repo / 'patches/php83').rglob('*.patch'):
            rel = file.relative_to(repo).as_posix()
            confined(repo, rel)
            actual.add(rel)
        counts = {}
        for record in records:
            counts[record['patch']] = counts.get(record['patch'], 0) + 1
        for name in sorted(actual | set(counts)):
            if name not in actual:
                report['errors'].append('metadata references missing patch: ' + name)
            elif counts.get(name, 0) != 1:
                report['errors'].append('patch metadata count must be one: ' + name)
        groups = {}
        for record in records:
            groups.setdefault(record['path'], []).append(record['patch'])
        report['alternative_groups'] = [dict(path=p, patches=names, stacked=False)
                                        for p, names in sorted(groups.items()) if len(names) > 1]
        for record in records:
            result = dict(record, result='FAIL')
            try:
                source = confined(source_root, record['path']).read_bytes()
                patch = confined(repo, record['patch']).read_bytes()
                if digest(patch) != record['patch_sha256']:
                    raise ValueError('patch SHA256 drift')
                if digest(source) != record['before_sha256']:
                    raise ValueError('original source SHA256 drift')
                after, output = apply_isolated(source, patch, record['path'])
                if digest(after) != record['after_sha256']:
                    raise ValueError('patched source SHA256 drift')
                result.update(result='PASS', patch_output=output)
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                result['error'] = str(exc)
                report['errors'].append(record['patch'] + ': ' + str(exc))
            report['entries'].append(result)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        report['errors'].append('inventory: ' + str(exc))
    report['result'] = 'FAIL' if report['errors'] else 'PASS'
    report['counts'] = {scope: sum(e['scope'] == scope for e in report['entries'])
                        for scope in ('active', 'held')}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path.cwd())
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    for protected in (args.source_root.resolve(), (args.repo_root / 'patches/php83').resolve()):
        if output.is_relative_to(protected):
            parser.error('--output must not overwrite audited sources or patch metadata')
    report = audit(args.repo_root, args.source_root)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(result=report['result'], counts=report['counts'], errors=report['errors'])))
    return 0 if report['result'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
