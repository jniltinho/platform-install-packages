"""Pinned ZIP literal notice census; never infers license inheritance or executes PHP."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

PIN = '58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
ROOT = 'server-Rigel-18.20.0/'
MARKER = re.compile(r'@license\b|SPDX-License-Identifier\s*:|under the .{0,100}licen[cs]e|permission is hereby granted|licensed under|copyright', re.I)
NOTICE_NAME = re.compile(r'^(?:[A-Za-z0-9-]+_)?(license|licence|copying|notice|copyright)(?:_[A-Za-z0-9-]+)?(\.[A-Za-z0-9_-]+)?$',re.I)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def inspect(path, raw):
    # Bounded header evidence plus complete identified notice files. No inference
    # that a copyright line grants rights or that adjacent files inherit a license.
    notice = NOTICE_NAME.fullmatch(PurePosixPath(path).name) is not None
    text = raw.decode('utf-8', 'replace')
    # LF-based line numbering agrees with source editors; form feeds stay in-line.
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    limit = len(lines) if notice else min(100, len(lines))
    evidence = [{'line': i+1, 'literal': line.strip()[:400], 'truncated': len(line.strip())>400}
                for i,line in enumerate(lines[:limit]) if MARKER.search(line)]
    return {'path':path,'sha256':digest(raw),'bytes':len(raw),
            'dedicated_notice_name':notice,'inspected_lines':limit,
            'text_representation':'UTF-8 replacement decoding; stripped display excerpts, not byte-exact quotations',
            'decode_replacement_present':'\ufffd' in text,
            'literal_notice_candidates':evidence,
            'license_applicability':'NOT_ADJUDICATED',
            'absence_claim':False}


def build(archive):
    archive = Path(archive)
    before = archive.read_bytes()
    if digest(before) != PIN:
        raise ValueError('ARCHIVE_PIN')
    rows = []
    with zipfile.ZipFile(archive) as z:
        seen=set()
        for item in sorted(z.infolist(),key=lambda x:x.filename):
            if item.filename in seen:raise ValueError('DUPLICATE_MEMBER')
            seen.add(item.filename)
            if not item.filename.startswith(ROOT):raise ValueError('ROOT')
            rel=item.filename[len(ROOT):]
            if '..' in PurePosixPath(rel).parts or rel.startswith('/'):raise ValueError('MEMBER_PATH')
            if item.is_dir() or not rel.startswith('vendor/'):continue
            rows.append(inspect(rel,z.read(item)))
    if digest(archive.read_bytes())!=PIN:raise ValueError('ARCHIVE_CHANGED')
    groups={}
    for row in rows:
        parts=PurePosixPath(row['path']).parts
        directory='/'.join(parts[:2])+'/' if len(parts)>2 else 'vendor/'
        g=groups.setdefault(directory,{'files':0,'files_with_literal_candidates':0,'dedicated_notice_files':0})
        g['files']+=1;g['files_with_literal_candidates']+=bool(row['literal_notice_candidates']);g['dedicated_notice_files']+=row['dedicated_notice_name']
    return {'schema':1,'archive_sha256':PIN,'scope':'All vendor file identities; lexical header/notice candidates only, not legal approval, whole-file absence or runtime reachability.',
            'header_line_limit':100,'summary':{'files':len(rows),'groups':groups},'files':rows}


def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    result=build(a.archive)
    with Path(a.output).open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'files':result['summary']['files'],'output_sha256':digest(Path(a.output).read_bytes()),'license_approvals':0}))

if __name__=='__main__':main()
