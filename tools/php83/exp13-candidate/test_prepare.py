import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
s=importlib.util.spec_from_file_location('prepare',Path(__file__).with_name('prepare.py'));p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
class Guards(unittest.TestCase):
 def test_pinned_inputs(self):self.assertEqual(len(p.metadata()[1]),8)
 def test_exact_delta_inventory(self):self.assertEqual(len(p.entries(p.metadata()[0])),13)
 def test_input_drift(self):
  with patch.object(p,'repo',return_value=b'corrupt'):
   with self.assertRaises(ValueError):p.metadata()
 def test_duplicate_delta(self):
  d=p.metadata()[0];d['aws']['changes'].append(d['aws']['changes'][0])
  with self.assertRaises(ValueError):p.entries(d)
 def test_existing_output(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):p.prepare(b'',b'',Path(d))
 def test_archive_identity(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):p.prepare(b'',b'',Path(d)/'new')
 def test_cumulative_replay(self):
  a=b'first\nlast\n';b=b'first\nnew\nlast\n';delta=p.cumulative(a,b,'source.php');self.assertEqual(p.apply(a,'source.php',delta,p.sha(b)),b)
 def test_after_hash(self):
  a=b'a\n';b=b'b\n'
  with self.assertRaises(ValueError):p.apply(a,'x.php',p.cumulative(a,b,'x.php'),'0'*64)
 def test_proposal_not_selected(self):
  m=json.loads((p.E/'proposed-r1/manifest.json').read_bytes())
  self.assertIs(m['selection_approved'],False);self.assertIs(m['zip_built'],False);self.assertEqual(len(m['patches']),75)
  self.assertEqual(sum(r['operation']=='add' for r in m['patches'] if 'operation' in r),1)
if __name__=='__main__':unittest.main()
