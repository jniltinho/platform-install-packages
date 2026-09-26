import importlib.util,json,unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('proposal',Path(__file__).with_name('prepare.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Proposal(unittest.TestCase):
 def test_pinned_native_proof(self):self.assertEqual(len(m.native_proof()),11)
 def test_exact_seven_bytes(self):
  E=m.ROOT/'doc/php83/evidence/rank-signature-repair/prepared-r1';m.rank_bytes((E/'original.php').read_bytes(),(E/'candidate.php').read_bytes())
 def test_body_mutation(self):
  E=m.ROOT/'doc/php83/evidence/rank-signature-repair/prepared-r1'
  with self.assertRaises(ValueError):m.rank_bytes((E/'original.php').read_bytes(),(E/'candidate.php').read_bytes()+b'\n')
 def test_no_change(self):
  b=m.BEFORE
  with self.assertRaises(ValueError):m.rank_bytes(b,b)
 def test_existing_output(self):
  with self.assertRaises(ValueError):m.prepare(b'',b'',m.HERE)
 def test_proof_drift(self):
  with patch.object(m,'sha',return_value='bad'):
   with self.assertRaises(ValueError):m.native_proof()
 def test_proposal_preserves75_not_selected(self):
  d=json.loads((m.ROOT/'doc/php83/evidence/exp14-candidate/proposed-r1/manifest.json').read_bytes());prior=m.inputs()[0]['exp13']
  self.assertEqual(d['patches'][:75],prior['patches']);self.assertEqual(len(d['patches']),76);self.assertFalse(d['selection_approved']);self.assertFalse(d['zip_built']);self.assertFalse(d['rank_body_persistence_tested']);self.assertNotIn('selection_authorization',d)
if __name__=='__main__':unittest.main()
