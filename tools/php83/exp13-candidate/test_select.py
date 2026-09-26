import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
s=importlib.util.spec_from_file_location('selector',Path(__file__).with_name('select.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Selection(unittest.TestCase):
 def test_authorized(self):
  original=(m.PROPOSAL/'manifest.json').read_bytes();d=json.loads(original);r=m.selected(original)
  self.assertIs(r['selection_approved'],True);self.assertIs(r['application_acceptance'],False);self.assertIs(r['zip_built'],False)
  self.assertEqual(r['patches'],d['patches']);self.assertIs(r['selection_authorization']['production_approved'],False)
 def test_drift(self):
  with self.assertRaises(ValueError):m.selected((m.PROPOSAL/'manifest.json').read_bytes()+b' ')
 def test_existing(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.stage(Path(d))
 def test_sql_drift(self):
  original=m.sha
  def changed(b):return 'bad' if b.startswith(b'{\n  "status": "BOUNDED_SQL') else original(b)
  with patch.object(m,'sha',side_effect=changed):
   with self.assertRaises(ValueError):m.selected((m.PROPOSAL/'manifest.json').read_bytes())
if __name__=='__main__':unittest.main()
