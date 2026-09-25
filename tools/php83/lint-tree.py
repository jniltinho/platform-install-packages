#!/usr/bin/env python3
"""Inventory/lint an extracted tree without executing application PHP code."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('root', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('--php', default='php8.3')
parser.add_argument('--workers', type=int, default=4)
args = parser.parse_args()
root = args.root.resolve(strict=True)
if not root.is_dir() or not 1 <= args.workers <= 16:
    parser.error('root must be a directory; workers must be 1..16')
paths = sorted(p for p in root.rglob('*') if p.is_file() and not p.is_symlink()
               and p.suffix.lower() in {'.php', '.phtml', '.inc', '.php5'})
version = subprocess.check_output([args.php, '-v'], text=True).splitlines()[0]


def lint(path):
    relative = str(path.relative_to(root))
    try:
        result = subprocess.run(
            [args.php, '-d', 'short_open_tag=1', '-d', 'error_reporting=32767',
             '-d', 'display_errors=stderr', '-l', str(path)],
            capture_output=True, text=True, timeout=30)
        diagnostics = '\n'.join(line for line in (result.stdout + result.stderr).splitlines()
                                if not line.startswith('No syntax errors detected'))
        return {'path': relative, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'returncode': result.returncode,
                'diagnostics': diagnostics.replace(str(root) + '/', '')}
    except subprocess.TimeoutExpired:
        return {'path': relative, 'returncode': 124, 'diagnostics': 'Lint timed out'}


with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
    records = list(executor.map(lint, paths))
report = {'php': version, 'scope': 'Syntax/compile checks only; not runtime acceptance',
          'file_count': len(records),
          'failed_count': sum(r['returncode'] != 0 for r in records),
          'diagnostic_count': sum(bool(r['diagnostics']) for r in records),
          'files': records}
args.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'files'}, indent=2))
