"""Adversarial replay of retained native observations; no PHP/VM commands."""
import copy,hashlib,importlib.util,json,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('validation_observed',HERE/'validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
REPORT=HERE.parents[2]/'doc/php83/evidence/criteria-selection/composition-primary.json'
class ObservedContractTests(unittest.TestCase):
    def setUp(self):self.report=json.loads(REPORT.read_text())
    def check(self):return v.validate(self.report['records'],self.report['identities'])
    def mutate_body(self,idx,fn):
        r=self.report['records'][idx];fn(r['body']);r['stdout']=json.dumps(r['body'])
    def test_actual_four_process_report(self):self.assertEqual(self.check()['hierarchy_events_before'],24)
    def test_bool_exit_rejected(self):
        self.report['records'][0]['exit']=False
        with self.assertRaisesRegex(ValueError,'Exit'):self.check()
    def test_extra_native_stderr(self):
        self.report['records'][0]['stderr']+='unexpected\n'
        with self.assertRaisesRegex(ValueError,'stderr'):self.check()
    def test_stdout_body_binding(self):
        self.report['records'][0]['stdout']='{}'
        with self.assertRaisesRegex(ValueError,'binding'):self.check()
    def test_source_drift(self):
        self.mutate_body(0,lambda b:b['source_sha256'].update(criteria='bad'))
        with self.assertRaisesRegex(ValueError,'identity'):self.check()
    def test_missing_case(self):
        self.mutate_body(0,lambda b:b['rows'].pop('clear'))
        with self.assertRaisesRegex(ValueError,'inventory'):self.check()
    def test_changed_candidate_state(self):
        self.mutate_body(1,lambda b:b['rows'].update(disabled='different'))
        with self.assertRaisesRegex(ValueError,'parity'):self.check()
    def test_missing_negative_class_control(self):
        self.mutate_body(1,lambda b:b.update(events=[]))
        with self.assertRaisesRegex(ValueError,'negative'):self.check()
    def test_lost_return_type(self):
        self.mutate_body(2,lambda b:b['contracts'].update({'CriterionIterator::key':None}))
        with self.assertRaisesRegex(ValueError,'contract'):self.check()
    def test_missing_invalid_control(self):
        self.mutate_body(3,lambda b:b['invalid_controls'].pop())
        with self.assertRaisesRegex(ValueError,'inventory'):self.check()
if __name__=='__main__':unittest.main()
