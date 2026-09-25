#!/usr/bin/env python3
"""Read-only paired ZIP/source inventory and PHP -n -l; never include application code."""
import concurrent.futures
import hashlib
import json
import os
import re
from pathlib import Path
import stat
import subprocess
import time
import zipfile

EXP9_PIN = 'cb61e4cd11009bbf9e6e362dfafa5ef2f4af22da817c75fedbd7741a08e44cbc'
CONTRACT = Path(__file__).with_name('input-contract.json')


def load_contract(path=CONTRACT):
    contract = json.loads(Path(path).read_text())
    require(contract.get('schema') == 1, 'Unsupported contract')
    pins = contract.get('pins', {})
    require(set(pins) == {'exp9', 'exp10'} and pins['exp9'] == EXP9_PIN,
            'Wrong paired artifact contract')
    require(isinstance(pins['exp10'], str) and re.fullmatch(r'[0-9a-f]{64}', pins['exp10']),
            'Exp10 pin pending or invalid; do not stage or run')
    require(pins['exp10'] != pins['exp9'], 'Candidate must differ from baseline')
    targets = contract.get('targets', [])
    require(isinstance(targets, list) and len(targets) == 43, 'Expected 43 reviewed targets')
    paths = set()
    for target in targets:
        name = target.get('path', '')
        path = Path(name)
        require(name and not path.is_absolute() and '..' not in path.parts and
                str(path) == name and '\\' not in name and path.suffix.lower() in SUFFIXES,
                'Unsafe target path')
        require(name not in paths, 'Duplicate target')
        paths.add(name)
        for variant in ('exp9', 'exp10'):
            require(isinstance(target.get(variant + '_sha256'), str) and
                    re.fullmatch(r'[0-9a-f]{64}', target[variant + '_sha256']), 'Invalid target hash')
        require(target['exp9_sha256'] != target['exp10_sha256'], 'Unchanged target')
    return contract

SUFFIXES = {'.php', '.phtml', '.inc', '.php5'}
PHP = '/usr/bin/php8.3'
FLAGS = ['-n', '-d', 'short_open_tag=1', '-d', 'error_reporting=32767',
         '-d', 'display_errors=stderr', '-d', 'log_errors=0', '-l']

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def archive_inventory(archive, source, expected):
    require(sha(archive) == expected, 'Archive identity mismatch')
    source = Path(source)
    require(source.is_dir() and not source.is_symlink(), 'Invalid source root')
    inventory = {}
    seen = set()
    with zipfile.ZipFile(archive) as z:
        for entry in z.infolist():
            p = Path(entry.filename)
            require(not p.is_absolute() and '..' not in p.parts and p.parts[0] == 'server-Rigel-18.20.0', 'Unsafe archive path')
            require(entry.filename not in seen, 'Duplicate archive entry')
            seen.add(entry.filename)
            require(not stat.S_ISLNK(entry.external_attr >> 16), 'Archive symlink')
            if entry.is_dir():
                continue
            path = source.joinpath(*p.parts[1:])
            require(path.is_file() and not path.is_symlink(), 'Missing/nonregular source')
            data = z.read(entry)
            require(path.read_bytes() == data, 'Extracted bytes mismatch')
            inventory[str(Path(*p.parts[1:]))] = hashlib.sha256(data).hexdigest()
    files = []
    for path in source.rglob('*'):
        require(not path.is_symlink(), 'Source symlink')
        if path.is_file():
            files.append(str(path.relative_to(source)))
        else:
            require(path.is_dir(), 'Special source object')
    require(set(files) == set(inventory), 'Unexpected source files')
    return inventory

def summarize(records):
    return {'files_scanned': len(records),
            'compiler_rejected': sum(r['exit'] == 255 for r in records),
            'compiler_accepted': sum(r['exit'] == 0 for r in records),
            'incomplete': sum(r['exit'] not in (0, 255) for r in records),
            'diagnostic_files': sum(bool(r['diagnostics']) for r in records),
            'accepted_with_diagnostics': sum(r['exit'] == 0 and bool(r['diagnostics']) for r in records)}

def lint(source, relative, expected_hash):
    path = source/relative
    command = [PHP]+FLAGS+[str(path)]
    require(sha(path) == expected_hash, 'Pre-lint source drift')
    started = time.monotonic_ns()
    try:
        run = subprocess.run(command, capture_output=True, text=True, timeout=20)
        code = run.returncode
        diagnostics = '\n'.join(line for line in (run.stdout+run.stderr).splitlines()
                                if not line.startswith('No syntax errors detected'))
        diagnostics = diagnostics.replace(str(source)+'/', '')
    except subprocess.TimeoutExpired:
        code = 124
        diagnostics = 'Syntax subprocess timed out; incomplete evidence'
    require(sha(path) == expected_hash, 'Post-lint source drift')
    return {'path': relative, 'sha256': expected_hash, 'command': command, 'exit': code,
            'diagnostics': diagnostics, 'duration_ns': time.monotonic_ns()-started}

def runtime_identity():
    require(os.geteuid() == 1000, 'Requires unprivileged lab runner')
    require(Path('/audit').is_dir(), 'Missing audit mounts')
    for mounted in ('/audit/tools', '/audit/exp9', '/audit/exp10', '/audit/exp9.zip', '/audit/exp10.zip'):
        require(os.statvfs(mounted).f_flag & os.ST_RDONLY, 'Audit bind is not read-only')
    links = subprocess.check_output(['/usr/bin/ldd', PHP], text=True)
    require('not found' not in links, 'Missing runtime library')
    libraries = {path: sha(path) for path in sorted(set(re.findall(r'(/[^\s()]+)', links)))}
    version = subprocess.check_output([PHP, '-n', '-v'], text=True)
    require(version.startswith('PHP 8.3.'), 'Requires PHP8.3 runtime')
    modules = subprocess.check_output([PHP, '-n', '-m'], text=True)
    ini = subprocess.check_output([PHP, '-n', '--ini'], text=True)
    require('Loaded Configuration File:         (none)' in ini, 'Unexpected INI loaded')
    return {'command': PHP, 'resolved_path': str(Path(PHP).resolve()), 'sha256': sha(PHP),
            'version': version, 'modules': modules, 'ini': ini, 'linked_library_sha256': libraries,
            'environment': {'LC_ALL': os.environ.get('LC_ALL'), 'TZ': os.environ.get('TZ')}}

