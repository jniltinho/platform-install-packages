"""Local negative controls; no SSH/database operations."""
import hashlib
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path
spec = importlib.util.spec_from_file_location('pdo_bootstrap_collect', Path(__file__).with_name('collect.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class CollectorValidation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.archive = Path(self.temp.name)/'fixture.zip'
        self.body = {'variant': 'exp9', 'php': '8.3.30', 'rows': module.expected_rows('exp9'), 'sources': {}}
        with zipfile.ZipFile(self.archive, 'w') as z:
            for name in module.CLASSES:
                path = 'fixture/'+name+'.php'
                data = ('<?php class '+name+' {}').encode()
                z.writestr('server-Rigel-18.20.0/'+path, data)
                self.body['sources'][name] = {'path': path, 'sha256': hashlib.sha256(data).hexdigest()}
    def test_named_input_fixture_regression(self):
        # Static guard for the retained first-attempt HY093 fixture defect.
        probe = Path(__file__).with_name('probe.php').read_text()
        self.assertIn("INSERT INTO bool_probe VALUES (2, :p1)", probe)
        self.assertIn("$statement->execute(array('p1' => 23))", probe)
        self.assertNotIn("$statement->execute(array(23))", probe)
    def test_candidate(self):
        self.assertEqual(module.validate(self.body, 'exp9', self.archive), self.body)
    def test_previous_null_contract(self):
        self.body.update(variant='exp8', rows=module.expected_rows('exp8'))
        self.assertEqual(module.validate(self.body, 'exp8', self.archive), self.body)
    def test_integer_not_boolean(self):
        self.body['rows'][1][1] = 1
        with self.assertRaises(RuntimeError): module.validate(self.body, 'exp9', self.archive)
    def test_extra_secret_field(self):
        self.body['token'] = 'do-not-persist'
        with self.assertRaises(RuntimeError): module.validate(self.body, 'exp9', self.archive)
    def test_unexpected_case_text(self):
        self.body['rows'].append(['secret', 'do-not-persist'])
        with self.assertRaises(RuntimeError): module.validate(self.body, 'exp9', self.archive)
    def test_source_drift(self):
        self.body['sources']['KalturaPDO']['sha256'] = '0'*64
        with self.assertRaises(RuntimeError): module.validate(self.body, 'exp9', self.archive)
    def test_traversal(self):
        self.body['sources']['KalturaPDO']['path'] = '../private.php'
        with self.assertRaises(RuntimeError): module.validate(self.body, 'exp9', self.archive)
    def test_variant_mismatch(self):
        with self.assertRaises(RuntimeError): module.validate(self.body, 'exp8', self.archive)
    def test_wrong_runtime(self):
        self.body['php'] = '7.4.33'
        with self.assertRaises(RuntimeError): module.validate(self.body, 'exp9', self.archive)
    def test_missing_real_dependency(self):
        del self.body['sources']['kApiCache']
        with self.assertRaises(RuntimeError): module.validate(self.body, 'exp9', self.archive)

if __name__ == '__main__': unittest.main()
