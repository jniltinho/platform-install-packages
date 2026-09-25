import unittest
import prepare
class PreparationTests(unittest.TestCase):
    def test_single_declaration(self):
        old=b'<?php\nclass Criteria implements IteratorAggregate {\n}\n'
        new=prepare.propose(old)
        self.assertEqual(new.replace(b'\n\tpublic $creteria_filter_attached = null;',b''),old)
    def test_missing_anchor(self):
        with self.assertRaises(ValueError):prepare.propose(b'wrong')
    def test_duplicate_anchor(self):
        with self.assertRaises(ValueError):prepare.propose(b'class Criteria implements IteratorAggregate {'*2)
    def test_existing_property(self):
        with self.assertRaises(ValueError):prepare.propose(b'class Criteria implements IteratorAggregate { $creteria_filter_attached; }')

class SourceLineTests(unittest.TestCase):
    def setUp(self):
        self.sources={prepare.CRITERIA:b'\n'*37+b'class Criteria implements IteratorAggregate {\n',prepare.FILTER:b'\n'*50+b'  $criteria_to_filter->creteria_filter_attached = true;\n'}
    def test_exact_lines(self):prepare.assert_source_lines(self.sources)
    def test_declaration_shift(self):
        self.sources[prepare.CRITERIA]=b'\n'+self.sources[prepare.CRITERIA]
        with self.assertRaises(ValueError):prepare.assert_source_lines(self.sources)
    def test_filter_shift(self):
        self.sources[prepare.FILTER]=b'\n'+self.sources[prepare.FILTER]
        with self.assertRaises(ValueError):prepare.assert_source_lines(self.sources)
