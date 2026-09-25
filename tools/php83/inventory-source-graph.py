#!/usr/bin/env python3
"""Join the public archive inventory with exported graph membership/coverage."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('archive', type=Path)
parser.add_argument('raw_tree', type=Path)
parser.add_argument('graph_view', type=Path)
parser.add_argument('graph_files', type=Path, help='query_graph File path table export')
parser.add_argument('evidence_dir', type=Path, help='Contains complete coverage.json')
a = parser.parse_args()
expected = '58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
if hashlib.sha256(a.archive.read_bytes()).hexdigest() != expected:
    raise ValueError('Wrong upstream archive')
coverage = json.loads((a.evidence_dir / 'coverage.json').read_text())
entries = coverage['scopes'][0]['entries']
if len(entries) != coverage['scopes'][0]['total']:
    raise ValueError('Incomplete coverage pagination')
partial = {e['path'] for e in entries if e['kind'] == 'parse_partial'}
ignored = {e['path']: e['detail'] for e in entries if e['kind'] == 'not_indexed_file'}
files = {line[2:] for line in a.graph_files.read_text().splitlines()[1:] if line.startswith('  ')}
rows, differences = [], []
counts, top = Counter(), Counter()
with zipfile.ZipFile(a.archive) as archive:
    for member in sorted(archive.infolist(), key=lambda item: item.filename):
        if member.is_dir():
            continue
        path = member.filename.split('/', 1)[1]
        data = archive.read(member)
        if (a.raw_tree / path).read_bytes() != data:
            raise ValueError('Raw source changed: ' + path)
        if (a.graph_view / path).read_bytes() != data:
            if Path(path).name != '.gitignore':
                raise ValueError('Unexpected analysis source change: ' + path)
            differences.append(path)
        status = ('partial_parse' if path in partial else 'file_node_present' if path in files
                  else 'excluded:' + ignored[path] if path in ignored else 'no_file_node')
        rows.append([path, len(data), hashlib.sha256(data).hexdigest(), status])
        counts[status] += 1
        top[path.split('/')[0]] += 1
with (a.evidence_dir / 'file-inventory.csv').open('w') as stream:
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['path', 'bytes', 'sha256', 'graph_status'])
    writer.writerows(rows)
summary = {'archive_sha256': expected, 'project': coverage['project'],
           'generation': coverage['metadata']['generation'], 'source_files': len(rows),
           'graph_status_counts': dict(counts), 'top_level_file_counts': dict(top),
           'analysis_only_metadata_differences': differences,
           'analysis_only_added_files': ['.cbmignore', '.codebase-memory.json'],
           'raw_tree_bytes_verified': True}
(a.evidence_dir / 'inventory-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