def compare_reports(reports, contract):
    old = {r['path']: r for r in reports['exp9']['records']}
    new = {r['path']: r for r in reports['exp10']['records']}
    require(len(old) == len(reports['exp9']['records']) and
            len(new) == len(reports['exp10']['records']), 'Duplicate scan record')
    require(old.keys() == new.keys(), 'Selected pathset mismatch')
    targets = {t['path']: t for t in contract['targets']}
    require(targets.keys() <= old.keys(), 'Target absent from scan')
    for path, target in targets.items():
        require(old[path]['sha256'] == target['exp9_sha256'] and
                new[path]['sha256'] == target['exp10_sha256'], 'Target identity mismatch')
    changed = {p for p in old if old[p]['sha256'] != new[p]['sha256']}
    require(changed == targets.keys(), 'Unexpected changed PHP source pathset')
    unchanged = old.keys() - targets.keys()
    differing = sorted(p for p in unchanged if
                       (old[p]['exit'], old[p]['diagnostics']) !=
                       (new[p]['exit'], new[p]['diagnostics']))
    old_rejected = {p for p in old if old[p]['exit'] == 255}
    new_rejected = {p for p in new if new[p]['exit'] == 255}
    checks = {
        'both_scan_all_11784_files': len(old) == len(new) == 11784,
        '43_selected_targets': len(targets) == 43,
        'all_targets_previously_rejected': all(old[p]['exit'] == 255 for p in targets),
        'all_targets_now_accepted': all(new[p]['exit'] == 0 for p in targets),
        'unchanged_sources_same_outcome_and_diagnostics': not differing,
        'remaining_rejected_paths_unchanged': new_rejected == old_rejected - targets.keys(),
        'no_incomplete_subprocesses': all(r['exit'] in (0, 255) for variant in reports.values()
                                         for r in variant['records']),
        'observed_exp9_rejections_54': len(old_rejected) == 54,
        'observed_exp10_rejections_11': len(new_rejected) == 11,
    }
    return {'checks': checks, 'bounded_regression_pass': all(checks.values()),
            'unchanged_outcome_differences': differing,
            'target_rejections_after': sorted(targets.keys() & new_rejected),
            'remaining_rejected_paths': sorted(new_rejected),
            'scope': '43-target compiler repair only; remaining rejections are not waived'}

def run():
    contract = load_contract()
    runtime = runtime_identity()
    harness = {p.name: sha(p) for p in Path('/audit/tools').iterdir() if p.is_file()}
    reports = {}
    for variant, pin in contract['pins'].items():
        archive = Path('/audit')/(variant+'.zip')
        source = Path('/audit')/variant
        before = archive_inventory(archive, source, pin)
        selected = sorted(path for path in before if Path(path).suffix.lower() in SUFFIXES)
        require(len(selected) == 11784, 'Unexpected PHP-like inventory')
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            records = list(pool.map(lambda path: lint(source, path, before[path]), selected))
        require(archive_inventory(archive, source, pin) == before, 'Post-scan artifact drift')
        excluded = [{'path': path, 'sha256': before[path], 'suffix': Path(path).suffix.lower(),
                     'reason': 'not-selected-PHP-like-extension'} for path in sorted(set(before)-set(selected))]
        reports[variant] = {'zip_sha256': pin, 'verified_source_files': len(before),
                            'selected_extensions': sorted(SUFFIXES), 'excluded_files': excluded,
                            'summary': summarize(records), 'records': records}
    require(runtime_identity() == runtime, 'Runtime identity drift')
    require({p.name: sha(p) for p in Path('/audit/tools').iterdir() if p.is_file()} == harness, 'Harness drift')
    comparison = compare_reports(reports, contract)
    old = {r['path']: r for r in reports['exp9']['records']}
    new = {r['path']: r for r in reports['exp10']['records']}
    require(old.keys() == new.keys(), 'Selected pathset mismatch')
    changed = []
    for path in old:
        a, b = old[path], new[path]
        if a['sha256'] != b['sha256'] or (a['exit'], a['diagnostics']) != (b['exit'], b['diagnostics']):
            changed.append({'path': path, 'source_changed': a['sha256'] != b['sha256'],
                            'exp9_exit': a['exit'], 'exp10_exit': b['exit'],
                            'diagnostics_changed': a['diagnostics'] != b['diagnostics']})
    complete = all(r['summary']['incomplete'] == 0 for r in reports.values())
    report = {'schema': 1, 'scope': 'paired PHP8.3 -n syntax only, no application runtime acceptance',
              'runtime': runtime, 'harness': harness, 'flags': FLAGS, 'workers': 4,
              'variants': reports, 'delta': changed, 'collection_complete': complete,
              'input_contract': contract, 'comparison': comparison,
              'candidate_all_files_compile': complete and reports['exp10']['summary']['compiler_rejected'] == 0,
              'application_acceptance': False}
    print(json.dumps(report, indent=2))
    return 0 if complete and comparison['bounded_regression_pass'] else 2

if __name__ == '__main__':
    raise SystemExit(run())
