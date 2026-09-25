import copy
import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compare

class ComparisonTests(unittest.TestCase):
    def report(self):
        return {'variants': {'exp9': {'records': [{'duration_ns': 12, 'exit': 255, 'diagnostics': 'failure', 'sha256': 'a'}]},
                             'exp10': {'records': [{'duration_ns': 15, 'exit': 0, 'diagnostics': '', 'sha256': 'b'}]}},
                'duration_ns': 'top-level value must not be ignored', 'runtime': {'sha256': 'compiler-pin'}}
    def test_ignores_only_per_record_duration(self):
        a = self.report(); b = copy.deepcopy(a)
        b['variants']['exp9']['records'][0]['duration_ns'] += 99
        self.assertEqual(compare.normalized(a), compare.normalized(b))
        self.assertIn('duration_ns', a['variants']['exp9']['records'][0])
    def test_diagnostics_not_ignored(self):
        a = self.report(); b = copy.deepcopy(a)
        b['variants']['exp10']['records'][0]['diagnostics'] = 'Warning'
        self.assertNotEqual(compare.normalized(a), compare.normalized(b))
    def test_runtime_not_ignored(self):
        a = self.report(); b = copy.deepcopy(a); b['runtime']['sha256'] = 'other'
        self.assertNotEqual(compare.normalized(a), compare.normalized(b))
    def test_top_level_duration_not_ignored(self):
        a = self.report(); b = copy.deepcopy(a); b['duration_ns'] = 'different'
        self.assertNotEqual(compare.normalized(a), compare.normalized(b))
    def test_missing_duration_rejected(self):
        a = self.report(); del a['variants']['exp9']['records'][0]['duration_ns']
        with self.assertRaises(KeyError): compare.normalized(a)
    def test_invalid_duration_rejected(self):
        for value in (None, True, -1, '12'):
            a = self.report(); a['variants']['exp9']['records'][0]['duration_ns'] = value
            with self.assertRaises(RuntimeError): compare.normalized(a)
    def test_frozen_files_exclude_new_host_comparator(self):
        self.assertEqual(len(compare.FROZEN_FILES), 6)
        self.assertNotIn('compare.py', compare.FROZEN_FILES)
        self.assertNotIn('test_compare.py', compare.FROZEN_FILES)

if __name__ == '__main__': unittest.main()
