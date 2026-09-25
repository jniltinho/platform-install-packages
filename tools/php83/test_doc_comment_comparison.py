import copy
import unittest
from compare_doc_comment import compare, PATHS


class DocCommentComparisonTests(unittest.TestCase):
    def setUp(self):
        self.before = dict(harness_hashes={'fixture': 'same'}, records=[dict(runtime='83', tree='candidate', returncode=0, stdout='same', diagnostics=[dict(path=sorted(PATHS)[0], count=4)])])
        self.after = copy.deepcopy(self.before)
        self.after['records'][0]['diagnostics'] = []

    def test_reduction_passes(self):
        self.assertTrue(compare(self.before, self.after)['passed'])

    def test_no_before_failure_is_not_a_repair_proof(self):
        self.before['records'][0]['diagnostics'] = []
        self.assertFalse(compare(self.before, self.after)['passed'])

    def test_remaining_warning_fails(self):
        self.assertFalse(compare(self.before, self.before)['passed'])

    def test_harness_drift_fails(self):
        self.after['harness_hashes']['fixture'] = 'changed'
        self.assertFalse(compare(self.before, self.after)['passed'])

    def test_failure_or_changed_contract_fails(self):
        for key, value in [('stdout', 'different'), ('returncode', 1)]:
            changed = copy.deepcopy(self.after)
            changed['records'][0][key] = value
            self.assertFalse(compare(self.before, changed)['passed'])
