"""Offline harness failure-path tests; real PHP evidence lives under doc/php83."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch, Mock

spec = importlib.util.spec_from_file_location(
    'runtime_probes', Path(__file__).with_name('run-runtime-probes.py'))
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


class RuntimeTests(unittest.TestCase):
    def test_probe_ids_unique(self):
        self.assertEqual(len(runtime.PROBES), len(set(runtime.PROBES)))
        self.assertEqual(len(runtime.PROBES), 15)

    def test_records_failure_without_success_claim(self):
        with tempfile.TemporaryDirectory() as folder:
            probe = Path(folder) / 'probe.php'
            probe.write_text('<?php')
            result = Mock(returncode=255, stdout=folder + '/test', stderr='fatal')
            with patch.object(runtime, 'PROBES', ['one']), \
                 patch.object(runtime.subprocess, 'run', return_value=result), \
                 patch.object(runtime.subprocess, 'check_output', side_effect=['PHP test', 'json\npdo', 'test.ini']):
                report = runtime.collect(Path(folder), 'php', probe)
            self.assertEqual(report['results'][0]['returncode'], 255)
            self.assertEqual(report['results'][0]['stdout'], '<public-app>/test')
            self.assertEqual(report['modules'], ['json', 'pdo'])

    def test_timeout_is_not_success(self):
        with tempfile.TemporaryDirectory() as folder:
            probe = Path(folder) / 'probe.php'
            probe.write_text('<?php')
            with patch.object(runtime, 'PROBES', ['one']), \
                 patch.object(runtime.subprocess, 'run', side_effect=subprocess.TimeoutExpired('php', 30)), \
                 patch.object(runtime.subprocess, 'check_output', return_value='PHP test'):
                report = runtime.collect(Path(folder), 'php', probe)
            self.assertIsNone(report['results'][0]['returncode'])
            self.assertTrue(report['results'][0]['timeout'])

    def test_sandbox_rejects_root(self):
        with patch.object(runtime.os, 'geteuid', return_value=0):
            with self.assertRaises(RuntimeError):
                runtime.verify_sandbox(Path('/'))

    def test_sandbox_rejects_writable_payload(self):
        with patch.object(runtime.os, 'geteuid', return_value=65534), \
             patch.object(runtime.os, 'statvfs', return_value=Mock(f_flag=0)):
            with self.assertRaises(RuntimeError):
                runtime.verify_sandbox(Path('/'))


if __name__ == '__main__':
    unittest.main()
