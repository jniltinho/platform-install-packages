#!/usr/bin/env python3
"""Build a content-pinned, lab-only source ZIP; never change the upstream archive."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import stat
import subprocess
import tempfile
import zipfile
import zlib

STAMP = (2020, 1, 1, 0, 0, 0)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(name):
    parts = (name[:-1] if name.endswith('/') else name).split('/')
    if not name or '\\' in name or any(ord(c) < 32 for c in name):
        raise ValueError('Unsafe archive path')
    if any(p in ('', '.', '..') for p in parts) or PurePosixPath(name).is_absolute():
        raise ValueError('Unsafe archive path')
    return name


def encode(data):
    return (json.dumps(data, sort_keys=True, indent=2) + '\n').encode()


def build(archive, patch_dir, output_dir):
    manifest_bytes = (patch_dir / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    archive_bytes = archive.read_bytes()
    if sha(archive_bytes) != manifest['upstream_sha256']:
        raise ValueError('Upstream checksum mismatch')
    root = safe_path(manifest['upstream_root'])
    if '/' in root or not re.fullmatch(r'[A-Za-z0-9.-]+', manifest['revision']):
        raise ValueError('Invalid root/revision')
    patches = []
    changed = set()
    patch_names = set()
    for entry in manifest['patches']:
        path = safe_path(entry['path'])
        name = safe_path(entry['patch'])
        if '/' in name or not name.endswith('.patch') or path in changed or name in patch_names:
            raise ValueError('Duplicate target or non-leaf patch name')
        data = (patch_dir / name).read_bytes()
        if sha(data) != entry['sha256']:
            raise ValueError('Patch checksum mismatch')
        patches.append((entry, data))
        changed.add(path)
        patch_names.add(name)
    metadata = dict(manifest, builder_sha256=sha(Path(__file__).read_bytes()),
                    manifest_sha256=sha(manifest_bytes))
    reserved = root + '/.php83-experimental/'
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as source, tempfile.TemporaryDirectory() as temp:
        metadata['upstream_zip_comment_hex'] = source.comment.hex()
        members = source.infolist()
        names = set()
        for item in members:
            name = safe_path(item.filename)
            if name in names or not (name == root + '/' or name.startswith(root + '/')):
                raise ValueError('Duplicate or unexpected root entry')
            if name.startswith(reserved) or stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError('Reserved metadata path or symlink in source')
            names.add(name)
        stage = Path(temp)
        for entry, data in patches:
            original = source.read(root + '/' + entry['path'])
            if sha(original) != entry['before_sha256']:
                raise ValueError('Patch input checksum mismatch')
            target = stage / entry['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(original)
        for entry, data in patches:
            run = subprocess.run(['patch', '--batch', '--forward', '--fuzz=0', '--no-backup-if-mismatch', '-p1'],
                                 input=data, cwd=stage, capture_output=True, timeout=60,
                                 env=dict(os.environ, LC_ALL='C'))
            diagnostics = (run.stdout + run.stderr).decode(errors='replace')
            if run.returncode or 'offset' in diagnostics or 'fuzz' in diagnostics:
                raise ValueError('Patch did not apply exactly: ' + entry['patch'])
        # Recheck every output after the whole series, including cross-patch writes.
        for entry, _ in patches:
            if sha((stage / entry['path']).read_bytes()) != entry['after_sha256']:
                raise ValueError('Patch output checksum mismatch')
        if {str(p.relative_to(stage)) for p in stage.rglob('*') if p.is_file()} != changed:
            raise ValueError('Unexpected patch output files')
        extras = {reserved + 'manifest.json': encode(metadata),
                  reserved + 'README.txt': b'EXPERIMENTAL PHP 8.3 SOURCE ONLY. NOT A RELEASE.\n'
                  b'Known incompatibilities remain. Do not deploy to production.\n'
                  b'Original library license headers are retained. See patch manifest.\n'}
        extras.update({reserved + e['patch']: data for e, data in patches})
        output_dir.mkdir(parents=True, exist_ok=False)
        basename = root[7:] if root.startswith('server-') else root
        output = output_dir / (basename + '-php83-experimental.' + manifest['revision'] + '.zip')
        temporary = output.with_suffix('.zip.partial')
        try:
            with zipfile.ZipFile(temporary, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as target:
                target.comment = source.comment
                by_name = {i.filename: i for i in members}
                for name in sorted(set(by_name) | set(extras)):
                    entry = zipfile.ZipInfo(name, date_time=STAMP)
                    entry.create_system = 3
                    entry.compress_type = zipfile.ZIP_DEFLATED
                    if name in extras:
                        data, mode = extras[name], 0o100644
                    else:
                        original = by_name[name]
                        entry.comment = original.comment
                        relative = name[len(root) + 1:]
                        data = (stage / relative).read_bytes() if relative in changed else source.read(original)
                        mode = 0o40755 if original.is_dir() else (0o100755 if (original.external_attr >> 16) & 0o111 else 0o100644)
                    entry.external_attr = (mode << 16) | (0x10 if name.endswith('/') else 0)
                    target.writestr(entry, data, compresslevel=9)
            temporary.rename(output)
        finally:
            temporary.unlink(missing_ok=True)
    digest = sha(output.read_bytes())
    (output_dir / 'SHA256SUMS').write_text(digest + '  ' + output.name + '\n')
    (output_dir / 'build-report.json').write_bytes(encode(dict(metadata,
        zip_sha256=digest, zip_name=output.name,
        python=platform.python_version(), zlib=zlib.ZLIB_RUNTIME_VERSION)))
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('output_dir', type=Path, help='Must not exist')
    parser.add_argument('--patch-dir', type=Path,
                        default=Path(__file__).resolve().parents[2] / 'patches/php83')
    args = parser.parse_args()
    print(build(args.archive, args.patch_dir, args.output_dir))
