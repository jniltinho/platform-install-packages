"""Synthetic consumer guards only: no PHP, archives, stages, /tmp, or SSH reads."""
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
import report_contract as contract

spec = importlib.util.spec_from_file_location('collector', Path(__file__).with_name('collect-r2.py'))
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
PIN = 'a' * 64


def fixture():
    manifest = {'files': {'probe.php': 'b' * 64, 'cache-probe.php': 'c' * 64}}
    rows = []
    for variant, kind, operation, writer in contract.expected_keys74():
        target = collector.TARGETS[kind]
        manifest['files']['original/' + target] = 'd' * 64
        body = {'kind': kind, 'operation': operation, 'runtime': '7.4.synthetic',
                'probe_sha256': manifest['files']['cache-probe.php' if kind == 'cache' else 'probe.php'],
                'loaded': {target: 'd' * 64}, 'diagnostics': [], 'result': {}}
        if operation == 'roundtrip':
            raw = ('C:SYNTHETIC_NOT_NATIVE:' + kind).encode()
            body['result']['wire'] = {'base64': base64.b64encode(raw).decode(),
                                      'sha256': hashlib.sha256(raw).hexdigest(), 'format': 'C'}
        rows.append({'variant': variant, 'kind': kind, 'operation': operation, 'writer': writer,
                     'exit': 0, 'stdout': json.dumps(body), 'stderr': ''})
    report = {'mode': '74', 'status': 'OBSERVED_NOT_ACCEPTED', 'application_acceptance': False,
              'errors': [], 'stage_manifest_sha256': PIN, 'records': rows}
    return report, manifest


class ConsumerGuards(unittest.TestCase):
    def setUp(self):
        self.report, self.manifest = fixture()

    def consume(self):
        return collector.prior74_wires(self.report, PIN, self.manifest)

    def reject(self):
        with self.assertRaises((ValueError, KeyError, TypeError)):
            self.consume()

    def mutate_body(self, index, field, value):
        body = json.loads(self.report['records'][index]['stdout'])
        body[field] = value
        self.report['records'][index]['stdout'] = json.dumps(body)

    def test_complete_synthetic_report(self):
        self.assertEqual(set(self.consume()), set(collector.KINDS))
        keys = contract.expected_keys74()
        self.assertEqual(len(keys), 38)
        self.assertEqual(len(set(keys)), 38)

    def test_duplicate_preserving_count(self):
        self.report['records'][-1] = copy.deepcopy(self.report['records'][-2]); self.reject()

    def test_reordered_preserving_count(self):
        self.report['records'][0], self.report['records'][1] = self.report['records'][1], self.report['records'][0]; self.reject()

    def test_missing_record(self):
        self.report['records'].pop(); self.reject()

    def test_extra_record(self):
        self.report['records'].append(copy.deepcopy(self.report['records'][0])); self.reject()

    def test_wrong_variant(self):
        self.report['records'][-1]['variant'] = 'candidate'; self.reject()

    def test_wrong_writer(self):
        self.report['records'][18]['writer'] = 'original74'; self.reject()

    def test_wrong_key_type(self):
        self.report['records'][0]['kind'] = False; self.reject()

    def test_wrong_pin(self):
        self.report['stage_manifest_sha256'] = 'f' * 64; self.reject()

    def test_errors_retained(self):
        self.report['errors'] = [{'error': 'some failed row'}]; self.reject()

    def test_acceptance_not_boolean_false(self):
        self.report['application_acceptance'] = 0; self.reject()

    def test_wrong_status(self):
        self.report['status'] = 'PASS'; self.reject()

    def test_wrong_mode(self):
        self.report['mode'] = '83'; self.reject()

    def test_bool_exit_nonproducer(self):
        self.report['records'][-1]['exit'] = False; self.reject()

    def test_float_exit_nonproducer(self):
        self.report['records'][-1]['exit'] = 0.0; self.reject()

    def test_failure_nonproducer(self):
        self.report['records'][-1]['exit'] = 255; self.reject()

    def test_missing_stderr(self):
        del self.report['records'][-1]['stderr']; self.reject()

    def test_stderr_wrong_type(self):
        self.report['records'][-1]['stderr'] = []; self.reject()

    def test_nonproducer_body_runtime(self):
        self.mutate_body(-1, 'runtime', '8.3.synthetic'); self.reject()

    def test_nonproducer_loaded_hash(self):
        self.mutate_body(-1, 'loaded', {collector.TARGETS['cache']: 'e' * 64}); self.reject()

    def test_nonproducer_probe_hash(self):
        self.mutate_body(-1, 'probe_sha256', 'e' * 64); self.reject()

    def test_nonproducer_diagnostics_missing(self):
        self.mutate_body(-1, 'diagnostics', None); self.reject()

    def test_nonproducer_bad_json(self):
        self.report['records'][-1]['stdout'] = 'not json'; self.reject()

    def test_producer_wire_hash(self):
        body = json.loads(self.report['records'][0]['stdout'])
        body['result']['wire']['sha256'] = 'f' * 64
        self.report['records'][0]['stdout'] = json.dumps(body); self.reject()


if __name__ == '__main__':
    unittest.main()
