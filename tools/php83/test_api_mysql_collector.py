import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('api_mysql_collector', Path(__file__).parent / 'patch-tests' / 'collect-api-mysql.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class ApiMySQLCollectorTests(unittest.TestCase):
    def rows(self, baseline=0, candidate=0, output='ok'):
        return [dict(runtime='74', tree='original', returncode=baseline, stdout='ok'),
                dict(runtime='83', tree='candidate', returncode=candidate, stdout=output)]

    def test_matching_success(self):
        self.assertTrue(collector.comparisons(self.rows())[0]['matches_baseline'])

    def test_baseline_or_candidate_failure(self):
        for codes in [(1, 0), (0, 1), (1, 1)]:
            self.assertFalse(collector.comparisons(self.rows(*codes))[0]['matches_baseline'])

    def test_changed_contract(self):
        self.assertFalse(collector.comparisons(self.rows(output='different'))[0]['matches_baseline'])
