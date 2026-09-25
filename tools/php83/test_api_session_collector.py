import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('api_session', Path(__file__).parent / 'patch-tests' / 'collect-api-session.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class SessionDiagnosticsTests(unittest.TestCase):
    def test_logs_do_not_retain_tokens(self):
        log = "Exception: secret-token\n#4 ks::fromSecureString('secret-token')\n"
        log += "Warning: sensitive-token in /audit/app/file.php on line 42\n" * 2
        self.assertEqual(collector.diagnostics(log), [dict(severity='Warning', path='/audit/app/file.php', line=42, count=2)])

    def test_empty_and_unrecognized_logs_are_not_invented_diagnostics(self):
        self.assertEqual(collector.diagnostics('SQL token or ordinary log'), [])

    def test_php_prefix(self):
        self.assertEqual(collector.diagnostics('PHP Deprecated: message in /audit/app/test.php on line 1')[0]['severity'], 'Deprecated')
