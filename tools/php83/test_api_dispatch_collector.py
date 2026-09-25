"""Offline checks: diagnostic collection must not turn dispatch failures green."""
import json
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).parent / 'patch-tests' / 'collect-api-dispatch.py'


class DispatchCollectorTests(unittest.TestCase):
    def collect(self, codes):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'report.json'
            results = [subprocess.CompletedProcess([], code, 'output', 'diagnostic') for code in codes]
            with patch('sys.argv', [str(SCRIPT), str(output)]), \
                    patch('subprocess.run', side_effect=results) as runner, \
                    patch('builtins.print'), self.assertRaises(SystemExit) as caught:
                runpy.run_path(str(SCRIPT), run_name='__main__')
            report = json.loads(output.read_text())
            self.assertEqual([r['returncode'] for r in report['records']], codes)
            self.assertIn('not API acceptance', report['scope'])
            self.assertEqual(runner.call_count, 2)
            self.assertEqual(runner.call_args_list[0].args[0][3], 'baseline74')
            self.assertEqual(runner.call_args_list[1].args[0][3], 'php83')
            return caught.exception.code

    def test_both_fail(self):
        self.assertEqual(self.collect([255, 255]), 1)

    def test_one_fails(self):
        self.assertEqual(self.collect([0, 255]), 1)

    def test_collection_success_is_bounded(self):
        self.assertEqual(self.collect([0, 0]), 0)
