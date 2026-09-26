"""Offline adapter guards; never SSH or run a PHP/application body."""
import hashlib, importlib.util, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
class Adaptation(unittest.TestCase):
 def test_parent_frozen(self):
  pins=json.loads((ROOT/'doc/php83/evidence/exp13-runtime/adaptation-parent-pins.json').read_text())
  for path,pin in pins.items(): self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),pin,path)
 def test_exact_pin(self):
  self.assertEqual((HERE/'artifact-sha256.txt').read_text().strip(),'6d0bc4947207e6c5457b7843948d263aa8d5f251480e58cbf9086c0add79a944')
 def test_prior_references(self):
  for p in [HERE/'collect.py',HERE.parent/'exp13-regression/batch.py']:
   s=p.read_text(); self.assertIn('/home/vagrant/php-exp12-regression/api/verify-source.py',s)
   self.assertIn('de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b',s)
   self.assertNotIn('exp11',s)
 def test_stage_scope(self):
  s=(HERE/'stage.sh').read_text()
  self.assertNotIn('autoload83',s);self.assertNotIn('curly-offsets',s)
  self.assertIn('EXTRACTED_VERIFIED_EXP13',s)
 def test_cli_inventory(self):
  import ast
  t=ast.parse((HERE.parent/'exp13-regression/batch.py').read_text())
  vals=[n.value for n in ast.walk(t) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
  for case in ['environment','legacy-json','zend-json','doc-comment','doc-comment-export','doc-comment-consumer']:self.assertIn(case,vals)
  for ini in ['standard','minimal']:self.assertIn(ini,vals)
  self.assertIn('exp12/php74',vals);self.assertIn('exp13/php74',vals)
if __name__=='__main__':unittest.main()
