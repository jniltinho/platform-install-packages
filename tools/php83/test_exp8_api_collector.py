"""Fault injection only: these tests never SSH or start a database."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('exp8_api', Path(__file__).parent / 'exp8-api/collect.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class Exp8CleanupTests(unittest.TestCase):
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
        self.assertIn('systemctl stop php83-exp8-api-' + token, calls[-1])

    def test_malformed_startup_stops_known_unit(self):
        self.check_failure('not json')

    def test_untrusted_identity_cannot_choose_cleanup_target(self):
        self.check_failure(json.dumps({'datadir':'/var/lib/mysql', 'unit':'mysql'}))

    def test_startup_timeout_stops_known_unit(self):
        self.check_failure(subprocess.TimeoutExpired('startup', 120))


class Exp8MatrixTests(unittest.TestCase):
    def test_target_runtime_and_baseline_are_explicit(self):
        self.assertEqual(collector.api_cases(), [
            ('74','original'),('83','original'),('83','exp7'),('83','exp8')])
        self.assertNotIn(('74','exp8'), collector.api_cases())
        self.assertEqual(len(set(collector.api_cases())), 4)


class Exp8AcceptanceTests(unittest.TestCase):
    """Synthetic collector control tests; never execute SSH, PHP or SQL."""
    def run_matrix(self, change=None, cleanup='inactive'):
        def remote(command, timeout=200):
            rc, stdout, stderr = 0, '', ''
            if 'sha256sum' in command:
                names = command.split('sha256sum ', 1)[1].split()
                lines = []
                for name in names:
                    directory, leaf = name.split('/')
                    path = (collector.HERE if directory == 'api' else collector.OLD) / leaf
                    lines.append(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + name)
                stdout = '\n'.join(lines)
            elif 'verify-source.py' in command:
                stdout = '{}'
            elif 'start-db.sh' in command:
                token = command.rsplit(' ', 1)[1]
                stdout = json.dumps({'datadir':'/tmp/kaltura-pdo-mysql.' + token,
                                     'unit':'php83-exp8-api-' + token})
            elif 'run-apache.sh' in command:
                runtime, tree = command.split()[-3:-1]
                if (runtime, tree) == ('83', 'original'):
                    rc, stderr = 1, 'Declaration of KalturaPDO::query() must be compatible'
                else:
                    stdout = collector.EXPECTED_STDOUT
                if change:
                    rc, stdout, stderr = change(runtime, tree, rc, stdout, stderr)
            elif 'systemctl stop' in command:
                stdout = cleanup + '\n'
            else:
                self.fail('Unexpected remote command: ' + command)
            return subprocess.CompletedProcess(command, rc, stdout, stderr)
        with tempfile.TemporaryDirectory() as d, patch.object(collector, 'remote', side_effect=remote), patch('sys.argv', ['collect.py', d + '/report.json']):
            exit_code = collector.main()
            raw = Path(d, 'report.json').read_text()
            return exit_code, json.loads(raw), raw

    def test_complete_matrix_success(self):
        code, report, _ = self.run_matrix()
        self.assertEqual(code, 0)
        self.assertTrue(report['functional_checks_passed'])
        self.assertEqual(len(report['records']), 4)
        self.assertEqual(len(report['comparisons']), 2)
        self.assertFalse(report['application_acceptance'])

    def test_baseline_failure_is_not_parity_success(self):
        code, report, _ = self.run_matrix(lambda r,t,c,o,e: (1,o,e) if (r,t)==('74','original') else (c,o,e))
        self.assertEqual(code, 1)
        self.assertFalse(report['functional_checks_passed'])

    def test_candidate_failure_is_not_parity_success(self):
        code, report, _ = self.run_matrix(lambda r,t,c,o,e: (1,o,e) if t=='exp8' else (c,o,e))
        self.assertEqual(code, 1)
        self.assertFalse(report['functional_checks_passed'])

    def test_unrelated_original_failure_is_not_signature_control(self):
        code, report, _ = self.run_matrix(lambda r,t,c,o,e: (c,o,'different failure') if (r,t)==('83','original') else (c,o,e))
        self.assertEqual(code, 1)
        self.assertFalse(report['original83_signature_control'])

    def test_unexpected_stdout_is_rejected_and_not_persisted(self):
        marker = 'synthetic-unexpected-output-never-a-real-secret'
        code, report, raw = self.run_matrix(lambda r,t,c,o,e: (c,marker,e) if t=='exp8' else (c,o,e))
        self.assertEqual(code, 1)
        self.assertNotIn(marker, raw)
        row = next(r for r in report['records'] if r['tree']=='exp8')
        self.assertEqual(row['stdout'], '')
        self.assertFalse(row['stdout_whitelisted'])
        self.assertEqual(row['stdout_sha256'], hashlib.sha256(marker.encode()).hexdigest())

    def test_cleanup_failure_prevents_success(self):
        code, report, _ = self.run_matrix(cleanup='active')
        self.assertEqual(code, 1)
        self.assertFalse(report['cleanup']['stopped'])
        self.assertFalse(report['functional_checks_passed'])
