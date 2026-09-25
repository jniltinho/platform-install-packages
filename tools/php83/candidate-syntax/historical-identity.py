#!/usr/bin/env python3
"""Read-only audit of historical report identities and selected pathsets."""
import hashlib
import json
from pathlib import Path
import zipfile
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
AUDIT = Path('/tmp/kaltura-php83-audit')
names = ['source-lint.json', 'source-phpcompatibility.json', 'packaged-lint.json', 'packaged-phpcompatibility.json', 'php74-packaged-lint.json']
inputs = {str(AUDIT/n): {'sha256': hashlib.sha256((AUDIT/n).read_bytes()).hexdigest(), 'bytes': (AUDIT/n).stat().st_size} for n in names}
inputs[str(AUDIT/'Rigel-18.20.0.zip')] = {'sha256': hashlib.sha256((AUDIT/'Rigel-18.20.0.zip').read_bytes()).hexdigest(), 'bytes': (AUDIT/'Rigel-18.20.0.zip').stat().st_size}
data = {n: json.loads((AUDIT/n).read_text()) for n in names}
raw = data['source-lint.json']
with zipfile.ZipFile(AUDIT/'Rigel-18.20.0.zip') as z:
    selected = {i.filename.split('/', 1)[1] for i in z.infolist() if not i.is_dir() and Path(i.filename).suffix.lower() in {'.php', '.phtml', '.inc', '.php5'}}
    source_equal = selected == {r['path'] for r in raw['files']}
    hashes_equal = all(hashlib.sha256(z.read('server-Rigel-18.20.0/'+r['path'])).hexdigest() == r['sha256'] for r in raw['files'])
    rawstatic_equal = selected == {p.removeprefix('/home/vagrant/php83-audit/server-Rigel-18.20.0/') for p in data['source-phpcompatibility.json']['files']}
package_equal = {r['path'] for r in data['packaged-lint.json']['files']} == {p.removeprefix('/home/vagrant/php83-audit/packaged/') for p in data['packaged-phpcompatibility.json']['files']}
counts = {}
for name, report in data.items():
    if 'phpcompatibility' in name:
        counts[name] = {'files_scanned': len(report['files']), 'files_with_nonempty_messages': sum(bool(v['messages']) for v in report['files'].values()), 'totals': report['totals']}
    else:
        counts[name] = {'files_scanned': len(report['files']), 'compiler_rejected': sum(r['returncode'] == 255 for r in report['files']), 'other_nonzero': sum(r['returncode'] not in (0, 255) for r in report['files']), 'diagnostic_files': sum(bool(r['diagnostics']) for r in report['files']), 'accepted_with_diagnostics': sum(r['returncode'] == 0 and bool(r['diagnostics']) for r in report['files'])}
lockpath = REPO/'tools/php83/analyzer/composer.lock'
lock = json.loads(lockpath.read_text())
print(json.dumps({'schema': 1, 'scope': 'read-only historical report/path/hash accounting; no VM or PHP execution',
 'command': 'python3 tools/php83/candidate-syntax/historical-identity.py',
 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'inputs': inputs,
 'checks': {'raw_lint_paths_equal_selected_zip_paths': source_equal, 'all_raw_lint_file_hashes_match_original_zip': hashes_equal, 'raw_static_paths_equal_selected_zip_paths': rawstatic_equal, 'packaged_static_paths_equal_packaged_lint_paths': package_equal},
 'counts': counts, 'analyzer': {'lock_sha256': hashlib.sha256(lockpath.read_bytes()).hexdigest(), 'lock_content_hash': lock['content-hash'], 'packages': [{'name': p['name'], 'version': p['version'], 'reference': p['source']['reference'], 'dist_shasum': p['dist']['shasum']} for p in lock['packages']]},
 'correction': 'Historical static-summary.json files_with_findings=11784 is scanned files; actual raw files with messages=562 and packaged=919.',
 'limits': ['4,711 static rows overlap raw/package scope and are not distinct confirmed defects.', 'Syntax accepted files with diagnostics are not compiler rejections.', 'These report-set checks do not authenticate packaged payload bytes.', 'Other extensions, generated runtime code, dynamic includes, entrypoint reachability and analyzer manual blind spots remain open.', 'Installed analyzer file hashes/configuration and historical shell/exit provenance were not captured by these imported reports.']}, indent=2))
