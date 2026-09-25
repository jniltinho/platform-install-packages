import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('api_auth_dispatch', Path(__file__).parent / 'patch-tests' / 'collect-api-auth-dispatch.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class AuthDispatchCollectorTests(unittest.TestCase):
    def compare(self, baseline_code=0, candidate_code=0, candidate_output='contract'):
        return collector.mysql.comparisons([
            dict(runtime='74', tree='original', returncode=baseline_code, stdout='contract'),
            dict(runtime='83', tree='candidate', returncode=candidate_code, stdout=candidate_output),
        ])[0]['matches_baseline']

    def test_identical_success(self):
        self.assertTrue(self.compare())

    def test_nonzero_reference_or_candidate_never_passes(self):
        self.assertFalse(self.compare(baseline_code=255))
        self.assertFalse(self.compare(candidate_code=255))

    def test_changed_error_contract_never_passes(self):
        self.assertFalse(self.compare(candidate_output='different denial code'))

    def test_no_token_arguments_in_diagnostics(self):
        self.assertEqual(collector.diagnostics("#1 dispatch('token')\nSQL token\n"), [])
        self.assertEqual(collector.diagnostics('Warning: token in /audit/app/source.php on line 12'),
                         [dict(severity='Warning', path='/audit/app/source.php', line=12, count=1)])
