"""Offline checks of the diagnostic collector using sanitized lab records."""
import contextlib
import copy
import io
import json
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'tools/php83/patch-tests/collect-pdo-edges.py'
EVIDENCE = ROOT / 'doc/php83/evidence/debug-pdo/v2-extended/edges.json'


class EdgeCollectorTests(unittest.TestCase):
    def setUp(self):
        self.records = copy.deepcopy(json.loads(EVIDENCE.read_text())['records'])

    def collect(self):
        results = [subprocess.CompletedProcess([], r['returncode'], r['stdout'], r['stderr'])
                   for r in self.records]
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'report.json'
            with patch('sys.argv', [str(SCRIPT), str(output)]), \
                    patch('subprocess.run', side_effect=results), \
                    contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as stop:
                runpy.run_path(str(SCRIPT), run_name='__main__')
            return stop.exception.code, json.loads(output.read_text())

    def test_recorded_controls_pass(self):
        code, report = self.collect()
        self.assertEqual(code, 0)
        self.assertEqual(report['failures'], [])

    def test_execution_failure_rejected(self):
        self.records[-1]['returncode'] = 255
        self.assertTrue(self.collect()[0])

    def test_unexpected_original_failure_rejected(self):
        self.records[2]['stderr'] = 'unrelated failure'
        self.assertTrue(self.collect()[0])

    def test_same_error_on_both_sides_is_not_positive_success(self):
        rows = json.loads(self.records[-1]['stdout'])
        rows[1]['2'] = {'PDO': ['throw', 'RuntimeException'], 'DebugPDO': ['throw', 'RuntimeException']}
        rows[1]['matches_native'] = True
        self.records[-1]['stdout'] = json.dumps(rows)
        code, report = self.collect()
        self.assertTrue(code)
        self.assertTrue(any('positive fixture' in f for f in report['failures']))

    def test_missing_case_rejected(self):
        rows = json.loads(self.records[-1]['stdout'])
        self.records[-1]['stdout'] = json.dumps(rows[:-1])
        self.assertTrue(self.collect()[0])

    def test_native_difference_rejected(self):
        rows = json.loads(self.records[-1]['stdout'])
        rows[1]['matches_native'] = False
        self.records[-1]['stdout'] = json.dumps(rows)
        self.assertTrue(self.collect()[0])
