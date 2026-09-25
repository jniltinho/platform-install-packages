"""Fault injection only: these tests never SSH or start a database."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('exp3_api', Path(__file__).parent / 'exp3-api/collect.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class Exp3CleanupTests(unittest.TestCase):
    def check_failure(self, startup):
        calls = []
        def remote(command, timeout=200):
            calls.append(command)
            if 'sha256sum' in command:
                names = command.split('sha256sum ', 1)[1].split()
                lines = []
                for name in names:
                    directory, leaf = name.split('/')
                    path = (collector.HERE if directory == 'api' else collector.OLD) / leaf
                    lines.append(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + name)
                return subprocess.CompletedProcess(command, 0, '\n'.join(lines), '')
            if 'verify-source.py' in command:
                return subprocess.CompletedProcess(command, 0, '{}', '')
            if 'start-db.sh' in command:
                if isinstance(startup, Exception):
                    raise startup
                return subprocess.CompletedProcess(command, 0, startup, '')
            if 'systemctl stop' in command:
                return subprocess.CompletedProcess(command, 3, 'inactive\n', '')
            self.fail('Unexpected remote call: ' + command)
        with tempfile.TemporaryDirectory() as d, patch.object(collector, 'remote', side_effect=remote), patch('sys.argv', ['collect.py', d + '/report.json']):
            with self.assertRaises((ValueError, RuntimeError, subprocess.TimeoutExpired)):
                collector.main()
            self.assertFalse(Path(d, 'report.json').exists())
        start = next(c for c in calls if c.startswith('bash ') and 'start-db.sh' in c)
        token = start.rsplit(' ', 1)[1]
        self.assertRegex(token, r'^[a-f0-9]{32}$')
        self.assertIn('systemctl stop php83-exp3-api-' + token, calls[-1])

    def test_malformed_startup_stops_known_unit(self):
        self.check_failure('not json')

    def test_untrusted_identity_cannot_choose_cleanup_target(self):
        self.check_failure(json.dumps({'datadir':'/var/lib/mysql', 'unit':'mysql'}))

    def test_startup_timeout_stops_known_unit(self):
        self.check_failure(subprocess.TimeoutExpired('startup', 120))
