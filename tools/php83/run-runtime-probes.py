#!/usr/bin/env python3
"""Run fixed public-library probes, not full Kaltura acceptance."""
import argparse
import hashlib
import json
import os
import socket
from pathlib import Path
import subprocess

PROBES = [
    'zend_application', 'zend_registry', 'zend_config', 'propel_load', 'legacy_json',
    'zend_json_default', 'zend_json_fallback_encode', 'zend_json_fallback_decode',
    *('propel_' + name for name in ['DebugPDO', 'DebugPDOStatement',
      'PropelConfigurationIterator', 'Criteria', 'BasePeer', 'BaseObject', 'PropelPager']),
]
PHP_FLAGS = ['-d', 'allow_url_fopen=0', '-d', 'allow_url_include=0',
             '-d', 'opcache.enable_cli=0', '-d', 'date.timezone=UTC', '-d', 'log_errors=0']


EXPECTED = {
    'zend_application': 'testing', 'zend_registry': 'ok', 'zend_config': 'ok',
    'propel_load': '1.4.2\nPDO subclass loaded', 'legacy_json': '{"synthetic":true}',
    'zend_json_default': '{"synthetic":true}\n{"synthetic":true}',
    'zend_json_fallback_encode': '{"synthetic":true}',
    'zend_json_fallback_decode': '{"synthetic":true}',
    **{name: name[len('propel_'):] + ' loaded' for name in PROBES
       if name.startswith('propel_') and name != 'propel_load'},
}


def collect(root, php, probe):
    records = []
    for name in PROBES:
        try:
            run = subprocess.run([php, *PHP_FLAGS, str(probe), str(root), name],
                                 capture_output=True, text=True, timeout=30)
            record = {'probe': name, 'returncode': run.returncode,
                      'stdout': run.stdout.replace(str(root), '<public-app>'),
                      'stderr': run.stderr.replace(str(root), '<public-app>')}
        except subprocess.TimeoutExpired:
            record = {'probe': name, 'returncode': None, 'timeout': True}
        record['expected_output_matches'] = (record.get('stdout', '').split('\nAUDIT_INCLUDED=')[0].strip() == EXPECTED.get(name))
        records.append(record)
    return {
        'php': subprocess.check_output([php, '-v'], text=True, timeout=30).splitlines()[0],
        'modules': subprocess.check_output([php, '-m'], text=True, timeout=30).splitlines(),
        'ini_files': subprocess.check_output([php, '--ini'], text=True, timeout=30).splitlines(),
        'php_flags': PHP_FLAGS,
        'wrapper_sha256': hashlib.sha256(Path(__file__).with_name('run-sandboxed-probes.sh').read_bytes()).hexdigest(),
        'probe_sha256': hashlib.sha256(probe.read_bytes()).hexdigest(),
        'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': 'Fixed unpatched library probes; no full application reachability claim',
        'summary': {'total': len(records),
                    'passed_output': sum(r['returncode'] == 0 and r['expected_output_matches'] for r in records),
                    'failed_or_incomplete': sum(r['returncode'] != 0 or not r['expected_output_matches'] for r in records)},
        'results': records,
    }


def verify_sandbox(root):
    if os.geteuid() == 0 or not os.statvfs(root).f_flag & os.ST_RDONLY:
        raise RuntimeError('Expected unprivileged user and read-only payload')
    paths = {}
    for path in ['/root', '/home', '/opt/kaltura']:
        try:
            with os.scandir(path):
                pass
        except PermissionError:
            paths[path] = 'denied'
            continue
        except FileNotFoundError:
            paths[path] = 'absent'
            continue
        raise RuntimeError('Protected directory visible: ' + path)
    denied = []
    for family in [socket.AF_INET, socket.AF_INET6, socket.AF_UNIX]:
        try:
            sock = socket.socket(family, socket.SOCK_STREAM)
        except OSError as error:
            if error.errno not in (1, 13, 97):
                raise
            denied.append(family.name)
        else:
            sock.close()
            raise RuntimeError('Socket creation unexpectedly allowed')
    return {'uid': os.geteuid(), 'payload_read_only': True,
            'protected_directories': paths, 'socket_families_denied': denied}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-sandbox', action='store_true')
    parser.add_argument('root', type=Path)
    parser.add_argument('php')
    parser.add_argument('output', help='JSON file or - for stdout')
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    sandbox = verify_sandbox(root) if args.require_sandbox else None
    report = collect(root, args.php, Path(__file__).with_name('runtime-probes.php'))
    report['sandbox_checks'] = sandbox
    payload = json.dumps(report, indent=2) + '\n'
    if args.output == '-':
        print(payload, end='')
    else:
        Path(args.output).write_text(payload)
        print([(x['probe'], x['returncode']) for x in report['results']])


if __name__ == '__main__':
    main()
