import copy
import json
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('syntax_scan', Path(__file__).with_name('scan.py'))
scan = importlib.util.module_from_spec(spec); spec.loader.exec_module(scan)

class ScanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.source = self.root/'source'; self.source.mkdir()
        self.archive = self.root/'input.zip'
        self.data = b'<?php echo 1;'
        (self.source/'test.php').write_bytes(self.data)
        self.write_zip([('server-Rigel-18.20.0/test.php', self.data)])
    def write_zip(self, entries):
        with zipfile.ZipFile(self.archive, 'w') as z:
            for name, data in entries: z.writestr(name, data)
        self.pin = scan.sha(self.archive)
    def verify(self): return scan.archive_inventory(self.archive, self.source, self.pin)
    def test_valid(self):
        self.assertEqual(self.verify(), {'test.php': hashlib.sha256(self.data).hexdigest()})
    def test_wrong_hash(self):
        self.pin = '0'*64
        with self.assertRaises(RuntimeError): self.verify()
    def test_source_drift(self):
        (self.source/'test.php').write_bytes(b'changed')
        with self.assertRaises(RuntimeError): self.verify()
    def test_extra_source(self):
        (self.source/'extra.php').write_text('extra')
        with self.assertRaises(RuntimeError): self.verify()
    def test_traversal(self):
        self.write_zip([('server-Rigel-18.20.0/../escape.php', b'bad')])
        with self.assertRaises(RuntimeError): self.verify()
    def test_wrong_root(self):
        self.write_zip([('other/test.php', self.data)])
        with self.assertRaises(RuntimeError): self.verify()
    def test_symlink(self):
        (self.source/'link.php').symlink_to('test.php')
        with self.assertRaises(RuntimeError): self.verify()
    def test_duplicate_entry(self):
        with self.assertWarns(UserWarning):
            self.write_zip([('server-Rigel-18.20.0/test.php', self.data)]*2)
        with self.assertRaises(RuntimeError): self.verify()
    def test_diagnostics_are_not_rejections(self):
        summary = scan.summarize([{'exit': 0, 'diagnostics': 'Deprecated'}, {'exit': 255, 'diagnostics': 'Parse error'}, {'exit': 124, 'diagnostics': 'Timeout'}])
        self.assertEqual(summary, {'files_scanned': 3, 'compiler_rejected': 1, 'compiler_accepted': 1, 'incomplete': 1, 'diagnostic_files': 3, 'accepted_with_diagnostics': 1})
    def test_explicit_syntax_only_flags(self):
        self.assertEqual(scan.FLAGS, ['-n', '-d', 'short_open_tag=1', '-d', 'error_reporting=32767', '-d', 'display_errors=stderr', '-d', 'log_errors=0', '-l'])
    def test_extension_selection(self):
        self.assertEqual(scan.SUFFIXES, {'.php', '.phtml', '.inc', '.php5'})

