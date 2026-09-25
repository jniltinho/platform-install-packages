"""Offline tests of characterization gates using sanitized probe evidence."""
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
SCRIPT = ROOT / 'tools/php83/patch-tests/collect-mysql-init.py'


class MysqlInitCollectorTests(unittest.TestCase):
    def setUp(self):
        evidence = ROOT / 'doc/php83/evidence/debug-pdo/mysql-serializer/behavior.json'
        self.records = copy.deepcopy(json.loads(evidence.read_text())['records'])

    def collect(self):
        runs = [subprocess.CompletedProcess([], r['returncode'], r['stdout'], r['stderr'])
                for r in self.records]
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'report.json'
            with patch('sys.argv', [str(SCRIPT), str(output)]), patch('subprocess.run', side_effect=runs), \
                    contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as stop:
                runpy.run_path(str(SCRIPT), run_name='__main__')
            return stop.exception.code, json.loads(output.read_text())

    def test_known_raw_mismatch_is_recorded_not_hidden(self):
        code, report = self.collect()
        self.assertFalse(code)
        self.assertTrue(any(not c['raw_json_matches_74'] for c in report['comparisons']))

    def test_hydrated_regression_rejected(self):
        data = json.loads(self.records[-1]['stdout'])
        data['results'][0]['hydrated_json'] = '{"views":"42"}'
        self.records[-1]['stdout'] = json.dumps(data)
        self.assertTrue(self.collect()[0])

    def test_missing_configuration_rejected(self):
        data = json.loads(self.records[-1]['stdout'])
        data['results'].pop()
        self.records[-1]['stdout'] = json.dumps(data)
        self.assertTrue(self.collect()[0])

    def test_candidate_execution_failure_rejected(self):
        self.records[-1]['returncode'] = 255
        self.assertTrue(self.collect()[0])

    def test_unrelated_original_failure_rejected(self):
        self.records[2]['stderr'] = 'unrelated error'
        self.assertTrue(self.collect()[0])
