import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    'compare_probes', Path(__file__).with_name('compare-runtime-probes.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CompareTests(unittest.TestCase):
    def setUp(self):
        self.baseline = {'probe_sha256': 'same', 'runner_sha256': 'same', 'wrapper_sha256': 'same', 'php_flags': [],
                         'results': [{'probe': 'one', 'returncode': 0, 'expected_output_matches': True}]}
        self.candidate = copy.deepcopy(self.baseline)

    def test_new_failure(self):
        self.candidate['results'][0]['returncode'] = 255
        self.assertEqual(module.compare(self.baseline, self.candidate)[0]['classification'],
                         'new failing library probe')

    def test_timeout_not_regression_claim(self):
        self.candidate['results'][0].update(returncode=None, timeout=True)
        self.assertIn('incomplete', module.compare(self.baseline, self.candidate)[0]['classification'])

    def test_changed_harness_rejected(self):
        self.candidate['probe_sha256'] = 'different'
        with self.assertRaises(ValueError):
            module.compare(self.baseline, self.candidate)

    def test_missing_probe_rejected(self):
        self.candidate['results'] = []
        with self.assertRaises(ValueError):
            module.compare(self.baseline, self.candidate)

    def test_baseline_failure_not_new(self):
        self.baseline['results'][0]['returncode'] = 255
        self.assertIn('baseline failure', module.compare(self.baseline, self.candidate)[0]['classification'])
