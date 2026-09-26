import importlib.util,json,unittest,tempfile
from pathlib import Path
s=importlib.util.spec_from_file_location('selected_phase',Path(__file__).with_name('select.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Selection(unittest.TestCase):
 def test_selected_rows_exact(self):
  raw=m.PROPOSAL.read_bytes();a=m.selected(raw);self.assertEqual(a['patches'],json.loads(raw)['patches']);self.assertTrue(a['selection_approved']);self.assertFalse(a['application_acceptance']);self.assertFalse(a['rank_body_persistence_tested']);self.assertFalse(a['zip_built'])
 def test_drift(self):
  with self.assertRaises(ValueError):m.selected(m.PROPOSAL.read_bytes()+b' ')
 def test_existing(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.stage(Path(d))
if __name__=='__main__':unittest.main()
