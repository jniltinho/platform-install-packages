#!/usr/bin/env python3
"""Owned SQL/bootstrap boolean probe. Output is strictly whitelisted, no raw logs."""
import argparse
import hashlib
import importlib.util
import json
import re
import uuid
import zipfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('exp9_api', HERE.parent/'exp9-api/collect.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
ROOT = '/home/vagrant/php-pdo-bootstrap'
ARTIFACTS = HERE.parents[2].parent/'platform-install-packages-php83-artifacts'
CLASSES = {'KalturaPDO', 'PropelPDO', 'KalturaStatement', 'KalturaLog', 'KalturaMonitorClient', 'kApiCache', 'kQueryCache'}

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def expected_rows(variant):
    yes = True if variant == 'exp9' else None
    no = False if variant == 'exp9' else None
    return [['connection', 'KalturaPDO'], ['native-success', True],
            ['set-supported', yes], ['set-unsupported', no],
            ['cache-set-on', yes], ['cache-identity-on', True],
            ['cache-set-off', yes], ['cache-identity-off', False],
            ['statement', 'KalturaStatement'], ['comment-prefix', True],
            ['bind-int', True], ['execute-bound', yes], ['bound-data', 17],
            ['execute-array', yes], ['array-data', 23],
            ['native-false', False], ['execute-false', no],
            ['native-exception', ['PDOException', '42S02']],
            ['execute-exception', ['PDOException', '42S02']],
            ['dryrun-insert', yes], ['dryrun-no-write', 0],
            ['dryrun-select', yes], ['dryrun-select-data', 19]]

def validate(body, variant, archive):
    require(set(body) == {'variant', 'php', 'rows', 'sources'}, 'Unexpected result fields')
    require(body['variant'] == variant and re.fullmatch(r'8\.3\.\d+(?:[^\s]*)?', body['php']), 'Runtime/variant mismatch')
    # JSON text equality intentionally distinguishes bool from int (Python == does not).
    require(json.dumps(body['rows']) == json.dumps(expected_rows(variant)), 'Unexpected case output')
    require(set(body['sources']) == CLASSES, 'Dependency class inventory mismatch')
    with zipfile.ZipFile(archive) as z:
        for source in body['sources'].values():
            require(set(source) == {'path', 'sha256'}, 'Unexpected source fields')
            require(re.fullmatch(r'[A-Za-z0-9_./-]+\.php', source['path']) and '..' not in source['path'].split('/'), 'Unsafe source path')
            data = z.read('server-Rigel-18.20.0/'+source['path'])
            require(hashlib.sha256(data).hexdigest() == source['sha256'], 'Loaded dependency drift')
    return body

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    require(not args.output.exists(), 'Evidence exists')
    selected = {ROOT+'/'+n: HERE/n for n in ('probe.php', 'run.sh')}
    selected.update({api.ROOT+'/tests/'+n: api.OLD/n for n in ('api-bootstrap.php', 'api-permission-schema.sql')})
    for variant in ('exp8', 'exp9'):
        selected['/home/vagrant/php-'+variant+'-regression/api/verify-source.py'] = HERE.parent/(variant+'-api')/'verify-source.py'
    selected[api.ROOT+'/api/start-db.sh'] = api.HERE/'start-db.sh'
    hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in selected.items()}
    result = api.remote('sha256sum '+' '.join(hashes))
    require(result.returncode == 0 and {line.split()[1]: line.split()[0] for line in result.stdout.splitlines()} == hashes, 'Fixture drift')
    def verify():
        found = {}
        for variant in ('exp8', 'exp9'):
            result = api.remote('python3 /home/vagrant/php-'+variant+'-regression/api/verify-source.py')
            require(result.returncode == 0, 'Artifact verification failed')
            found[variant] = json.loads(result.stdout)
        return found
    artifacts = verify()
    for variant, artifact in artifacts.items():
        archive = ARTIFACTS/variant/('Rigel-18.20.0-php83-experimental.'+variant+'.zip')
        require(hashlib.sha256(archive.read_bytes()).hexdigest() == artifact['zip_sha256'], 'Local archive identity drift')
    token = uuid.uuid4().hex
    db = {'datadir': '/tmp/kaltura-pdo-mysql.'+token, 'unit': 'php83-exp9-api-'+token}
    rows = []
    try:
        result = api.remote('bash '+api.ROOT+'/api/start-db.sh '+token, 120)
        require(result.returncode == 0 and json.loads(result.stdout) == db, 'Owned DB startup failed')
        for variant in ('exp8', 'exp9'):
            command = 'bash '+ROOT+'/run.sh '+variant+' '+db['datadir']
            result = api.remote(command, 90)
            body = None
            if result.returncode == 0:
                body = validate(json.loads(result.stdout), variant, ARTIFACTS/variant/('Rigel-18.20.0-php83-experimental.'+variant+'.zip'))
            rows.append({'variant': variant, 'command': command, 'exit': result.returncode, 'result': body,
                         'stdout_sha256': hashlib.sha256(result.stdout.encode()).hexdigest(),
                         'stderr_sha256': hashlib.sha256(result.stderr.encode()).hexdigest(),
                         'diagnostics': api.old.diagnostics(result.stderr)})
    finally:
        stop = api.remote('sudo systemctl stop '+db['unit']+'; systemctl is-active '+db['unit'], 30)
        cleanup = {'unit': db['unit'], 'state': stop.stdout.strip(), 'stopped': stop.stdout.strip() in ('inactive', 'failed', 'unknown')}
    require(verify() == artifacts, 'Artifact changed during probe')
    passed = len(rows) == 2 and all(row['exit'] == 0 for row in rows) and cleanup['stopped']
    report = {'schema': 1, 'scope': 'real KalturaPDO/bootstrap synthetic SQL; not full application acceptance',
              'artifacts': artifacts, 'harness': hashes, 'collector_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'imported_helper_sha256': {str(p.relative_to(HERE.parents[2])): hashlib.sha256(p.read_bytes()).hexdigest() for p in (api.HERE/'collect.py', api.OLD/'collect-api-apache.py', api.OLD/'collect-api-mysql.py')},
              'db': db, 'cleanup': cleanup, 'rows': rows, 'functional_checks_passed': passed, 'application_acceptance': False}
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'functional_checks_passed': passed, 'cleanup': cleanup}))
    return 0 if passed else 1

if __name__ == '__main__':
    raise SystemExit(main())