class ContractAndComparisonTests(unittest.TestCase):
    def setUp(self):
        self.contract = {'schema': 1, 'pins': {'exp10': scan.EXP10_PIN, 'exp11': 'e' * 64},
                         'targets': [{'path': f'target-{i}.php', 'exp10_sha256': 'a' * 64,
                                      'exp11_sha256': 'b' * 64} for i in range(4)]}
        old = [{'path': f'target-{i}.php', 'sha256': 'a' * 64, 'exit': 255,
                'diagnostics': 'curly offsets rejected'} for i in range(4)]
        old += [{'path': f'other-{i}.php', 'sha256': 'c' * 64,
                 'exit': 255 if i < 7 else 0,
                 'diagnostics': 'remaining syntax error' if i < 7 else ''}
                for i in range(11784 - 4)]
        new = copy.deepcopy(old)
        for record in new[:4]:
            record.update(sha256='b' * 64, exit=0, diagnostics='')
        self.reports = {'exp10': {'records': old}, 'exp11': {'records': new}}
        for name,v in self.reports.items():
            for row in v['records']:row.update(command=[scan.PHP]+scan.FLAGS+['/audit/'+name+'/'+row['path']],duration_ns=1)
    def load(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'contract.json'
            path.write_text(json.dumps(self.contract))
            return scan.load_contract(path)
    def compare(self):
        return scan.compare_reports(self.reports, self.contract)
    def test_noninteger_status_rejected(self):
        for value in (False,0.0,255.0):
            self.reports['exp11']['records'][0]['exit']=value
            with self.assertRaisesRegex(RuntimeError,'typed'):self.compare()
    def test_wrong_command_rejected(self):
        self.reports['exp11']['records'][0]['command'].remove('-l')
        with self.assertRaisesRegex(RuntimeError,'command'):self.compare()
    def test_extra_row_field_rejected(self):
        self.reports['exp11']['records'][0]['ignored']='surprise'
        with self.assertRaisesRegex(RuntimeError,'inventory'):self.compare()
    def test_pending_pin_fail_closed(self):
        self.contract['pins']['exp11'] = None
        with self.assertRaisesRegex(RuntimeError, 'pending'): self.load()
    def test_valid_contract(self):
        self.assertEqual(self.load(), self.contract)
    def test_wrong_baseline_pin(self):
        self.contract['pins']['exp10'] = 'f' * 64
        with self.assertRaises(RuntimeError): self.load()
    def test_target_count(self):
        self.contract['targets'].pop()
        with self.assertRaises(RuntimeError): self.load()
    def test_duplicate_target(self):
        self.contract['targets'][1] = self.contract['targets'][0]
        with self.assertRaises(RuntimeError): self.load()
    def test_unsafe_target(self):
        self.contract['targets'][0]['path'] = '../escape.php'
        with self.assertRaises(RuntimeError): self.load()
    def test_target_invalid_hash(self):
        self.contract['targets'][0]['exp11_sha256'] = 'unknown'
        with self.assertRaises(RuntimeError): self.load()
    def test_expected_bounded_result_still_has_7_rejections(self):
        result = self.compare()
        self.assertTrue(result['bounded_regression_pass'])
        self.assertEqual(len(result['remaining_rejected_paths']), 7)
        self.assertEqual(result['target_rejections_after'], [])
    def test_target_rejection_is_failure(self):
        self.reports['exp11']['records'][0]['exit'] = 255
        self.assertFalse(self.compare()['bounded_regression_pass'])
    def test_target_timeout_is_incomplete_failure(self):
        self.reports['exp11']['records'][0]['exit'] = 124
        self.assertFalse(self.compare()['bounded_regression_pass'])
    def test_unchanged_diagnostic_drift_fails(self):
        self.reports['exp11']['records'][4]['diagnostics'] += ' changed'
        result = self.compare()
        self.assertFalse(result['bounded_regression_pass'])
        self.assertEqual(result['unchanged_outcome_differences'], ['other-0.php'])
    def test_unchanged_acceptance_change_is_not_silent_success(self):
        self.reports['exp11']['records'][4].update(exit=0, diagnostics='')
        self.assertFalse(self.compare()['bounded_regression_pass'])
    def test_unexpected_source_change(self):
        self.reports['exp11']['records'][4]['sha256'] = 'd' * 64
        with self.assertRaisesRegex(RuntimeError, 'Unexpected changed'): self.compare()
    def test_target_hash_drift(self):
        self.reports['exp11']['records'][0]['sha256'] = 'd' * 64
        with self.assertRaisesRegex(RuntimeError, 'Target identity'): self.compare()
    def test_missing_path(self):
        self.reports['exp11']['records'].pop()
        with self.assertRaisesRegex(RuntimeError, 'pathset'): self.compare()
    def test_duplicate_record(self):
        self.reports['exp11']['records'].append(self.reports['exp11']['records'][0])
        with self.assertRaisesRegex(RuntimeError, 'Duplicate'): self.compare()
    def test_partial_both_scans_not_complete(self):
        for variant in self.reports.values(): variant['records'].pop()
        self.assertFalse(self.compare()['bounded_regression_pass'])

if __name__ == '__main__': unittest.main()

