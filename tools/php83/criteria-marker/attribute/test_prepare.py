import unittest
import prepare
class PrepareTests(unittest.TestCase):
    def setUp(self):self.source=b'<?php\n'+b'\n'*36+b'class Criteria implements IteratorAggregate {\n}\n'
    def test_exact_single_attribute(self):
        actual=prepare.attribute(self.source)
        self.assertEqual(actual.replace(b'#[\\AllowDynamicProperties]\n',b''),self.source)
    def test_line_drift(self):
        with self.assertRaises(ValueError):prepare.attribute(b'\n'+self.source)
    def test_duplicate_anchor(self):
        with self.assertRaises(ValueError):prepare.attribute(self.source+self.source)
    def test_existing_attribute(self):
        with self.assertRaises(ValueError):prepare.attribute(self.source+b'AllowDynamicProperties')
