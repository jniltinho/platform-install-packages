import copy
import json
import unittest
import selected

class SelectedTests(unittest.TestCase):
    def setUp(self):
        self.payload = selected.stage.MANIFEST.read_bytes()
        self.good = selected.make_selected(self.payload)
    def test_exact_transition(self):
        self.assertEqual(selected.validate_selected(self.payload, json.dumps(self.good)), self.good)
        self.assertEqual(self.good['patches'], json.loads(self.payload)['patches'])
    def test_prepared_drift(self):
        with self.assertRaises(ValueError): selected.make_selected(self.payload + b' ')
    def test_patch_reorder(self):
        self.good['patches'].reverse()
        with self.assertRaises(ValueError): selected.validate_selected(self.payload, json.dumps(self.good))
    def test_production_escalation(self):
        self.good['selection_authorization']['production_approved'] = True
        with self.assertRaises(ValueError): selected.validate_selected(self.payload, json.dumps(self.good))
    def test_unexpected_metadata(self):
        self.good['unexpected'] = True
        with self.assertRaises(ValueError): selected.validate_selected(self.payload, json.dumps(self.good))
    def test_prepared_is_not_selected(self):
        with self.assertRaises(ValueError): selected.validate_selected(self.payload, self.payload)
